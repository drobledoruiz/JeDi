#######################################################################################
rule piawka_pi:
	input:
		bed = config.get('sample_analysis_bed', '../sample_analysis/' + config['fasta2bed']['dir_stacks'] + 'catalog_sorted_merged.bed'),
		vcf = config.get('sample_analysis_vcf', '../sample_analysis/' + config['python_filter']['output_dir']  + 'all_merged_filtered.vcf.gz'),
		poi = config['pop_kept']
	output:
		config['piawka']['output_dir']  + 'piawka_pi_dxy_fst.tsv'
	params:
		config['piawka']['script_dir']
	threads:
		config['threads']
	log:
		config['piawka']['log_pi']
	shell:
		"piawka -j {threads} -b {input.bed} -g {input.poi} "
		"-v {input.vcf} -m -f 2>{log} 1>{output}"


#######################################################################################
rule piawka_agg_pi:
	input:
		config['piawka']['output_dir']  + 'piawka_pi_dxy_fst.tsv'		
	output:
		config['piawka_agg']['output_dir']  + 'genomic_dxy_matrix.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_dxy_table.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_fst_matrix.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_fst_table.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_pi_table.tsv'
	log:
		config['piawka_agg']['logs'] + 'pi_dxy.log'
	shell:
		"python /workspace/population_analysis/scripts/04_genomic_piawka_pi_dxy_fst.py {input} 2>{log}"

