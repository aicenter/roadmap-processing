import os.path
import numpy

from tqdm import tqdm

merged_filepath = r"C:\AIC data\csv load test/merged.csv"

test = numpy.recfromcsv(merged_filepath)

# MERGING CSV
# fout = open("C:\AIC data\csv load test/merged.csv","a")
#
#
# # now the rest:
# for num in tqdm(range(0,200)):
# 	filepath = r"C:\AIC data\csv load test/369749089_out.c-new-ltgproduction-adhoc-one-time.out_table.{}.csv".format(num)
# 	if os.path.isfile(filepath):
# 		f = open(filepath)
# 		for line in f:
# 			fout.write(line)
# 		f.close() # not really needed
# fout.close()