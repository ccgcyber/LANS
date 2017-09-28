import os
from os import listdir
import warnings


def find_all_filenames(path_to_dir):
    filenames = listdir(path_to_dir)
    return filenames

warnings.filterwarnings("ignore")
output_filename = "Configuration.txt"
if os.path.exists(output_filename):
    try:
        os.remove(output_filename)
    except OSError:
        pass

conf_file = open(output_filename,"a")
dir_path = os.path.dirname(os.path.realpath(__file__))
alt_dir_path = dir_path.replace('\\', '/')


conf_file.write(alt_dir_path+"/Properties.jar"+ "\n")
all_input_files = find_all_filenames(dir_path+"/input_files/")

for f in all_input_files:
    conf_file.write("input_files/"+f+ "\n")

conf_file.write(alt_dir_path)
conf_file.close()
