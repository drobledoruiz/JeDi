#######################################################################################
rule bcftools_call:
	input:
		bam = config['gstacks']['input_dir'] + '{xyz}.bam',
		bed = config['fasta2bed']['dir_stacks'] + 'catalog_sorted_merged.bed',
		genome = "00-reads/reference.fa",
		idx = "00-reads/reference.fa.fai"
	output:
		config['bcftools_call']['output_dir'] + '_{xyz}_.vcf.gz'
	log:
		config['bcftools_call']['logs'] + '{xyz}.log'
	shell:
		"bcftools mpileup -Ou -Q 30 -q 30 -a FORMAT/DP -R {input.bed} -f {input.genome} {input.bam} | "
		"bcftools call -c -f GQ -O u | bcftools filter -e 'QUAL<30' -O z -o {output} 2>{log} "

#########################################################################################
rule reheader:
	input:
		config['bcftools_call']['output_dir'] + '_{xyz}_.vcf.gz'
	output:
		config['bcftools_call']['output_dir'] + '{xyz}_reheaded.vcf.gz'
	log:
		config['bcftools_call']['logs'] + '{xyz}.log'
	params:
		config['bcftools_call']['output_dir'] + '{xyz}_reheaded.vcf'
	shell:
		"python /workspace/sample_analysis/scripts/01_vcf_reheader.py -v {input} -o {params} -gz 2>>{log} "


