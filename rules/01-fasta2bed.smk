#######################################################################################
rule fasta2bed:
	input:
		config['gstacks']['output_dir'] + 'catalog.fa.gz',
	output:
		config['fasta2bed']['dir_stacks'] + 'catalog_sorted_merged.bed',
	log:
		config['fasta2bed']['logs']
	params:
		pyscript = config['fasta2bed']['dir_script'] + '01-fasta2bed.py',
		bed = config['fasta2bed']['dir_stacks'] + 'catalog.bed',
		sorted_bed = config['fasta2bed']['dir_stacks'] + 'catalog_sorted.bed',
	shell:
		"python3 {params.pyscript} {input} {params.bed} 2>{log} && "
		"sortBed -i {params.bed} 1>{params.sorted_bed} 2>>{log} && "
		"mergeBed -i {params.sorted_bed} 1>{output}"
