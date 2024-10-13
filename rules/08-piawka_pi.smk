#######################################################################################
rule piawka_pi:
	input:
		bed = config['fasta2bed']['dir_stacks'] + 'catalog_sorted_merged.bed',
		vcf = config['python_filter']['output_dir']  + 'all_merged_filtered.vcf.gz',
		poi = config['piawka']['output_dir']  + 'ids_kept.tsv'
	output:
		config['piawka']['output_dir']  + 'piawka_pi_dxy_fst.tsv'
	params:
		config['piawka']['script_dir']
	threads:
		config['threads']
	log:
		config['piawka']['log_pi']
	shell:
		"bash {params}piawka_par.sh -a '-j {threads}' -b {input.bed} -g {input.poi} "
		"-v {input.vcf} -p 'MULT=1 FST=1 DXY=1 PIXY=1 VERBOSE=1' 2>{log} 1>{output}"


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
		"python scripts/04-genomic_piawka_pi_dxy_fst.py {input} 2>{log}"

