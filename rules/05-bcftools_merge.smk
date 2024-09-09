import os

idir = config['vcftools_filter']['output_dir']
odir = config['bcftools_merge']['output_dir'] 
nn = len(bams) // config['threads'] 
nn = nn if nn>1 else 3

# Creates groups of VCFs for partial parallel merge
subset_vcf = [bams[i:i+nn] for i in range(0,len(bams),nn)]
subfiles = [f"subcvf{i}" for i in range(len(subset_vcf))]

if len(subset_vcf[-1])==1:
	subfiles.append(subset_vcf.pop(-1))

# Creates files with filenames to merge
for i in range(len(subfiles)):
	with open(odir + subfiles[i], "w") as file:
		for line in subset_vcf[i]:
			file.write(idir + line + '.sort.vcf.gz\n')

with open(odir + 'merge.txt', "w") as file:
	for i in range(len(subfiles)):
		file.write(odir + f'merge.{i}.vcf.gz\n')

###############################################################################	
rule bcftools_submerge:
	input:
		files = expand(config['vcftools_filter']['output_dir'] + "{xyz}.sort.vcf.gz", xyz=bams,),
		names = odir + 'subcvf{i}'
	output:
		odir + 'merge.{i}.vcf.gz'
	log:
		config['bcftools_merge']['logs'] + 'merge.{i}.log'
	shell:
		"bcftools merge --file-list {input.names} -Oz -o {output} 2>{log} && "
		"bcftools index -t {output} 2>>{log}"

###############################################################################
rule bcftools_merge:
	input:
		files = expand(odir + 'merge.{i}.vcf.gz', i=[i for i in range(len(subfiles))]),
		names=odir + 'merge.txt',		
	output:
		config['bcftools_merge']['output_dir']  + 'all_merged.vcf.gz'
	log:
		config['bcftools_merge']['logs'] + 'all_merged.log'
	threads:
		config['threads'] 
	shell:
		"bcftools merge --file-list {input.names} --threads {threads} -Oz -o {output} 2>{log}"