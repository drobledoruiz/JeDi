		   __   _______  _______   __  
		  |  | |   ____||       \ |  | 
		  |  | |  |__   |  .--.  ||  | 
	.--.  |  | |   __|  |  |  |  ||  | 
	|  `--'  | |  |____ |  '--'  ||  | 
	 \______/  |_______||_______/ |__| 
                                    
An Snakemake pipeline for unbiased population metrics

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Running the pipeline](#running)


<img src="dag.svg " width="1000" height="550" />


## Requirements  <a name="requirements"></a>

It is required **MAMBA** to employ snakemake pipelines, however any other conda implementation such as micromamba also work. We recommend installing mamba trough [Miniforge](https://github.com/conda-forge/miniforge).

### Unix-like platforms (Mac OS & Linux)

Download the installer using curl or wget or your favorite program and run the script:

```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"    

bash Miniforge3-$(uname)-$(uname -m).sh

mamba init
```

Check mamba was installed correctly by running:
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

1. Clone the repo:
```
git clone https://github.com/xuxocast/snakemake_pi.git
```

2. Enter into the pipeline folder and create the environment:

```
mamba env create -f environment.yaml -n snakemake_pi
```

3. Activate the created environment:
```
 mamba activate snakemake_pi
```




## Running the pipeline  <a name="running"></a>


Once the environment its activated it is needed to populate the data folder and to modify the file paths defined in *config.yaml*:

1.  Copy the reference genome into the folder *00-data/*. Modify the entry *ref_genome: "00-data/MYFILE.fasta* in *config.yaml*.
2.  Copy the population index into the folder *00-data/*. Modify the entry *pop_index: "00-data/MYFILE.tsv* in *config.yaml*.
3.  Populate the folder *00-reads/* with *\*.bam* files. 
4. Modify other options on *config.yaml* such as:
	- *threads* employed by samtools, bcftools, piawka, or gstacks.
	-  *min_map_quality* minimum PHRED-scaled mapping quality to consider a read for gstacks.
	- *subsize.* The size of the groups for which bftools is merging vcf files in parallel. It is recommended to choose a number in the order of #VCF files / #Threads.


### Testing

Test everything is in order with a --dry-run:

```
snakemake -np
```

Also, visualise the DAG of jobs:

```
snakemake --dag | dot -Tsvg > dag.svg
```

or the DAG of rules:

```
snakemake --rulegraph | dot -Tsvg > ruledag.svg
```


### Running

Finally, run the snakemake pipeline in the background while sending its output and errors to *snake.log*:

```
nohup snakemake -j {number of cores} > snake.log 2>&1 &
```


This pipelines employs [piawk](https://github.com/novikovalab/piawka) in one of its steps, all credits for its authors :) 
