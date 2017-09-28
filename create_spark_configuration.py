import os
from os import listdir
import warnings



def find_all_filenames(path_to_dir):
    filenames = listdir(path_to_dir)
    return filenames

warnings.filterwarnings("ignore")
output_filename = "Spark_Config.sh"
if os.path.exists(output_filename):
    try:
        os.remove(output_filename)
    except OSError:
        pass

conf_file = open(output_filename,"a")
os.chmod("Spark_Config.sh", 0o777)
dir_path = os.path.dirname(os.path.realpath(__file__))
alt_dir_path = dir_path.replace('\\', '/')
all_input_files = find_all_filenames(dir_path+"/input_files/")

init_str = "#!/bin/bash"+"\n"\
           +"SPARK_MASTER_IP=$HOSTNAME"+"\n\n"

fixed_str = "$SPARK_HOME/bin/spark-submit \\"\
      +"\n"+"--master spark://$SPARK_MASTER_IP:7077 \\"\
      +"\n"+"--deploy-mode client \\"\
      +"\n"+"--class Properties \\"\
      +"\n"+"--executor-cores 5 \\"\
      +"\n"+"--executor-memory 120g \\"

conf_file.write(init_str)
for f in all_input_files:
    conf_file.write(fixed_str+ "\n")
    conf_file.write(alt_dir_path+"/Properties.jar"+ " \\"+ "\n")
    conf_file.write("input_files/"+f+ " \\"+ "\n")
    conf_file.write(alt_dir_path+ "\n\n")

conf_file.close()
