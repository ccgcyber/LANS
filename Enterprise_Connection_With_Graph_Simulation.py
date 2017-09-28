__author__ = 'fz56@msstate.edu'
__author__ = 'chrisl@dasi.msstate.edu'

import networkx as nx
from random import choice, shuffle, seed, sample, randint
from mpi4py import MPI
import datetime as dt
from itertools import chain
import ast
from operator import itemgetter
from graph_gen5 import create_graph
from graph_gen5 import get_size
from graph_gen5 import to_edge
import heapq
import sys
import os
import time
import json
from os import listdir



def find_all_filenames(path_to_dir):
    filenames = listdir(path_to_dir)
    return filenames

def main(comm = MPI.COMM_WORLD):
    numprocs = comm.size
    rank = comm.Get_rank()

    conf_file = open ('Configuration.txt',"r")
    lineList = conf_file.readlines()
    conf_file.close()

    input_folder = lineList[-1]+"/input_files/"
    with open(lineList[-1]+"/params.json") as json_file:
        data = json.load(json_file)
        if(data["seed"] == -1):
            data["seed"] = time
        seed(data["seed"])

    output_folder = os.path.dirname(os.path.dirname(input_folder))
    output_folder += "/SimulatedGraph/"
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    except:
        pass
    temp_folder = os.path.dirname(os.path.dirname(input_folder))
    temp_folder += "/temp/"

    if rank == 0:
        print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        print("Number of Processors: ", numprocs)
        print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        org_graphList = list(find_all_filenames(input_folder))
        
        graphList = []
        seedlist = []
        for n in range(numprocs):
            seedlist.append(randint(1,10000))
            graphList.append(choice(org_graphList))
        startIndex = []
        upperlevelNodes = []
        count = 0
        startIndex.append(count)

        for e in graphList:
            count += get_size(e, temp_folder)
            startIndex.append(count)
            upperlevelNodes.extend(sample(range(startIndex[-2], startIndex[-1]), 3))
    else:
        startIndex = None
        graphList = None
        seedlist = None

    startIndex = comm.bcast(startIndex, root=0)
    graphList = comm.bcast(graphList, root=0)
    seedlist = comm.bcast(seedlist, root=0)

    create_graph(temp_folder,graphList[rank], seed = seedlist[rank], startpoint = startIndex[rank])

    if rank == 0:
        #overallGraph = nx.MultiDiGraph()
        #print(upperlevelNodes)
        #upperlevelNodes = list(chain(*upperlevelNodes))
        degree = nx.utils.powerlaw_sequence(len(upperlevelNodes), 2)
        Outdegree = [int(round(e)) for e in degree]
        Indegree= [int(round(e)) for e in degree]
        shuffle(Indegree)
        edgesList = []
        outfile = open("SimulatedGraph/upperlevelGraph.csv", 'wb')
        while sum(Outdegree) >= 1:
            outIndex = Outdegree.index(max(Outdegree))
            temp = Indegree[outIndex]
            Indegree[outIndex] = 0
            for i in range(Outdegree[outIndex]):
                maxDegreeIndex = Indegree.index(max(Indegree))
                outfile.write((to_edge(temp_folder,upperlevelNodes[outIndex], upperlevelNodes[maxDegreeIndex]) + '\n').encode("utf-8"))
                Indegree[maxDegreeIndex] -= 1
            Outdegree[outIndex] = 0
            Indegree[outIndex] = temp
        outfile.close()

        #nx.write_graphml(overallGraph, "upperlevelGraph.graphml")
    MPI.Finalize()

if __name__ == "__main__":

    #print("---------------------------")
    startTime = dt.datetime.now ()
    #print('begin', startTime)
    #fileName = "CTU13_5.graphml" # this indicates input graph
    #G = nx.read_graphml(fileName) # load read graph into G
    main()
    #print('done', dt.datetime.now())
    #print(dt.datetime.now() - startTime)
