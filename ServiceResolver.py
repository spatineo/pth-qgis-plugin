from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.wmts import WebMapTileService

import csv

def doWms(url):
    wms = WebMapService(url)

    wmsGetMap = next((i for i in wms.getOperationByName('GetMap').methods if i['type'] == 'Get'), None)
    return {
        'type': 'WMS',
        'contents': list(wms.contents),
        'formats': wms.getOperationByName('GetMap').formatOptions,
        'url': wmsGetMap['url'],
        'service': wms
    }

def doWfs(url):
    ## Huom! Minulle tuli ongelmia ilman version-parametria.
    ##  - Ilmeisesti oman ympäristön owslib lähti hakemaan versiota 1.0.0, joka aiheutti virheen joka jäi joko ikilooppiin tai oli vaan törkeän hidas
    ##  - Aivan kaikki palvelut eivät tue WFS 1.1.0:aa, mutta koetetaan tällä kunnes tulee ongelmia vastaan
    wfs = WebFeatureService(url, version='1.1.0')
    wfsGetFeature = next((i for i in wfs.getOperationByName('GetFeature').methods if i['type'] == 'Get'), None)

    ## Ei taideta tarvita formaattia WFS:llä
    return {
        'type': 'WFS',
        'contents': list(wfs.contents),
        'url': wfsGetFeature['url'],
        'service': wfs
    }

def doWmts(url):
    wmts = WebMapTileService(url)

    ## Huom! Katsoin mitä QGIS tallentaa WMTS "sourceen" ja siellä näkyy olevan GetCapaiblities-osoite
    wmtsGetCaps = next((i for i in wmts.getOperationByName('GetCapabilities').methods if i['type'] == 'Get'), None)

    return {
        'type': 'WMTS',
        'contents': list(wmts.contents),
        'formatPerLayer': dict(map(lambda kv: (kv[0], kv[1].formats), wmts.contents.items())),
        'tileMatrixSetsPerLayer': dict(map(lambda kv: (kv[0], kv[1].tilematrixsets), wmts.contents.items())),
        'url': wmtsGetCaps['url'],
        'service': wmts
    }


wfsProtocols = [
    'http://www.opengis.net/def/serviceType/ogc/wfs',
    'OGC:WFS',
    'OGC:WFS-1.0.0-http-get-capabilities'
]

wmsProtocols = [
    'http://www.opengis.net/def/serviceType/ogc/wms',
    'OGC:WMS',
    'OGC:WMS-1.1.1-http-get-capabilities',
    'OGC:WMS-1.1.1-http-get-map',
    'OGC:WMS-1.3.0-http-get-capabilities'
]


def getLayersForDownloadLink(protocol, url):
    params = {
        'type': 'NA'
    }

    if url.startswith("http"):
        try:
            if protocol in wfsProtocols:
                params = doWfs(url)

            elif protocol in wmsProtocols:
                params = doWms(url)
        except Exception as e:
            params = {
                'type': 'ERROR',
                'exception': e.args
            }
    return params

