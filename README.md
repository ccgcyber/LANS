# About Graph-Simulation

This project is to generate simulated graph from a given graph. This script has strong dependency on the name of the columns, types of the columns and format of the input file.

This script requires the following softwares:

1. Spark 2.1.0, prebuilt for Hadoop 2.7 and later

2. R 3.2.1 to generate graph properties.

3. Python 2.7.8 is required along with the following packages: openmpi-1.10, numpy 1.10.4, panda 0.18.0, random, csv, gc (garbage collector), sklearn 0.18.1 (cluster, KMeans, kneighbors_graph, scale), sys, subprocess.

4. The code should be run with at least 4 processors. In this version, each processor is responsible for one role; so, the minimum number of processors must be equal to the number of roles. (This condition will be removed from the next versions.)


# How to run Graph-Simulation:

1.	Download "spark-2.1.0-bin-hadoop2.7.tgz" this package from http://spark.apache.org/downloads.html , unzip and save it in your cluster. 
2.	Make all the files in the "/Spark/..../bin" directory executable (e.g. using command chmod a+x bin).
3.	Download our project and unzip it.
4.	Copy all the jar files from the "Required_Packages" directory of our project to "/Spark/..../jars" directory of Spark.
5.	Copy our project (except "Required_Packages" directory) in the working directory of your cluster. Compile src/GraphProperties.scala, src/KCore.scala, and src/Properties.scala to /Spark/.../jars/Properties.jar.
6.	Keep all the input files (e.g. 11.binetflow, 5.binetflow and so on) in the "input_files" directory of our project. These input files are used as seed graphs while generating large-scale simulated graph. All the input seed graphs must be inside the "input_files" directory, otherwise the input graphs will not be considered as input.
7.	Configure Python package, R package and Home directory for Spark in the default configuration file of the cluster.
8.	Submit job "runProject.pbs" to a cluster.
9.	When the job ends it will provide the simulated graph in "SimulatedGraph" directory.


# Expected Results

1. When Graph-Simulation-4 is run it will create a new folder named SimulatedGraph. The contents of this folder should be a series of small graphs beginning with "localgen_0.csv" and ending with "localgen_N.csv" where N is the number of local graphs generated - 1. This folder will also contain a file named upperlevelGraph.csv which contains the connections between local graphs which unite all local graphs into a single larger graph.
2. In order to verify that the simulation has completed and is correct compare the number of files in the SimulatedGraph folder with the number of processors specified in the PBS script used to run the simulation. If the simulation is complete then all localgen_.csv files and upperlevelGraph.csv should be present and not empty.
