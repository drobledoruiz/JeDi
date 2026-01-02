#######################################################################################
rule gstacks:
	params:
		input_dir = config['gstacks']['input_dir'],
		output_dir = config['gstacks']['output_dir'],
		min_map_quality = config['gstacks']['min_map_quality'],
	threads:
		config['threads'],
	input:
		popmap = config['pop_index'],
		bams   = expand(config['gstacks']['input_dir'] + "{xyz}.bam", xyz=bams,),
		ibams  = expand(config['gstacks']['input_dir'] + "{xyz}.bam.csi", xyz=bams,),
	output:
		config['gstacks']['output_dir'] + 'catalog.fa.gz',
	log:
		config['gstacks']['logs']
	shell:
		"gstacks -I {params.input_dir} "
		"-M {input.popmap} "
		"-O {params.output_dir} "
		"--min-mapq {params.min_map_quality} "
		"-t {threads} >> {log} 2>&1"
