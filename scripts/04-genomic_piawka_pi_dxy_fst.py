import polars as pl
import argparse

def parse_piawka_dxy(input_filename,):
	# Name output files
	fname = input_filename.split('/')[-1]
	wdir = '/'.join(input_filename.split('/')[:-1])
	if '/' in input_filename:
		wdir +=  '/'
	output_pi_filename = wdir   + 'genomic_pi_table.tsv'
	output_dxy_filename1 = wdir + 'genomic_dxy_table.tsv'
	output_dxy_filename2 = wdir + 'genomic_dxy_matrix.tsv'
	output_fst_filename1 = wdir + 'genomic_fst_table.tsv'
	output_fst_filename2 = wdir + 'genomic_fst_matrix.tsv'

	schema={'column_1':pl.String, 'column_2':pl.Int32, 'column_3':pl.String, 
        'column_4':pl.String, 'column_5':pl.Int32, 'column_6':pl.String, 
        'column_7':pl.Float64,'column_8':pl.Float64,'column_9':pl.Float64,
        'column_10':pl.Int32,'column_11':pl.Int32}

	names = ['locus','nSites','pop1','pop2','nUsed ','metric','value','numerator','denominator','nGenotypes','nMissing']
	cols = ['column_1', 'column_2', 'column_3', 'column_4', 'column_5','column_6', 'column_7','column_8','column_9','column_10','column_11']

	# Read data into a Lazy DataFrame
	df = pl.scan_csv(input_filename,separator="\t",has_header=False,schema=schema).rename(dict(zip(cols,names)))

	# Filters per metric
	df_pi  = df.filter((pl.col('metric')=='pi_pixy')).select(['pop1','numerator','denominator'])
	df_dxy = df.filter((pl.col('metric')=='dxy_pixy')).select(['pop1','pop2','numerator','denominator'])
	df_fst = df.filter((pl.col('metric')=='Fst_HUD')).select(['pop1','pop2','value'])

	#--------------------------------------------------
	# PI Table
	df_pi = df_pi.group_by("pop1").agg(pl.col("numerator").sum(), pl.col("denominator").sum()).sort('pop1')
	df_pi = df_pi.with_columns((pl.col('numerator') / pl.col('denominator')).alias('pi')).collect().rename({"numerator":'diffs','denominator':'comps'})
	df_pi.write_csv(output_pi_filename,separator='\t',)
	del df_pi

	#--------------------------------------------------
	# DXY Table
	df_dxy = df_dxy.group_by(["pop1","pop2"]).agg(pl.col("numerator").sum(), pl.col("denominator").sum()).sort(['pop1','pop2'])
	df_dxy = df_dxy.with_columns((pl.col('numerator') / pl.col('denominator')).alias('dxy')).collect().rename({"numerator":'diffs','denominator':'comps'})
	df_dxy.write_csv(output_dxy_filename1,separator='\t',)
	# DXY Matrix
	df_Mdxy = df_dxy.pivot('pop2', index='pop1', values='dxy')
	df_Mdxy.write_csv(output_dxy_filename2,separator='\t',)
	del df_dxy, df_Mdxy

	#--------------------------------------------------
	# FST Table
	df_fst = df_fst.group_by(['pop1','pop2']).agg([pl.mean('value').alias('avg_fst'), pl.std('value').alias('std_fst')])
	df_fst = df_fst.collect().sort(['pop1', 'pop2'])
	df_fst.write_csv(output_fst_filename1,separator='\t',)
	# FST Matrix
	df_Mfst = df_fst.pivot('pop2', index='pop1', values='avg_fst')
	df_Mfst.write_csv(output_fst_filename2,separator='\t',)
	del df_fst, df_Mfst, df
	return


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='A Python script to reduce a pixy PI dataframe.')
	parser.add_argument('filename', help='The path of the dataframe')           # positional argument  
	args = vars(parser.parse_args())
	parse_piawka_dxy(args['filename'],)