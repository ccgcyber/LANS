import numpy
import mpi4py
from mpi4py import MPI
import os
import time
import sys
import ast
import gc
import random


def set_attr(at_list, attrdict):
    res = []
    count = 0
    accumulator = 0
    flag1 = 0
    for each in at_list:
        obj = ""
        if len(attrdict[each]) != 0:
            rand = random.randint(0,1000000)
            rand = float(rand)/1000000
            for item in attrdict[each][1]:
                accumulator += item
                count += 1
                if accumulator >= rand:
                    try:
                        obj = str(attrdict[each][0][count-1]).strip("(").strip("[").strip("]").split(",")
                        if len(obj) == 1:
                            obj = obj[0]

                        if isinstance(obj,(list,tuple)):
                            try:
                                obj[0] = float(obj[0])
                                obj[1] = float(obj[1])
                                obj = random.uniform(obj[0],obj[1])
                            except ValueError,e:
                                obj = obj[0]

                    except SyntaxError, e:
                        obj = str(attrdict[each][0][0]).split(",")[0].strip("(")
                    break
            count = 0
        res.append(obj)
        count = 0
    return [res]


def protocol(protoarray):
    prot = random.randint(0,100000)
    prot = float(prot)/100000
    accumulator = float(0)
    count = 0
    for each in protoarray[1]:
        accumulator += each
        if accumulator >= prot:
            return protoarray[0][count]
        count += 1
    return protoarray[0][count-1]


def get_size(size_input,temp_folder):
    #returns the number of nodes that will be present in a simulation of scenario
    size_file = open(temp_folder +'Param_Roles_Information' + size_input.split('.')[0] + '.csv','r')
    size_ar = []
    for each in size_file:
        size_ar.append(each)
    size_file.close()
    size_ar[0] = int(float(size_ar[0].strip(' ').strip('\n')))
    loc = size_ar[0] * size_ar[0] + size_ar[0] * 2 + size_ar[0] + 4
    count = 0
    accum = 0
    while count < loc + size_ar[0]:
        if count >= loc:
            accum += int(float(size_ar[count]))
        count += 1
    return accum


def to_edge(temp_folder, source, dest):
    # creates the crossover edges between enterprises
    fsource = open(temp_folder +'samples.csv','r')
    tempar = []
    for each in fsource:
        tempar.append(each)
    ran = random.randint(0,len(tempar)-1)
    line = tempar[ran].strip('\n').split(',')
    line[0] = str(source)
    line[1] = str(dest)
    st = ''
    for each in line:
        st += each + ','
    line = st.strip(',')
    return line


def add_edge(b,c,role,mal_role,mal_nodes,protoarray,temparray,attrdict):
    d = protocol(protoarray)
    oth = set_attr(temparray,attrdict)
    ret = [b,c,d]
    botflag = 0
    for each in mal_nodes:
        if int(each) == int(b):
            botflag = 1
    for each in oth:
        for item in each:
            ret.append(item)
    if('otnet' in ret[-1] or 'alicious' in ret[-1]):
        ret[-1] = 'flow = background'
    if(role == mal_role and botflag == 1):
        ret[-1] = 'flow = Botnet Activity'
    else:
        ret[-1] = 'flow = normal dataflow'
    return ret,False


def generate_edge(f,TM,nodes,innodes,outnodes):
    #determines the start and end point for an edge to be added to the graph, also modifies innodes and outnodes
    if len(outnodes[f]) > 1:
        gen = random.randint(0, len(outnodes[f])-1)
    elif len(outnodes[f]) == 1:
        gen = 0
    else:
        count = 0
        f = -1
        for each in outnodes:
            if len(each) >= 1:
                f = count
            count += 1
        if f >= 0:
            if len(outnodes[f]) > 1:
                gen = random.randint(0, len(outnodes[f])-1)
            else:
                gen = 0
        else:
            return 'complete', 'complete'
    p = outnodes[f][gen][1]  # previous role connection
    i = outnodes[f][gen][0]  # node ID
#    count = 0
#    for each in innodes:
#        for item in each:
#            if int(item[2]) < 1:
#                innodes[count].remove(item)
#        count += 1
    j = TM[f][p]  # matrix entry for previously connected role
    k = float(random.randint(0, 10000))/10000
    dest = -1
    count = 0
    for each in nodes:  # assign the destination role to a non-empty role
        if len(each) != 0:
            dest = count
            break
        count += 1

    tmp = 0
    count = 0
    for each in j:  # determine, based on probability, which role we should connect to
        tmp += each
        if tmp >= k:
            dest = count
            break
        count += 1
    flag2 = 0
    if len(innodes) > dest:  # make sure we didnt select an invalid role
        if len(innodes[dest]) > 1:  # if the role is has nodes in it, we will choose a destination from it
            tflag = 1
            while tflag == 1:
                k = random.randint(0,len(innodes[dest])-1)
                if int(innodes[dest][k][2]) < 1:
                    innodes[dest].remove(innodes[dest][k])

                else:
                    tflag = 0
        elif len(innodes[dest]) == 1:  # one entry condition
            k = 0
        else:
            flag2 = 1
            k = random.randint(0,len(nodes[dest])-1)  # choosing a random value from the chosen destination role

    if flag2 == 1:

        count = 0
        for each in innodes:
            count += len(each)
        if count >= 1:
            tmp = random.randrange(0,count)
            count = 0
            k = -1
            for each in innodes:
                if len(each) <= tmp:
                    tmp -= len(each)
                    count += 1
                elif k == -1:
                    k = tmp
                    tmp -= len(each)
                    dest = count
        else:
            ret = nodes[dest][k][0]
            outnodes[f][gen][2] = dest
            outnodes[f][gen][3] -= 1  # decrement the outdegree of the source node
            if outnodes[f][gen][3] == 0:  # if the source node is now empty of out degree, we remove it from the list
                outnodes[f].remove(outnodes[f][gen])
            global totalflag
            if totalflag == 1:
                return dest, i, ret,innodes,outnodes,nodes
            else:
                print "report this error to Chris", innodes[dest][k][0]
                sys.exit(-1)

    ret = innodes[dest][k][0]  # get the ID for the chosen destination node     IF IN ERROR, REPORT TO CHRIS

    innodes[dest][k][2]  = int(innodes[dest][k][2]) - 1  # decrement the indegree for destination node
    if innodes[dest][k][2] <= 0:  # if after decrement the indegree becomes zero, we remove it from innodes
        innodes[dest].remove(innodes[dest][k])

    outnodes[f][gen][2] = dest  # Update previously connected role in the source node
    outnodes[f][gen][3] -= 1  # decrement the outdegree of the source node
    if outnodes[f][gen][3] == 0:  # if the source node is now empty of out degree, we remove it from the list
        outnodes[f].remove(outnodes[f][gen])

    return dest, i, ret,innodes,outnodes,nodes


def edge_creation(RPM,TM,nodes,mal_role,innodes,outnodes,proto,at_list,attrdict,mal_info):
    # this function generates the edgelist that will become the final graph when written to file
    edgelist = []
    count = 0
    flag = 0
    warn = False
    warn_flag = False
    # identify which nodes are considered botnet nodes from the malicious activity file for labeling netflow
    potential_bots = []
    for each in nodes[mal_role]:
        if each[2] >= mal_info[2] and each[2] <= mal_info[3] and each[3] >= mal_info[4] and each[3]<= mal_info[5]:
            potential_bots.append(each[0])
    if len(potential_bots) < mal_info[1]:
        num_bots = len(potential_bots)
    else:
        num_bots = mal_info[1]
    mal_nodes = numpy.random.choice(potential_bots,num_bots,replace=False)
    # this loop continues until the total remaining outdegree is equal to zero
    while flag != 1:
        role = 0
        x = float(random.randint(0,99999999))
        x /= 100000000
        accumulator = 0
        for each in RPM:
            for item in each:
                if accumulator <= x:
                    accumulator += item
            if accumulator <= x:
                role += 1
        x,y,z,innodes,outnodes,nodes = generate_edge(role,TM,nodes,innodes,outnodes)
        if y == 'complete':
            break
        if y != z:
            edge,warn = add_edge(y,z,role,mal_role,mal_nodes,proto,at_list,attrdict)
            edgelist.append(edge)
        flag = 1
        if warn == True:
            # this is set for indication of whether the warning file needs to contain a warning or an all clear message
            warn_flag = True
        for each in outnodes:
            if len(each) > 0:
                flag = 0
        count += 1

    edgelist.sort(key=lambda x: x[3])
    return edgelist,warn_flag,innodes,outnodes


def write_graph_to_file(temp_folder,at_list,edgelist):
    # this function creates the graph file and
    comm = mpi4py.MPI.COMM_WORLD
    MPI_rank = comm.Get_rank()
    #name_outputfile = "SimulatedGraph/localgen_" + str(MPI_rank)+'.csv'
    name_outputfile = os.path.dirname(os.path.dirname(temp_folder))
    name_outputfile = name_outputfile + "/SimulatedGraph/localgen_" + str(MPI_rank)+'.csv'
    #name_outputfile = name_outputfile + "\\SimulatedGraph\\localgen_" + str(MPI_rank)+'.csv'

    # starts the graph file with a header for identification of collumns
    outfile = open(name_outputfile, 'wb')
    topline = "source,destination,proto,"
    for each in at_list:
        topline = topline + each + ","
    outfile.write((topline + '\n').encode("utf-8"))
    count = 0
    miscfile = open(temp_folder+'samples.csv','wb')
    i = 0
    #this series of loops writes the graph to a file and also creates a samples file for enterprise connection
    for each in edgelist:
        for item in each:
            count += 1
            outfile.write(str(item).encode("utf-8"))
            if(i < 50 and each[-1] != 'flow=Botnet Activity' and len(each) > 2 and MPI_rank == 0):
                miscfile.write(str(item).encode("utf-8"))
                if count < len(each):
                    miscfile.write(','.encode("utf-8"))
                else:
                    miscfile.write('\n'.encode("utf-8"))
                    i += 1
            if count < len(each):
                outfile.write(','.encode("utf-8"))
            else:
                outfile.write('\n'.encode("utf-8"))
                count = 0


def write_warning_file(temp_folder,warn_flag):
    # writes a warning file that indicates whether indgree ran out or if there has been an error with histograms
    LOC = os.path.dirname(os.path.dirname(temp_folder))
    warn = open(LOC+'/Warning_File.txt',"wb")
    #warn = open(LOC+'\\SimulatedGraph\\Warning_File.txt',"w")
    if warn_flag == True:
        warn.write("WARNING\n")
        warn.write("detected edge connection between unanticipated roles or missing histogram\n")
        warn.write("edge attributes have been randomly assigned from existing histograms for any such connections\n")
    else:
        warn.write("generation complete with no warnings")


def make_node(num,bucket,rolecounter):
    node = []
    indeg = numpy.random.randint(int(float(bucket[0])),int(float(bucket[1])))
    outdeg = numpy.random.randint(int(float(bucket[2])),int(float(bucket[3])))
    node.append(num)
    node.append(rolecounter)
    node.append(indeg)
    node.append(outdeg)

    return node


def node_generator(nodecounter,bucket,rolecounter):
    generated = []
    num = int(float(bucket[4]))
    i = 0
    while i < num:
        val = nodecounter + i
        generated.append(make_node(val,bucket,rolecounter))
        i += 1
    return generated


def node_maker(histograms):
    nodecounter = 0
    rolecounter = 0
    l1 = []
    for item in histograms:
        elist = []
        l1.append(elist)
        for each in item:
            num = each[4]
            if int(float(num)) > 0:
                temp = node_generator(nodecounter,each,rolecounter)
                for each in temp:
                    l1[rolecounter].append(each)
            nodecounter += int(float(num))

        rolecounter += 1
    return l1


def setstart(r1,TM):
    flag = -1
    for each in TM[r1][r1]:
        if each > 0.01:
            flag = r1
    count = 0
    if flag == -1:
        for each in TM[r1]:
            for item in each:
                if item > 0.01:
                    flag = count
            count += 1
    if flag == -1:
        flag = 0
    return flag


def nodeCreation(roles,TM,a,startpoint,GI,histlist,innodes,outnodes):
    # this function creates the list of nodes (vertices) for the graph including the in and out degree and assigned role
    count = 0
    startpos = []
    gc.collect()
    #generate the nodes
    nodes = node_maker(histlist)
    # each role gets it's own list of member nodes
    while count < roles:
        startpos.append(setstart(count,TM))
        count += 1
    #generate the nodes to fill the required number for each role


    count = 0
    for each in nodes:
        for item in each:
            count += 1
            item[0] += startpoint
    count = 0
    RPM = []
    while count < roles:
        n = GI[count]
        n = n.split(',')
        o = []
        for m in n:
            o.append(float(m) / float(GI[roles*3]))
        count += 1
        RPM.append(o)

    count = 0
    iterator = 0

    # these loops create the indegree and outdegree objects that are used to determine where edges when they are generated
	# they also delete any entries that have a zero for the associated degree so that node will not be used in the associated direction

    for each in nodes:
        outnodes.append([])
        innodes.append([])
        for item in each:
            outnodes[count].append([])
            innodes[count].append([])
            for obj in item:
                outnodes[count][iterator].append(obj)
                innodes[count][iterator].append(obj)
            iterator += 1
        iterator = 0
        count += 1
    count = 0
    iterator = 0
    for each in nodes:
        if len(each) != 0:
            for item in each:
                if int(item[2]) <= 0:
                    innodes[count].remove(item)
                iterator += 1


        count += 1


    count = 0
    for each in nodes:
        if len(each) != 0:
            for item in each:
                if int(item[3]) == 0:
                    outnodes[count].remove(item)
        count += 1
    intotal = 0
    intop = 0
    for each in innodes:
        for item in each:
            intotal += item[2]
            if item[2] > intop:
                intop = item[2]
    outtotal = 0
    for each in outnodes:
        for item in each:
            outtotal += item[3]
    global totalflag
    totalflag = 0
    if intotal <= outtotal:
        totalflag = 1

    return nodes,RPM,innodes,outnodes


def protoinput(temp_folder,scenario):
    count = 0
    protofile = open(temp_folder+'Proto'+scenario+'.txt','r')
    protoarray = []
    for each in protofile:
        each = each.rstrip('\n')
        each = ast.literal_eval(each)
        if count > 0:
            protoarray.append(each)
        count += 1
    protofile.close()
    return protoarray


def read_node_histograms(loc):
    f1 = open(loc,"r")
    i = 0
    num = -1
    histlist = []
    l1 = []
    for each in f1:
        each = each.strip("\n")
        if i < num:
            each = each.split(",")
            obj = each[4].strip("\n")
            obj = float(obj)
            if obj >= 1.0:
                l1.append(each)
            i += 1
        elif num == -1:
            num = int(each) * int(each)
        else:
            i = 0
            num = int(each) * int(each)
            histlist.append(l1)
            l1 = []
    if l1 != []:
        histlist.append(l1)
    return histlist


def attrinput(temp_folder,scenario,at_list):
    ret = dict()
    for each in at_list:
        title = each
        count = 0
        try:
            attrfile = open(temp_folder+each+scenario+'.txt','r')
        except IOError,e:
            ret[title]= []
            continue
        attrarray = []
        for each in attrfile:
            each = each.rstrip('\n')
            each = ast.literal_eval(each)
            if count > 0:
                attrarray.append(each)
            count += 1
        attrfile.close()
        ret[title] = attrarray
    return ret


def setupAndFiles(temp_folder,scenario,seed):
    fname = scenario.split('.')
    infilename = "_" + scenario
    scenario = ''
    count = 1
    if len(fname) == 1:
        scenario = fname[0]
    for each in fname:
        if count < len(fname):
            scenario = scenario + each
        count += 1
    if(seed == 0):
        seed = time
    random.seed(seed)
    roles = 0
    input_folder = os.path.dirname(os.path.dirname(temp_folder))
    input_folder += "/input_files/"
    #input_folder += "\\input_files\\"
    at_list = ["StartTime","Dur","Sport","Dir","Dport","State","sTos","dTos","TotPkts","TotBytes","Label"]
    proto = protoinput(temp_folder,scenario)
    attrdict = attrinput(temp_folder,scenario,at_list)
    #attribute_histograms = get_histograms(scenario,temp_folder, at_list)
    mal_role = temp_folder+ "malicious_role" +scenario + ".txt"
    mal_role = open(mal_role,'r')
    mal_info = []
    for each in mal_role:
        mal_info.append(int(each))
    mal_role = mal_info[0]
    if len(fname) > 1:
        name_inputfile = input_folder+ scenario + "." + fname[-1]#name_inputfile = "" + scenario + "." + fname[-1]
    else:
        name_inputfile = input_folder+ scenario


    TPM = open(temp_folder+"Param_Roles_Information" + scenario + ".csv", 'r')
    histfile = temp_folder+"node_degree_histogram2"+ scenario + ".txt"
    histlist = read_node_histograms(histfile)
    return at_list,proto,mal_role,TPM,histlist,attrdict,mal_info


def setupAndFilesCont(TPM):
    TM = []
    GI = []
    count = -1
    i = 0
    for each in TPM:
        if count == -1:
            roles = int(float(each.strip(',').strip('\n')))
        if count > 0:
            GI.append(each.strip('\n'))
        count += 1
        if count > roles:
            if i < roles:
                TM.append(GI)
                GI = []
            count = 0
            i += 1
    TPM.close()
    tp = []
    for each in GI:
        x = each.strip(',')
        if len(x) > 0:
            tp.append(x)
    tmp = []
    tp = []
    a = []
    for each in TM:
        for item in each:
            item = item.split(',')
            for part in item:
                part = float(part)
                tp.append(part)
            tmp.append(tp)
            tp = []
        a.append(tmp)
        tmp = []

    TM = a
    count = 0
    a = []
    while count < roles:
        a.append(0)
        count += 1
    count = 0
    while count < roles:
        x = GI[(len(GI)-1-roles+count)]
        a[count] = int(float(x))
        count += 1
    return roles,TM,a,GI


def create_graph(temp_folder,scenario,seed = 0,startpoint = 0):
    # this is the primary controller function
    innodes = []
    outnodes = []
    at_list,proto,mal_role,TPM,histlist,attrdict,mal_info = setupAndFiles(temp_folder,scenario,seed)
    roles,TM,a,GI = setupAndFilesCont(TPM)
    nodes,RPM,innodes,outnodes = nodeCreation(roles,TM,a,startpoint,GI,histlist,innodes,outnodes)
    edgelist,warn_flag,innodes,outnodes = edge_creation(RPM,TM,nodes,mal_role,innodes,outnodes,proto,at_list,attrdict,mal_info)
    write_graph_to_file(temp_folder,at_list,edgelist)

    write_warning_file(temp_folder,warn_flag)


if __name__ == "__main__":

    start = time.time()
    #create_graph("5",startpoint=0)
    TF = "C:\\Users\\Chris\\Desktop\\role4_bins200\\temp\\"
    #TF = "/work/fz56/Graph-Simulation-4-master/newfolder/"
    create_graph(TF,"11",seed=0)
    print(time.time() - start)
    #comm = mpi4py.MPI.COMM_WORLD
    #MPI_size = comm.Get_size()
    #MPI_rank = comm.Get_rank()