
from com.healthmarketscience.jackcess import Table, Database   
from java.io import File, IOException
from java.lang import StringBuilder
import sys, os
from struct import unpack, unpack_from, pack_into, pack
import StringIO
import array
from   java.awt.event import ActionListener;
from java.awt import Component, GridLayout, Dimension, BorderLayout
from javax.swing import (BoxLayout, Box, ImageIcon, JButton, JFrame, JPanel,
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
hu = Namespace('http://cegis.usgs.gov/rdf/nhd/huc/')
huf = Namespace('http://cegis.usgs.gov/rdf/nhd/hucf/')
hug = Namespace('http://cegis.usgs.gov/rdf/nhd/hucg/')
nhd_ontology = Namespace('http://cegis.usgs.gov/NHDOntology/')

int_type =  '^^<http://www.w3.org/2001/XMLSchema#int>'
string_type = '^^<http://www.w3.org/2001/XMLSchema#string>'
wkt_type = URIRef('http://www.opengis.net/sf#wktLiteral')

layer_models = {}

layer_models['NHDPoint'] = {'ID_URI_TEMPLATE': (nhdf[''], 'Permanent_Identifier'), 
                            'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'Permanent_Identifier'),
                             'TYPE': nhd['point'],
                             'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                             'FDate': (nhd['fDate'], '{0}', str),
                             'Resolution': (nhd['resolution'], '{0}', int),
							 'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                             'GNIS_Name': (rdfs['label'], '{0}', unicode),
                             }

layer_models['NHDFlowline'] = {'ID_URI_TEMPLATE': (nhdf[''], 'Permanent_Identifier'),
                                'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'Permanent_Identifier'),
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
                                'Shape_Length': (nhd['shapeLength'], '{0}', float),
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
                            'HU_12_Name': (rdf['label'], '{0}', unicode),
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
                            'HU_12_Name': (rdfs['label'], '{0}', unicode),
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
                            'HU_8_Name': (rdfs['label'], '{0}', unicode),
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
                            'HU_10_Name': (rdfs['label'], '{0}', unicode),
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
                            'HU_6_Name': (rdfs['label'], '{0}', unicode),
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
                            'HU_4_Name': (rdfs['label'], '{0}', unicode),
                            'HU_4_Type': (hu['hu4Type'], '{0}', unicode),
                            'HU_4_Mode': (hu['hu4Mod'],  '{0}', unicode),
                            'Shape_Length':  (hu['shapeLength'], '{0}', float),
                            'Shape_Area':   (hu['shapeArea'],    '{0}', float),
                            }

ftypes = {'558': nhd_ontology['ArtificialPath'],
          '336': nhd_ontology['CanalOrDitch'],
          '566': nhd_ontology['Coastline'],
          '334': nhd_ontology['Connector'],
          '428': nhd_ontology['Pipeline'],
          '460': nhd_ontology['StreamOrRiver'],
          '420': nhd_ontology['UndergroundConduit'],
          '493': nhd_ontology['Estuary'],
          '378': nhd_ontology['IceMass'],
          '390': nhd_ontology['LakeOrPond'],
          '361': nhd_ontology['Playa'],
          '436': nhd_ontology['Reservoir'],
          '466': nhd_ontology['SwampOrMarsh'],
          '318': nhd_ontology['Bridge'],
          '343': nhd_ontology['DamOrWeir'],
          '362': nhd_ontology['Flume'],
          '369': nhd_ontology['Gate'],
          '568': nhd_ontology['Levee'],
          '398': nhd_ontology['LockChamber'],
          '411': nhd_ontology['NonearthenShore'],
          '431': nhd_ontology['Rapids'],
          '434': nhd_ontology['Reef'],
          '450': nhd_ontology['SinkOrRise'],
          '503': nhd_ontology['SoundingDatumLine'],
          '533': nhd_ontology['SpecialUseZoneLimit'],
          '478': nhd_ontology['Tunnel'],
          '483': nhd_ontology['Wall'],
          '487': nhd_ontology['Waterfall'],
          '343': nhd_ontology['DamOrWier'],
          '367': nhd_ontology['GagingStation'],
          '441': nhd_ontology['Rock'],
          '458': nhd_ontology['SpringOrSeep'],
          '485': nhd_ontology['WaterIntakeOrOutflow'],
          '487': nhd_ontology['Waterfall'],
          '488': nhd_ontology['Well'],
          '537': nhd_ontology['AreaOfComplexChannels'],
          '307': nhd_ontology['AreaToBeSubmerged'],
          '312': nhd_ontology['BayOrInlet'],
          '364': nhd_ontology['Foreshore'],
          '373': nhd_ontology['HazardZone'],
          '403': nhd_ontology['InundationArea'],
          '445': nhd_ontology['SeaOrOcean'],
          '454': nhd_ontology['SpecialUseZone'],
          '455': nhd_ontology['Spillway'],
          '461': nhd_ontology['SubmergedStream'],
          '484': nhd_ontology['Wash']}

fcodes = {'33601': ((nhd_ontology['CanalOrDitchType'],
                     nhd_ontology['Aqueduct']),),
          '33603': ((nhd_ontology['CanalOrDitchType'],
                     nhd_ontology['Stormwater']),),
          '42801': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Aqueduct']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['AtOrNear'])),
          '42802': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Aqueduct']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Elevated'])),
          '42803': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Aqueduct']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Underground'])),
          '42804': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Aqueduct']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Underwater'])),
          '42805': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['GeneralCase']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['AtOrNearSurface'])),
          '42806': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['GeneralCase']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Elevated'])),
          '42807': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['GeneralCase']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Underground'])), 
          '42808': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['GeneralCase']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Underwater'])), 
          '42809': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Penstock']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['AtOrNear'])), 
          '42810': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Penstock']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Elevated'])), 
          '42811': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Penstock']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Underground'])), 
          '42812': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Penstock']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Underwater'])), 
          '42813': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Siphon']),
                    (nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Unspecified'])), 
          '42814': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['GeneralCase'])),
          '42815': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Penstock'])),
          '42816': ((nhd_ontology['Product'],
                     nhd_ontology['Water']),
                    (nhd_ontology['PipelineType'],
                     nhd_ontology['Aqueduct'])),
          '46003': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Intermittent']),),
          '46006': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial']),),
          '46007': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Ephemeral']),),
          '42001': ((nhd_ontology['PositionalAccuracy'],
                     nhd_ontology['Definite']),),
          '42002': ((nhd_ontology['PositionalAccuracy'],
                     nhd_ontology['Indefinite']),),
          '42003': ((nhd_ontology['PositionalAccuracy'],
                     nhd_ontology['Approximate']),),
          '39001': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Intermittent']),),
          '39004': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial']),),
          '39005': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Intermittent']),
                     (nhd_ontology['Stage'],
                      nhd_ontology['HighWaterElevation'])),
          '39006': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Intermittent']),
                     (nhd_ontology['Stage'],
                      nhd_ontology['DateOfPhotography'])),
          '39009': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial']),
                     (nhd_ontology['Stage'],
                      nhd_ontology['AverageWaterElevation'])),
          '39010': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial']),
                     (nhd_ontology['Stage'],
                      nhd_ontology['HighWaterElevation'])),
          '39011': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial']),
                     (nhd_ontology['Stage'],
                      nhd_ontology['DateOfPhotography'])),
          '39012': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial']),
                     (nhd_ontology['Stage'],
                      nhd_ontology['AverageWaterElevation'])),
          '43601': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Aquaculture']),),
          '43603': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['DecorativePool']),),
          '43604': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['DisposalTailingsPond']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Earthen'])),
          '43605': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['DisposalTailingsPond']),),
          '43606': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['DisposalUnspecified']),),
          '43607': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Evaporator']),),
          '43608': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['SwimmingPool']),),
          '43609': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['TreatmentCoolingPond']),),
          '43610': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['TreatmentFiltrationPond']),),
          '43611': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['TreatmentSettlingPond']),),
          '43612': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['TreatmentSewageTreatmentPond']),),
          '43613': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['WaterStorage']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Nonearthen'])),
          '43614': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['WaterStorage']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Nonearthen']),
                    (nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Intermittent'])),
          '43615': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['WaterStorage']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Nonearthen']),
                    (nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial'])),
          '43617': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['WaterStorage']),),
          '43618': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Unspecified']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Earthen'])),
          '43619': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Unspecified']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Nonearthen'])),
          '43621': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['WaterStorage']),
                    (nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial'])),
          '43623': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Evaporator']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Earthen'])),
          '43624': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Treatment']),),
          '43625': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Disposal']),),
          '43625': ((nhd_ontology['ReservoirType'],
                     nhd_ontology['Disposal']),
                    (nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['nonearthen'])),
          '46601': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Intermittant']),),
          '46602': ((nhd_ontology['HydrographicCategory'],
                     nhd_ontology['Perennial']),),
          '34305': ((nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Earthen']),),
          '34306': ((nhd_ontology['ConstructionMaterial'],
                     nhd_ontology['Nonearthen']),),
          '50301': ((nhd_ontology['PositionalAccuracy'],
                     nhd_ontology['Approximate']),),
          '50302': ((nhd_ontology['PositionalAccuracy'],
                     nhd_ontology['Definite']),),
          '53301': ((nhd_ontology['PositionalAccuracy'],
                     nhd_ontology['Definite']),),
          '53302': ((nhd_ontology['PositionalAccuracy'],
                     nhd_ontology['Indefinite']),),
          '44101': ((nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Abovewater']),),
          '44102': ((nhd_ontology['RelationshipToSurface'],
                     nhd_ontology['Underwater']),),
          '40307': ((nhd_ontology['InundationControlStatus'],
                     nhd_ontology['NotControlled']),),
          '40308': ((nhd_ontology['InundationControlStatus'],
                     nhd_ontology['Controlled']),),
          '40307': ((nhd_ontology['InundationControlStatus'],
                     nhd_ontology['NotControlled']),
                    (nhd_ontology['Stage'],
                     nhd_ontology['FloodElevation'])),
          '45401': ((nhd_ontology['SpecialUseZoneType'],
                     nhd_ontology['DumpSite']),
                    (nhd_ontology['OperationalStatus'],
                     nhd_ontology['Operational'])),
          '45402': ((nhd_ontology['SpecialUseZoneType'],
                     nhd_ontology['DumpSite']),
                    (nhd_ontology['OperationalStatus'],
                     nhd_ontology['Abandoned'])),
          '45403': ((nhd_ontology['SpecialUseZoneType'],
                     nhd_ontology['SpoilArea']),
                    (nhd_ontology['OperationalStatus'],
                     nhd_ontology['Operational'])),
          '45402': ((nhd_ontology['SpecialUseZoneType'],
                     nhd_ontology['SpoilArea']),
                    (nhd_ontology['OperationalStatus'],
                     nhd_ontology['Abandoned'])),
}

          
def ftype_to_rdftype(ftype):
    """ ftype is a string """
    rdftype = ftypes[ftype[:3]]

    if rdftype == None:
        print("Couldn't find rdf type!")
        return ''

    else:
        return rdftype

def fcode_to_attributes(fcode):
    attributes = fcodes.get(fcode, None)

    if attributes == None:
        return ()
    else:
        return attributes
    
    
def triple_to_nt(sub, pred, obj):
    nt = StringBuilder()
    nt.append(sub.n3())
    nt.append(' ')
    nt.append(pred.n3())
    nt.append(' ')
    nt.append(obj.n3())
    nt.append(' . \n')

    return nt.toString()

def clean_uri(uri):
    allowed = r""""ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="""
    return uri
    
def InsertFeature(feature, model, output_file):
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

        output_file.write(triple_to_nt(URIRef(feature_uri), URIRef(v[0].format(f_val)), obj))
            
    wkt = Literal(binary_shape_to_wkt(feature['Shape']), datatype=wkt_type)
    output_file.write(triple_to_nt(URIRef(feature_uri), geo['hasGeometry'], URIRef(geometry_uri)))
    output_file.write(triple_to_nt(URIRef(feature_uri), rdf['type'], model['TYPE']))
    # Now determine rdf type from NHD Ontology
    if feature['FCode'] != None:
        rdftype = ftype_to_rdftype(str(feature['FCode']))
        if len(rdftype) > 0:
            output_file.write(triple_to_nt(URIRef(feature_uri), rdf['type'], rdftype))
        # Now parse attributes from last two digits of FCode
        attributes = fcode_to_attributes(str(feature['FCode']))
        for attr in attributes:
            output_file.write(triple_to_nt(URIRef(feature_uri), attr[0], attr[1]))
            

    # Create Geometry 
    output_file.write(triple_to_nt(URIRef(geometry_uri), geo['asWKT'], wkt))
    output_file.write(triple_to_nt(URIRef(geometry_uri), rdf['type'], geo['Geometry']))

    return True

def InsertLayer(layer, output_file):
    if layer.getName() in layer_models:
        print('  Model found')
        model = layer_models[layer.getName()]
        for feature in layer:
            InsertFeature(feature, model, output_file)


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

    for table in d:
        print('Processing table: ' + table.getName())
        InsertLayer(table, o)

    print('All tables processed')
    

    return True

class ConversionGUI(object):
    chooser = JFileChooser()
    inputFile = None
    outputFile = None
    outputField = JLabel('')
    frame = JFrame("National Map 2 RDF",
                            defaultCloseOperation = WindowConstants.EXIT_ON_CLOSE)
     

    def convert(self):
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
    
     
    class Selected(ActionListener):		
        def __init__(self, conversion_gui):
            self.gui = conversion_gui
            
        def actionPerformed(self, event):
            if event.getActionCommand() == "ApproveSelection":
                self.gui.inputFile = self.gui.chooser.getSelectedFile().getCanonicalPath()
                suggestedOutputFile = self.gui.inputFile
                suggestedOutputFile = os.path.splitext(suggestedOutputFile)[0]
        
                self.gui.outputField.setText(suggestedOutputFile)
                self.gui.outputFile = self.gui.outputField.getText()
                
                self.gui.convert()
                    
            elif event.getActionCommand() == "CancelSelection":
                sys.exit()
    
    def __init__(self):	
	    #Splash Screen Creation
        self.splash = JFrame("National Map 2 RDF", 
	                        defaultCloseOperation = WindowConstants.EXIT_ON_CLOSE)
        self.splash.setSize(Dimension(300, 300))
        self.splash.setMinimumSize(Dimension(300, 300))
        self.splash.setMaximumSize(Dimension(300, 300))

        self.background = JPanel()
        self.background.setLayout(BorderLayout())
        self.splash.add(self.background)
        
  
        self.greeting = JLabel("Welcome to the National Map RDF Converter")
        self.background.add(self.greeting, BorderLayout.CENTER)
		
        self.next = JButton('Continue', actionPerformed=self.changeVisibility)
        self.next.preferredSize = (50, 20)
        self.background.add(self.next, BorderLayout.SOUTH)
		
		
	    #Main screen with file chooser
        
        self.frame.setPreferredSize(Dimension(500, 500))
        self.frame.setMinimumSize(Dimension(500, 500))
				
        
        self.convertPanel = JPanel()
        self.convertPanel.setLayout(BoxLayout(self.convertPanel, BoxLayout.Y_AXIS))
        self.frame.add(self.convertPanel)
		
		
		#File chooser
        self.chooser.setApproveButtonText("Convert File")
        self.chooser.addActionListener(self.Selected(self))
        self.convertPanel.add(self.chooser)
        
        self.labelPanel = JPanel()
        self.labelPanel.setLayout(BoxLayout(self.labelPanel, BoxLayout.X_AXIS))
        self.convertPanel.add(self.labelPanel)
        self.labelPanel.add(JLabel('Output N3 file Location:  '))
        self.labelPanel.add(self.outputField)

        self.frame.setVisible(False)
        self.splash.setVisible(True)
		
        self.frame.pack()
        self.splash.pack()


    def changeVisibility(self, event):
        self.frame.setVisible(True)
        self.splash.setVisible(False)	


        
if __name__ == '__main__':
    ConversionGUI()
