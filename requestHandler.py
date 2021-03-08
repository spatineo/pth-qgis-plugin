import requests
import urllib
import json
from PyQt5.QtCore import QUrl, QJsonDocument
from PyQt5.QtNetwork import QNetworkRequest
from xml.etree import ElementTree
from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsBlockingNetworkRequest, QgsNetworkReplyContent
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
    request = QNetworkRequest()
    request.setUrl(QUrl("https://paikkatietojentuottajat-koekaytto.maanmittauslaitos.fi/api/public/v1/search?X-CLIENT-LANG=FI"))
    request.setHeader(request.ContentTypeHeader, "application/json")
    jsonByteArray = QJsonDocument(createJson(queryString, language)).toJson()

    blockingNetworkRequest = QgsBlockingNetworkRequest()
    err = blockingNetworkRequest.post(request, jsonByteArray, True)

    if not err:
        response = blockingNetworkRequest.reply().content()
        dict_str = response.data().decode("utf-8")
        if dict_str:
            resp_json = json.loads(dict_str)
            return resp_json.get("hits")
        else:
            #No result returned
            LOG("Nothing returned")
            pass
    else:
        LOG(blockingNetworkRequest.errorMessage())
        #Show error

def createJson(queryString, language):
    return {"skip": 0, "pageSize": 100, "query": queryString.split(), "queryLanguage": language, "facets": {"types": ["isService"]}, "sort": []}

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
