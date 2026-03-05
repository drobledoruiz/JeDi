					       __     ___     ______     __  
					      |  |  /  __ \  |       \  |__| 
					      |  | |  |__| | |  .--.  |  __
					.--.  |  | |  ___ /  |  |  |  | |  | 
					|  '--'  | |  \____  |  '--'  | |  | 
	 				 \______/   \_____/  |_______/  |__| 
                                    
A Snakemake pipeline to calculate unbiased genetic diversity metrics: individual heterozygosity, population nucleotide diversity (π) and populations sequence divergence (Dxy). *JeDi* avoids common pitfalls that lead to biased genetic diversity estimates (e.g., it keeps and accounts for tri- and tetra-allelic sites and invariant [monomorphic] sites, which is essential for the correct computation of π and Dxy).
<br>

<img width="6622" height="9362" alt="Poster_JeDi" src="https://github.com/user-attachments/assets/8d1324f1-fa58-428f-9ffc-8ae4d4f90384" />
<br>
<br>
<br>

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Running JeDi](#running)
4. [JeDi output](#output)
5. [Citation](#citation)

<br>
<br>

<p align="center">
<img src="JeDi_pipeline_v2.png" width="400" height="714" />
</p>



## REQUIREMENTS  <a name="requirements"></a>
**mamba** needs to be installed to run *JeDi*, however any other conda implementation such as micromamba or miniconda also work. We recommend installing mamba through [Miniforge](https://github.com/conda-forge/miniforge).

### Linux (x86) platforms
Download the installer using 'curl' or 'wget' (or your favorite program) and run the script:
```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"    
bash Miniforge3-$(uname)-$(uname -m).sh
mamba init
```

Check that mamba was installed correctly by running:
```
mamba --help   
```

### Windows and MacOs (Not supported)

Please note that these operating systems are currently not supported.



## INSTALLATION AND CONFIGURATION OF *JeDi* <a name="installation"></a>

1. Enter your local directory and clone *JeDi*'s github repository:
```
cd /my_path/my_directory/
git clone https://github.com/drobledoruiz/JeDi
```

2. Enter the pipeline folder and create a mamba environment (you can chose its name, e.g. _snakemake_JeDi_):
```
cd JeDi/
mamba env create -f environment.yaml -n snakemake_JeDi
```

3. Activate the created environment:
```
 mamba activate snakemake_JeDi
```




## RUNNING *JeDi*  <a name="running"></a>
*JeDi* is divided in two modules: Module 1 produces estimates of individual heterozygosity and Module 2 produces population-level estimates of nucleotide diversity (π) and divergence (dxy). We recommend inspecting the estimates of individual heterozygosity produced by Module 1 to make a judgement on the inclusion of individuals for Module 2. For example, one may encounter individuals with unusually high heterozygosity that one may want to exclude from the calculation of population parameters because they are likely contaminated samples. Or one may decide to keep them because they are admixed individuals. Similarly, one may decide to modify the population assigned to some individuals after inspecting the values of individual heterozygosity (e.g., assign hybrids to their own population, etc.). The user must use their knowledge of the study system and samples to make their own informed judgement. Any desired changes should be done on the input file for Module 2 (see below).

**Module 1** requires 3 inputs:
1. A reference genome in FASTA format
2. A tab-separated file with two columns (individual IDs and population; e.g. ind_A	pop_X)
3. A directory with mapped reads in BAM format (each BAM file should be named with the individual ID; e.g. *ind_A.bam*)

To tell *JeDi* Module 1 the location of each input, modify the first 3 lines of the *JeDi/config.yaml* file, writing the absolute path to each input:
1. ref_genome: "*/my_path/my_directory/my_genome.fasta*"
2. pop_index: "*/my_path/another_directory/id_pop.tsv*"
3. reads_dir: "*/my_path/bams_directory/*"

(Optional) Modify other options in *JeDi/config.yaml* such as:
- *threads* employed by samtools, bcftools, piawka, and gstacks
- *min_map_quality* minimum PHRED-scaled mapping quality to consider a read for gstacks [default 30]
- *minDP* minimum genotype depth for vcftools [default 15]
- *mac* remove private doubletons (i.e., alternative allele present twice only in one individual) [2], or private doubletons *and* singletons [default 1] with vcftools. Use [0] to skip this filtering step.

**Module 2** requires:
- A tab-separated file with two columns (individual IDs and population). This is the file that can be modified after inspecting the output from Module 1 (i.e., individual heterozygosities).

To tell *JeDi* Module 2 the location of the input file, modify the 4th line of the *JeDi/config.yaml* file, writing the absolute path of the ID file:
-  pop_kept: "*../my_path/another_directory/id_pop2.tsv*"




### Testing with a dry-run
With the mamba environment activated, test that everything is in order with a --dry-run. For example, for Module 1:
```
cd /my_path/my_directory/JeDi/module_1
mamba activate snakemake_JeDi
snakemake -np > dry_run.log
```

To visualize the steps to be run, produce the Directed Acyclic Graph (DAG):
```
snakemake --dag | dot -Tsvg > dag.svg
```

or the rule graph:
```
snakemake --rulegraph | dot -Tsvg > ruledag.svg
```

The same can be done for Module 2:
```
cd /my_path/my_directory/JeDi/module_2
mamba activate snakemake_JeDi
snakemake -np dry_run.log
```



### Run *JeDi*

- Run *JeDi* Module 1 with 'nohup' in the background while sending standard output and errors to a log file (e.g., *mod1_2024-10-02.log*):
```
cd /my_path/my_directory/JeDi/module_1
nohup snakemake -j {number of cores} > mod1_2024-10-02.log 2>&1 &
```
Don't forget to check the output individual heterozygosities before running Module 2.

- Run *JeDi* Module 2:
```
cd /my_path/my_directory/JeDi/module_2
nohup snakemake -j {number of cores} > mod2_2024-10-03.log 2>&1 &
```

To leave the mamba environment:
```
mamba deactivate
```




## *JeDi*'s OUTPUT  <a name="output"></a>
- The output of ***JeDi* Module 1** is:

Final per-individual genome-wide standardized heterozygosities
```
/my_path/my_directory/JeDi/module_1/06-genomic_diversity/genomic_het_table.tsv
```

Per-locus (i.e., genomic region) standardized heterozygosities that can be used to create Manhattan plots (raw output from piawka)
```
/my_path/my_directory/JeDi/module_1/06-genomic_diversity/piawka_het.tsv
```

The structure of this file is locus_start_end, locus_n_sites, id, ".", n_used_sites, metric, value, numerator(differences), denominator(comparisons):
```
chr1_3314_3441        198     ind_A     .       110     het_pixy        0.00909091      2       220
chr1_3314_3441        198     ind_B     .       100     het_pixy        0.01      	2       200
```

- The output of ***JeDi* Module 2** is:

Final per-population genome-wide π
```
/my_path/my_directory/JeDi/module_1/06-genomic_diversity/genomic_het_table.tsv
```

Final population-pairwise genome-wide dxy in vertical table and matrix format, respectively
```
/my_path/my_directory/JeDi/module_2/06-genomic_diversity/genomic_dxy_table.tsv
/my_path/my_directory/JeDi/module_2/06-genomic_diversity/genomic_dxy_matrix.tsv
```

Per-locus (i.e., genomic region) π and dxy that can be used to create Manhattan plots (raw output from piawka)
```
/my_path/my_directory/JeDi/module_2/06-genomic_diversity/2_piawka_pi_dxy_fst.txt
```

The structure of this file is locus_start_end, locus_n_sites, pop1, pop2, n_used_sites, metric, value, numerator(differences), denominator(comparisons), n_geno, n_miss
```
chr1_3314_3441        198     pop_X     .           110     pi_pixy	0.00909091      2       220     220     10120
chr1_3314_3441        198     pop_X     pop_Y       100     dxy_pixy	0       	0       1108    1110    18214
```

You can find intermediate outputs in the other directories:
```
/my_path/my_directory/JeDi/module_1/01-gstacks/
/my_path/my_directory/JeDi/module_1/02-bcftools_call/
/my_path/my_directory/JeDi/module_1/03-vcftools_filter/
/my_path/my_directory/JeDi/module_1/04-bcftools_merge/
/my_path/my_directory/JeDi/module_1/05-python_filter/
```

*JeDi* uses [piawka](https://github.com/novikovalab/piawka); all credits to its authors :)




---------------------------------------------------------------------------
## CITATION <a name="citation"></a>
If you use *JeDi*, please cite: **"Pavlova, et al. (2025) A shift to metapopulation genetic management for persistence of a species threatened by fragmentation: the case of an endangered Australian freshwater fish. *Molecular Ecology* 34 (23), e70005."** [DOI:  https://doi.org/10.1111/mec.70005]

Do not hesitate to contact us if you have any questions. We are happy to help!
- Diana A. Robledo-Ruiz, diana.robledoruiz1@monash.edu
- Jesús Castrejón-Figueroa, j.castrejon@unsw.edu.au

