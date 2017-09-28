import shutil
import os
import warnings
warnings.filterwarnings("ignore")

conf_file = open ( 'Configuration.txt',"r" )
lineList = conf_file.readlines()
conf_file.close()
temp_folder = lineList[-1]+"/temp/"
shutil.rmtree(temp_folder)
os.remove('Configuration.txt')