#-------------------------------------------------------------------------------
# Name:        gravityfactor.py
# Purpose:     calculate the 'gravity factor' - the contribution of each grid block to the signal at each
#              gravity measurement station. Uses equation 10 from Li and Chouteau 1998 
#              (the derivation from Okabe 1979).
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
#    along with Gravity-ReservoirModelling.  If not, see <http://www.gnu.org/licenses/>.#
#
#
#
#
# File requirements:
#       cellcorners.dat - a file containing the grid block name and the minimum and maximum of each grid block in the x,y,z directions.
#       station locations.csv - the measured gravity station name, x, y and z coordinates.
#
# Code dependencies:
#       cellcorners.py to create cellcorners.dat from TOUGH2 input file (if required).
#       Used as input for gravity.py.
#
#
# Command line: gravityfactor.py [-g grid file (optional)] [-s station locations (optional)] [-o output filename (optional)]
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

import numpy as np
import argparse

parser=argparse.ArgumentParser(description='Calculate contribution of each grid block to each gravity measurement station signal')
parser.add_argument('-g',type=str, help='optional grid information filename. Default is cellcorners.dat')
parser.add_argument('-s',type=str, help='optional station locations filename. Default is "station locations.csv"')
parser.add_argument('-o',type=str, help='optional output filename. Default is gravityfactor.dat')
args=parser.parse_args()



print 'Calculating the contribution of each model element to the gravity signal.'


# import grid. Format is cell number, x min, x max, y min, y max, z min, z max
if args.g:
    grid=np.loadtxt(args.g,delimiter = ',')
else:
    grid=np.loadtxt('cellcorners.dat',delimiter = ',') #cell number, x min, x max, y min, y max, z min, z max

# import station locations. x,y,z. Skips the first row, which is the headers, and the first column, which contains the station name.
if args.s:
    stationlocs=np.loadtxt(args.s, delimiter=',', skiprows=1, usecols=range(1,4))
else:
    stationlocs=np.loadtxt('station locations.csv', delimiter=',', skiprows=1, usecols=range(1,4)) 

    
    
# a subroutine to carry out the multiplication and summation in the main term of equation 10 from Li and Chouteau 1998. Also to multiply by G (density is calculated elsewhere as it varies between model runs/time steps).
def gravitycalculation(stationlocs,cellcorners):
    r=np.zeros((2,2,2))
    mu=np.zeros((2,2,2))
    g=np.zeros((2,2,2))
    l=np.zeros((2,2,2))
    x=np.zeros((2))
    y=np.zeros((2))
    z=np.zeros((2))

    x[0]=stationlocs[0]-cellcorners[1] #x1
    x[1]=stationlocs[0]-cellcorners[2] #x2
    y[0]=stationlocs[1]-cellcorners[3] #y1
    y[1]=stationlocs[1]-cellcorners[4] #y2
    z[0]=-(stationlocs[2]-cellcorners[5]) #z1  Negative because z is positive downwards, but is negative downwards in Petrasim
    z[1]=-(stationlocs[2]-cellcorners[6]) #z2

#loop through each x,y,z combination calculating the terms for summation.
    for i in range(2):
        for j in range(2):
            for k in range(2):
                r[i,j,k]=np.sqrt(np.square(x[i])+np.square(y[j])+np.square(z[k])) #  Equation 6, to get the scalar distance.
                mu[i,j,k]=((-1)**i)*((-1)**j)*((-1)**k) # Equation 7, to determine if positive or negative term.
                g[i,j,k]=mu[i,j,k]*((x[i]*np.log(y[j]+r[i,j,k]))+(y[j]*np.log(x[i]+r[i,j,k]))+(2*z[k]*np.arctan((x[i]+y[j]+r[i,j,k])/z[k]))) # Equation 10, to determine the gravity factor for each x,y,z combination.

    gravityfactor=-6.67384e-11*np.sum(g) # Sum and multiply by G.
    return gravityfactor # send gravity factor for that model cell-measurement station pair back to main routine.


# main routine to calculate gravity factor for each model cell for each measurement station. Calls gravitycalculation subroutine.
gf=np.zeros((len(grid),len(stationlocs)+1)) # extra column to include cell names
for station in range(len(stationlocs)):
    for element in range(len(grid)):
        gf[element,0]=grid[element,0] # column zero of output is cell name
        gf[element,station+1]=gravitycalculation(stationlocs[station,:],grid[element,:]) #other columns are gravity factors

        
# save output to file        
if args.o:
    np.savetxt(args.o, gf, fmt='%g', delimiter=',')
else:        
    np.savetxt('gravityfactor.dat', gf, fmt='%g', delimiter=',')
