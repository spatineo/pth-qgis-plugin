import requests
import urllib
from .LayerMeta import LayerMeta
from xml.etree import ElementTree
from qgis.core import QgsVectorLayer, QgsRasterLayer
from qgis.PyQt.QtWidgets import QListWidgetItem
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.wmts import WebMapTileService

def LOG(message):
    #TODO: Remove
    if not isinstance(message, str):
         message = str(message)
    f = open("/Users/patrickalaspaa/pylog", "a")
    f.write(message + "\n\n")
    f.close()

def SearchPTA(queryString, language):
    url = "https://beta.paikkatietoalusta.fi/api/public/v1/search?X-CLIENT-LANG=FI"
    response = requests.post(url, json = createPTAJSON(queryString, language))
    responseStatus = response.status_code

    if(responseStatus == 200 or responseStatus == 201 or responseStatus == 204 ):
        json = response.json()
        return json.get("hits")

def createPTAJSON(queryString, language):
    return {"skip": 0, "pageSize": 10, "query": queryString.split(), "queryLanguage": language, "facets": {"types": ["isService"], "keywordsInspire": ["Ortoilmakuvat"]}, "sort": [{"field": "title", "order": "asc"}]}

#TODO: Use item to actualy make a query and get real layer
def getCapabilities(item):
    links = item.get("downloadLinks")
    if links:
        items = []
        for link in links:
            url = link.get("url")
            if url:
                if "?" in url:
                    url = url.split("?")[0]
                if url.endswith("wms"):
                    return WebMapService(url)
                elif url.endswith("wfs"):
                    return WebFeatureService(url, version='1.1.0')
                elif url.endswith("wmts"):
                    return WebMapTileService(url)

def listServiceContent(index, service, url):
    LOG("Listing service content")
    LOG(index)
    LOG(service)
    LOG(url)
    items = []
    layers = service.contents

    for layer in layers:
        item = QListWidgetItem()
        item.setText(layers[layer].title)
        layerMeta = LayerMeta(index, url, layer)
        item.setData(1, layerMeta)
        items.append(item)

    return items


def getWFSFeature(layerMeta, service, crs):
    if not crs:
        crs = "EPSG:3067"
    #params = {
    #    "service": "WFS",
    #    #"version": "1.0.0",
    #    "request": "GetFeature",
    #    "typename": featureName,
    #    #"srsname": "EPSG23030"
    #}

    #url = featureUrl + "?" + urllib.parse.unquote(urllib.parse.urlencode(params))
    #Check crs options
    #Testing source format
    #url = "restrictToRequestBBOX='1' srsname='EPSG:3067' typename='avoindata:Kaavahakemisto_alue_kaava_vireilla' url='https://kartta.hel.fi/ws/geoserver/avoindata/wfs' table=''"
    url = "restrictToRequestBBOX='1' srsname='" + crs + "' typename='" + layerMeta.layerName + "' url='" + layerMeta.serviceUrl + "' table=''"

    vlayer = QgsVectorLayer(url, service[layerMeta.layerName].title, "wfs")
    return vlayer

def getWMSFeature(layerUrl, layerName):

    #Get crs
    #Get layer name
    source = "crs=CRS:84&dpiMode=7&format=image/png&layers=AM.GroundWaterBody&styles&url=http://paikkatieto.ymparisto.fi/arcgis/services/INSPIRE/SYKE_AlueidenHallintaJaRajoitukset1/MapServer/WMSServer"
    rlayer = QgsRasterLayer(source, "my wms test layer", "wms")

    LOG("Raster layer is valid: " + str(rlayer.isValid()))
    if rlayer.isValid():
        return rlayer
