#######################################################################################
rule bcftools_sort:
	input:
		config['vcftools_filter']['output_dir'] + '{xyz}.vcf.gz'
	output:
		config['vcftools_filter']['output_dir'] + '{xyz}.sort.vcf.gz'
	log:
		config['bcftools_sort']['logs'] + '{xyz}.log'
	params:
		tempdir = config['vcftools_filter']['output_dir'] + '{xyz}/'
	shell:
		"mkdir -p {params.tempdir} && "
		"bcftools sort --temp-dir {params.tempdir} {input} -Oz -o {output} 2>{log} && "
		"bcftools index -c {output} 2>>{log} && "
		"rmdir {params.tempdir}"