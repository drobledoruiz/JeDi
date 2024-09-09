#######################################################################################
rule samtools_index:
	input:
		config['gstacks']['input_dir'] + '{xyz}.bam'
	output:
		config['gstacks']['input_dir'] + '{xyz}.bam.bai'
	threads:
		config['threads']
	shell:
		"samtools index -@ {threads} {input}"
