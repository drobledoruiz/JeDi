import os
import math

ndir = os.path.normpath(config['python_filter']['output_dir'])

# Ensure output directory exists for intermediate files
os.makedirs(ndir, exist_ok=True)

# Creates files with filenames to merge
for i in range(len(subfiles)):
        with open(ndir + '/' + subfiles[i], "w") as file:
                for line in subset_vcf[i]:
                        file.write(ndir + '/' + line + '.sort.vcf.gz\n')

with open(ndir + '/merge.txt', "w") as file:
        for i in range(len(subfiles)):
                file.write(ndir + f'/merge.{i}.vcf.gz\n')

# Calculate merge levels for filtered VCFs (at top level like 05_bcftools_merge.smk)
batch_size_filter = 2
num_filter_files = len(subfiles)

# Calculate number of outputs at each level
filter_level_counts = []
current_count = num_filter_files
while current_count > batch_size_filter:
	current_count = math.ceil(current_count / batch_size_filter)
	filter_level_counts.append(current_count)
filter_level_counts.append(math.ceil(current_count / batch_size_filter))

# Functions for getting inputs
def get_filter_merge_files(wildcards):
	"""Get input merge files for level 0 batching"""
	i = int(wildcards.i)
	start_idx = i * batch_size_filter
	end_idx = min(start_idx + batch_size_filter, num_filter_files)
	return [ndir + f'/merge.{j}.vcf.gz' for j in range(start_idx, end_idx)]

def get_filter_level_inputs(wildcards, from_level):
	"""Get input files for a given merge level"""
	i = int(wildcards.i)
	start_idx = i * batch_size_filter
	prev_level_count = filter_level_counts[from_level]
	end_idx = min(start_idx + batch_size_filter, prev_level_count)
	return [f"{ndir}/filter_level{from_level}_merge.{j}.vcf.gz" for j in range(start_idx, end_idx)]

#######################################################################################

if config['python_filter']['mac'] > 0:

	rule get_singletons:
		input:
			config['bcftools_merge']['output_dir']  + 'all_merged.vcf.gz'
		output:
			ndir + '/all_merged.singletons'
		log:
			config['bcftools_merge']['logs'] + 'all_merged.log'
		params:
			file = ndir + '/all_merged',
			mac = config['python_filter']['mac']
		shell:
			"vcftools --gzvcf {input} --min-alleles 2 --mac {params.mac} "
			"--max-mac 2 --singletons --out {params.file} 2>>{log}"


	##################################################################################
	rule filter_singletons:
		input:
			vcf  = config['vcftools_filter']['output_dir']  + "{xyz}.sort.vcf.gz",
			sing = ndir + "/all_merged.singletons"
		output:
			ndir + "/{xyz}.sort.vcf.gz"
		log:
			config['python_filter']['logs'] + "{xyz}.log"
		params:
			new_vcf = ndir  + "/{xyz}.sort.vcf",
		shell:
			"python /workspace/sample_analysis/scripts/02_filter_singletons.py -v {input.vcf} -o {params.new_vcf} -s {input.sing} -n {wildcards.xyz} -gz > {log} 2>&1"
	#########################################################################################       	
	rule bcftools_submerge2:
		input:
			files = expand(ndir + "/{xyz}.sort.vcf.gz", xyz=bams,),
			names = ndir + '/subcvf{i}'
		output:
			ndir + '/merge.{i}.vcf.gz'
		log:
			config['python_filter']['logs'] + 'merge.{i}.log'
		shell:
			"bcftools merge --file-list {input.names} --force-single -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"

	###############################################################################
	# Hierarchical merge rules for filtered VCFs
	
	rule bcftools_filter_level0_merge:
		input:
			get_filter_merge_files
		output:
			ndir + '/filter_level0_merge.{i}.vcf.gz'
		threads:
			config['threads']
		log:
			config['python_filter']['logs'] + 'filter_level0_merge.{i}.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"
	
	if len(filter_level_counts) > 1:
		rule bcftools_filter_level1_merge:
			input:
				lambda wildcards: get_filter_level_inputs(wildcards, 0)
			output:
				ndir + '/filter_level1_merge.{i}.vcf.gz'
			threads:
				config['threads']
			log:
				config['python_filter']['logs'] + 'filter_level1_merge.{i}.log'
			shell:
				"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"
	
	if len(filter_level_counts) > 2:
		rule bcftools_filter_level2_merge:
			input:
				lambda wildcards: get_filter_level_inputs(wildcards, 1)
			output:
				ndir + '/filter_level2_merge.{i}.vcf.gz'
			threads:
				config['threads']
			log:
				config['python_filter']['logs'] + 'filter_level2_merge.{i}.log'
			shell:
				"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"
	
	if len(filter_level_counts) > 3:
		rule bcftools_filter_level3_merge:
			input:
				lambda wildcards: get_filter_level_inputs(wildcards, 2)
			output:
				ndir + '/filter_level3_merge.{i}.vcf.gz'
			threads:
				config['threads']
			log:
				config['python_filter']['logs'] + 'filter_level3_merge.{i}.log'
			shell:
				"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"
	
	if len(filter_level_counts) > 4:
		rule bcftools_filter_level4_merge:
			input:
				lambda wildcards: get_filter_level_inputs(wildcards, 3)
			output:
				ndir + '/filter_level4_merge.{i}.vcf.gz'
			threads:
				config['threads']
			log:
				config['python_filter']['logs'] + 'filter_level4_merge.{i}.log'
			shell:
				"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"
	
	if len(filter_level_counts) > 5:
		rule bcftools_filter_level5_merge:
			input:
				lambda wildcards: get_filter_level_inputs(wildcards, 4)
			output:
				ndir + '/filter_level5_merge.{i}.vcf.gz'
			threads:
				config['threads']
			log:
				config['python_filter']['logs'] + 'filter_level5_merge.{i}.log'
			shell:
				"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"
	
	final_filter_level = len(filter_level_counts) - 1
	rule bcftools_filter_final_merge:
		input:
			expand(ndir + f'/filter_level{final_filter_level}_merge.{{i}}.vcf.gz',
			       i=range(filter_level_counts[final_filter_level]))
		output:
			ndir + '/all_merged_filtered.vcf.gz'
		threads:
			config['threads']
		log:
			config['python_filter']['logs'] + 'filter_final_merge.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && bcftools index -c {output} 2>>{log}"

else:
	rule skip_merge2:
		input:
			config['bcftools_merge']['output_dir']  + 'all_merged.vcf.gz'
		output:
			ndir + '/all_merged_filtered.vcf.gz'
		log:
			config['python_filter']['logs'] + 'skip_all_merged.log'
		shell:
			"ln -sf $(pwd)/{input} {output} && bcftools index -c {output} 2>>{log}"
