from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'geosparqlviz.views.home', name='home'),
    # url(r'^geosparqlviz/', include('geosparqlviz.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^$', 'viz.views.loadindex'),
    (r'^viz/$', 'viz.views.loadindex'),
    (r'^sparql(?P<path>.*)$', 'viz.views.sparqlproxy', {'target_url': 'http://usgs-ybother.srv.mst.edu:8890/parliament/sparql'}),
    (r'^viz/sparql(?P<path>.*)$', 'viz.views.sparqlproxy', {'target_url': 'http://usgs-ybother.srv.mst.edu:8890/parliament/sparql'}),
)
