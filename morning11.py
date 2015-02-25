"""Generate a new image based on keywords"""

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
import sys
import json
import PythonMagick as Magick
import urllib2
import simplejson
import cStringIO
import os
import os.path
import hashlib
import pickle
from PIL import Image

"""Class for a new creation, required to be able to keep track of what was the source"""
class NewCreation:
    def __init__(self, imagestouse, ad_keywords, resultpath):
        #creations += self
        self.exploredfrom = self # other NewCreation
        self.filename = resultpath
        self.sourcefiles = imagestouse    # a specific class with file urls, dates, format, etc
        self.keywords = ad_keywords       # either string or class to be defined
        #redundant

    blendingmethod = "" # currently only one, could also be a class
    generationtime = "" #DateTime.now()

"""Class for an image required to make a new image"""
class SrcImage:
    def __init__(self, path, keyword):
        self.path = path
        self.keyword = keyword
"""Blend multiple images together and naming it based on the images used to make it"""
def blend(imagestouse, ad_keywords):
    hash_object = hashlib.md5('_'.join(str(x.path) for x in imagestouse).encode())
    imageHash = hash_object.hexdigest()
    resultpath = "results/result_" + imageHash + ".png"
    os.system("montage " + ' '.join(str(x.path) for x in imagestouse) + " " + resultpath)
    return NewCreation(imagestouse, ad_keywords, resultpath)
    # Move to PIL PIllow equivalent, no need to add a rare library
    # http://pillow.readthedocs.org/reference/ImageChops.html
    # Consider a list of blending functions instead

def blendPIL(imagestouse, ad_keywords):
    A6size = (1748, 1240)
    pilimg = []
    pilimgresized = []
    pilimgmodded = []
    for il in imagestouse:
        pilimg.append(Image.open(il.path))
        pilimgresized.append(pilimg[-1].resize(A6size))
        pilimgmodded.append(pilimgresized[-1].convert('RGBA'))
    blended = Image.blend(pilimgmodded[0], pilimgmodded[1], 0.5)
    blended = Image.blend(blended, pilimgmodded[-1], 0.7)
    hash_object = hashlib.md5('_'.join(str(x.path) for x in imagestouse).encode())
    imageHash = hash_object.hexdigest()
    resultpath = "results/result_" + imageHash + ".png"
    blended.save(resultpath)
    return NewCreation(imagestouse, ad_keywords, resultpath)

def addImageToLibrary(keyword, startIndex):
    #to move to Google CSE new API
    # Secret key AIzaSyAc1XPUe3mmW90ca-6nIF-XyH40WTdO_ZQ
    fetcher = urllib2.build_opener()
    searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&as_rights=cc_publicdomain&q=" + keyword + "&start=" + str(startIndex)
    f = fetcher.open(searchUrl)
    deserialized_output = simplejson.load(f)
    imageUrl = deserialized_output['responseData']['results'][0]['unescapedUrl']

    hash_object = hashlib.md5(imageUrl.encode())
    imageHash = hash_object.hexdigest()
    newimagepath = srcimagespath + imageHash + ".png"
    if os.path.isfile(newimagepath):
        return 1
    # limited to only 4 results
    try:
        #should check if already downloaded
        # could use hash on URL
        img = Magick.Image(imageUrl)
        # can fail easilly
    except:
        return 1 
    img.quality(100) #full compression
    img.magick('PNG')
    #consider using hashing or URL instead
    img.write(newimagepath)
    newimage = SrcImage(newimagepath, keyword)
    return newimage

if __name__ == "__main__":

    #All this should move to a JSON or similar configuration file
    rooturl = "done.with.software"
    #important for QRcode
    srcimagespath = "srcimages/img"
    resultsfile = "results.json"

    #initializing DBs
    imagestouse = []
    imagesdb = []
    createdimagesdb = []
    ad_keywords = []

    for arg in sys.argv[1:]:
        ad_keywords.append(arg)
    if len(ad_keywords) < 3:
        ad_keywords = ['banana', 'car', 'Blue']

    storedcreatedimages = "storedcreatedimages.pkl"
    if os.path.isfile(storedcreatedimages):
        with open(storedcreatedimages, 'rb') as inputfile:
            createdimagesdb = pickle.load(inputfile)

    storedsourceimages = "storedsourceimages.pkl"
    if os.path.isfile(storedsourceimages):
        with open(storedsourceimages, 'rb') as inputfile:
            imagesdb = pickle.load(inputfile)

    #expected_number_results = 10
    #result_size = 1000

    for keyword in ad_keywords:
        i = 0
        newimage = addImageToLibrary(keyword, i)
        while newimage == 1:
            i += 1
            newimage = addImageToLibrary(keyword, i)
        imagestouse.append(newimage)
        imagesdb.append(newimage)

    # should JSON dump else either re-downloading every time or losing data like keyword used
    #print "manual test : https://www.google.com/searchbyimage?&image_url="+serverRootUrl+resultname
    # print "Not h-creative, make other ..."
    #newpic = blend(imagestouse,ad_keywords)
    newpic = blendPIL(imagestouse, ad_keywords)

    createdimagesdb.append(newpic)

    #to move to its own function, will be later on delegated to proper web framework
    resultjson = []
    for image in createdimagesdb:
        resultjson.append({'category': 'Basic montage',
            'fullsrc': '../' +image.filename + '',
                            'description': 'basic montage relying on the keywords ' + ' '.join(str(x) for x in image.keywords),
                            'lowsrc': '../' + image.filename})

    with open(resultsfile, 'w') as outputfile:
        json.dump(resultjson, outputfile)

    with open(storedsourceimages, 'wb') as output:
        pickle.dump(imagesdb, output, pickle.HIGHEST_PROTOCOL)
    with open(storedcreatedimages, 'wb') as output:
        pickle.dump(createdimagesdb, output, pickle.HIGHEST_PROTOCOL)

    #delegated web server proper to lighttpd
