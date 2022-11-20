#!/usr/bin/python3
import argparse
import os
import subprocess
import tempfile
import matplotlib.pyplot as plt
import numpy as np

'''This script generates the plot of distance between two particles over the course of the simulation (only the trajectory plot)
   by going over different folders of simulation carrying out the oat command and storing the data for final combined plotting'''

parser = argparse.ArgumentParser(description='Gives the combined plot of interparticle distances from different folders')
parser.add_argument('-f', '--folders', metavar = 'folders',  nargs='+',  action='append', help = 'Folders to do analysis in')
parser.add_argument('-p', '--particle IDs', metavar = 'particles',  nargs='+',  action='append', help = 'Particles to find the distance between')
parser.add_argument('-o', '--outputfilename', metavar = 'outputfile',  nargs='+',  action='append', help = 'Name of the output file')
args = parser.parse_args()

#Storing the current working directory
#initialising a list called processes and a dict called timedict

#Goes through each directory (taken from -f arguments) and does 1) stores the total runtime (in SU) in the timedict and 2) runs the oat command taking the
#particle IDs from the -p arguments. Then tmeporary file and the stdout of the oat command are stored in processes after which it returns to starting directory

processes = []
wd = os.getcwd()
timedict = {}
for i in vars(args).get('folders')[0]:
    os.chdir(i)
    time = 1
    with open('input.txt', 'r') as inputfile:
        for line in inputfile.readlines():
            if line.startswith('steps ='):
                time = time*float(line[7:].strip())
            if line.startswith('dt ='):
                time = time*float(line[4:].strip())
            timedict[i] = time
    f = tempfile.TemporaryFile()
    p = subprocess.run(['oat', 'distance_oxDNA_modified', '-i', 'input.txt', 'trajectory.dat', vars(args).get('particle IDs')[0][0], vars(args).get('particle IDs')[0][1], '-f', 'trajectory'], capture_output=True, text = True)
    processes.append((p.stdout, f))
    os.chdir(wd)

#the data from processes is filtered into a list, distancepoints: only numbers are collected, sublist is split, spaces and newlines are stripped
#and string is converted to float such that a 1D list is obtained
print(processes)

array = []
for i in range(len(processes)):
    x1 = processes[i][0].index('array([')
    x2 = processes[i][0].index(']])]\n')
    array.append(processes[i][0][x1 + len('array([') + 1: x2])

distancepoints = []
for i in array:
    split = i.split(',')
    for j in split:
        strip = float(j.strip())
        distancepoints.append(strip)


distancepoints = np.array(distancepoints)
mean = np.mean(distancepoints)
stdev = np.std(distancepoints)
median = np.median(distancepoints)

#total run time of each simulation segment is added and then multiplied with 3 picoseconds to obtain the total runtime
#which is then used for plotting

totaltime = sum(timedict.values())*(3e-12)/1e-9
print(timedict)
timepoints = np.linspace(0,totaltime,len(distancepoints))

full_array = np.stack([timepoints, distancepoints], axis = 1)
np.savetxt("distancepoints.txt", full_array, delimiter = ",", header = "time, distance", fmt='%f', comments = '')
print(timepoints)

#string formatting to use the outputfilename from the -o argument and assign it to the outputting image of the plot


#the stdout from the processes is pasted in a text file and the file is outputted along with the stats
with open('distancedata.txt', 'w+') as r:
        for a, b in processes:
                    r.write(a)
        r.write(f'For all simulation segments that stats are: mean - {mean}; median - {median}; stdev - {stdev}')

imagefilename = vars(args).get('outputfilename')[0][0]
plt.plot(timepoints,distancepoints)
plt.xlabel('time(ns)')
plt.ylabel('distance(nm)')
plt.show()
plt.savefig(f'{imagefilename}.png')
plt.close()
plt.hist(distancepoints)
plt.ylabel('frequency')
plt.xlabel('distance(nm)')
plt.savefig('histogram.png')