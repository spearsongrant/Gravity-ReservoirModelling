#-------------------------------------------------------------------------------
# Name:        cellcorners.py
# Purpose:     File to calculate the cell corners of a TOUGH2 model from the input file.
#
# Author:      Sophie Pearson-Grant
#
# Created:     10/07/2014
# Copyright:   (c) s.pearson-grant@gns.cri.nz
#
# 
#
# Command line needs name of file, number of elements in x direction, number of elements in y direction:
#     cellcorners.py modelname.extension #_x_elements #_y_elements
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

print 'Calculating cell corners from TOUGH2 input file'

from t2data import *
import sys

dat=t2data(sys.argv[1])

m=int(sys.argv[2])#input("Number of elements in x direction: ")      uncomment these 2 if would prefer prompted within script rather than written in command line.
n=int(sys.argv[3])#input("Number of elements in y direction: ")

vertices=np.zeros((len(dat.grid.block),7)) #create empty matrix to save vertices to.


for blk in dat.grid.blocklist:    #go through every element
    for conn in dat.grid.connectionlist: #go through every connection
        blockname0=float(str(conn.block[0]))    #need to turn the names of cells to floats so can see if they are in x,y or z directions.
        blockname1=float(str(conn.block[1]))

        if conn.block[0]==blk:           #if the first element in the connection is the same as the block, do calculation
            if blockname0==blockname1-1:            #x direction elements are +1
               vertices[blockname0-1,0]=blk.name #first is element name
               vertices[blockname0-1,1]=blk.centre[0]-conn.distance[0]   #then x min and max
               vertices[blockname0-1,2]=blk.centre[0]+conn.distance[0]
            elif blockname0==blockname1-m:          #y direction (elements are within same layer but m elements apart)
               vertices[blockname0-1,3]=blk.centre[1]-conn.distance[0]
               vertices[blockname0-1,4]=blk.centre[1]+conn.distance[0]
            elif blockname0==blockname1-(m*n):          #z direction (elements are next layer)
               vertices[blockname0-1,5]=blk.centre[2]-conn.distance[0]
               vertices[blockname0-1,6]=blk.centre[2]+conn.distance[0]

        elif conn.block[1]==blk:    # if at the end of the row there won't be a connection, so need to use the second element instead
            if vertices[blockname1-1,0]==0: #if it doesn't have a blockname, it didn't get caught in the previous x loop
               vertices[blockname1-1,0]=blk.name #first is element name
               vertices[blockname1-1,1]=blk.centre[0]-conn.distance[1]   #then x min and max
               vertices[blockname1-1,2]=blk.centre[0]+conn.distance[1]
            if blockname0==blockname1-m and vertices[blockname1-1,3]==vertices[blockname1-1,4]:  #y direction (elements are within same layer but m elements apart). If the min and max are equal didn't get found last time
               vertices[blockname1-1,3]=blk.centre[1]-conn.distance[1]
               vertices[blockname1-1,4]=blk.centre[1]+conn.distance[1]
            if blockname0==blockname1-(m*n) and vertices[blockname1-1,5]==vertices[blockname1-1,6]:          #z direction (elements are next layer)
               vertices[blockname1-1,5]=blk.centre[2]-conn.distance[1]
               vertices[blockname1-1,6]=blk.centre[2]+conn.distance[1]

l=len(vertices)
#for i in range(len(vertices)-(m*n)):   #if want to see the output
#    np.set_printoptions(suppress=True)
#    print vertices[:l,:]

np.savetxt('cellcorners.dat',vertices[:l,:],fmt='%d,%g,%g,%g,%g,%g,%g')