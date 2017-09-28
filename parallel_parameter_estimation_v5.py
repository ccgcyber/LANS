'''
Created on Feb 7, 2017

@author: sh2364@msstate.edu, tb2038@msstate.edu
'''

from __future__ import division
from mpi4py import MPI
import numpy as np
import pandas as pd
import csv
import sys
import os
import warnings
import Read_Params as rp
import timeit
import time
import math
from os import listdir

warnings.filterwarnings("ignore")

#Use MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
numprocs = comm.Get_size()

#Read params from json file
params = rp.Read_Params().Params
nRole = params['nRole']
noOfBins = params['noBin']
noOf_ThinBins = 20

#Read all input files from folder
def find_all_filenames(path_to_dir):
    filenames = listdir(path_to_dir)
    return filenames

#Read configuration, input and output file
conf_file = open('Configuration.txt',"r")
lineList = conf_file.readlines()
conf_file.close()
input_folder = lineList[-1]+"/input_files/"
allFiles = find_all_filenames(input_folder)
temp_folder = os.path.dirname(os.path.dirname(input_folder))
temp_folder += "/temp/"

for f in allFiles:
    Data_file = input_folder+f #Read each input file
    Role_info = temp_folder +"role_information"+ f.split('.')[0] +".csv"
    Role_df = pd.read_csv(Role_info, delimiter=',', usecols=[0, 1])
    Data_file_df = pd.read_csv(Data_file, delimiter=',',usecols=[0, 3, 6])
    s = (nRole, nRole)
    if rank == 0:
        #Initialize per file
        All_Role_Matrix = dict()
        Role_Nodelist_Matrix = dict()
        All_hist1_2 = dict()
        All_bins_indegree = dict()
        All_bins_outdegree = dict()
        nNodes = []

    for i in range(nRole):
        if rank == 0:
            merge_Indegree_Lst = []
            merge_Outdegree_Lst = []
            #Find all nodes in Role i
            nodeList = Role_df.loc[Role_df['Role'] == i, "Node"].tolist()
            Role_Nodelist_Matrix[i] = nodeList
            nNodes.append(len(nodeList))
        else:
            nodeList = None
            merge_Indegree_Lst = None
            merge_Outdegree_Lst = None

        #Broadcast list of nodes of role i to all processors
        nodeList = comm.bcast(nodeList, root=0)

        #All processors do the works below except processor zero
        noRow = int(np.ceil(len(nodeList)/float(numprocs-1)))#exclude rank 0
        start = (rank-1)*noRow
        end = start+noRow
        if start > len(nodeList) or start < 0:
            start = len(nodeList)
        if end > len(nodeList) or end == 0:
            end = len(nodeList)

        #Find the #indegree and #outdegree for each node
        Indegree_Lst = []
        Outdegree_Lst = []
        for node in nodeList[start:end]:
            node_data = Data_file_df[Data_file_df['SrcAddr']== node]
            Indegree_df = Data_file_df[Data_file_df['DstAddr'] == node]
            Indegree_Lst.append(len(Indegree_df))
            Outdegree_Lst.append(len(node_data))

        merge_Indegree_Lst = comm.gather(Indegree_Lst, root=0)
        merge_Outdegree_Lst = comm.gather(Outdegree_Lst, root=0)

        if rank == 0:
            #Merge all indegrees and outdegrees
            merge_Indegree_Lst = [val for sublist in merge_Indegree_Lst for val in sublist]
            merge_Outdegree_Lst = [val for sublist in merge_Outdegree_Lst for val in sublist]

            if merge_Indegree_Lst and merge_Outdegree_Lst:
                #Customized bins for both indegree and outdegree
                indeg_Edges = []
                outDeg_Edges = []
                for k in range(noOf_ThinBins+1):
                    indeg_Edges.append(k)
                    outDeg_Edges.append(k)

                #For this version number of bins are same for indegrees and outdegrees
                noOf_WideBins = noOfBins - noOf_ThinBins
                ind_BinWidth = math.ceil(((max(merge_Indegree_Lst)+1) - noOf_ThinBins)/noOf_WideBins)
                outd_BinWidth = math.ceil(((max(merge_Outdegree_Lst)+1) - noOf_ThinBins)/noOf_WideBins)

                if ind_BinWidth <= 0:
                   ind_BinWidth = 1
                if outd_BinWidth <= 0:
                    outd_BinWidth = 1

                #Calculating customized edges
                for l in range(noOf_WideBins):
                    indeg_Edges.append(indeg_Edges[-1] + ind_BinWidth)
                    outDeg_Edges.append(outDeg_Edges[-1] + outd_BinWidth)

                s1 = (noOfBins,noOfBins)
                hist1_2 = np.zeros(s1)
                bins_indegree = []
                bins_outdegree = []

                #Find histogram using numpy
                hist1_2, bins_indegree, bins_outdegree = np.histogram2d(merge_Indegree_Lst, merge_Outdegree_Lst, bins=(indeg_Edges, outDeg_Edges))

                #Save all work for role i
                All_hist1_2[i] = hist1_2
                All_bins_indegree[i] = bins_indegree
                All_bins_outdegree[i] = bins_outdegree

            else:
                #Save all work for empty role i
                s1 = (noOfBins,noOfBins)
                hist1_2 = np.zeros(s1)
                bins_indegree = np.zeros(noOfBins+1)
                bins_outdegree = np.zeros(noOfBins+1)
                All_hist1_2[i] = hist1_2
                All_bins_indegree[i] = bins_indegree
                All_bins_outdegree[i] = bins_outdegree

    #Write down everything for file f
    if rank == 0:
        output_filename = temp_folder +"Param_Roles_Information"+ f.split('.')[0] +".csv"
        output_nodehist = temp_folder +"node_degree_histogram2"+ f.split('.')[0] +".txt"
        if os.path.exists(output_filename):
            try:
                os.remove(output_filename)
            except OSError:
                pass
        if os.path.exists(output_nodehist):
            try:
                os.remove(output_nodehist)
            except OSError:
                pass

        Edge_Matrix = np.zeros(s)
        for i in range(nRole):
            for j in range(nRole):
                netflows_betw_role_ij = Data_file_df.loc[(Data_file_df['SrcAddr'].isin(Role_Nodelist_Matrix[i])) & Data_file_df['DstAddr'].isin(Role_Nodelist_Matrix[j])]
                Edge_Matrix[i][j] = len(netflows_betw_role_ij.index)
            All_Role_Matrix[i] = np.tile(Edge_Matrix[i], (nRole, 1))

        for i in range(nRole):
            All_Role_Matrix[i] = All_Role_Matrix[i]/All_Role_Matrix[i].sum(axis = 1) [:, None]
            All_Role_Matrix[i] = np.nan_to_num(All_Role_Matrix[i])

        matrices_file = open(output_filename,'ab')

        np.savetxt(matrices_file, np.array(nRole)[np.newaxis],fmt="%5.1f",  delimiter=",")
        np.savetxt(matrices_file, np.array([-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99])[np.newaxis], fmt="%5.1f", delimiter=",")

        for n in range(nRole):
            np.savetxt(matrices_file, All_Role_Matrix[n], fmt="%5.3f", delimiter=",")
            np.savetxt(matrices_file, np.array([-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99])[np.newaxis], fmt="%5.1f", delimiter=",")

        Edge_matrix_prob = Edge_Matrix[:]
        Matrix_sum = np.sum(Edge_matrix_prob)
        Edge_matrix_prob = Edge_matrix_prob/Matrix_sum
        Edge_matrix_prob = np.nan_to_num(Edge_matrix_prob)

        np.savetxt(matrices_file, Edge_Matrix,  fmt="%5.1f", delimiter=",")
        np.savetxt(matrices_file, np.array([-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99])[np.newaxis], fmt="%5.1f", delimiter=",")
        np.savetxt(matrices_file, Edge_matrix_prob,  fmt="%5.3f", delimiter=",")

        np.savetxt(matrices_file, np.array([-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99])[np.newaxis], fmt="%5.1f", delimiter=",")

        np.savetxt(matrices_file, np.array(nNodes[0:nRole]),fmt="%5.1f",  delimiter=",")
        np.savetxt(matrices_file, np.array([-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99,-99])[np.newaxis], fmt="%5.1f", delimiter=",")

        np.savetxt(matrices_file, np.array(Matrix_sum)[np.newaxis],fmt="%5.1f",  delimiter=",")
        matrices_file.close()

        #--------------------------------------------------------------------------------------------#

        nodehist_file = open(output_nodehist,'a')
        for n in range(nRole):
            a = All_bins_indegree[n]
            b = All_bins_outdegree[n]
            c = All_hist1_2[n]
            nodehist_file.write("%s\n" %(noOfBins))
            for i in range(0, noOfBins):
                for j in range(0, noOfBins):
                    nodehist_file.write("%s, %s, %s, %s, %s \n" % (a[i], a[i+1], b[j], b[j+1], c[i,j]))

        nodehist_file.close()

    #text_file.close()