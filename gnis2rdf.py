
import csv
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import URIRef, Namespace
from rdflib.term import Literal
from rdflib.term import URIRef
import sys
import re

gnis = Namespace('http://cegis.usgs.gov/rdf/gnis/')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
geo = Namespace('http://www.opengis.net/def/geosparql/')

date_type = 'http://www.w3.org/2001/XMLSchema#date'

def FeatureName2URI(feature_name):
    feature_name = re.sub(r'\s', '', feature_name)
    uri = gnis['featureType/{0}'.format(feature_name)]
    return uri

def ParseDate(date_string):
    d = date_string.split('/', 3)
    
    if len(d) < 3:
        return Literal('')
    
    lit = str(d[2]) + '-' + str(d[0]) + '-' + str(d[1])

    return Literal(lit, datatype=date_type)

def InsertGNISFeature(feature_tuple, store):
    uri = gnis['Features/{0}'.format(feature_tuple[0])]

    for i in range(0, len(feature_tuple)):
        feature_tuple[i] = Literal(feature_tuple[i])

    store.add((uri, rdf['type'], gnis['gnisfeature']))
    store.add((uri, rdfs['label'], feature_tuple[1]))
    store.add((uri, gnis['featureClass'], FeatureName2URI(feature_tuple[2])))
    store.add((uri, gnis['stateAlpha'], feature_tuple[3]))
    store.add((uri, gnis['stateNumeric'], feature_tuple[4]))
    store.add((uri, gnis['countyName'], feature_tuple[5]))
    store.add((uri, gnis['countyNumeric'], feature_tuple[6]))
    store.add((uri, gnis['mapName'], feature_tuple[17]))
    store.add((uri, gnis['dateCreated'], ParseDate(feature_tuple[18])))
    if feature_tuple[19] != '':
        store.add((uri, gnis['dateEdited'], ParseDate(feature_tuple[19])))

    # Create geometry object
    geo_uri = gnis['Geometries/{0}'.format(feature_tuple[0])]
    wkt_string = Literal('POINT ( ' + feature_tuple[10] + ' ' + feature_tuple[9] + ' )')
       
    store.add((uri, geo['hasGeometry'], geo_uri))
    store.add((geo_uri, rdf['type'], geo['Geometry']))
    store.add((geo_uri, geo['asWKT'], wkt_string))
    
def gnis2rdf(gnisfilename, rdffilename):
    gnisfile = open(gnisfilename, 'rb')
    store = ConjunctiveGraph(identifier='temp')
        
    if not gnisfile:
        print('Error opening gnis file!')
        return False

    gnisreader = csv.reader(gnisfile, delimiter='|')

    # Drop first row
    gnisreader.next()

    for r in gnisreader:
        InsertGNISFeature(r, store)

    # Add prefixes to store
    store.bind('gnis', gnis)
    store.bind('geo', geo)

    print('Serializing rdf...')
    store.serialize(destination=rdffilename, format='n3')
    print('created ' + str(len(store)) + ' triples')
    
if __name__ == '__main__':
    if len(sys.argv) >= 3:
        gnis2rdf(sys.argv[1], sys.argv[2])
