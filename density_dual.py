#-------------------------------------------------------------------------------
# Name:        density.py
# Purpose:     Code to calculate density of each model cell for each time step.
#
# Copyright:   2016 Sophie Pearson-Grant
#
# This file is part of Gravity-ReservoirModelling.
#
#    Gravity-ReservoirModelling is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Gravity-ReservoirModelling is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Gravity-ReservoirModelling.  If not, see <http://www.gnu.org/licenses/>.
#
#
# 
# Dependent on: input tough2 file
#               output tough2 file.
#               Optionally can include the timesteps that you want on the command line, otherwise it will step through every timestep.
#
# Command line format ([] means optional):
# density.py filename.dat filename.out [-o output_filename] [-t time1 time2 time3...]
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()


import numpy as np
from t2listing import *
from t2data import *
import argparse


parser=argparse.ArgumentParser(description='Calculate density in each model cell')
parser.add_argument('i',type=str, help='TOUGH2 input file')
parser.add_argument('r',type=str, help='TOUGH2 results/listing file')
parser.add_argument('-o',type=str, help='optional output filename. Default is density.dat')
parser.add_argument('-t',type=float, nargs='*', help='timesteps to calculate at (rounded to nearest output step). Default is every timestep')
args=parser.parse_args()


print 'Calculating density of fluid in each element from TOUGH2 output at time (s):'


#import the input and output files
dat=t2data(args.i)
lst=t2listing(args.r)

#Calculate the density for each time step
#First check if want specific time steps or do all
if not args.t: #if no time steps on command line calculate for each timestep
    lst.first()
    fluid=np.zeros((len(dat.grid.blocklist),len(lst.times)+1)) #create empty matrix for each element at each time
    
    for time in range(len(lst.times)): #loop through each time
        element=0
        
        for cell in range(len(lst.element.row_name)): #loop through each element
            rowname=str(lst.element.row_name[cell])
            
            if rowname[0]=='2': # Elements that have a 2 in the first column are fracture properties so are incorporated elsewhere
                continue
            else: # if it's not a facture property do the calculation
                
                for rock in range(len(dat.grid.rocktypelist)):
                    if dat.grid.block[rowname].rocktype==dat.grid.rocktypelist[rock]: # loop through finding the relevant rocktype
                        
                        matpor=dat.grid.rocktypelist[rock+2].porosity
                        if cell==len(lst.element.row_name)-1: # If it's the last element and it's not a fracture property calculate it directly because there isn't a next block to compare it to and it can't be MINC. 1 row less because has titles.
                            fluid[element,time+1]=matpor*(lst.element['DG'][cell]*lst.element['SG'][cell]+lst.element['DW'][cell]*lst.element['SW'][cell]) # porosity of block * density of fluid.
                        elif rowname[1:5]==lst.element.row_name[cell+1][1:5]: # If the element is the same (minus the 2) it's a MINC block
                            fracpor=dat.grid.rocktypelist[rock+1].porosity #MINC files go main rock properties (an index really), fracture properties, matrix properties. At least as currently set up - think can change it.
                            matfluid=matpor*(1-dat.meshmaker[0][1]['vol'][0])*(lst.element['DG'][cell]*lst.element['SG'][cell]+lst.element['DW'][cell]*lst.element['SW'][cell])
                            fracfluid=fracpor*(dat.meshmaker[0][1]['vol'][0])*(lst.element['DG'][cell+1]*lst.element['SG'][cell+1]+lst.element['DW'][cell+1]*lst.element['SW'][cell+1])
                            fluid[element,time+1]=matfluid+fracfluid # The fluid density is the porosity*fluid density*fracture volume, summed for matrix and fracture
                        else:
                            fluid[element,time+1]=matpor*(lst.element['DG'][cell]*lst.element['SG'][cell]+lst.element['DW'][cell]*lst.element['SW'][cell]) #if it's a standard block just do the straight-forward calculation.
                        fluid[element,0]=lst.element.row_name[cell]
                        element=element+1
                        
        print lst.time
        lst.next()
    title=np.hstack((0.000000,lst.times))
    fluidoutput=np.vstack((title,fluid))

# if time steps are specified
else:
    notimes=len(args.t)
    times=np.zeros((notimes+1))
    fluid=np.zeros((len(dat.grid.blocklist),notimes+1)) #create empty matrix for each element at each time
    
    for time in range(notimes): #loop through each time
        lst.time=float(args.t[time])
        element=0
        
        for cell in range(len(lst.element.row_name)): #loop through each element
            rowname=str(lst.element.row_name[cell])
            if rowname[0]=='2': # Elements that have a 2 in the first column are fracture properties so are incorporated elsewhere
                continue
            else: # if it's not a facture property do the calculation
                for rock in range(len(dat.grid.rocktypelist)):
                    if dat.grid.block[rowname].rocktype==dat.grid.rocktypelist[rock]: # loop through finding the relevant rocktype
                        matpor=dat.grid.rocktypelist[rock+2].porosity
                        if cell==len(lst.element.row_name)-1: # If it's the last element and it's not a fracture property calculate it directly because there isn't a next block to compare it to and it can't be MINC.
                            fluid[element,time+1]=matpor*(lst.element['DG'][cell]*lst.element['SG'][cell]+lst.element['DW'][cell]*lst.element['SW'][cell]) # porosity of block * density of fluid.
                        elif rowname[1:5]==lst.element.row_name[cell+1][1:5]: # If the element is the same (minus the 2) it's a MINC block
                            fracpor=dat.grid.rocktypelist[rock+1].porosity #MINC files go main rock properties (an index really), fracture properties, matrix properties. At least as currently set up - think can change it.
                            matfluid=matpor*(1-dat.meshmaker[0][1]['vol'][0])*(lst.element['DG'][cell]*lst.element['SG'][cell]+lst.element['DW'][cell]*lst.element['SW'][cell])
                            fracfluid=fracpor*(dat.meshmaker[0][1]['vol'][0])*(lst.element['DG'][cell+1]*lst.element['SG'][cell+1]+lst.element['DW'][cell+1]*lst.element['SW'][cell+1])
                            fluid[element,time+1]=matfluid+fracfluid # The fluid density is the porosity*fluid density*fracture volume, summed for matrix and fracture
                        else:
                            fluid[element,time+1]=matpor*(lst.element['DG'][cell]*lst.element['SG'][cell]+lst.element['DW'][cell]*lst.element['SW'][cell]) #if it's a standard block just do the straight-forward calculation.
                        fluid[element,0]=lst.element.row_name[cell]
                        element=element+1
        print lst.time
        times[time+1]=lst.time
    fluidoutput=np.vstack((times,fluid))

fluidoutput=fluidoutput[np.argsort(fluidoutput[:,0])]


# save to file. columns are index, time 1, time 2,.... First row is the times.
if args.o:
    np.savetxt(args.o,fluidoutput,delimiter=",",fmt='%f')
else:
    np.savetxt('density.dat',fluidoutput,delimiter=",",fmt='%f')




