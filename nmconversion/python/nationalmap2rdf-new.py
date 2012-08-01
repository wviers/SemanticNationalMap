
from com.healthmarketscience.jackcess import Table, Database   
from java.io import File, IOException
from java.lang import StringBuilder
import sys, os
from struct import unpack, unpack_from, pack_into, pack
import StringIO
import array
from java.awt import Component, GridLayout, Dimension
from javax.swing import (BoxLayout, ImageIcon, JButton, JFrame, JPanel,
        JPasswordField, JLabel, JTextArea, JTextField, JScrollPane,
        SwingConstants, WindowConstants, JFileChooser, JOptionPane,
        JProgressBar, JDialog)

import shapefile
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import URIRef, Namespace
from rdflib.term import Literal
from rdflib.term import URIRef


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

def create_point(point_list):
    wkt = 'POINT ( '
    
    for c in point_list:
        wkt += ' {0}'.format(c)

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
    sf = shapefile.Reader(shp=s)
    shape = sf.shapes()[0]

    return points_to_wkt(shape.shapeType, shape.points)


nhd = Namespace('http://cegis.usgs.gov/rdf/nhd/')
nhdf = Namespace('http://cegis.usgs.gov/rdf/nhd/Features/')
nhdg = Namespace('http://cegis.usgs.gov/rdf/nhd/Geometries/')
gnis = Namespace('http://cegis.usgs.gov/rdf/gnis/')
trans = Namespace('http://cegis.usgs.gov/rdf/trans/')
transf = Namespace('http://cegis.usgs.gov/rdf/trans/Features/')
transg = Namespace('http://cegis.usgs.gov/rdf/trans/Geometries/')
geo = Namespace('http://www.opengis.net/geosparql#')
geof = Namespace('http://www.opengis.net/def/geosparql/function/')
sf = Namespace('http://www.opengis.net/def/sf/')
gml = Namespace('http://www.opengis.net/def/gml/')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
struct = Namespace('http://cegis.usgs.gov/rdf/struct/')
gu = Namespace('http://cegis.usgs.gov/rdf/gu/')
guf = Namespace('http://cegis.usgs.gov/rdf/gu/Features/')
gug = Namespace('http://cegis.usgs.gov/rdf/gu/Geometries/')
hu = Namespace('http://cegis.usgs.gov/rdf/huc/')
huf = Namespace('http://cegis.usgs.gov/rdf/hucf/')
hug = Namespace('http://cegis.usgs.gov/rdf/hucg/')

int_type =  '^^<http://www.w3.org/2001/XMLSchema#int>'
string_type = '^^<http://www.w3.org/2001/XMLSchema#string>'
wkt_type = 'http://www.opengis.net/geosparql#wktLiteral'

layer_models = {}

layer_models['NHDPoint'] = {'ID_URI_TEMPLATE': (nhdf[''], 'Permanent_Identifier'), 
                            'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                             'TYPE': nhd['point'],
                             'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                             'FDate': (nhd['fDate'], '{0}', str),
                             'Resolution': (nhd['resolution'], '{0}', int),
							 'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                             'GNIS_Name': (rdfs['label'], '{0}', unicode),
                             }

layer_models['NHDFlowline'] = {'ID_URI_TEMPLATE': (nhdf[''], 'Permanent_Identifier'),
                                'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                                'TYPE': nhd['flowline'],
                                'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                                'FDate': (nhd['fDate'], '{0}', unicode),
                                'Resolution': (nhd['resolution'], '{0}', int),
                                'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                'GNIS_Name': (rdfs['label'], '{0}', unicode),
                                'LengthKM': (nhd['lengthKM'], '{0}', float),
                                'ReachCode': (nhd['reachCode'], nhd['reachCode/{0}']),
                                'FlowDir': (nhd['flowDir'], nhd['flowDir/{0}']),
                                'WBAreaComID': (nhd['wbAreaComID'], nhdf['{0}']),
                                'FType': (nhd['fType'], nhd['fType/{0}']),
                                'Shape_Length': (nhd['shapeLength'], '{0}'),
                                'Enabled': (nhd['enabled'], '{0}', unicode)
                                }

layer_models['NHDArea'] = {'ID_URI_TEMPLATE': (nhdf[''], 'Permanent_Identifier'),
                           'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'Permanent_Identifier'),
                           'TYPE': nhd['area'],
                           'FDate': (nhd['fDate'], '{0}', unicode),
                           'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                           'Resolution': (nhd['resolution'], '{0}', int),
                           'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                           'GNIS_Name': (rdfs['label'], '{0}', unicode),
                           'AreaSqKm': (nhd['areaSqKM'], '{0}', float),
                           'Elevation': (nhd['elevation'], '{0}', float),
                           'FType': (nhd['fType'], nhd['fType/{0}']),
                           'Shape_Length': (nhd['shapeLength'], '{0}', float),
                           'Shape_Area': (nhd['shapeArea'], '{0}', float),
                           }

layer_models['NHDWaterBody'] = {'ID_URI_TEMPLATE': (nhdf[''], 'Permanent_Identifier'),
                                'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                                'TYPE': nhd['waterbody'],
                                'FDate': (nhd['fDate'], '{0}', unicode),
                                'Resolution': (nhd['resolution'], '{0}', int),
                                'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                'GNIS_Name': (rdfs['label'], '{0}', unicode),
                                'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                                'Shape_Length': (nhd['shapeLength'], '{0}', float),
                                'Shape_Area': (nhd['shapeArea'], '{0}', float),
                                'Elevation': (nhd['elevation'], '{0}', float),
                                'FDate': (nhd['fDate'], '{0}', unicode),
                                'ReachCode': (nhd['reachCode'], nhd['reachCode/{0}']),
                                'AreaSqKm': (nhd['areaSqKM'], '{0}', float),
                                }


layer_models['Trans_RoadSegment'] = {'ID_URI_TEMPLATE': (transf[''], 'Source_FeatureID'),
                                     'GEOMETRY_URI_TEMPLATE': (transg[''], 'Source_FeatureID'),
                                     'TYPE': trans['roadSegment'],
                                     'Source_DatasetID': (trans['sourceDatasetID'], '{0}', unicode),
                                     'Source_DataDesc': (trans['sourceDataDesc'], '{0}', unicode),
                                     'Source_Originator': (trans['sourceOriginator'], '{0}', unicode),
                                     'Data_Security': (trans['dataSecurity'], '{0}', unicode),
                                     'Distribution_Policy': (trans['distributionPolicy'], '{0}', unicode),
                                     'LoadDate': (trans['loadDate'], '{0}', unicode),
                                     'Interstate': (trans['interstate'], '{0}', unicode),
                                     'US_Route': (trans['usRoute'], '{0}', unicode),
                                     'State_Route': (trans['stateRoute'], '{0}', unicode),
                                     'County_Route': (trans['countyRoute'], '{0}', unicode),
                                     'StCo_FIPSCode': (trans['stCoFIPSCode'], '{0}', unicode),
                                     'Road_Class': (trans['roadClass'], trans['roadClass/{0}']),
                                     'IsOneWay': (trans['isOneWay'], '{0}', lambda x: bool(int(x))),
                                     'OneWay_Direction': (trans['oneWayDirection'], trans['oneWayDirection/{0}']),
                                     'Low_Address_Left': (trans['lowAddressLeft'], '{0}', unicode),
                                     'High_Address_Left': (trans['highAddressLeft'], '{0}', unicode),
                                     'Low_Address_Right': (trans['lowAddressRight'], '{0}', unicode),
                                     'High_Address_Right': (trans['highAddressRight'], '{0}', unicode),
                                     'Full_Street_Name': (trans['fullStreetName'], '{0}', unicode),
                                     'Zip_Left': (trans['zipLeft'], '{0}', int),
                                     'Zip_Right': (trans['zipRight'], '{0}', int),
                                     'CFCC_Code': (trans['cffcCode'], '{0}', unicode),
                                     'Shape_Length': (trans['shapeLength'], '{0}', float),
                                     }

layer_models['Trans_AirportPoint'] = {'ID_URI_TEMPLATE': (transf[''], 'Source_FeatureID'),
                                     'GEOMETRY_URI_TEMPLATE': (transg[''], 'Source_FeatureID'),
                                     'TYPE': trans['airportPoint'],
                                     'Source_DatasetID': (trans['sourceDatasetID'], '{0}', unicode),
                                     'Source_DataDesc': (trans['sourceDataDesc'], '{0}', unicode),
                                     'Source_Originator': (trans['sourceOriginator'], '{0}', unicode),
                                     'Data_Security': (trans['dataSecurity'], '{0}', unicode),
                                     'Distribution_Policy': (trans['distributionPolicy'], '{0}', unicode),
                                     'LoadDate': (trans['loadDate'], '{0}', unicode),
                                     'FType': (trans['fType'], trans['fType/{0}']),
                                     'FCode': (trans['fCode'], trans['fCode/{0}']),
                                     'Airport_Class': (trans['airportClass'], '{0}', unicode),
                                     'FAA_Airport_Code': (trans['faaAirportCode'], '{0}', unicode),
                                     'Name': (rdfs['label'], '{0}', unicode),
                                     'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                     }

layer_models['Trans_RailFeature'] = {'ID_URI_TEMPLATE': (transf[''], 'Source_FeatureID'),
                                     'GEOMETRY_URI_TEMPLATE': (transg[''], 'Source_FeatureID'),
                                     'TYPE': trans['railFeature'],
                                     'Source_DatasetID': (trans['sourceDatasetID'], '{0}', unicode),
                                     'Source_DataDesc': (trans['sourceDataDesc'], '{0}', unicode),
                                     'Source_Originator': (trans['sourceOriginator'], '{0}', unicode),
                                     'Data_Security': (trans['dataSecurity'], '{0}', unicode),
                                     'Distribution_Policy': (trans['distributionPolicy'], '{0}', unicode),
                                     'LoadDate': (trans['loadDate'], '{0}', unicode),
                                     'FCode': (trans['fCode'], trans['fCode/{0}']),
                                     'Name': (rdfs['label'], '{0}', unicode),
                                     'Rail_Usage': (trans['railUsage'], '{0}', unicode),
                                     'Rail_Class': (trans['railClass'], '{0}', unicode),
                                     'Owner': (trans['owner'], '{0}', unicode),
                                     'LengthKM': (trans['lengthKM'], '{0}', float),
                                     'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                     'Shape_Length': (gnis['shapeLength'], '{0}', float),
                                     }

layer_models['Trans_AirportRunway'] = {'ID_URI_TEMPLATE': (transf[''], 'Source_FeatureID'),
                                       'GEOMETRY_URI_TEMPLATE': (transg[''], 'Source_FeatureID'),
                                       'TYPE': trans['airportRunway'],
                                       'Source_DatasetID': (trans['sourceDatasetID'], '{0}', unicode),
                                       'Source_DataDesc': (trans['sourceDataDesc'], '{0}', unicode),
                                       'Source_Originator': (trans['sourceOriginator'], '{0}', unicode),
                                       'Data_Security': (trans['dataSecurity'], '{0}', unicode),
                                       'Distribution_Policy': (trans['distributionPolicy'], '{0}', unicode),
                                       'LoadDate': (trans['loadDate'], '{0}', unicode),
                                       'FCode': (trans['fCode'], trans['fCode/{0}']),
                                       'Name': (rdfs['label'], '{0}', unicode),
                                       'FAA_Airport_Code': (trans['faaAirportCode'], '{0}', unicode),
                                       'Surface_Material': (trans['surfaceMaterial'], '{0}', unicode),
                                       'Runway_Length': (trans['runwayLength'], '{0}', float),
                                       'Runway_Width': (trans['runwayWidth'], '{0}', float),
                                       'Runway_Status': (trans['runwayStatus'], '{0}', unicode),
                                       'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                       'Shape_Length': (gnis['shapeLength'], '{0}', float),
                                       'Shape_Area': (gnis['shapeArea'], '{0}', float),
                                       }

layer_models['Struct_Point'] = {'ID_URI_TEMPLATE': (struct['Features/'], 'Source_FeatureID'),
                                'GEOMETRY_URI_TEMPLATE': (struct['Geometries/'], 'Source_FeatureID'),
                                'TYPE': struct['structPoint'],
                                'Source_DatasetID': (struct['sourceDatasetID'], '{0}', unicode),
                                'Source_DataDesc': (struct['sourceDataDesc'], '{0}', unicode),
                                'Source_Originator': (struct['sourceOriginator'], '{0}', unicode),
                                'Data_Security': (struct['dataSecurity'], '{0}', unicode),
                                'Distribution_Policy': (struct['distributionPolicy'], '{0}', unicode),
                                'LoadDate': (struct['loadDate'], '{0}', unicode),
                                'FCode': (struct['fCode'], struct['fCode/{0}']),
                                'FType': (struct['fType'], struct['fType/{0}']),
                                'Name': (rdfs['label'], '{0}', unicode),
                                'IsLandmark': (struct['isLandmark'], '{0}', unicode),
                                'PointLocationType': (struct['pointLocationType'], '{0}', unicode),
                                'AdminType': (struct['adminType'], '{0}', unicode),
                                'AddressBuildingName': (struct['addressBuildingName'], '{0}', unicode),
                                'Address': (struct['address'], '{0}', unicode),
                                'City': (struct['City'], '{0}', unicode),
                                'State': (struct['State'], '{0}', unicode),
                                'ZipCode': (struct['zipCode'], '{0}', unicode),
                                'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                'Foot_ID': (struct['footID'], '{0}', unicode),
                                'Complex_ID': (struct['complexID'], '{0}', unicode),
                                }

layer_models['GU_CountyOrEquivalent'] = {'ID_URI_TEMPLATE': (guf[''], 'Source_FeatureID'),
                                         'GEOMETRY_URI_TEMPLATE': (gug[''], 'Source_FeatureID'),
                                         'TYPE': gu['countyOrEquivalent'],
                                         'Source_DatasetID': (gu['sourceDatasetID'], '{0}', unicode),
                                         'Source_DataDesc': (gu['sourceDataDesc'], '{0}', unicode),
                                         'Source_Originator': (gu['sourceOriginator'], '{0}', unicode),
                                         'Data_Security': (gu['dataSecurity'], '{0}', unicode),
                                         'Distribution_Policy': (gu['distributionPolicy'], '{0}', unicode),
                                         'LoadDate': (gu['loadDate'], '{0}', unicode),
                                         'FCode': (gu['fCode'], gu['fCode/{0}']),
                                         'State_FIPSCode': (gu['stateFIPSCode'], '{0}', unicode),
                                         'State_Name': (gu['stateName'], '{0}', unicode),
                                         'County_FIPSCode': (gu['countyFIPSCode'], '{0}', unicode),
                                         'County_Name': (rdfs['label'], '{0}', unicode),
                                         'StCo_FIPSCode': (gu['stCoFIPSCode'], '{0}', unicode),
                                         'Population2000': (gu['population2000'], '{0}', unicode),
                                         'AreaSqKM': (gu['areaSqKM'], '{0}', float),
                                         'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                         'Shape_Length': (gnis['shapeLength'], '{0}', float),
                                         'Shape_Area': (gnis['shapeArea'], '{0}', float),
                                         }

layer_models['GU_IncorporatedPlace'] = {'ID_URI_TEMPLATE': (guf[''], 'Source_FeatureID'),
                                         'GEOMETRY_URI_TEMPLATE': (gug[''], 'Source_FeatureID'),
                                         'TYPE': gu['incorporatedPlace'],
                                         'Source_DatasetID': (gu['sourceDatasetID'], '{0}', unicode),
                                         'Source_DataDesc': (gu['sourceDataDesc'], '{0}', unicode),
                                         'Source_Originator': (gu['sourceOriginator'], '{0}', unicode),
                                         'Data_Security': (gu['dataSecurity'], '{0}', unicode),
                                         'Distribution_Policy': (gu['distributionPolicy'], '{0}', unicode),
                                         'LoadDate': (gu['loadDate'], '{0}', unicode),
                                         'FCode': (gu['fCode'], gu['fCode/{0}']),
                                         'State_Name': (gu['stateName'], '{0}', unicode),
                                         'Place_FIPSCode': (gu['placeFIPSCode'], '{0}', unicode),
                                         'Place_Name': (rdfs['label'], '{0}', unicode),
                                         'Population2000': (gu['population2000'], '{0}', unicode),
                                         'AreaSqKM': (gu['areaSqKM'], '{0}', float),
                                         'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                         'Shape_Length': (gnis['shapeLength'], '{0}', float),
                                         'Shape_Area': (gnis['shapeArea'], '{0}', float),
                                         }
layer_models['GU_StateOrTerritory'] = {'ID_URI_TEMPLATE': (guf[''], 'Source_FeatureID'),
                                       'GEOMETRY_URI_TEMPLATE': (gug[''], 'Source_FeatureID'),
                                       'TYPE': gu['stateOrTerritory'],
                                       'Source_DatasetID': (gu['sourceDatasetID'], '{0}', unicode),
                                       'Source_DataDesc': (gu['sourceDataDesc'], '{0}', unicode),
                                       'Source_Originator': (gu['sourceOriginator'], '{0}', unicode),
                                       'Data_Security': (gu['dataSecurity'], '{0}', unicode),
                                       'Distribution_Policy': (gu['distributionPolicy'], '{0}', unicode),
                                       'LoadDate': (gu['loadDate'], '{0}', unicode),
                                       'FCode': (gu['fCode'], gu['fCode/{0}']),
                                       'State_FIPSCode': (gu['stateFIPSCode'], '{0}', unicode),
                                       'State_Name': (rdfs['label'], '{0}', unicode),
                                       'Population2000': (gu['population2000'], '{0}', unicode),
                                       'AreaSqKM': (gu['areaSqKM'], '{0}', float),
                                       'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                       'Shape_Length': (gnis['shapeLength'], '{0}', float),
                                       'Shape_Area': (gnis['shapeArea'], '{0}', float),
                                       }

layer_models['GU_MinorCivilDivision'] = {'ID_URI_TEMPLATE': (guf[''], 'Source_FeatureID'),
                                         'GEOMETRY_URI_TEMPLATE': (gug[''], 'Source_FeatureID'),
                                         'TYPE': gu['minorCivilDivision'],
                                         'Source_DatasetID': (gu['sourceDatasetID'], '{0}', unicode),
                                         'Source_DataDesc': (gu['sourceDataDesc'], '{0}', unicode),
                                         'Source_Originator': (gu['sourceOriginator'], '{0}', unicode),
                                         'Data_Security': (gu['dataSecurity'], '{0}', unicode),
                                         'Distribution_Policy': (gu['distributionPolicy'], '{0}', unicode),
                                         'LoadDate': (gu['loadDate'], '{0}', unicode),
                                         'FCode': (gu['fCode'], gu['fCode/{0}']),
                                         'State_Name': (gu['stateName'], '{0}', unicode),
                                         'MinorCivilDivision_FIPSCode': (gu['minorCivilDivisonFIPSCode'], '{0}', unicode),
                                         'MinorCivilDivision_Name': (gu['minorCivilDivisonName'], '{0}', unicode),
                                         'AreaSqKM': (gu['areaSqKM'], '{0}', float),
                                         'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                         'Shape_Length': (gnis['shapeLength'], '{0}', float),
                                         'Shape_Area': (gnis['shapeArea'], '{0}', float),
                                         }
layer_models['GU_Jurisdictional'] = {'ID_URI_TEMPLATE': (guf[''], 'Permanent_Identifier'),
                                     'GEOMETRY_URI_TEMPLATE': (gug[''], 'Permanent_Identifier'),
                                     'TYPE': gu['jurisdictional'],
                                     'Source_DatasetID': (gu['sourceDatasetID'], '{0}', unicode),
                                     'Source_DataDesc': (gu['sourceDataDesc'], '{0}', unicode),
                                     'Source_Originator': (gu['sourceOriginator'], '{0}', unicode),
                                     'Data_Security': (gu['dataSecurity'], '{0}', unicode),
                                     'Distribution_Policy': (gu['distributionPolicy'], '{0}', unicode),
                                     'LoadDate': (gu['loadDate'], '{0}', unicode),
                                     'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                                     'Name': (rdfs['label'], '{0}', unicode),
                                     'AreaSqKM': (gu['areaSqKM'], '{0}', float),
                                     'FCode': (gu['fCode'], gu['fCode/{0}']),
                                     'FType': (gu['fType'], gu['fType/{0}']),
                                     'Designation': (gu['designation'], '{0}', unicode),
                                     'State_FIPSCode': (gu['stateFIPSCode'], '{0}', unicode),
                                     'State_Name': (gu['stateName'], '{0}', unicode),
                                     'AdminType': (gu['adminType'], '{0}', unicode),
                                     'OwnerOrManagingAgency': (gu['ownerOrManagingAgency'], '{0}', unicode),
                                     'Shape_Length': (gnis['shapeLength'], '{0}', float),
                                     'Shape_Area': (gnis['shapeArea'], '{0}', float),
                                     }
layer_models['WBD_HU14'] = {'ID_URI_TEMPLATE': (huf[''], 'HUC_14'),
                            'GEOMETRY_URI_TEMPLATE': (hug[''], 'HUC_14'),
                            'TYPE': hu['WBD_HU14'],
                            'Gaz_ID': (hu['gazID'], '{0}', unicode),
                            'Area_Acres': (hu['areaAcres'], '{0}', float),
                            'Area_SqKm': (hu['areaSqKm'], '{0}', float),
                            'States':    (hu['states'], '{0}', unicode),
                            'LoadDate':  (hu['loadDate'], '{0}', unicode),
                            'HU_12_Name': (hu['hu14Name'], '{0}', unicode),
                            'HU_12_Type': (hu['hu14Type'], '{0}', unicode),
                            'HU_12_Mode': (hu['hu14Mod'],  '{0}', unicode),
                            'NContrb_Acres': (hu['nContrbAcres'], '{0}', float),
                            'NContrb_SqKm':  (hu['nContrbSqKm'], '{0}', float),
                            'Shape_Length':  (hu['shapeLength'], '{0}', float),
                            'Shape_Area':   (hu['shapeArea'],    '{0}', float),
                            }

layer_models['WBD_HU12'] = {'ID_URI_TEMPLATE': (huf[''], 'HUC_12'),
                            'GEOMETRY_URI_TEMPLATE': (hug[''], 'HUC_12'),
                            'TYPE': hu['WBD_HU12'],
                            'Gaz_ID': (hu['gazID'], '{0}', unicode),
                            'Area_Acres': (hu['areaAcres'], '{0}', float),
                            'Area_SqKm': (hu['areaSqKm'], '{0}', float),
                            'States':    (hu['states'], '{0}', unicode),
                            'LoadDate':  (hu['loadDate'], '{0}', unicode),
                            'HU_12_Name': (hu['hu12Name'], '{0}', unicode),
                            'HU_12_Type': (hu['hu12Type'], '{0}', unicode),
                            'HU_12_Mode': (hu['hu12Mod'],  '{0}', unicode),
                            'NContrb_Acres': (hu['nContrbAcres'], '{0}', float),
                            'NContrb_SqKm':  (hu['nContrbSqKm'], '{0}', float),
                            'Shape_Length':  (hu['shapeLength'], '{0}', float),
                            'Shape_Area':   (hu['shapeArea'],    '{0}', float),
                            }

layer_models['WBD_HU8'] = {'ID_URI_TEMPLATE': (huf[''], 'HUC_8'),
                            'GEOMETRY_URI_TEMPLATE': (hug[''], 'HUC_8'),
                            'TYPE': hu['WBD_HU8'],
                            'Gaz_ID': (hu['gazID'], '{0}', unicode),
                            'Area_Acres': (hu['areaAcres'], '{0}', float),
                            'Area_SqKm': (hu['areaSqKm'], '{0}', float),
                            'States':    (hu['states'], '{0}', unicode),
                            'LoadDate':  (hu['loadDate'], '{0}', unicode),
                            'HU_8_Name': (hu['hu8Name'], '{0}', unicode),
                            'HU_8_Type': (hu['hu8Type'], '{0}', unicode),
                            'HU_8_Mode': (hu['hu8Mod'],  '{0}', unicode),
                            'Shape_Length':  (hu['shapeLength'], '{0}', float),
                            'Shape_Area':   (hu['shapeArea'],    '{0}', float),
                            }

layer_models['WBD_HU10'] = {'ID_URI_TEMPLATE': (huf[''], 'HUC_10'),
                            'GEOMETRY_URI_TEMPLATE': (hug[''], 'HUC_10'),
                            'TYPE': hu['WBD_HU10'],
                            'Gaz_ID': (hu['gazID'], '{0}', unicode),
                            'Area_Acres': (hu['areaAcres'], '{0}', float),
                            'Area_SqKm': (hu['areaSqKm'], '{0}', float),
                            'States':    (hu['states'], '{0}', unicode),
                            'LoadDate':  (hu['loadDate'], '{0}', unicode),
                            'HU_10_Name': (hu['hu10Name'], '{0}', unicode),
                            'HU_10_Type': (hu['hu10Type'], '{0}', unicode),
                            'HU_10_Mode': (hu['hu10Mod'],  '{0}', unicode),
                            'Shape_Length':  (hu['shapeLength'], '{0}', float),
                            'Shape_Area':   (hu['shapeArea'],    '{0}', float),
                            }


layer_models['WBD_HU6'] = {'ID_URI_TEMPLATE': (huf[''], 'HUC_6'),
                            'GEOMETRY_URI_TEMPLATE': (hug[''], 'HUC_6'),
                            'TYPE': hu['WBD_HU6'],
                            'Gaz_ID': (hu['gazID'], '{0}', unicode),
                            'Area_Acres': (hu['areaAcres'], '{0}', float),
                            'Area_SqKm': (hu['areaSqKm'], '{0}', float),
                            'States':    (hu['states'], '{0}', unicode),
                            'LoadDate':  (hu['loadDate'], '{0}', unicode),
                            'HU_6_Name': (hu['hu6Name'], '{0}', unicode),
                            'HU_6_Type': (hu['hu6Type'], '{0}', unicode),
                            'HU_6_Mode': (hu['hu6Mod'],  '{0}', unicode),
                            'Shape_Length':  (hu['shapeLength'], '{0}', float),
                            'Shape_Area':   (hu['shapeArea'],    '{0}', float),
                            }

layer_models['WBD_HU4'] = {'ID_URI_TEMPLATE': (huf[''], 'HUC_4'),
                            'GEOMETRY_URI_TEMPLATE': (hug[''], 'HUC_4'),
                            'TYPE': hu['WBD_HU4'],
                            'Gaz_ID': (hu['gazID'], '{0}', unicode), 
                            'Area_Acres': (hu['areaAcres'], '{0}', float),
                            'Area_SqKm': (hu['areaSqKm'], '{0}', float),
                            'States':    (hu['states'], '{0}', unicode),
                            'LoadDate':  (hu['loadDate'], '{0}', unicode),
                            'HU_4_Name': (hu['hu4Name'], '{0}', unicode),
                            'HU_4_Type': (hu['hu4Type'], '{0}', unicode),
                            'HU_4_Mode': (hu['hu4Mod'],  '{0}', unicode),
                            'Shape_Length':  (hu['shapeLength'], '{0}', float),
                            'Shape_Area':   (hu['shapeArea'],    '{0}', float),
                            }

def InsertFeature(feature, model, store):
    feature_uri = model['ID_URI_TEMPLATE'][0]
    subject_field = model['ID_URI_TEMPLATE'][1]
    feature_uri = feature_uri + unicode(feature[subject_field])
    geometry_uri = model['GEOMETRY_URI_TEMPLATE'][0]
    geometry_field = model['GEOMETRY_URI_TEMPLATE'][1]
    geometry_uri = geometry_uri + unicode(feature[geometry_field])
    
    for k,v in model.iteritems():
        f_val = feature[k]
        if f_val == None or f_val == ' ':
            continue
        elif len(v) == 3:
            obj = Literal(v[2](v[1].format(f_val)))
        else:
            obj = URIRef(v[1].format(str(int(f_val))))

        store.add((URIRef(feature_uri), URIRef(v[0].format(f_val)), obj))
            
    wkt = Literal(binary_shape_to_wkt(feature['Shape']))
    store.add((URIRef(feature_uri), geo['hasGeometry'], URIRef(geometry_uri)))
    store.add((URIRef(feature_uri), rdf['type'], model['TYPE']))
    # Create Geometry 
    store.add((URIRef(geometry_uri), geo['asWKT'], wkt))
    store.add((URIRef(geometry_uri), rdf['type'], geo['Geometry']))

    return True

def InsertLayer(layer, store):
    if layer.getName() in layer_models:
        print('  Model found')
        model = layer_models[layer.getName()]
        for feature in layer:
            InsertFeature(feature, model, store)


def load_namespaces(store):
    # bind namespaces
    store.bind('nhd', nhd)
    store.bind('nhdf', nhdf)
    store.bind('nhdg', nhdg)
    store.bind('gnis', gnis)
    store.bind('geo', geo)
    store.bind('trans', trans)
    store.bind('transf', transf)
    store.bind('transg', transg)
    store.bind('rdfs', rdfs)
    store.bind('gu', gu)
    store.bind('struct', struct)
    store.bind('hu', hu)
    
def nm_mdb_to_n3(inputFile, outputFile):
    f = File(inputFile)
    #    o = open(outputFile, 'w')
    print("Got this output filename: " + outputFile)
    store = ConjunctiveGraph(identifier='temp')
    
    if f.exists() == False:
        print("Error opening file.")
        return False
    try:
        d = Database.open(f)
    except IOException:
        print("Error opening database.")
        return False


    for table in d:
        store = ConjunctiveGraph(identifier='temp')
        load_namespaces(store)
        print('Processing table: ' + table.getName())
        InsertLayer(table, store)
        if len(store) > 0:
            store.serialize(destination=outputFile+table.getName(), format='n3')
        store = None
    print('All tables processed')
    

    return True

class ConversionGUI(object):
    def __init__(self):
        self.frame = JFrame("National Map 2 RDF",
                            defaultCloseOperation = WindowConstants.EXIT_ON_CLOSE)

        self.convertPanel = JPanel(GridLayout(0,3))
        self.frame.setPreferredSize(Dimension(500, 200))
        self.frame.setMaximumSize(Dimension(800, 600))

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
        self.inputFile = fc.getSelectedFile().getCanonicalPath()
        self.inputField.setText(self.inputFile)
        suggestedOutputFile = self.inputFile
        suggestedOutputFile = os.path.splitext(suggestedOutputFile)[0]
        
        self.outputField.setText(suggestedOutputFile + '.n3')
        self.outputFile = self.outputField.getText()

    def convert(self, event):
        ret_val = False
        progressBar = JProgressBar()
        progressBar.setIndeterminate(True)
        workLabel = JLabel('Working...')
        center_panel = JPanel()
        center_panel.add(workLabel)
        center_panel.add(progressBar)
        
        workingDialog = JDialog(None, "Working...")
        workingDialog.getContentPane().add(center_panel)
        workingDialog.pack()
        
        workingDialog.setVisible(True)
        ret_val = nm_mdb_to_n3(self.inputFile, self.outputFile)
        workingDialog.setVisible(False)

        
        
        if ret_val:
            JOptionPane.showMessageDialog(self.convertPanel, "Conversion Successful!.");
        else:
            JOptionPane.showMessageDialog(self.convertPanel, "Conversion Failed!.");
                
        

        
    def show(self):
        self.frame.visible = True
        
if __name__ == '__main__':
    ConversionGUI()
