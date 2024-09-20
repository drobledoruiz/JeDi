import polars as pl
import argparse

def parse_piawka_het(input_filename,pop_filename):
	# Name output files
	fname = input_filename.split('/')[-1]
	wdir = '/'.join(input_filename.split('/')[:-1])
	if '/' in input_filename:
		wdir +=  '/'
	output_het_filename = wdir + 'genomic_het_table.tsv'
	output_pop_filename = wdir + 'ids_filtered.tsv'

	schema={'column_1':pl.String, 'column_2':pl.Int32, 'column_3':pl.String, 
        'column_4':pl.String, 'column_5':pl.Int32, 'column_6':pl.String, 
        'column_7':pl.Float64,'column_8':pl.Float64,'column_9':pl.Float64,
        'column_10':pl.Int32,'column_11':pl.Int32}

	names = ['locus','nSites','pop1','pop2','nUsed ','metric','value','numerator','denominator',]
	cols = ['column_1', 'column_2', 'column_3', 'column_4', 'column_5','column_6', 'column_7','column_8','column_9','column_10','column_11']

	# Read data into a Lazy DataFrame
	df = pl.scan_csv(input_filename,separator="\t",has_header=False,schema=schema).rename(dict(zip(cols,names)))
	# Filters per metric
	df_het  = df.filter((pl.col('metric')=='het_pixy')).select(['pop1','numerator','denominator',])

	#--------------------------------------------------
	# HET Table
	df_het = df_het.group_by("pop1").agg(pl.col("numerator").sum(), pl.col("denominator").sum(), ).sort('pop1')
	df_het = df_het.with_columns((pl.col('numerator') / pl.col('denominator')).alias('het')).collect()#.rename({"numerator":'diffs','denominator':'comps'})
	
    # Filterin High Het
	den_min = df_het.select(pl.mean("denominator") - 2*pl.std('denominator')).item()
	max_het = df_het.select(pl.mean("het") + 2*pl.std('het')).item()
	filtered_ids = df_het.filter(pl.col('het') <= max_het, pl.col('denominator') >= den_min).select('pop1')
	print(f'The following induviduals were removed:')
	print(df_het.filter(~pl.col('pop1').is_in(filtered_ids)) )
	df_het.filter(pl.col('pop1').is_in(filtered_ids) ).write_csv(output_het_filename,separator='\t',)
	#--------------------------------------------------
	# ID POP
	df_pop = pl.read_csv(pop_filename,separator="\t",has_header=False)
	df_pop.filter( pl.col('column_1').is_in(filtered_ids) ).write_csv(output_pop_filename,separator='\t',include_header=False)

	del df_het, df, df_pop
	return


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='A Python script to reduce a pixy PI dataframe.')
	parser.add_argument('filename', help='The path of the dataframe')           # positional argument  
	parser.add_argument('-p','--pop', help='Population Dataframe',default='')
	args = vars(parser.parse_args())
	parse_piawka_het(args['filename'],args['pop'])