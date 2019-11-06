#-------------------------------------------------------------------------------
# Name:        gravity.py
# Purpose:     Calculate the gravity difference relative to initial timestep at each measurement station for a given model (in microgal).
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
#
# File requirements:
#       density.dat - file that contains the density information, calculated in density.py.
#       gravityfactor.dat - the contribution of each cell to each gravity measurement. Calculated in gravityfactor.py.
#       station locations.csv - the measured gravity station name, x, y and z coordinates.
#
# Command line ([] shows optional, with default filename. By default there is no gravity output, only gravity difference):
#       gravity.py [-d density.dat] [-f gravityfactor.dat] [-s "station locations.cvs"] [-o gravitydifference.dat] [-g gravity.dat]
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

import numpy as np
import argparse
import sys

parser=argparse.ArgumentParser(description='Calculate gravity difference at each measurement station (in microgal) relative to first timestep')
parser.add_argument('-d',type=str, help='optional density filename. Default is density.dat')
parser.add_argument('-f',type=str, help='optional gravityfactor filename. Default is gravityfactor.dat')
parser.add_argument('-s',type=str, help='optional station locations filename. Default is "station locations.csv"')
parser.add_argument('-o', type=str, help='optional output filename for calculated gravity difference. Default is gravitydifference.dat')
parser.add_argument('-g', type=str, help='optional output file for calculated gravity at each timestep. Default is no output')
args=parser.parse_args()



print('Calculating gravity signal')

# read in density file (cell number, density. First row is times)
if args.d:
    densitylong=np.loadtxt(args.d, delimiter=',')
else:
    densitylong=np.loadtxt('density.dat', delimiter=',') 
density=densitylong[1::]
#read in gravity factor (cell number, gravity factor for each station)
if args.f:
    gravityfactor=np.loadtxt(args.f,delimiter = ',')
else:
    gravityfactor=np.loadtxt('gravityfactor.dat',delimiter = ',') 
#read in station locations
if args.s:
    stationlocs=np.genfromtxt(args.s, delimiter=',', dtype='U20', autostrip=True)
else:    
    stationlocs=np.genfromtxt('station locations.csv', delimiter=',', dtype='U20', autostrip=True)
density=density[:len(gravityfactor),:]
gravity=np.zeros((gravityfactor.shape[1]-1,density.shape[1]-1)) #create file of zeroes for the results (number of columns minus one for cell name)



# Do the main calculation
# First check that the two files are in the same order, if not exit with an error
if np.array_equal(gravityfactor[:,0],density[:,0])!=True:
    sys.exit('Hold on, the orders of the density and gravity factor files are not right')

# Otherwise calculate density * gravity for each time, for each station
else:
    for station in range(1,gravityfactor.shape[1]):
        for time in range(1,density.shape[1]):
            gravity[station-1,time-1]=np.sum(density[:,time]*gravityfactor[:,station])*10**8 # in microgal
            
# If gravity values are requested, add the station name and x,y,z coordinates to the gravity output.
if args.g:
    gravityoutput=np.hstack((stationlocs[1::,0:4], gravity))
    fid=open(args.g,'wt')
    fid.write('Station, x, y, z'+', %g'*len(densitylong[0,1::]-1) % tuple(densitylong[0,1::])+'\n')
    np.savetxt(fid, gravityoutput,fmt='%s',delimiter=',')
    fid.close()


    
# Calculate the gravity difference between the current time and the first one
gravitydiff=np.zeros((gravity.shape[0],gravity.shape[1]-1))
for time in range(1,gravity.shape[1]):
    gravitydiff[:,time-1]=gravity[:,time]-gravity[:,0]

#Add the station name and x,y,z coordinates to the gravity difference and save.
gravitydiff=np.hstack((stationlocs[1::,0:4],gravitydiff))
if args.o:
    fid=open(args.o,'wt')
else:
    fid=open('gravitydifference.dat','wt')
fid.write('Station, x, y, z'+', %g'*len(densitylong[0,2::]-1) % tuple(densitylong[0,2::])+'\n')
np.savetxt(fid, gravitydiff, fmt='%s',delimiter=',')
fid.close()
