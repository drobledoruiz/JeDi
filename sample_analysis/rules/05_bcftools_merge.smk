import os
import math

idir = config['vcftools_filter']['output_dir']
odir = config['bcftools_merge']['output_dir'] 

# Ensure output directory exists before writing intermediate files
os.makedirs(odir, exist_ok=True)

# Use batch size of 2 for memory efficiency
batch_size = 2

# Level 0: merge original samples into batches
subset_vcf = [bams[i:i+batch_size] for i in range(0, len(bams), batch_size)]
num_level0_files = len(subset_vcf)
subfiles = [f"subcvf{i}" for i in range(num_level0_files)]

# Creates files with filenames to merge for level 0
for i in range(len(subset_vcf)):
	with open(odir + subfiles[i], "w") as file:
		for line in subset_vcf[i]:
			file.write(idir + line + '.sort.vcf.gz\n')

# Calculate how many subsequent levels we need
num_files = num_level0_files
level_counts = [num_files]
while num_files > batch_size:
	num_files = math.ceil(num_files / batch_size)
	level_counts.append(num_files)

# Function to get subset files for level 0
def get_subset_files(wildcards):
	i = int(wildcards.i)
	if i < len(subset_vcf):
		return [idir + s + '.sort.vcf.gz' for s in subset_vcf[i]]
	return []

# Function to get input files for higher levels
def get_level_inputs(wildcards, from_level):
	i = int(wildcards.i)
	start_idx = i * batch_size
	end_idx = min(start_idx + batch_size, level_counts[from_level])
	return [f"{odir}level{from_level}_merge.{j}.vcf.gz" for j in range(start_idx, end_idx)]

###############################################################################	
# Level 0: Merge original sample VCFs
rule bcftools_level0_merge:
	input:
		files = get_subset_files,
		names = odir + 'subcvf{i}'
	output:
		odir + 'level0_merge.{i}.vcf.gz'
	threads:
		config['threads']
	log:
		config['bcftools_merge']['logs'] + 'level0_merge.{i}.log'
	shell:
		"bcftools merge --file-list {input.names} --force-single --threads {threads} -Oz -o {output} 2>{log} && "
		"bcftools index -c {output} 2>>{log}"

###############################################################################
# Define enough intermediate merge levels to handle up to 7 levels deep
# (This handles up to 2^7 = 128 initial files with batch_size=2)

if len(level_counts) > 1:
	rule bcftools_level1_merge:
		input:
			lambda wildcards: get_level_inputs(wildcards, 0)
		output:
			odir + 'level1_merge.{i}.vcf.gz'
		threads:
			config['threads']
		log:
			config['bcftools_merge']['logs'] + 'level1_merge.{i}.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && "
			"bcftools index -c {output} 2>>{log}"

if len(level_counts) > 2:
	rule bcftools_level2_merge:
		input:
			lambda wildcards: get_level_inputs(wildcards, 1)
		output:
			odir + 'level2_merge.{i}.vcf.gz'
		threads:
			config['threads']
		log:
			config['bcftools_merge']['logs'] + 'level2_merge.{i}.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && "
			"bcftools index -c {output} 2>>{log}"

if len(level_counts) > 3:
	rule bcftools_level3_merge:
		input:
			lambda wildcards: get_level_inputs(wildcards, 2)
		output:
			odir + 'level3_merge.{i}.vcf.gz'
		threads:
			config['threads']
		log:
			config['bcftools_merge']['logs'] + 'level3_merge.{i}.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && "
			"bcftools index -c {output} 2>>{log}"

if len(level_counts) > 4:
	rule bcftools_level4_merge:
		input:
			lambda wildcards: get_level_inputs(wildcards, 3)
		output:
			odir + 'level4_merge.{i}.vcf.gz'
		threads:
			config['threads']
		log:
			config['bcftools_merge']['logs'] + 'level4_merge.{i}.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && "
			"bcftools index -c {output} 2>>{log}"

if len(level_counts) > 5:
	rule bcftools_level5_merge:
		input:
			lambda wildcards: get_level_inputs(wildcards, 4)
		output:
			odir + 'level5_merge.{i}.vcf.gz'
		threads:
			config['threads']
		log:
			config['bcftools_merge']['logs'] + 'level5_merge.{i}.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && "
			"bcftools index -c {output} 2>>{log}"

if len(level_counts) > 6:
	rule bcftools_level6_merge:
		input:
			lambda wildcards: get_level_inputs(wildcards, 5)
		output:
			odir + 'level6_merge.{i}.vcf.gz'
		threads:
			config['threads']
		log:
			config['bcftools_merge']['logs'] + 'level6_merge.{i}.log'
		shell:
			"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && "
			"bcftools index -c {output} 2>>{log}"

###############################################################################
# Final merge: get the final output from the last level
final_level = len(level_counts) - 1

rule bcftools_final_merge:
	input:
		expand(odir + f'level{final_level}_merge.{{i}}.vcf.gz', 
		       i=range(level_counts[final_level]))
	output:
		config['bcftools_merge']['output_dir'] + 'all_merged.vcf.gz'
	threads:
		config['threads']
	log:
		config['bcftools_merge']['logs'] + 'final_merge.log'
	shell:
		"bcftools merge --force-single --threads {threads} {input} -Oz -o {output} 2>{log} && "
		"bcftools index -c {output} 2>>{log}"