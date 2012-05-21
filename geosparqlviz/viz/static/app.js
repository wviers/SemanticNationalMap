

/* 
 * Configure jQuery to user Django's CRSF protection
 * 
 */
jQuery(document).ajaxSend(function(event, xhr, settings) {
			      function getCookie(name) {
				  var cookieValue = null;
				  if (document.cookie && document.cookie != '') {
				      var cookies = document.cookie.split(';');
				      for (var i = 0; i < cookies.length; i++) {
					  var cookie = jQuery.trim(cookies[i]);
					  // Does this cookie string begin with the name we want?
					  if (cookie.substring(0, name.length + 1) == (name + '=')) {
					      cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					      break;
					  }
				      }
				  }
				  return cookieValue;
			      }
			      function sameOrigin(url) {
				  // url could be relative or scheme relative or absolute
				  var host = document.location.host; // host + port
				  var protocol = document.location.protocol;
				  var sr_origin = '//' + host;
				  var origin = protocol + sr_origin;
				  // Allow absolute or scheme relative URLs to same origin
				  return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
				      (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
				      // or any other URL that isn't scheme relative or absolute i.e relative.
				      !(/^(\/\/|http:|https:).*/.test(url));
			      }
			      function safeMethod(method) {
				  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
			      }
			      
			      if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
				  xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			      }
			  });

/*
 Initializes the Openlayers map, its layers, the function that selects
 coordinates, and the events taht switch from the small to large scale
 maps
 Parameters:None
 Returns: None
 */
/*
 Destroys popups when the feature they members of are unselected.
 Parameters:
 {Openlayers.Feature} feature - The feature that is being unselected.
 Returns: None
 */
function onFeatureUnselect(feature){
    map.removePopup(feature.popup);
    feature.popup.destroy();
    feature.popup = null;
}


/*
 Creates popups when the feature is selected.
 Parameters:
 {Openlayers.Feature} feature - The feature that is being selected.
 Returns: None
 */
function onFeatureSelect(feature){
    selectedFeature = feature;
    var proj = new OpenLayers.Projection('EPSG:4326');
    var mercator = new OpenLayers.Projection('EPSG:900913');
    
    popup = new OpenLayers.Popup.FramedCloud('popup',
					     feature.geometry.getBounds().getCenterLonLat(),null,
					     feature.id + ': ' + feature.geometry.transform(mercator, proj).x +
					     ','+feature.geometry.y,
					     null, true, onPopupClose);
    
    feature.geometry.transform(proj, mercator);
    feature.popup = popup;
    map.addPopup(popup);
}


function init(){
    
    var maxExtent = new OpenLayers.Bounds(-20037508, -20037508, 20037508, 20037508),
    restrictedExtent = maxExtent.clone(),
    maxResolution = 156543.0339;
    
    
    
    var options = {
        projection: new OpenLayers.Projection('EPSG:900913'),
        displayProjection: new OpenLayers.Projection('EPSG:4326'),
        units: 'm',
        numZoomLevels: 18,
        maxResolution: maxResolution,
        maxExtent: maxExtent,
        restrictedExtent: restrictedExtent};
    
    map = new OpenLayers.Map('map', options);
    
    
    var smallScale = new OpenLayers.Layer.ArcGIS93Rest( 'SmallScale',
							'http://raster1.nationalmap.gov/ArcGIS/rest' +
							'/services/TNM_Small_Scale_Imagery/MapServer/export',
							{});
    
    
    
    var nationalMapWMS = new OpenLayers.Layer.WMS('NationalMapLarge',
						  'http://raster.nationalmap.gov/arcgis/services/Combined/' +
						  'TNM_Large_Scale_Imagery/MapServer/WMSServer',
						  {layers: '0'});
    
    
    vectors = new OpenLayers.Layer.Vector('Vector Layer');
    
  var control = new OpenLayers.Control();
    OpenLayers.Util.extend(control, {draw: function () {
					 this.box = new OpenLayers.Handler.Box( control, {'done': this.notice},
										{keyMask: OpenLayers.Handler.MOD_SHIFT});
					 this.box.activate(); },
				     
				     notice: function (bounds) {
					 var ll = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.left, bounds.bottom));
					 var ur = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.right, bounds.top));
					 var ul = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.left, bounds.top));
					 var lr = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.right, bounds.bottom));
					 
					 input(
					     OpenLayers.Layer.SphericalMercator.inverseMercator(ll.lon.toFixed(4), ll.lat.toFixed(4)),
					     OpenLayers.Layer.SphericalMercator.inverseMercator(ul.lon.toFixed(4), ul.lat.toFixed(4)),
					     OpenLayers.Layer.SphericalMercator.inverseMercator(lr.lon.toFixed(4), lr.lat.toFixed(4)),
					     OpenLayers.Layer.SphericalMercator.inverseMercator(ur.lon.toFixed(4), ur.lat.toFixed(4)));
				     }
				    });
    
    map.addControl(new OpenLayers.Control.MousePosition());
    map.addLayers([vectors, nationalMapWMS, smallScale]);
    map.addLayers([vectors, nationalMapWMS, nationalMapWMS]);
    map.addControl(control);
    
    selectControl = new OpenLayers.Control.SelectFeature(vectors,
							 {onSelect: onFeatureSelect, onUnselect: onFeatureUnselect});
    
    drawControls = {polygon: new OpenLayers.Control.DrawFeature(vectors,
								OpenLayers.Handler.Point), select: selectControl};
    
    for(var key in drawControls)
    {
	map.addControl(drawControls[key]);
    }
    
    
    nationalMapWMS.events.on({
				 moveend: function(e){
				     if (e.zoomChanged){
					 if(map.zoom < 12)
					     map.setBaseLayer(smallScale);
				     }
				 }
			     });
    
    
    smallScale.events.on({moveend: function(e){
			      if (e.zoomChanged){
				  if(map.zoom >= 12)
				      map.setBaseLayer(nationalMapWMS);
			      }
			  }
			 });
    
    var proj = new OpenLayers.Projection('EPSG:4326');
    var mercator = new OpenLayers.Projection('EPSG:900913');
    var point = new OpenLayers.LonLat(-84.445, 33.7991);
    map.setCenter(point.transform(proj, mercator), 12);
}

function updatetable(resultMsg)
{
    var $wrap = $('<div>').attr('id', 'tableWrap');

    var $tbl = $('<table>').attr('id', 'basicTable');

    /* Create table headings */
    var $tr = $('<tr>');
    for (var i=0; i < resultMsg['head']['vars'].length; ++i) {
	$tr.append($('<th>').text(resultMsg['head']['vars'][i]));
    }
    $tbl.append($tr);
    
    for (var j=0; j < resultMsg['results']['bindings'].length; ++j) {
	$tr = $('<tr>');
	for (var key in resultMsg['results']['bindings'][j]) {
            if (key == "wkt") {
		var bindings = resultMsg['results']['bindings'];
		$tr.append($('<td>').text(bindings[j][key].value.substring(0, 100) + '...'));
	    } else {
		var bindings = resultMsg['results']['bindings'];
		$tr.append($('<td>').text(bindings[j][key].value));
	    }
	}
	$tbl.append($tr);
    }

    $('#tab_2').empty();
    $('#tab_2').append($tbl);

    return true;
}

function updatemap(resultMsg)
{
    var features = new Array();
    var bounds;
    var options = {
        'internalProjection': map.baseLayer.projection, 
        'externalProjection': new OpenLayers.Projection('EPSG:4269')
    };   
    var parser = new OpenLayers.Format.WKT(options);

    vectors.removeAllFeatures();

    for (i=0; i < resultMsg['results']['bindings'].length; ++i) {
	var wkt = resultMsg['results']['bindings'][i]['wkt'];

	if (wkt == undefined) {
	    return true;
	}

	// Remove CRS from from of wkt
	var wkt2 = wkt['value'];
	if (wkt2.split(/\>/)[1] != undefined) {
	    wkt2 = wkt2.split(/\>/)[1];
	}


	var feat = parser.read(wkt2);
	if (feat != undefined) {
	    features.push(feat);	    
	}
    }

    for (i=0; i<features.length; ++i) {
	if (!bounds) {
	    bounds = features[i].geometry.getBounds();
	} else {
	    bounds.extend(features[i].geometry.getBounds());   
	}
    }
    
    vectors.addFeatures(features);
    map.zoomToExtent(bounds);
    /*
    var overCallback = { over: featureOver, out: hideTooltip };
    var layers = map.getLayersByClass('OpenLayers.Layer.Vector');
    var selectControl = new OpenLayers.Control.SelectFeature(layers,
							     { callbacks: overCallback });
    selectControl.onSelect = function(feature) {
        if (feature.attributes.clickable != 'off') alert('Feature!');
    };
    map.addControl(selectControl);
    selectControl.activate();
    function featureOver(feature) {
            // 'this' is selectFeature control
            var fname = feature.attributes.name || feature.attributes.title || feature.attributes.id || feature.fid;
            if (feature.geometry.CLASS_NAME == "OpenLayers.Geometry.LineString") {
                fname += ' '+ Math.round(feature.geometry.getGeodesicLength(feature.layer.map.baseLayer.projection) * 0.1) / 100 + 'km';
            }
            var xy = this.map.getControl('ll_mouse').lastXy || { x: 0, y: 0 };
            showTooltip(fname, xy.x, xy.y);
        }

        function getViewport() {
            var e = window, a = 'inner';
            if ( !( 'innerWidth' in window ) ) {
                a = 'client';
                e = document.documentElement || document.body;
            }
            return { width : e[ a+'Width' ], height : e[ a+'Height' ] };
        }
        function showTooltip(ttText, x, y) {
            var windowWidth = getViewport().width;
            var o = document.getElementById('tooltip');
            o.innerHTML = ttText;
            if(o.offsetWidth) {
                var ew = o.offsetWidth;
            } else if(o.clip.width) {
                var ew = o.clip.width;
            }
            y = y + 16;
            x = x - (ew / 4);
            if (x < 2) {
                x = 2;
            } else if(x + ew > windowWidth) {
                x = windowWidth - ew - 4;
            }
            o.style.left = x + 'px';
            o.style.top = y + 'px';
            o.style.visibility = 'visible';
        }
        function hideTooltip() {
            document.getElementById('tooltip').style.visibility = 'hidden';
        }
     */

    return true;
}

function submitquery()
{

    var request = $.ajax({
			     type: "GET",
			     url: "/parliament/sparql",
			     data: {
				 "query": $("#queryarea").val(),
				 "output": "json"
			     }
			 });

    request.done(function( msg ) {
		     updatetable(msg);
		     updatemap(msg);
		 });

    request.fail(function(jqXHR, textStatus) {
		     alert( "Request Failed: " + textStatus);
		 });
}
