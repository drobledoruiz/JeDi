#######################################################################################
rule piawka_het:
	input:
		bed = config['fasta2bed']['dir_stacks'] + 'catalog_sorted_merged.bed',
		vcf = config['python_filter']['output_dir'] + 'all_merged_names_filtered.vcf.gz',
		poi = config['pop_index']
	output:
		config['piawka']['output_dir']  + 'piawka_het.tsv'
	params:
		config['piawka']['script_dir']
	threads:
		config['threads']
	log:
		config['piawka']['log_het']
	shell:
		'export PATH="{params}:$PATH" && '
		'bash {params}piawka_par.sh -a "-j {threads}"  -b {input.bed} -g {input.poi} -v {input.vcf} '
		'-p "HET=1 MULT=1 PIXY=1 VERBOSE=1" 2>{log} 1>{output}'

#######################################################################################
rule piawka_agg_het:
	input:
		het = config['piawka']['output_dir']  + 'piawka_het.tsv',
		poi = config['pop_index']
	output:
		config['piawka_agg']['output_dir']  + 'genomic_het_table.tsv',
		config['piawka']['output_dir']  + 'ids_filtered.tsv'
	log:
		config['piawka_agg']['logs'] + 'het.log'
	shell:
		'python scripts/03-genomic_piawka_het.py {input.het} -p {input.poi} 2>{log}'	
