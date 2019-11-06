#-------------------------------------------------------------------------------
# Name:        cellcorners.py
# Purpose:     File to calculate the cell corners of a TOUGH2 model from the input file.
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
# Command line needs name of file, number of elements in x direction, number of elements in y direction:
#     cellcorners.py modelname.extension #_x_elements #_y_elements output_filename(optional)
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

from t2data import *
import argparse

parser=argparse.ArgumentParser(description='Calculate cell corners from TOUGH2 input file')
parser.add_argument('i',type=str, help='input file')
parser.add_argument('x', type=int, help='number of elements in x')
parser.add_argument('y', type=int, help='number of elements in y')
parser.add_argument('-o', type=str, help='optional output filename. Default is cellcorners.dat')
args=parser.parse_args()


print 'Calculating cell corners from TOUGH2 input file'

dat=t2data(args.i)
vertices=np.zeros((len(dat.grid.block),7)) #create empty matrix to save vertices to.


for blk in dat.grid.blocklist:    #go through every element
    for conn in dat.grid.connectionlist: #go through every connection
        blockname0=int(str(conn.block[0]))    #need to turn the names of cells to floats so can see if they are in x,y or z directions.
        blockname1=int(str(conn.block[1]))

        if conn.block[0]==blk:           #if the first element in the connection is the same as the block, do calculation
            if blockname0==blockname1-1:            #x direction elements are +1
               vertices[blockname0-1,0]=blk.name #first is element name
               vertices[blockname0-1,1]=blk.centre[0]-conn.distance[0]   #then x min and max
               vertices[blockname0-1,2]=blk.centre[0]+conn.distance[0]
            elif blockname0==blockname1-args.x:          #y direction (elements are within same layer but m elements apart)
               vertices[blockname0-1,3]=blk.centre[1]-conn.distance[0]
               vertices[blockname0-1,4]=blk.centre[1]+conn.distance[0]
            elif blockname0==blockname1-(args.x*args.y):          #z direction (elements are next layer)
               vertices[blockname0-1,5]=blk.centre[2]-conn.distance[0]
               vertices[blockname0-1,6]=blk.centre[2]+conn.distance[0]

        elif conn.block[1]==blk:    # if at the end of the row there won't be a connection, so need to use the second element instead
            if vertices[blockname1-1,0]==0: #if it doesn't have a blockname, it didn't get caught in the previous x loop
               vertices[blockname1-1,0]=blk.name #first is element name
               vertices[blockname1-1,1]=blk.centre[0]-conn.distance[1]   #then x min and max
               vertices[blockname1-1,2]=blk.centre[0]+conn.distance[1]
            if blockname0==blockname1-args.x and vertices[blockname1-1,3]==vertices[blockname1-1,4]:  #y direction (elements are within same layer but m elements apart). If the min and max are equal didn't get found last time
               vertices[blockname1-1,3]=blk.centre[1]-conn.distance[1]
               vertices[blockname1-1,4]=blk.centre[1]+conn.distance[1]
            if blockname0==blockname1-(args.x*args.y) and vertices[blockname1-1,5]==vertices[blockname1-1,6]:          #z direction (elements are next layer)
               vertices[blockname1-1,5]=blk.centre[2]-conn.distance[1]
               vertices[blockname1-1,6]=blk.centre[2]+conn.distance[1]

l=len(vertices)

# save the vertices to a file. Output format is index, x min, x max, y min, y max, z min, z max)
if args.o:
    np.savetxt(args.o,vertices[:l,:],fmt='%d,%g,%g,%g,%g,%g,%g')
else:
    np.savetxt('cellcorners.dat',vertices[:l,:],fmt='%d,%g,%g,%g,%g,%g,%g')
