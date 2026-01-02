#######################################################################################
# Rule to copy reference genome to writable location and create index
# This is needed because bcftools requires write access to create .fai index
rule prepare_reference:
	input:
		ref = config['ref_genome']
	output:
		ref = "00-reads/reference.fa",
		idx = "00-reads/reference.fa.fai"
	shell:
		"""
		cp {input.ref} {output.ref}
		samtools faidx {output.ref}
		"""
