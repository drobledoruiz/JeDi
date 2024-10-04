import polars as pl
import gzip as gz
import argparse
import os

class MyException(Exception):
    pass

def write_header(ivcf_path, ovcf_path, gzip=True,):
    ifile = gz.open(ivcf_path, "rt") if gzip else open(ivcf_path, "rt")
    ofile = open(ovcf_path, "wt")
    counter = 0
    nl = int(os.popen(f'zcat {ivcf_path} | wc -l').read())
    with ifile:
        with ofile:
            for line in ifile:
                counter +=1
                if line.startswith("#CHROM"):
                    vcf_names = [x for x in line.split('\t')]
                    if (nl == counter):
                        ofile.write(line)
                        raise MyException("VCF file is empty")
                    break
                else:
                    ofile.write(line)
    return [x.split('\n')[0] if '\n' in x else x for x in vcf_names]

def filter_singletons_vcf(vcf_path, out_vcf_path, singletons_path, indv_name, gzip=True):
    names = write_header(vcf_path,out_vcf_path, gzip=gzip)
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
    positions = dfs.filter(pl.col('INDV')==indv_name).drop('INDV').to_dicts()

    df = df.filter( 
            ~(pl.struct('#CHROM','POS').is_in(positions)) 
        )
    
    with open(out_vcf_path, "at") as  ofile:
        df.collect().write_csv(ofile,separator="\t" ) 
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Python script to add the number of derived alleles per sample to the gerp output file.')
    parser.add_argument('-v','--vcf', help='VCF Dataframe',required=True)    # VCF file to be mergedd)
    parser.add_argument('-o','--output', help='Output file path',required=True) # output file path
    parser.add_argument('-s','--singletons', help='Singletons file path',required=True) # output file path
    parser.add_argument('-n','--name', help='Name of the individual', required=True)
    parser.add_argument('-gz','--gzip', help='Boolean to indicate whether vcf file is gunzip compressed or not (default False)',action='store_true')  

    args = vars(parser.parse_args())
    # Call the function
    try:
        filter_singletons_vcf(args['vcf'], args['output'], args['singletons'], args['name'], gzip=args['gzip'])
    except Exception as e:
        print(f"## An exception occurred in {args['vcf']}")
        print(e)