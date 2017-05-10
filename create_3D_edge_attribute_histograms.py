import pandas as pd
import numpy as np
import sys
import re
import warnings
import os
from os import listdir
import mpi4py
from mpi4py import MPI
warnings.simplefilter('ignore', category=FutureWarning)

comm = mpi4py.MPI.COMM_WORLD
w = comm.Get_rank()
w = int(w)

def find_csv_filenames(path_to_dir):
    filenames = listdir(path_to_dir)
    return filenames

## Uncomment these lines for Shadow submission
#conf_file = open ( 'Configuration.txt',"r" )
#lineList = conf_file.readlines()
#conf_file.close()
#filePrefix = lineList[-1]+"/input_files/"

## Comment out this line for Shadow submission
filePrefix = "C:/Users/Jonathan/Dropbox/HPDA_Simulation_Project/code/Edge attributes/Test Files/input_files/"

## Get a list of filenames from the files in the directory
ctu_files = find_csv_filenames(filePrefix)
temp_folder = os.path.dirname(os.path.dirname(filePrefix))
temp_folder += "/temp/"

## Assign role file names
role_files = []
for f in ctu_files:
	role_files.append(f)
i = 0
for f in role_files:
	role_files[i] = f.split('.', 1)[0] + '_roles.csv'
	i = i + 1

if w >= len(ctu_files):
	sys.exit(0)

# Read files into pandas (pd)
ctu_pd = pd.read_csv(filePrefix + ctu_files[w])
roles_pd = pd.read_csv(role_files[w])

# Get list of attributes
attributes = list(ctu_pd)

# Get list of role numbers
role_attribute = roles_pd['Role']
role_count = role_attribute.value_counts()
role_numbers = role_count.index.tolist()

# Create a text file for each attribute
i = 0
for x in attributes:
	text_file = open(attributes[i] + '_' + role_files[w].split('_', 1)[0] + '.txt', 'w')
	text_file.close()
	i = i + 1

# Check to see if the combined file already exists
# If it doesn't exist, then create it by combining the two source files
if not os.path.exists('merged_dataframe_' + ctu_files[w].split('.', 1)[0] + '.csv'):
	# Create empty columns for our roles
	ctu_pd['SrcRole'] = ''
	ctu_pd['DstRole'] = ''
	i = 0
	number_of_rows = len(ctu_pd.index)
	while i < number_of_rows:
		# Assign the corresponding role numbers for SrcAddr & DstAddr to SrcRole & DstRole
		SrcRole = roles_pd.loc[roles_pd['Node'] == ctu_pd['SrcAddr'].iloc[i]]
		SrcRole = SrcRole['Role'].iloc[0]
		ctu_pd['SrcRole'].iloc[i] = SrcRole
		DstRole = roles_pd.loc[roles_pd['Node'] == ctu_pd['DstAddr'].iloc[i]]
		DstRole = DstRole['Role'].iloc[0]
		ctu_pd['DstRole'].iloc[i] = DstRole
		print i
		i = i + 1
	print 'Combined file created'
	# Output the combined dataframe to a .csv
	ctu_pd.to_csv('merged_dataframe_' + ctu_files[w])

# Open the csv for next part
merged_df = pd.read_csv('merged_dataframe_' + ctu_files[w].split('.', 1)[0] + '.csv')

i = 0
j = 0
k = 0
for x in role_numbers:
	for y in role_numbers:
		# Only look at i -> j 
		data_slice = merged_df.loc[merged_df['SrcRole'] == role_numbers[i]]
		data_slice = data_slice.loc[data_slice['DstRole'] == role_numbers[j]]
		
		# Create and process histograms
		for z in attributes:
			attribute = attributes[k]
			
			# Each unique value and the number of times it appears
			counts = data_slice[attribute].value_counts()
			# Number of unique values
			number_unique = len(counts.index)
			
			## Process data differently depending on which attribute it is
			if(attribute == 'StartTime'):
				## Convert to date-time, and then to seconds since Unix epoch
				data = pd.to_datetime(data_slice[attribute], format="%Y/%m/%d %H:%M:%S.%f")
				data = pd.DatetimeIndex(data)
				data = data.astype(np.int64) // 10**9
				data = data.astype(float)
			elif(attribute == 'Sport' or attribute == 'Dport'):
				## Force hex conversion 
				data = data_slice[attribute].convert_objects(convert_numeric='force')
			elif(attribute == 'Dur' or attribute == 'TotPkts' or attribute == 'TotBytes' or attribute == 'SrcBytes'):
				data = data_slice[attribute].astype(float)
			elif(attribute == 'Dir' or attribute == 'Proto'):
				data = data_slice[attribute]
			else:
				## Ignore the unwanted attribute and continue the loop
				k = k + 1
				continue
				   
			## Put it into buckets if there are more than 'x' unique values
			x = 100 
			if number_unique > x:            
				## Put data into buckets
				bucket_size = 100
				while True:
					try:
						data = pd.qcut(data, bucket_size).value_counts()
					except ValueError:
						## Decrease bucket size  and try again until it fits
						bucket_size = bucket_size - 1
						continue
					break
			
				## Calculate distribution probabilities for bucketed items
				probabilities = []
				for item in data:
					probabilities.append((float(item) / np.sum(data)))
											
				## Append histogram to .txt file
				#print (attribute + '_' + str(role_numbers[i]))
				text_file = open(attribute + '_' + ctu_files[w].split('.', 1)[0] + '.txt', 'a')
				text_file.write(str(role_numbers[i]))
				text_file.write('->')
				text_file.write(str(role_numbers[j]))
				text_file.write(',') 
				text_file.write(str(len(data.index)))
				text_file.write(',')
				labels = data.index.tolist()
				text_file.write(str(labels))
				text_file.write(',') 
				text_file.write(str(probabilities))
				text_file.write('\n')
				text_file.close()
				
			else:
				#Calculate distribution probabilities for non-bucketed items
				probabilities = []
				for item in counts:
					probabilities.append((float(item) / len(data_slice.index)))
				
				# Append histogram to .txt file
				#print (attribute + '_' + str(role_numbers[i]))
				text_file = open(attribute + '_' + ctu_files[w].split('.', 1)[0] + '.txt', 'a')
				text_file.write(str(role_numbers[i]))
				text_file.write('->')
				text_file.write(str(role_numbers[j]))
				text_file.write(',') 
				text_file.write(str(number_unique))
				text_file.write(',')
				text_file.write(str(counts.index.tolist()))
				text_file.write(',') 
				text_file.write(str(probabilities))
				text_file.write('\n')
				text_file.close()
			
			k = k + 1
		k = 0
		j = j + 1
	j = 0
	i = i + 1
i = 0