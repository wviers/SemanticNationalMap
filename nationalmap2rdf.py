#!/usr/bin/python

import osgeo 
from osgeo import ogr
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import URIRef, Namespace
from rdflib.term import Literal
from rdflib.term import URIRef
import sys

nhd = Namespace('http://cegis.usgs.gov/rdf/nhd/')
nhdf = Namespace('http://cegis.usgs.gov/rdf/nhd/Features/')
nhdg = Namespace('http://cegis.usgs.gov/rdf/nhd/Geometries/')
gnis = Namespace('http://cegis.usgs.gov/rdf/gnis/')
trans = Namespace('http://cegis.usgs.gov/rdf/trans/')
transf = Namespace('http://cegis.usgs.gov/rdf/trans/Features/')
transg = Namespace('http://cegis.usgs.gov/rdf/trans/Geometries/')
geo = Namespace('http://www.opengis.net/def/geosparql/')
geof = Namespace('http://www.opengis.net/def/geosparql/function/')
sf = Namespace('http://www.opengis.net/def/sf/')
gml = Namespace('http://www.opengis.net/def/gml/')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
struct = Namespace('http://cegis.usgs.gov/rdf/struct/')
gu = Namespace('http://cegis.usgs.gov/rdf/gu/')
guf = Namespace('http://cegis.usgs.gov/rdf/gu/Features/')
gug = Namespace('http://cegis.usgs.gov/rdf/gu/Geometries/')

int_type =  '^^<http://www.w3.org/2001/XMLSchema#int>'
string_type = '^^<http://www.w3.org/2001/XMLSchema#string>'
wkt_type = 'http://www.opengis.net/def/sf/wktLiteral'

layer_models = {}

layer_models['NHDPoint'] = {'ID_URI_TEMPLATE': (nhdf[''], 'ComID'), 
                            'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                             'TYPE': nhd['point'],
                             'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                             'FDate': (nhd['fDate'], '{0}', str),
                             'Resolution': (nhd['resolution'], '{0}', int),
							 'GNIS_ID': (gnis['id'], gnis['Features/{0}']),
                             'GNIS_Name': (rdfs['label'], '{0}', unicode),
                             }

layer_models['NHDFlowline'] = {'ID_URI_TEMPLATE': (nhdf[''], 'ComID'),
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

layer_models['NHDArea'] = {'ID_URI_TEMPLATE': (nhdf[''], 'ComID'),
                           'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
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

layer_models['NHDWaterBody'] = {'ID_URI_TEMPLATE': (nhdf[''], 'ComID'),
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

def InsertFeature(feature, model, store):
    feature_uri = model['ID_URI_TEMPLATE'][0]
    subject_field = model['ID_URI_TEMPLATE'][1]
    i = feature.GetFieldIndex(subject_field)
    feature_uri = feature_uri + unicode(feature.GetField(i))
    geometry_uri = model['GEOMETRY_URI_TEMPLATE'][0]
    geometry_field = model['GEOMETRY_URI_TEMPLATE'][1]
    i = feature.GetFieldIndex(subject_field)
    geometry_uri = geometry_uri + unicode(feature.GetField(i))
    
    for k,v in model.iteritems():
        i = feature.GetFieldIndex(k)
        if i != -1:
            f_val = feature.GetField(i)
            if f_val == None or f_val == ' ':
                continue
            elif len(v) == 3:
                obj = Literal(v[2](v[1].format(f_val)))
            else:
                obj = URIRef(v[1].format(str(int(f_val))))

            store.add((URIRef(feature_uri), URIRef(v[0].format(f_val)), obj))
            
    wkt = Literal(feature.GetGeometryRef().ExportToWkt(), datatype=wkt_type)
    #    gml = Literal(feature.GetGeometryRef().ExportToGML(), datatype=u'http://www.opengis.net/def/dataType/OGC-GML/3.2/GMLLiteral')
    store.add((URIRef(feature_uri), geo['hasGeometry'], URIRef(geometry_uri)))
    store.add((URIRef(feature_uri), rdf['type'], model['TYPE']))
    # Create Geometry 
    store.add((URIRef(geometry_uri), geo['asWKT'], wkt))
    store.add((URIRef(geometry_uri), rdf['type'], geo['Geometry']))

    return True
				
				
def InsertLayer(layer, store):
    if layer.GetName() in layer_models:
        model = layer_models[layer.GetName()]
        feature = layer.GetNextFeature()
        while feature:
            InsertFeature(feature, model, store)
            feature = layer.GetNextFeature()
				
				
def ConvertMdbToN3(mdb_filename, n3_filename):
    ds = ogr.Open(mdb_filename, False)
    store = ConjunctiveGraph(identifier='temp')

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

    
    layers = [ds.GetLayer(i) for i in range(0, ds.GetLayerCount())]
    # Loop through layers of the dataset and check if we have a model
    print('Converting data...\n')
    for i in layers:
        InsertLayer(i, store)

    print('Conversion complete, writing output file...')
    # Write output file

    print(len(store))
    store.serialize(destination=n3_filename, format='n3')

    return True
			
    
if __name__ == '__main__':
    if len(sys.argv) >= 3:
        ConvertMdbToN3(sys.argv[1], sys.argv[2])
