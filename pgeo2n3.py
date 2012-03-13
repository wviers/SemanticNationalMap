#!/usr/bin/python

import osgeo 
from osgeo import ogr
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import URIRef, Namespace
from rdflib.term import Literal
from rdflib.term import URIRef

nhd = Namespace('http://cegis.usgs.gov/rdf/nhd/')
nhdf = Namespace('http://cegis.usgs.gov/rdf/nhd/Features/')
nhdg = Namespace('http://cegis.usgs.gov/rdf/nhd/Geometries/')
gnis = Namespace('http://cegis.usgs.gov/rdf/gnis/')
geo = Namespace('http://opengis.net/ont/OGC-GeoSPARQL/1.0/')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')

int_type =  '^^<http://www.w3.org/2001/XMLSchema#int>'
string_type = '^^<http://www.w3.org/2001/XMLSchema#string>'

layer_models = {}

layer_models['NHDPoint'] = {'ID_URI_TEMPLATE': (nhdf['points/'], 'ComID'), 
'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                             'TYPE': nhd['point'],
                             'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                             'FDate': (nhd['fDate'], '{0}', str),
                             'Resolution': (nhd['resolution'], '{0}', int),
							 'GNIS_ID': (gnis['id'], '{0}', int)
                             }

layer_models['NHDFlowline'] = {'ID_URI_TEMPLATE': (nhdf['flowline/'], 'ComID'),
                                'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                                'TYPE': nhd['flowline'],
                                'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                                'FDate': (nhd['fDate'], '{0}', unicode),
                                'Resolution': (nhd['resolution'], '{0}', int),
                                'GNIS_ID': (gnis['id'], '{0}', int),
                                'LengthKM': (nhd['lengthKM'], '{0}', float),
                                'ReachCode': (nhd['reachCode'], nhd['reachCode/{0}']),
                                'FlowDir': (nhd['flowDir'], nhd['flowDir/{0}']),
                                'WBAreaComID': (nhd['wbAreaComID'], nhdf['{0}']),
                                'FType': (nhd['fType'], nhd['fType/{0}']),
                                'Shape_Length': (nhd['shapeLength'], '{0}'),
                                'Enabled': (nhd['enabled'], '{0}', unicode)
                                }

layer_models['NHDArea'] = {'ID_URI_TEMPLATE': (nhdf['area/'], 'ComID'),
                           'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                           'TYPE': nhd['area'],
                           'FDate': (nhd['fDate'], '{0}', unicode),
                           'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                           'Resolution': (nhd['resolution'], '{0}', int),
                           'GNIS_ID': (gnis['id'], '{0}', int),
                           'AreaSqKm': (nhd['areaSqKM'], '{0}', float),
                           'Elevation': (nhd['elevation'], '{0}', float),
                           'FType': (nhd['fType'], nhd['fType/{0}']),
                           'Shape_Length': (nhd['shapeLength'], '{0}', float),
                           'Shape_Area': (nhd['shapeArea'], '{0}', float),
                           }

layer_models['NHDWaterBody'] = {'ID_URI_TEMPLATE': (nhdf['waterBody/'], 'ComID'),
                                'GEOMETRY_URI_TEMPLATE': (nhdg[''], 'ComID'),
                                'TYPE': nhd['waterbody'],
                                'FDate': (nhd['fDate'], '{0}', unicode),
                                'Resolution': (nhd['resolution'], '{0}', int),
                                'GNIS_ID': (gnis['id'], '{0}', int),
                                'FCode': (nhd['fCode'], nhd['fCode/{0}']),
                                'Shape_Length': (nhd['shapeLength'], '{0}', float),
                                'Shape_Area': (nhd['shapeArea'], '{0}', float),
                                'Elevation': (nhd['elevation'], '{0}', float),
                                'FDate': (nhd['fDate'], '{0}', unicode),
                                'ReachCode': (nhd['reachCode'], nhd['reachCode/{0}']),
                                'AreaSqKm': (nhd['areaSqKM'], '{0}', float),
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
            if f_val == None:
                obj = Literal("")
            elif len(v) == 3:
                obj = Literal(v[2](v[1].format(f_val)))
            else:
                obj = URIRef(v[1].format(f_val))
            store.add((URIRef(feature_uri), URIRef(v[0].format(f_val)), obj))
            
    wkt = Literal(feature.GetGeometryRef().ExportToWkt(), datatype=u'http://www.opengis.net/def/dataType/OGC-SF/1.0/WKTLiteral')
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
    store.bind('nhd', 'http://cegis.usgs.gov/rdf/nhd/')
    store.bind('nhdf', 'http://cegis.usgs.gov/rdf/nhd/Features/')
    store.bind('nhdg', 'http://cegis.usgs.gov/rdf/nhd/Geometries/')
    store.bind('gnis', 'http://cegis.usgs.gov/rdf/gnis/')
    store.bind('geo', 'http://opengis.net/ont/OGC-GeoSPARQL/1.0/')

    
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
			
    
