import os

ndir = config['python_filter']['output_dir']

# Creates files with filenames to merge
for i in range(len(subfiles)):
        with open(ndir + subfiles[i], "w") as file:
                for line in subset_vcf[i]:
                        file.write(ndir + line + '.sort.vcf.gz\n')

with open(ndir + 'merge.txt', "w") as file:
        for i in range(len(subfiles)):
                file.write(ndir + f'merge.{i}.vcf.gz\n')


#######################################################################################
rule get_singletons:
	input:
		config['bcftools_merge']['output_dir']  + 'all_merged.vcf.gz'
	output:
		ndir + 'all_merged.singletons'
	log:
		config['bcftools_merge']['logs'] + 'all_merged.log'
	params:
		file = ndir + 'all_merged',
		mac = config['python_filter']['mac']
	shell:
		"vcftools --gzvcf {input} --min-alleles 2 --mac {params.mac} "
		"--max-mac 2 --singletons --out {params.file} 2>>{log}"


##################################################################################
rule filter_singletons:
	input:
		vcf  = config['vcftools_filter']['output_dir']  + "{xyz}.sort.vcf.gz",
		sing = ndir + "all_merged.singletons"
	output:
		ndir + "{xyz}.sort.vcf.gz"
	log:
		config['python_filter']['logs'] + "{xyz}.log"
	params:
		new_vcf = ndir  + "{xyz}.sort.vcf",
	shell:
		"python scripts/02-filter_singletons.py -v {input.vcf} "
		"-o {params.new_vcf} -s {input.sing} -gz -n {wildcards.xyz} 2>>{log} "


#########################################################################################       	
rule bcftools_submerge2:
	input:
		files = expand(ndir + "{xyz}.sort.vcf.gz", xyz=bams,),
		names = ndir + 'subcvf{i}'
	output:
		ndir + 'merge.{i}.vcf.gz'
	log:
		config['python_filter']['logs'] + 'merge.{i}.log'
	shell:
		"bcftools merge --file-list {input.names} -Oz -o {output} 2>{log} && "
		"bcftools index -t {output} 2>>{log}"


###############################################################################
rule bcftools_merge2:
	input:
		files = expand(ndir + 'merge.{i}.vcf.gz', i=[i for i in range(len(subfiles))]),
		names = ndir + 'merge.txt',		
	output:
		ndir + 'all_merged_filtered.vcf.gz'
	log:
		config['python_filter']['logs'] + 'all_merged.log'
	threads:
		config['threads'] 
	shell:
		"bcftools merge --file-list {input.names} --threads {threads} -Oz "
		"-o {output} 2>{log} && bcftools index -t {output} 2>>{log}"