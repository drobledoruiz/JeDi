#######################################################################################
rule get_singletons:
	input:
		config['bcftools_merge']['output_dir']  + 'all_merged.vcf.gz'
	output:
		config['python_filter']['output_dir'] + 'all_merged_names.singletons'
	log:
		config['python_filter']['log']
	params:
		file = config['python_filter']['output_dir'] + 'all_merged_names'
	shell:
		"vcftools --gzvcf {input} --min-alleles 2 --mac 2 --max-mac 2 --singletons --out {params.file} 2>{log}"
		
#######################################################################################
rule filter_singletons:
	input:
		vcf  = config['bcftools_merge']['output_dir']  + 'all_merged.vcf.gz',
		sing = config['python_filter']['output_dir'] + 'all_merged_names.singletons'
	output:
		config['python_filter']['output_dir'] + 'all_merged_names_filtered.vcf.gz'
	log:
		config['python_filter']['log']
	params:
		file = config['python_filter']['output_dir'] + 'all_merged_names_filtered.vcf'
	shell:
		"python scripts/02-filter_singletons.py -v {input.vcf} -o {params.file} -s {input.sing} -g 2>>{log} && "
		"bgzip {params.file} 2>>{log} && "
		"bcftools index {output}"
