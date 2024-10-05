import os

# Create list of reads
configfile: "config.yaml"
os.system(f"cat {config['pop_index']} | awk '{{print $1}}' > 00-data/id.txt")

with open('00-data/id.txt') as f:
	bams = f.read().splitlines()
bams.sort()

for x in bams:
	obam = config['reads_dir'] + x + '.bam'
	sbam = '00-reads/' + x + '.bam'
	if not os.path.islink(sbam):
		os.symlink( obam, sbam)

# Load rules
include: "rules/00-samtools_index.smk"
include: "rules/01-gstacks.smk"
include: "rules/01-fasta2bed.smk"
include: "rules/02-bcftools_call.smk"
include: "rules/03-vcftools_filter.smk"
include: "rules/04-bcftools_sort.smk"
include: "rules/05-bcftools_merge.smk"
include: "rules/06-python_filter.smk"
include: "rules/07-piawka_het.smk"
include: "rules/08-piawka_pi.smk"

#######################################################################################
rule all:
	input:
		config['piawka_agg']['output_dir']  + 'genomic_dxy_matrix.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_dxy_table.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_fst_matrix.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_fst_table.tsv',
		config['piawka_agg']['output_dir']  + 'genomic_pi_table.tsv',
