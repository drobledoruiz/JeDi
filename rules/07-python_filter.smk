#######################################################################################
rule get_singletons:
	input:
		config['bcftools_merge']['output_dir']  + 'all_merged_names.vcf.gz'
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
		vcf  = config['bcftools_merge']['output_dir']  + 'all_merged_names.vcf.gz',
		sing = config['python_filter']['output_dir'] + 'all_merged_names.singletons'
	output:
		head = config['python_filter']['output_dir']  + 'temp.header',
		temp = config['python_filter']['output_dir']  + 'temp.file',
	log:
		config['python_filter']['log']
	params:
		old_vcf = config['bcftools_merge']['output_dir']  + 'all_merged_names.vcf',
	shell:
		"bgzip -d -k -f {input.vcf} && "
		"python scripts/02-filter_singletons.py -v {params.old_vcf} -o {output.temp} -s {input.sing} 2>>{log} && "
		"rm {params.old_vcf}"
	
#########################################################################################	
rule create_filltered_vcf:
	input:
		head = config['python_filter']['output_dir']  + 'temp.header',
		temp = config['python_filter']['output_dir']  + 'temp.file',
	output:
		config['python_filter']['output_dir'] + 'all_merged_names_filtered.vcf.gz'
	params:
		new_file = config['python_filter']['output_dir'] + 'all_merged_names_filtered.vcf',
	shell:
		"cat {input.head} > {params.new_file} && cat {input.temp} >> {params.new_file} && "
		"bgzip {params.new_file} && "
		"bcftools index {output} && "
		"rm {input.head} {input.temp}"
 
				
		
