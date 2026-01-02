#######################################################################################
rule piawka_het:
	input:
		bed = config['fasta2bed']['dir_stacks'] + 'catalog_sorted_merged.bed',
		vcf = config['python_filter']['output_dir'] + 'all_merged_filtered.vcf.gz',
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
		"piawka -j {threads} -b {input.bed} -g {input.poi} -v {input.vcf} -H -m 2>{log} 1>{output}"

#######################################################################################
rule piawka_agg_het:
	input:
		het = config['piawka']['output_dir']  + 'piawka_het.tsv',
		poi = config['pop_index']
	output:
		config['piawka_agg']['output_dir']  + 'genomic_het_table.tsv'
	log:
		config['piawka_agg']['logs'] + 'het.log'
	shell:
		"python /workspace/sample_analysis/scripts/03_genomic_piawka_het.py {input.het} -p {input.poi} 2>{log}"
