from __future__ import print_function
from Property import Property
import networkx as nx
import csv
import os

def main(original_in_degree, original_out_degree, parent_dir
         # original_average_neighbor_degree, \
         # original_pageRank, \
         # original_triangle, \
         # original_local_clustering_coefficient,\
         # original_core_number
         ):
    #############################Random Node###############################################################################
    #GraphGT = nx.read_graphml("Simulation.graphml")
    EdgeList_Simulation = []

    simulated_file = parent_dir + "/SimulatedGraph/localgen_0.csv"
    #with open('/work/fz56/LANS-6.0/SimulatedGraph/localgen_0.csv') as csvfile:
    with open(simulated_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            EdgeList_Simulation.append((row["source"], row["destination"]))
    GraphGT = nx.MultiDiGraph()
    GraphGT.add_edges_from(EdgeList_Simulation)

    PropertyGT = Property(GraphGT)
    propertyDistance = [0.0]*7

    in_degree = PropertyGT.getInDegree()
    New_Node_In_Degree = open('New_Node_In_Degree.txt', "w")
    for e in in_degree:
        New_Node_In_Degree.write(str(e) + "\n")
    New_Node_In_Degree.close()

    out_degree = PropertyGT.getOutDegree()
    New_Node_Out_Degree = open('New_Node_Out_Degree.txt', "w")
    for e in out_degree:
        New_Node_Out_Degree.write(str(e) + "\n")
    New_Node_Out_Degree.close()

    # average_neighbor_degree = PropertyGT.getAverageNeighborDegree()
    # New_Average_Neighbor_Degree = open('New_Average_Neighbor_Degree.txt', "w")
    # for e in average_neighbor_degree:
    #     New_Average_Neighbor_Degree.write(str(e) + "\n")
    # New_Average_Neighbor_Degree.close()
    #
    # pageRank = PropertyGT.getPageRank()
    # New_pageRank = open('New_pageRank.txt', "w")
    # for e in pageRank:
    #     New_pageRank.write(str(e) + "\n")
    # New_pageRank.close()
    #
    # triangle = PropertyGT.getTriangles()
    # New_triangle = open('New_triangle.txt', "w")
    # for e in triangle:
    #     New_triangle.write(str(e) + "\n")
    # New_triangle.close()
    #
    # local_clustering_coefficient = PropertyGT.getLocalClusteringCoefficient()
    # New_local_clustering_coefficient = open('New_local_clustering_coefficient.txt', "w")
    # for e in local_clustering_coefficient:
    #     New_local_clustering_coefficient.write(str(e) + "\n")
    # New_local_clustering_coefficient.close()
    #
    # core_number = PropertyGT.getCoreNumber()
    # New_core_number = open('New_core_number.txt', "w")
    # for e in core_number:
    #     New_core_number.write(str(e) + "\n")
    # New_core_number.close()

    propertyDistance[0] = originalPropertyGT.averageKL(original_in_degree, in_degree)
    propertyDistance[1] = originalPropertyGT.averageKL(original_out_degree, out_degree)
    # propertyDistance[2] = originalPropertyGT.averageKL(original_average_neighbor_degree, average_neighbor_degree)
    # propertyDistance[3] = originalPropertyGT.averageKL(original_pageRank, pageRank)
    # propertyDistance[4] = originalPropertyGT.averageKL(original_triangle, triangle)
    # propertyDistance[5] = originalPropertyGT.averageKL(original_local_clustering_coefficient, local_clustering_coefficient)
    # propertyDistance[6] = originalPropertyGT.averageKL(original_core_number, core_number)

    print('\n')
    for i in range(len(propertyDistance)):
        print(propertyDistance[i], end="\t")
    print('\n')

#Function: Find all input files in given folder
def find_all_filenames(path_to_dir):
    filenames = os.listdir(path_to_dir)
    return filenames

if __name__ == "__main__":

    EdgeList_Original = []
    conf_file = open('Configuration.txt',"r")
    lineList = conf_file.readlines()
    conf_file.close()

    #Find input folder name
    input_folder = lineList[-1]+"/input_files/"
    allFiles = find_all_filenames(input_folder)
    data_file = input_folder+allFiles[0] #Read first input file

    #with open('/work/fz56/LANS-6.0/input_files/8.binetflow') as csvfile:
    with open(data_file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            EdgeList_Original.append((row["SrcAddr"], row["DstAddr"]))
    GT = nx.MultiDiGraph()
    GT.add_edges_from(EdgeList_Original)
    #GT = nx.read_graphml("CTU13_4_Original.graphml")
    originalPropertyGT = Property(GT)
    original_in_degree = originalPropertyGT.getInDegree()
    Original_Node_In_Degree = open('Original_Node_In_Degree.txt', "w")
    for e in original_in_degree:
        Original_Node_In_Degree.write(str(e) + "\n")
    Original_Node_In_Degree.close()

    original_out_degree = originalPropertyGT.getOutDegree()
    Original_Node_Out_Degree = open('Original_Node_Out_Degree.txt', "w")
    for e in original_out_degree:
        Original_Node_Out_Degree.write(str(e) + "\n")
    Original_Node_Out_Degree.close()

    # original_average_neighbor_degree = originalPropertyGT.getAverageNeighborDegree()
    # Original_average_neighbor = open('Original_average_neighbor_Degree.txt', "w")
    # for e in original_average_neighbor_degree:
    #     Original_average_neighbor.write(str(e) + "\n")
    # Original_average_neighbor.close()
    #
    # original_pageRank = originalPropertyGT.getPageRank()
    # Original_PageRank = open('Original_PageRank.txt', "w")
    # for e in original_pageRank:
    #     Original_PageRank.write(str(e) + "\n")
    # Original_PageRank.close()
    #
    # original_triangle = originalPropertyGT.getTriangles()
    # Original_Triangle = open('Original_triangle.txt', "w")
    # for e in original_triangle:
    #     Original_Triangle.write(str(e) + "\n")
    # Original_Triangle.close()
    #
    # original_local_clustering_coefficient = originalPropertyGT.getLocalClusteringCoefficient()
    # Original_Local_Clustering_Coefficient = open('Original_local_clustering_coefficient.txt', "w")
    # for e in original_local_clustering_coefficient:
    #     Original_Local_Clustering_Coefficient.write(str(e) + "\n")
    # Original_Local_Clustering_Coefficient.close()
    #
    # original_core_number = originalPropertyGT.getCoreNumber()
    # Original_Core_Number = open('Original_core_number.txt', "w")
    # for e in original_core_number:
    #     Original_Core_Number.write(str(e) + "\n")
    # Original_Core_Number.close()

    main(original_in_degree, original_out_degree, lineList[-1]
         # original_average_neighbor_degree, \
         # original_pageRank, \
         # original_triangle, \
         # original_local_clustering_coefficient,\
         # original_core_number
         )