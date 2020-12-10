import requests
import urllib
from xml.etree import ElementTree
from qgis.core import QgsVectorLayer, QgsRasterLayer
from qgis.PyQt.QtWidgets import QListWidgetItem

def LOG(message):
    #TODO: Remove
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
                LOG("***** Capabilities url *****")
                LOG(url)
                response = requests.get(url, stream=True)
                xmlString = response.content

                if xmlString:
                    root = ElementTree.fromstring(xmlString)
                    url = "https://kartta.hel.fi/ws/geoserver/avoindata/wfs"
                    featureName = "avoindata:Kaavahakemisto_alue_kaava_vireilla"

                    getWFSFeature(url, featureName)
                    #Only works for wfs services. Distinction needs to be made between wfs and wms
                    for feature in root[3]:
                        #TODO: Strip namespace from json
                        title = feature.find("{http://www.opengis.net/wfs/2.0}Title").text
                        item = QListWidgetItem()
                        item.setText(title)
                        item.setData(1, feature)
                        items.append(item)
    return items


def getWFSFeature(featureUrl, featureName):
    params = {
        "service": "WFS",
        #"version": "1.0.0",
        "request": "GetFeature",
        "typename": featureName,
        #"srsname": "EPSG23030"
    }

    url = featureUrl + "?" + urllib.parse.unquote(urllib.parse.urlencode(params))
    #Testing source format
    url = "restrictToRequestBBOX='1' srsname='EPSG:3067' typename='avoindata:Kaavahakemisto_alue_kaava_vireilla' url='https://kartta.hel.fi/ws/geoserver/avoindata/wfs' table='&quot;&quot;'"

    vlayer = QgsVectorLayer(url, "my testing wfs layer", "wfs")
    return vlayer

def getWMSFeature(featureUrl, featureName):
    params = {

    }
    url = featureUrl + "?" + urllib.parse.unquote(urllib.parse.urlencode(params))
    #url = "http://sampleserver1.arcgisonline.com/ArcGIS/services/Specialty/ESRI_StatesCitiesRivers_USA/MapServer/WMSServer?version=1.3.0&request=GetMap&CRS=CRS:84&bbox=-178.217598,18.924782,-66.969271,71.406235&width=760&height=360&layers=0&styles=default&format=image/png"
    url = "https://geodata.tampere.fi/geoserver/ows?service=wms&version=1.3.0&request=GetMap&layers=Pirkanmaan_virkistysaluekartta&width=1000&height=1000&format=image/png&bbox=22.242404736354036,25.06800276336246,60.92749544859188,62.45816638701644&styles=,,,,,,"
    source = "crs=EPSG:3067&amp;dpiMode=7&amp;format=image/png&amp;layers=AM.GroundWaterBody&amp;styles&amp;url=http://paikkatieto.ymparisto.fi/arcgis/services/INSPIRE/SYKE_AlueidenHallintaJaRajoitukset1/MapServer/WMSServer"
    rlayer = QgsRasterLayer(url, "my wms test layer", "wms")

    LOG("Raster layer is valid: " + str(rlayer.isValid()))
    if rlayer.isValid():
        return rlayer
