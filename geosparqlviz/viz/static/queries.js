
var queries = [{
		   'name': 'Query 1',
		   'text': """"
				       SELECT DISTINCT
					   *
					   WHERE {
					       GRAPH <http://cegis.usgs.gov/rdf/> {
						   ?sub <http://www.opengis.net/def/geosparql/asWKT> ?wkt .
					   }
				   } LIMIT 10
	       """"
}
];