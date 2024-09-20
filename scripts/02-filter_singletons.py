import polars as pl
import gzip as gz
import argparse


def write_header(ivcf_path, ovcf_path, gzip=True,):
    ifile = gz.open(ivcf_path, "rt") if gzip else open(ivcf_path, "rt")
    ofile = open(ovcf_path, "wt")
    with ifile:
        with ofile:
            for line in ifile:
                if line.startswith("#CHROM"):
                    break
                else:
                    ofile.write(line)
    ifile.close()
    ofile.close()
    return


def get_names(ivcf_path,  gzip=True,):
    ifile = gz.open(ivcf_path, "rt") if gzip else open(ivcf_path, "rt")
    with ifile:
        for line in ifile:
            if line.startswith("#CHROM"):
                vcf_names = [x for x in line.split('\t')]
                break
    ifile.close()
    return [x.split('\n')[0] if '\n' in x else x for x in vcf_names]


def filter_singletons_vcf(vcf_path, out_vcf_path, singletons_path, gzip=True):
    names = get_names(vcf_path,gzip=gzip,) 
    inds = names[names.index('FORMAT')+1:]

    if(gzip):
        # Reads (in-memory) vcf file
        with gz.open(vcf_path, "rt") as f:   
            df = pl.read_csv(f,comment_prefix='#', separator="\t", has_header=False,ignore_errors=True).lazy()
        f.close()
    else:
        # Reads (lazy) vcf file
        df = pl.scan_csv(vcf_path,comment_prefix='#', separator="\t", has_header=False,)
       
    cols = df.collect_schema().names()
    df = df.rename(dict(zip(cols,names)))
   
    dfs = pl.read_csv(singletons_path,separator="\t").rename({"CHROM": "#CHROM"}).drop(["ALLELE","SINGLETON/DOUBLETON"])

    for row in dfs.iter_rows():
        df = df.with_columns(
                pl.when(pl.col('#CHROM') == row[0],
                        pl.col('POS')    == row[1])
                .then(pl.col(row[2]).str.replace_all('(.)/(.) | (.)\\|(.)','./.'))
                .otherwise(pl.col(row[2]))
                .alias(row[2])
                )
    df.sink_csv(out_vcf_path,separator="\t" ) 
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Python script to add the number of derived alleles per sample to the gerp output file.')
    parser.add_argument('-v','--vcf', help='VCF Dataframe',required=True)    # VCF file to be mergedd)
    parser.add_argument('-o','--output', help='Output file path',required=True) # output file path
    parser.add_argument('-s','--singletons', help='Singletons file path',required=True) # output file path
    parser.add_argument('-gz','--gzip', help='Boolean to indicate whether vcf file is gunzip compressed or not (default False)',action='store_true')  

    args = vars(parser.parse_args())
    # Call the function
    filter_singletons_vcf(args['vcf'], args['output'], args['singletons'], gzip=args['gzip'])
    write_header(args['vcf'], args['output'].split('.')[0]+'.header', gzip=args['gzip'])