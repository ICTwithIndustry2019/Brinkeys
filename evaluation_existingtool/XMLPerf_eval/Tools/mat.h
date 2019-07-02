#pragma once

#include <iostream>
#include <string>
#include <algorithm>
#include <vector>
#include <fstream>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <cfloat>
#include <cassert>

#include "config.h"
#include "utils.h"

using namespace std;

/* ------------------- Sparse and dense matrix and vector resources ---------------------- */

template <typename T>
class SVec // a sparse column-vector of type T
{
public:
	_int nr;
	_int size;
	pair<_int,T>* data;

	SVec()
	{
		nr = 0;
		size = 0;
		data = NULL;
	}

	SVec(_int nr, _int size)
	{
		this->nr = nr;
		this->size = size;
		data = new pair<_int,T>[size];
	}

	~SVec()
	{
		delete [] data;
	}

	pair<_int,T>& operator[](const _int i)
	{
		return data[i];
	}

};

template <typename T>
class SMat // a column-major sparse matrix of type T
{
public:
	_int nc;
	_int nr;
	_int* size;
	pair<_int,T>** data;

	SMat()
	{
		nc = 0;
		nr = 0;
		size = NULL;
		data = NULL;
	}

	SMat(_int nr, _int nc)
	{
		this->nr = nr;
		this->nc = nc;
		size = new _int[nc]();
		data = new pair<_int,T>*[nc];
		for(_int i=0; i<nc; i++)
			data[i] = NULL;
	}
	
	SMat(SMat<T>* mat)
	{
		nc = mat->nc;
		nr = mat->nr;
		size = new _int[nc];

		for(_int i=0; i<nc; i++)
			size[i] = mat->size[i];

		data = new pair<_int,T>*[nc];
		for(_int i=0; i<nc; i++)
		{
			data[i] = new pair<_int,T>[size[i]];
			for(_int j=0; j<size[i]; j++)
			{
				data[i][j] = mat->data[i][j];
			}	
		}	
	}

	SMat(string fname)
	{
		check_valid_filename(fname,true);

		ifstream fin;
		fin.open(fname);		

		vector<_int> inds;
		vector<T> vals;

		fin>>nc>>nr;
		size = new _int[nc];
		data = new pair<_int,T>*[nc];

		fin.ignore();
		for(_int i=0; i<nc; i++)
		{
			inds.clear();
			vals.clear();
			string line;
			getline(fin,line);
			line += "\n";
			_int pos = 0;
			_int next_pos;

			while(next_pos=line.find_first_of(": \n",pos))
			{
				if((size_t)next_pos==string::npos)
					break;
				inds.push_back(stoi(line.substr(pos,next_pos-pos)));
				pos = next_pos+1;

				next_pos = line.find_first_of(": \n",pos);
				if((size_t)next_pos==string::npos)
					break;

				vals.push_back(stof(line.substr(pos,next_pos-pos)));
				pos = next_pos+1;

			}

			assert(inds.size()==vals.size());
			assert(inds.size()==0 || inds[inds.size()-1]<nr);

			size[i] = inds.size();
			data[i] = new pair<_int,T>[inds.size()];

			for(_int j=0; j<size[i]; j++)
			{
				data[i][j].first = inds[j];
				data[i][j].second = (T)vals[j];
			}
		}	

		fin.close();
	}

	SMat<T>* transpose()
	{
		SMat<T>* tmat = new SMat<T>;
		tmat->nr = nc;
		tmat->nc = nr;
		tmat->size = new _int[tmat->nc]();
		tmat->data = new pair<_int,T>*[tmat->nc];

		for(_int i=0; i<nc; i++)
		{
			for(_int j=0; j<size[i]; j++)
			{
				tmat->size[data[i][j].first]++;
			}
		}

		for(_int i=0; i<tmat->nc; i++)
		{
			tmat->data[i] = new pair<_int,T>[tmat->size[i]];
		}

		_int* count = new _int[tmat->nc]();
		for(_int i=0; i<nc; i++)
		{
			for(_int j=0; j<size[i]; j++)
			{
				_int ind = data[i][j].first;
				T val = data[i][j].second;

				tmat->data[ind][count[ind]].first = i;
				tmat->data[ind][count[ind]].second = val;
				count[ind]++;
			}
		}

		delete [] count;
		return tmat;
	}

	void unit_normalize_columns()
	{
		for(_int i=0; i<nc; i++)
		{
			T normsq = 0;
			for(_int j=0; j<size[i]; j++)
				normsq += SQ(data[i][j].second);
			normsq = sqrt(normsq);

			if(normsq==0)
				normsq = 1;

			for(_int j=0; j<size[i]; j++)
				data[i][j].second /= normsq;
		}
	}

	vector<T> column_norms()
	{
		vector<T> norms(nc,0);

		for(_int i=0; i<nc; i++)
		{
			T normsq = 0;
			for(_int j=0; j<size[i]; j++)
				normsq += SQ(data[i][j].second);
			norms[i] = sqrt(normsq);
		}

		return norms;
	}

	~SMat()
	{
		delete [] size;
		for(_int i=0; i<nc; i++)
			delete [] data[i];
		delete [] data;
	}

	void write(string fname)
	{
		check_valid_filename(fname,false);

		ofstream fout;
		fout.open(fname);

		fout<<nc<<" "<<nr<<endl;

		for(_int i=0; i<nc; i++)
		{
			for(_int j=0; j<size[i]; j++)
			{
				if(j==0)
					fout<<data[i][j].first<<":"<<data[i][j].second;
				else
					fout<<" "<<data[i][j].first<<":"<<data[i][j].second;
			}
			fout<<endl;
		}

		fout.close();
	}

	void add(SMat<T>* smat)
	{
		if(nc != smat->nc || nr != smat->nr)
		{
			cerr<<"SMat::add : Matrix dimensions do not match"<<endl;
			cerr<<"Matrix 1: "<<nc<<" x "<<nr<<endl;
			cerr<<"Matrix 2: "<<smat->nc<<" x "<<smat->nr<<endl;
			exit(1);
		}

		bool* ind_mask = new bool[nr]();
		T* sum = new T[nr]();

		for(_int i=0; i<nc; i++)
		{
			vector<_int> inds;
			for(_int j=0; j<size[i]; j++)
			{
				_int ind = data[i][j].first;
				T val = data[i][j].second;

				sum[ind] += val;
				if(!ind_mask[ind])
				{
					ind_mask[ind] = true;
					inds.push_back(ind);
				}
			}

			for(_int j=0; j<smat->size[i]; j++)
			{
				_int ind = smat->data[i][j].first;
				T val = smat->data[i][j].second;

				sum[ind] += val;
				if(!ind_mask[ind])
				{
					ind_mask[ind] = true;
					inds.push_back(ind);
				}
			}

			sort(inds.begin(), inds.end());
			Realloc(size[i], inds.size(), data[i]);
			for(_int j=0; j<inds.size(); j++)
			{
				_int ind = inds[j];
				data[i][j] = make_pair(ind,sum[ind]);
				ind_mask[ind] = false;
				sum[ind] = 0;
			}
			size[i] = inds.size();
		}

		delete [] ind_mask;
		delete [] sum;
	}

	SMat<T>* prod(SMat<T>* mat2)
	{
		_int dim1 = nr;
		_int dim2 = mat2->nc;

		assert(nc==mat2->nr);

		SMat<T>* prodmat = new SMat<T>(dim1,dim2);
		vector<T> sum(dim1,0);

		for(_int i=0; i<dim2; i++)
		{
			vector<_int> indices;
			for(_int j=0; j<mat2->size[i]; j++)
			{
				_int ind = mat2->data[i][j].first;
				T prodval = mat2->data[i][j].second;

				for(_int k=0; k<size[ind]; k++)
				{
					_int id = data[ind][k].first;
					T val = data[ind][k].second;

					if(sum[id]==0)
						indices.push_back(id);

					sum[id] += val*prodval;
				}
			}

			sort(indices.begin(), indices.end());

			_int siz = indices.size();
			prodmat->size[i] = siz;
			prodmat->data[i] = new pair<_int,T>[siz];

			for(_int j=0; j<indices.size(); j++)
			{
				_int id = indices[j];
				T val = sum[id];
				prodmat->data[i][j] = make_pair(id,val);
				sum[id] = 0;
			}
		}

		return prodmat;
	}
};


template <typename T>
class DMat // a column-major dense matrix of type T
{
public:
	_int nc;
	_int nr;
	float** data;

	DMat()
	{
		nc = 0;
		nr = 0;
		data = NULL;
	}

	DMat(_int nc, _int nr)
	{
		this->nc = nc;
		this->nr = nr;
		data = new T*[nc];
		for(_int i=0; i<nc; i++)
			data[i] = new T[nr]();
	}

	DMat(SMat<T>* mat)
	{
		nc = mat->nc;
		nr = mat->nr;
		data = new T*[nc];
		for(_int i=0; i<nc; i++)
			data[i] = new T[nr]();

		for(_int i=0; i<mat->nc; i++)
		{
			pair<_int,T>* vec = mat->data[i];
			for(_int j=0; j<mat->size[i]; j++)
			{
				data[i][vec[j].first] = vec[j].second;
			}
		}
	}

	~DMat()
	{
		for(_int i=0; i<nc; i++)
			delete [] data[i];
		delete [] data;
	}
};

typedef vector<_int> VecI;
typedef vector<_float> VecF;
typedef vector<_double> VecD;
typedef vector<pairII> VecII;
typedef vector<pairIF> VecIF;
typedef vector<_bool> VecB;
typedef SMat<_float> SMatF;
