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
import json
import PythonMagick as Magick
import urllib2
import simplejson
import cStringIO
import os
import os.path
import hashlib
import pickle

def loadData(resultsfile):
    jsonresults = open(resultsfile)
    pastcreations = json.load(jsonresults)
    for i in pastcreations:
        print i
        #nothing yet
    jsonresults.close()

class NewCreation:
    def __init__(self):
        #creations += self
        exploredfrom = self # other NewCreation

    filename = ""
    sourcefiles = []    # a specific class with file urls, dates, format, etc
    keywords = []       # either string or class to be defined
    blendingmethod = "" # currently only one, could also be a class
    generationtime = "" #DateTime.now() 
     
class SrcImage:
    def __init__(self, path, keyword ):
        self.path=path
        self.keyword=keyword

def blend(imagestouse, ad_keywords):
    
    os.system("montage " + ' '.join(str(x) for x in imagestouse) + " result_" + '_'.join(str(x) for x in ad_keywords) + ".png")
    # horrible, should use the ImageQuick binding but no time left to check the documentation...
    # http://www.imagemagick.org/Usage/montage/
    # or rather PIL PIllow equivalent, no need to add a rare library
    # http://pillow.readthedocs.org/reference/ImageChops.html

def addImageToLibrary(keyword, startIndex):
    fetcher = urllib2.build_opener()
    searchUrl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + keyword + "&start=" + str(startIndex)
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
    newimage = SrcImage(newimagepath,keyword)
    return newimage

if __name__ == "__main__":

    rooturl = "done.with.software"
    #important for QRcode 
    srcimagespath = "srcimages/img" 
    resultsfile = "results.json"
    imagestouse = []
    imagesdb = []
    ad_keywords = ['banana','car','Blue']
    

    previousdata = "data.pkl"
    if os.path.isfile(previousdata):
        with open(previousdata, 'rb') as input:
            imagesdb = pickle.load(input)

    for i in imagesdb:
        print i.keyword
        print i.path

    exit()
    #expected_number_results = 10
    #result_size = 1000
    
    creations = []
    
    #loadData(resultsfile)
    
    for keyword in ad_keywords:
        i = 0
        newimage = addImageToLibrary(keyword, i)
        while newimage == 1:
            i += 1
            newimage = addImageToLibrary(keyword, i)
        imagestouse.append(newimage.path)
        imagesdb.append(newimage)
    
    with open(previousdata, 'wb') as output:
        pickle.dump(imagesdb, output, pickle.HIGHEST_PROTOCOL)
    exit()
    
    # should JSON dump else either re-downloading every time or losing data like keyword used
    #print "manual test : https://www.google.com/searchbyimage?&image_url="+serverRootUrl+resultname
    # print "Not h-creative, make other ..."
    blend(imagestouse,ad_keywords)
    resultname = "result_" + '_'.join(str(x) for x in ad_keywords) + ".png"
    # overwrite, does not append
    resultjson = {'category': 'Basic montage',
        'fullsrc': '../' + resultname + '',
        'description': 'basic montage relying on the keywords ' + ' '.join(str(x) for x in ad_keywords),
        'lowsrc': '../' + resultname}
    with open(resultsfile, 'w') as outputfile:
        json.dump(resultjson, outputfile)
    
    
    #delegate web server proper to lighttpd
