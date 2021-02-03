from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.wmts import WebMapTileService

from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from lxml import etree

from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtCore import QUrl
from qgis.core import QgsBlockingNetworkRequest, QgsNetworkReplyContent

import csv

def getOGCCapabilitiesUrlCombinations(initurl, serviceType, versions):
    # 1. Remove possible SERVICE, REQUEST and VERSION parameters from initurl (case insensitive)
    # 2. Create baseurl (initurl + SERVICE=service&REQUEST=GetCapabilities)
    # 3. Return a list with baseurl + versions combinatiosn (baseurl + VERSION=x)

    url = urlparse(initurl)
    qs = parse_qs(url.query)

    base_qs = {}
    base_qs['SERVICE'] = serviceType
    base_qs['REQUEST'] = 'GetCapabilities'

    for key in qs:
        if key.lower() == 'service' or key.lower() == 'request' or key.lower() == 'version':
            continue
        base_qs[key] = qs[key][0]


    ret = []
    for version in versions:
        base_qs['VERSION'] = version
        variant = urlunparse((url.scheme, url.netloc, url.path, "", urlencode(base_qs), ""))
        ret.append({ 'version': version, 'url': variant})

    return ret

def downloadDocument(url):
    request = QNetworkRequest()
    request.setUrl(QUrl(url))

    blockingNetworkRequest = QgsBlockingNetworkRequest()
    err = blockingNetworkRequest.get(request)
    if err:
        print(err)
        raise Exception

    response = blockingNetworkRequest.reply().content()
    dict_str = response.data()

    return dict_str

def getWmsService(baseurl):
    variants = getOGCCapabilitiesUrlCombinations(baseurl, "WMS", ["1.3.0", "1.1.1"])

    for variant in variants:
        try:
            doc = downloadDocument(variant['url'])
            service = WebMapService(variant['url'], xml=doc, version=variant['version'])
            if service is not None:
                return service
        except Exception as e:
            print("Unable to process {}, got error: {}".format(variant, e))

def doWms(url):
    wms = getWmsService(url)

    wmsGetMap = next((i for i in wms.getOperationByName('GetMap').methods if i['type'] == 'Get'), None)
    return {
        'type': 'WMS',
        'contents': list(wms.contents),
        'formats': wms.getOperationByName('GetMap').formatOptions,
        'url': wmsGetMap['url'],
        'service': wms
    }

def getWfsService(baseurl):
    variants = getOGCCapabilitiesUrlCombinations(baseurl, "WFS", ["2.0.0", "1.1.0", "1.0.0"])

    for variant in variants:
        try:
            doc = downloadDocument(variant['url'])
            service = WebFeatureService(variant['url'], xml=doc, version=variant['version'])
            if service is not None:
                return service
        except:
            print("Unable to process {}".format(variant))

def doWfs(url):
    wfs = getWfsService(url)
    wfsGetFeature = next((i for i in wfs.getOperationByName('GetFeature').methods if i['type'] == 'Get'), None)

    ## Ei taideta tarvita formaattia WFS:llä
    return {
        'type': 'WFS',
        'contents': list(wfs.contents),
        'url': wfsGetFeature['url'],
        'service': wfs
    }


def getWmtsService(baseurl):
    variants = getOGCCapabilitiesUrlCombinations(baseurl, "WMTS", ["1.0.0"])

    for variant in variants:
        try:
            doc = downloadDocument(variant['url'])
            service = WebMapTileService(variant['url'], xml=doc, version=variant['version'])
            if service is not None:
                return service
        except:
            print("Unable to process {}".format(variant))

def doWmts(url):
    wmts = getWmtsService(url)

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
