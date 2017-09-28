import pandas as pd
import numpy as np
import sys
import re
import warnings
import os
from os import listdir
warnings.simplefilter('ignore', category=FutureWarning)


def find_csv_filenames(path_to_dir):
    filenames = listdir(path_to_dir)
    return filenames

conf_file = open ( 'Configuration.txt',"r" )
lineList = conf_file.readlines()
conf_file.close()
filePrefix = lineList[-1]+"/input_files/"

#filePrefix = "C:/Users/Jonathan/Dropbox/HPDA_Simulation_Project/code/Edge attributes/Test Files/input files/"

## get a list of filenames from the files in the directory


allFiles = find_csv_filenames(filePrefix)
temp_folder = os.path.dirname(os.path.dirname(filePrefix))
temp_folder += "/temp/"

##initialize counters
i = 0
j = 0

##create histograms
for f in allFiles:
    dataset = filePrefix + f

    ## read in dataset_file
    data1 = pd.read_csv(dataset)
    ## get column names
    column = list(data1)

    for item in column:
        ## read in the specified column into pandas
        data = data1[column[i]]
        ## get a count of each item that appears and the number of unique values
        counts = data.value_counts()
        unique_values = len(counts.index)

        if column[i] == 'SrcAddr' or column[i] == 'DstAddr' or column[i] == 'State' or column[i].lower() == 'label':
            ## ignore these columns and continue loop
            i = i + 1
            continue
        elif column[i] == 'Sport' or column[i] == 'Dport':
            ## force hex conversion
            data = data.convert_objects(convert_numeric='force')
            data = data.astype(float)
        elif column[i] == 'StartTime':
            ## convert to date-time, and then to Unix epoch time
            data = pd.to_datetime(data, format="%Y/%m/%d %H:%M:%S.%f")
            data = pd.DatetimeIndex(data)
            data = data.astype(np.int64) // 10**9
            data = data.astype(float)
        elif column[i] == 'Dur' or column[i] == 'sTos' or column[i] == 'dTos' or column[i] == 'TotPkts' or column[i] == 'TotBytes' or column[i] == 'SrcBytes':
            data = data.astype(float)

        ## process into buckets if more than 100 unique values
        if unique_values > 100:
            ## put data into buckets
            bucket_size = 100
            while True:
                try:
                    #print "-----------------------------------------------------"
                    #print column[i]
                    #print data
                    data = pd.qcut(data, bucket_size).value_counts()
                except ValueError:
                    #print "ValueError"
                    ## decrease bucket size until it fits
                    bucket_size = bucket_size - 1
                    continue
                except Exception as e:
                    print "Capture error"
                    print(e)

                break

            ## ready the text file for output
            text_file = open(temp_folder+column[i] + allFiles[j].split('.')[0] + ".txt", "w")

            ## get the number of buckets and output to file
            number_of_bars = len(data.index)
            text_file.write(str(number_of_bars))
            text_file.write("\n")

            ## get the column headers and output to file
            labels = data.index.tolist()
            text_file.write(str(labels))
            text_file.write("\n")

            ## get the frequency of each bucket and output to file
            probabilities = []
            for item1 in data:
                probabilities.append((float(item1) / np.sum(data)))
            text_file.write(str(probabilities))

            ## close reader
            text_file.close()

            ## go to next column
            i = i + 1
        else:
            ## ready the text file for output
            text_file = open(temp_folder+column[i]  + allFiles[j].split('.')[0] + ".txt", "w")

            ## get the number of unique entries and output to file
            number_of_bars = len(counts.index)
            text_file.write(str(number_of_bars))
            text_file.write("\n")

            ## get the column headers and output to file
            labels = counts.index.tolist()
            text_file.write(str(labels))
            text_file.write("\n")

            ## calculate the frequency each string appears and output to file
            probabilities = []
            for item1 in counts:
                probabilities.append((float(item1) / len(data.index)))
            text_file.write(str(probabilities))

            ## close reader
            text_file.close()

            ## go to next column
            i = i + 1
    ## reset columns
    i = 0
    ## go to next dataset
    j = j + 1