#######################################################################################

#print(os.system(f'ls 00-reads/'))

rule samtools_index:
	input:
		config['gstacks']['input_dir'] + '{xyz}.bam'
	output:
		config['gstacks']['input_dir'] + '{xyz}.bam.csi'
	threads:
		config['threads']
	shell:
		"samtools index -c -@ {threads} {input}"
