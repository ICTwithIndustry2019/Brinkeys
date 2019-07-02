To compile the performance evaluation scripts, execute "make" in the Tools folder from the Matlab terminal.

Following command outputs a struct containing all the metrics:

	[metrics] = get_all_metrics([test score matrix], [test label matrix], [inverse label propensity vector])

Individual metrics can be computed using following command:
- nDCG@k
		[nDCG@<1 to k>] = nDCG_k([test score matrix], [test label matrix], k)

- Precision@k
		[Precision@<1 to k>] = precision_k([test score matrix], [test label matrix], k)

- Propensity scored nDCG@k
		[Propensity scored nDCG@<1 to k>] = nDCG_wt_k([test score matrix], [test label matrix], [inverse label propensity vector], k)

- Propensity scored Precision@k
		[Propensity scored Precision@<1 to k>] = precision_wt_k([test score matrix], [test label matrix], [inverse label propensity vector], k)


test label and score matrices are in [num label] x [num points] sparse format.

[inverse label propensity vector] contains inverse propensity weights for each label. This vector can be obtained using the following command:
	[weights] = inv_propensity([train label matrix],A,B);
	A,B are parameters of the propensity model. Refer to the PfastreXML paper for more details.
	A,B values used for different datasets in the repository:
  WikiLSHTC-325K and Wikipedia-500K: A=0.5,  B=0.4
	Amazon-670K and Amazon-3M:         A=0.6,  B=2.6
	Other:			 											 A=0.55, B=1.5

