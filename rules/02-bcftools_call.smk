#######################################################################################
rule bcftools_call:
	input:
		bam = config['gstacks']['input_dir'] + '{xyz}.bam',
		bed = config['fasta2bed']['dir_stacks'] + 'catalog_sorted_merged.bed',
		genome = config['ref_genome'],
	output:
		config['bcftools_call']['output_dir'] + '{xyz}.vcf.gz'
	log:
		config['bcftools_call']['logs'] + '{xyz}.log'
	shell:
		"bcftools mpileup -Ou -Q 30 -q 30 -a FORMAT/DP -R {input.bed} -f {input.genome} {input.bam} | "
		"bcftools call -c -f GQ -O u | bcftools filter -e 'QUAL<30' -O z -o {output} 2>{log} "
