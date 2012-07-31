
from com.healthmarketscience.jackcess import Table, Database   
from java.io import File, IOException
from java.lang import StringBuilder
import sys, os
from struct import unpack, unpack_from, pack_into, pack
import StringIO
import array
from java.awt import Component, GridLayout
from javax.swing import (BoxLayout, ImageIcon, JButton, JFrame, JPanel,
        JPasswordField, JLabel, JTextArea, JTextField, JScrollPane,
        SwingConstants, WindowConstants, JFileChooser, JOptionPane)

import java.lang.ClassLoader 
import java.io.InputStreamReader
import java.io.BufferedReader

loader = java.lang.ClassLoader.getSystemClassLoader()
stream = loader.getResourceAsStream("python/shapefile.py")
print(stream)
reader = java.io.BufferedReader(java.io.InputStreamReader(stream))

script = ""                          
line = reader.readLine()
while (line != None) : 
    script += line + "\n"
    line = reader.readLine()

exec(script)

# Constants for shape types
NULL = 0
POINT = 1
POLYLINE = 3
POLYGON = 5
MULTIPOINT = 8
POINTZ = 11
POLYLINEZ = 13
POLYGONZ = 15
MULTIPOINTZ = 18
POINTM = 21
POLYLINEM = 23
POLYGONM = 25
MULTIPOINTM = 28
MULTIPATCH = 31


#f = File(sys.argv[1])
#d = Database.open(f) 

#full_shape = array.array('b', [0x0])*108

    
#tab = d.getTable("NHDFlowline")
#shape_array = tab.getNextRow()["Shape"]
#full_shape.extend(shape_array)
#shape_string = full_shape.tostring()
#shape_length = len(full_shape) / 2
#length = pack(">i", shape_length)

# Create full string
#final_string = shape_string[:24] + length + shape_string[28:]
#s = StringIO.StringIO(final_string)

#sf = shapefile.Reader(shp=s)
#shapes = sf.shapes()
#print(shapes[0].points)

def create_point(point_list):
    wkt = 'POINT ( '
    
    for c in point_list:
        wkt += c

    wkt += ' )'

    return wkt
        

def finish_point_list(point_list, buffer):
   buffer.append('( ')
    
   for p in point_list[:-1]:
       for c in p:
           buffer.append(' {0}'.format(c))
       buffer.append(', ')
   for c in point_list[-1]:
       buffer.append(' {0}'.format(c))
   buffer.append(' )')
   return buffer

def create_linestring(point_list):
    wkt = StringBuilder('LINESTRING')

    finish_point_list(point_list, wkt)
    return wkt.toString()

def create_multipoints(points):
    wkt = StringBuilder('MULTIPOINT')

    finish_point_list(point_list, wkt)
    
    return wkt.toString()

def create_polygon(point_list):
    wkt = StringBuilder('POLYGON (')
    poly_list = point_list
    poly_list.append(point_list[0])
    finish_point_list(poly_list, wkt)

    wkt.append(')')

    return wkt.toString()
    
def points_to_wkt(shapeType, points):
    if shapeType == NULL:
        return ""
    if shapeType in (1,9,11,21): # Point
        return create_point(points[0])
    elif shapeType in (3,23,13,10): # Arc, Polyline
        return create_linestring(points)
    elif shapeType in (8,28,18,20): # Multipoint
        return create_multipoint(points)
    elif shapeType in (5,25,15,19): # Polygon
        return create_polygon(points)
    
def binary_shape_to_wkt(binaryShape):
    full_shape = array.array('b', [0x0])*108
    full_shape.extend(binaryShape)
    shape_string = full_shape.tostring()
    shape_length = len(full_shape) / 2
    length = pack(">i", shape_length)
    final_string = shape_string[:24] + length + shape_string[28:]
    s = StringIO.StringIO(final_string)
    sf = Reader(shp=s)
    shape = sf.shapes()[0]

    return points_to_wkt(shape.shapeType, shape.points)
    
def nm_mdb_to_n3(inputFile, outputFile):
    f = File(inputFile)
    o = open(outputFile, 'w')
    
    if f.exists() == False:
        print("Error opening file.")
        return False
    try:
        d = Database.open(f)
    except IOException:
        print("Error opening database.")
        return False
    tables = d.getTableNames()

    for table in d:
        print(table.getName())
        for r in table:
            shape = r['Shape']
            if shape:
                wkt = binary_shape_to_wkt(shape)
                o.write(wkt)

    return true

class ConversionGUI(object):
    def __init__(self):
        self.frame = JFrame("National Map 2 RDF",
                            defaultCloseOperation = WindowConstants.EXIT_ON_CLOSE)

        self.convertPanel = JPanel(GridLayout(0,3))

        self.frame.add(self.convertPanel)

        self.inputField = JLabel('')
        self.convertPanel.add(JLabel('Input MDB filename:  ', SwingConstants.RIGHT))
        self.convertPanel.add(self.inputField)
                              
        self.fileButton = JButton('Select input file', actionPerformed=self.selectFile)
        self.convertPanel.add(self.fileButton)

        self.outputField = JLabel('')
        self.convertPanel.add(JLabel('Output N3 filename:  ', SwingConstants.RIGHT))
        self.convertPanel.add(self.outputField)
        self.convertButton = JButton('Convert!', actionPerformed = self.convert)
        self.convertPanel.add(self.convertButton)
        
        
        self.inputFile = None
        self.outputFile = None
        self.frame.pack()
        self.show()
        
    def selectFile(self, event):
        fc = JFileChooser()
        fc.showOpenDialog(self.frame)
        self.inputFile = fc.getSelectedFile().getPath()
        self.inputField.setText(self.inputFile)
        suggestedOutputFile = self.inputFile
        suggestedOutputFile = os.path.splitext(suggestedOutputFile)[0]
        
        self.outputField.setText(suggestedOutputFile + '.n3')
        self.outputFile = self.outputField.getText()

    def convert(self, event):
        if nm_mdb_to_n3(self.inputFile, self.outputFile): 
            JOptionPane.showMessageDialog(self.convertPanel, "Conversion Successful!.");
        else:
            JOptionPane.showMessageDialog(self.convertPanel, "Conversion Failed!.");
                
        

        
    def show(self):
        self.frame.visible = True
        
if __name__ == '__main__':
    ConversionGUI()
