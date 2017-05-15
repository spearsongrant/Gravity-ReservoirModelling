#-------------------------------------------------------------------------------
# Name:        gravity.py
# Purpose:     Calculate the gravity at each measurement station for a given model (in microgal).
#
# Author:      Sophie Pearson-Grant
#
# Created:     12/06/2014
# Copyright:   (c) s.pearson-grant@gns.cri.nz
# 
# 
#
# File requirements:
# density.dat - file that contains the density information, calculated in density.py.
# gravityfactor.dat - the contribution of each cell to each gravity measurement. Calculated in gravityfactor.py.
# station locations.csv - the measured gravity station name, x, y and z coordinates.
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

import numpy as np
import sys

print 'Calculating gravity signal'

# read in inputs
densitylong=np.loadtxt('density.dat', delimiter=',') # cell number, density. First row is times
density=densitylong[1::]
gravityfactor=np.loadtxt('gravityfactor.dat',delimiter = ',') # cell number, gravity factor for each station.
stationlocs=np.genfromtxt('station locations.csv', delimiter=',', dtype='S20',autostrip=True)

density=density[:len(gravityfactor),:]
gravity=np.zeros((gravityfactor.shape[1]-1,density.shape[1]-1)) #create file of zeroes for the results (number of columns minus one for cell name)



# Do the main calculation
# First check that the two files are in the same order, if not exit with an error
if np.array_equal(gravityfactor[:,0],density[:,0])!=True:
    sys.exit('Hold on, the orders of the density and gravity factor files are not right')

# Otherwise calculate density * gravity for each year, for each station
else:
    for station in range(1,gravityfactor.shape[1]):
        for year in range(1,density.shape[1]):
            gravity[station-1,year-1]=np.sum(density[:,year]*gravityfactor[:,station])*10**8 # in microgal

# Add the station name and x,y,z coordinates to the gravity output and save.
gravityoutput=np.hstack((stationlocs[1::,0:4], gravity))
fid=open('gravity.dat','wt')
fid.write('Station, x, y, z'+', %g'*len(densitylong[0,1::]-1) % tuple(densitylong[0,1::])+'\n')
np.savetxt(fid, gravityoutput,fmt='%s',delimiter=',')
fid.close()

# Calculate the gravity difference between years
gravitydiff=np.zeros((gravity.shape[0],gravity.shape[1]-1))
for year in range(1,gravity.shape[1]):
    gravitydiff[:,year-1]=gravity[:,year]-gravity[:,0]

gravitydiff=np.hstack((stationlocs[1::,0:4],gravitydiff))
fid=open('gravitydifference.dat','wt')
fid.write('Station, x, y, z'+', %g'*len(densitylong[0,2::]-1) % tuple(densitylong[0,2::])+'\n')
np.savetxt(fid, gravitydiff,fmt='%s',delimiter=',')
fid.close()
