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

def SearchPTH(queryString, language):
    url = "https://beta.paikkatietoalusta.fi/api/public/v1/search?X-CLIENT-LANG=FI"
    response = requests.post(url, json = createPTAJSON(queryString, language))
    responseStatus = response.status_code
    LOG(response.status_code)
    if(responseStatus == 200 or responseStatus == 201 or responseStatus == 204 ):
        json = response.json()
        return json.get("hits")

def createPTAJSON(queryString, language):
    return {"skip": 0, "pageSize": 100, "query": queryString.split(), "queryLanguage": language, "facets": {"types": ["isService"]}, "sort": [{"field": "title", "order": "asc"}]}

def listChildNodes(layers, index):
    items = []

    layerList = layers.get("contents")

    for layer in layerList:
        item = QTreeWidgetItem()
        item.setText(0, layers.get("service")[layer].title)
        item.setData(0, 1, {"layerName": layer, "index": index})
        items.append(item)

    return items


def getWFSFeature(layerName, data, crs):
    #TODO: CRS optionas should be added
    crs = checkCRSOptions(data.get("service")[layerName].crsOptions, crs)
    url = "restrictToRequestBBOX='1' srsname='" + crs + "' typename='" + layerName + "' url='" + data.get("url") + "' table=''"
    vlayer = QgsVectorLayer(url, data.get("service")[layerName].title, "wfs")
    return vlayer

def getWMSFeature(layerName, data, crs):
    #TODO: CRS optionas should be added
    crs = checkCRSOptions(data.get("service")[layerName].crsOptions, crs)
    #TODO: Format optins should be taken into account
    formatOptions = data.get("formats")
    format = "image/png"
    if format not in data.get("formats"):
        format = formatOptions[0]

    source = {
        "crs": crs,
        "dpiMode": "7",
        "format": format,
        #"layers": data.get("layer"),
        "layers": layerName,
        "url": data.get("url"),
        "styles": ""
    }
    source = urllib.parse.unquote(urllib.parse.urlencode(source))
    #source = "crs=CRS:84&dpiMode=7&format=image/png&layers=AM.GroundWaterBody&styles&url=http://paikkatieto.ymparisto.fi/arcgis/services/INSPIRE/SYKE_AlueidenHallintaJaRajoitukset1/MapServer/WMSServer"
    rlayer = QgsRasterLayer(source, data.get("service")[layerName].title, "wms")
    return rlayer

def checkCRSOptions(options, crs):
    if crs in options:
        return crs
    else:
        return "EPSG:3067"
