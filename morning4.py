# foreach marketplace
#     forall relevant_ads
#         extract interesting features
#             including at least deadline, price, format
#         rank based on features       
# filter realistic_ads from relevant_ads
#     price > minimum_price && now < deadline + average_required_time && format is supported
# for topX ad in realistic_ads
#     extract more features based on format
#     rank features by importance
#     generate N results matching all features as constraints ***current work***
#         generate N-M results matching all but some features as constraints
#     rank results according to
#         constraints matching
#         novelty
#         generic aesthetics rules
#         format specific aesthetics rules
#         domain specific aesthetics rules
#     display results
#         formatted to facilitate
#             manual review
#             annotation
#             submission
ad_format = 'image'
ad_keywords = ['banana','car','Blue']

expected_number_results = 10

result_size = 1000

serverRootUrl = "http://fabien.benetou.fr:8080/"
#import pattern

import PythonMagick as Magick

import urllib2
import simplejson
import cStringIO

fetcher = urllib2.build_opener()

def makeImage(ad_keywords,index):
    for word in ad_keywords:
        searchTerm = word
        startIndex = '0'
        searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + searchTerm + "&start=" + startIndex
        f = fetcher.open(searchUrl)
        deserialized_output = simplejson.load(f)
        imageUrl = deserialized_output['responseData']['results'][index]['unescapedUrl']
        # seems limited to only 3 results
        try:
        # can fail easilly
            img = Magick.Image(imageUrl)
        except:
            print "damn, fail grab, should change index and try the next"
            return 1 
        img.quality(100) #full compression
        img.magick('PNG')
        img.write("img" + word + ".png")

index = 0
imagenames = ""
resultname = ""
for word in ad_keywords:
    imagename = "img" + word + ".png"
    imagenames += imagename + " "
    resultname += imagename+str(index)
resultname += "result.png"


print "manual test : https://www.google.com/searchbyimage?&image_url="+serverRootUrl+resultname
# print "Not h-creative, make other ..."

import os.path
while os.path.isfile(resultname):
    print "Not p-creative, make other ..."
    index += 1
    resultname = ""
    for word in ad_keywords:
        resultname += "img" + word + ".png"+str(index)
    resultname += "result.png"
    while makeImage(ad_keywords,index) == 1:
        index += 1
        resultname = ""
        for word in ad_keywords:
            resultname += "img" + word + ".png"+str(index)
        resultname += "result.png"

if not os.path.isfile(resultname):
    while makeImage(ad_keywords,index) == 1:
        index += 1
        resultname = ""
        for word in ad_keywords:
            resultname += "img" + word + ".png"+str(index)
        resultname += "result.png"

import os
os.system("montage " + imagenames + resultname)
# horrible, should use the ImageQuick binding but no time left to check the documentation...
# http://www.imagemagick.org/Usage/montage/

import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
HandlerClass = SimpleHTTPRequestHandler
ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"
port = 8080
server_address = ('0.0.0.0', port)
HandlerClass.protocol_version = Protocol
httpd = ServerClass(server_address, HandlerClass)
sa = httpd.socket.getsockname()
print serverRootUrl
httpd.serve_forever()
