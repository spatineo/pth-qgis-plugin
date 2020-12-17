import requests
import urllib
from xml.etree import ElementTree
from qgis.core import QgsVectorLayer, QgsRasterLayer
from qgis.PyQt.QtWidgets import QListWidgetItem, QTreeWidgetItem
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.wmts import WebMapTileService
from os import path

def LOG(message):
    pathToLogFile = "/Users/patrickalaspaa/pylog"
    if not isinstance(message, str):
         message = str(message)
    if path.exists(pathToLogFile):
        f = open(pathToLogFile, "a")
        f.write(message + "\n\n")
        f.close()

def SearchPTA(queryString, language):
    url = "https://beta.paikkatietoalusta.fi/api/public/v1/search?X-CLIENT-LANG=FI"
    response = requests.post(url, json = createPTAJSON(queryString, language))
    responseStatus = response.status_code
    LOG(response.status_code)
    if(responseStatus == 200 or responseStatus == 201 or responseStatus == 204 ):
        json = response.json()
        return json.get("hits")

def createPTAJSON(queryString, language):
    return {"skip": 0, "pageSize": 100, "query": queryString.split(), "queryLanguage": language, "facets": {"types": ["isService"]}, "sort": [{"field": "title", "order": "asc"}]}

def listChildNodes(layers):
    items = []

    layerList = layers.get("contents")
    for layer in layerList:
        item = QTreeWidgetItem()
        item.setText(0, layer.title())
        item.setData(0, 1, {"layer": layer, "dict": layers})
        items.append(item)

    return items


def getWFSFeature(data, crs):
    #TODO: CRS optionas should be added
    crs = checkCRSOptions([], crs)
    url = "restrictToRequestBBOX='1' srsname='" + crs + "' typename='" + data.get("layer") + "' url='" + data.get("dict").get("url") + "' table=''"
    vlayer = QgsVectorLayer(url, data.get("layer").title(), "wfs")
    return vlayer

def getWMSFeature(data, crs):
    #TODO: CRS optionas should be added
    crs = checkCRSOptions([], crs)
    #TODO: Format optins should be taken into account
    formatOptions = data.get("dict").get("formats")
    LOG(formatOptions)

    source = {
        "crs": crs,
        "dpiMode": "7",
        "format": "image/png",
        "layers": data.get("layer"),
        "url": data.get("dict").get("url"),
        "styles": ""
    }
    source = urllib.parse.unquote(urllib.parse.urlencode(source))
    #source = "crs=CRS:84&dpiMode=7&format=image/png&layers=AM.GroundWaterBody&styles&url=http://paikkatieto.ymparisto.fi/arcgis/services/INSPIRE/SYKE_AlueidenHallintaJaRajoitukset1/MapServer/WMSServer"
    rlayer = QgsRasterLayer(source, data.get("layer").title(), "wms")
    return rlayer

def checkCRSOptions(options, crs):
    if crs in options:
        return crs
    else:
        return "EPSG:3067"
