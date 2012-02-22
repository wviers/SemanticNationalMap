#!/usr/bin/python

import osgeo 
from osgeo import ogr
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import URIRef, Namespace

nhd = Namespace('http://cegis.usgs.gov/rdf/nhd/')
nhdf = Namespace('http://cegis.usgs.gov/rdf/nhd/Features/')
nhdg = Namespace('http://cegis.usgs.gov/rdf/nhd/Geometries/')
gnis = Namespace('http://cegis.usgs.gov/rdf/gnis/')
geo = Namespace('http://opengis.net/ont/OGC-GeoSPARQL/1.0/')

int_type =  '^^<http://www.w3.org/2001/XMLSchema#int>'
string_type = '^^<http://www.w3.org/2001/XMLSchema#string>'

layer_models = {'NHDPoint': {'ID_URI_TEMPLATE': (nhdf['{0}'], 'ComID'), 
                             'GEOMETRY_URI_TEMPLATE': (nhdg['{0}'], 'ComID'),
                             'FCode': (nhd['fCode'], nhd['fCode/{0}']),
							 'FDate': (nhd['fDate'], '{0}'),
							 'Resolution': (nhd['resolution'], '{0}', int),
							 'GNIS_ID': (gnis['id'], '{0}')
                             }}

layer_models['NHDFlowline'] = {'ID_URI_TEMPLATE': (nhdf['{0}'], 'ComID'),
                                'GEOMETRY_URI_TEMPLATE': (nhdg['{0}'], 'ComID'),
                                'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                                'FDate': (nhd['fDate'], '{0}'),
                                'Resolution': (nhd['resolution'], '{0}', int),
                                'GNIS_ID': (gnis['id'], '{0}'),
                                'LengthKM': (nhd['lengthKM'], '{0}', float),
                                'ReachCode': (nhd['reachCode'], nhd['reachCode/{0}']),
                                'FlowDir': (nhd['flowDir'], nhd['flowDir/{0}']),
                                'WBAreaComID': (nhd['wbAreaComID'], nhdf['{0}']),
                                'FType': (nhd['fType'], nhd['fType/{0}']),
                                'Shape_Length': (nhd['shapeLength'], '{0}'),
                                'Enabled': (nhd['enabled'], '{0}')
                                }

layer_models['NHDArea'] = {'ID_URI_TEMPLATE': (nhdf['{0}'], 'ComID'),
                          'GEOMETRY_URI_TEMPLATE': (nhdg['{0}'], 'ComID'),
                           'FDate': (nhd['fDate'], '{0}'),
                           'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                           'Resolution': (nhd['resolution'], '{0}', int),
                           'GNIS_ID': (gnis['id'], '{0}'),
                           'AreaSqKm': (nhd['areaSqKM'], '{0}', float),
                           'Elevation': (nhd['elevation'], '{0}', float),
                           'FType': (nhd['fType'], nhd['fType/{0}']),
                           'Shape_Length': (nhd['shapeLength'], '{0}'),
                           'Shape_Area': (nhd['shapeArea'], '{0}'),
                           }

layer_models['NHDWaterBody'] = {'ID_URI_TEMPLATE': (nhdf['{0}'], 'ComID'),
                                'GEOMETRY_URI_TEMPLATE': (nhdg['{0}'], 'ComID'),
                                'FDate': (nhd['fDate'], '{0}'),
                                'Resolution': (nhd['resolution'], '{0}', int),
                                'GNIS_ID': (gnis['id'], '{0}'),
                                'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                                'Shape_Length': (nhd['shapeLength'], '{0}'),
                                'Shape_Area': (nhd['shapeArea'], '{0}'),
                                'Elevation': (nhd['elevation'], '{0}', float),
                                'FDate': (nhd['fDate'], '{0}'),
                                'ReachCode': (nhd['reachCode'], nhd['reachCode/{0}']),
                                'AreaSqKm': (nhd['areaSqKM'], '{0}', float),
                                }

def InsertFeature(feature, model, store):
    feature_uri = model['ID_URI_TEMPLATE'][0]
    subject_field = model['ID_URI_TEMPLATE'][1]
    i = feature.GetFieldIndex(subject_field)
    feature_uri = feature_uri.format(feature.GetField(i))
    geometry_uri = model['GEOMETRY_URI_TEMPLATE'][0]
    geometry_field = model['GEOMETRY_URI_TEMPLATE'][1]
    i = feature.GetFieldIndex(subject_field)
    geometry_uri = geometry_uri.format(feature.GetField(i))
    
    for k,v in model.iteritems():
        i = feature.GetFieldIndex(k)
        if i != -1:
            f_val = feature.GetField(i)
            if f_val == None:
                obj = ""
            elif len(v) == 3:
                obj = v[2](v[1].format(f_val))
            else:
                obj = v[1].format(f_val)
            store.add((feature_uri, v[0].format(f_val), obj))
            wkt = feature.GetGeometryRef().ExportToWkt()
            store.add((feature_uri, geo['hasGeometry'], geometry_uri))
            store.add((geometry_uri, geo['asWKT'], wkt))

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
    store = Graph()

	# Set up temp graph
    
    layers = [ds.GetLayer(i) for i in range(0, ds.GetLayerCount())]
    # Loop through layers of the dataset and check if we have a model
    for i in layers:
        InsertLayer(i, store)

    return store
			
    
