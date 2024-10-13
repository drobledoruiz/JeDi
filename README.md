	       __   _______  _______   __  
	      |  | |   ____||       \ |  | 
	      |  | |  |__   |  .--.  ||  | 
	.--.  |  | |   __|  |  |  |  ||  | 
	|  `--'  | |  |____ |  '--'  ||  | 
	 \______/  |_______||_______/ |__| 
                                    
An Snakemake pipeline to calculate unbiased genetic diversity metrics: individual heterozygosity, population nucleotide diversity (pi) and populations sequence divergence (dxy)

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Running JeDi](#running)
4. [JeDi output](#output)
5. [Contact](#contact)

<img src="dag.svg " width="1000" height="550" />




## Requirements  <a name="requirements"></a>

**mamba** needs to be installed to run snakemake pipelines, however any other conda implementation such as micromamba or miniconda also work. We recommend installing mamba through [Miniforge](https://github.com/conda-forge/miniforge).

### Unix-like platforms (Mac OS & Linux)

Download the installer using curl or wget (or your favorite program) and run the script:

```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"    

bash Miniforge3-$(uname)-$(uname -m).sh

mamba init
```

Check that mamba was installed correctly by running:
```
mamba --help   
```

### Windows

Download and execute the Windows installer. Follow the prompts, taking note of the options to
"Create start menu shortcuts" and "Add Miniforge3 to my PATH environment variable". The latter is
not selected by default due to potential conflicts with other software. Without Miniforge3 on the
path, the most convenient way to use the installed software (such as commands `conda` and `mamba`)
will be via the "Miniforge Prompt" installed to the start menu.




## Installation and configuration  <a name="installation"></a>

1. Enter your local directory and clone JeDi's github repository:
```
cd /my_path/my_directory/
git clone https://github.com/drobledoruiz/JeDi
```

2. Enter the pipeline folder and create a mamba environment (you can chose its name, e.g. snakemake_JeDi):
```
cd JeDi/
mamba env create -f environment.yaml -n snakemake_JeDi
```

3. Activate the created environment:
```
 mamba activate snakemake_JeDi
```




## Running JeDi  <a name="running"></a>
JeDi requires 3 inputs:
1. A reference genome in FASTA format
2. A tab-separated file with two columns (individual IDs and population)
3. A directory with mapped reads in BAM format (each BAM file should be named with the individual ID; e.g. ind_A.bam)

Modify the 3 first lines of the JeDi/*config.yaml* file, writing the absolute path to each input:
1. ref_genome: "/my_path/my_directory/my_genome.fasta"
2. pop_index: "/my_path/another_directory/id_pop.tsv"
3. reads_dir: "/my_path/bams_directory/"

(Optional) Modify other options in JeDi/*config.yaml* such as:
	- *threads* employed by samtools, bcftools, piawka, and gstacks
	- *min_map_quality* minimum PHRED-scaled mapping quality to consider a read for gstacks
 	- *minDP* minimum genotype depth for vcftools
	- *mac* identify singletons only [1], or singletons and private doubletons [2] with vcftools


### Testing
With the mamba environment activated, test that everything is in order with a --dry-run:
```
cd /my_path/my_directory/JeDi/
mamba activate snakemake_JeDi
snakemake -np
```

To visualize the steps to be run, produce the Directed Acyclic Graph (DAG):
```
snakemake --dag | dot -Tsvg > dag.svg
```

or the rule graph:
```
snakemake --rulegraph | dot -Tsvg > ruledag.svg
```


### Run JeDi

Run JeDi with nohup in the background while sending standard output and errors to a log file (e.g. *run_2024-10-02.log*):
```
nohup snakemake -j {number of cores} > run_2024-10-02.log 2>&1 &
```

To leave the mamba environment:
```
mamba deactivate
```




## JeDi output  <a name="output"></a>
The final outputs from JeDi are at:
```
/my_path/my_directory/JeDi/06-genomic_diversity/genomic_*.tsv
```

You can find intermediate outputs in the other directories:
```
/my_path/my_directory/JeDi/01-gstacks/
/my_path/my_directory/JeDi/02-bcftools_call/
/my_path/my_directory/JeDi/03-vcftools_filter/
/my_path/my_directory/JeDi/04-bcftools_merge/
/my_path/my_directory/JeDi/05-python_filter/
```

JeDi employs [piawk](https://github.com/novikovalab/piawka), all credits to its authors :)




---------------------------------------------------------------------------
## Contact <a name="contact"></a>
Do not hesitate to contact us if you have any questions. We are happy to help!
- Diana A. Robledo-Ruiz, diana.robledoruiz1@monash.edu
- Jesús Castrejón-Figueroa, j.castrejon@unsw.edu.au

