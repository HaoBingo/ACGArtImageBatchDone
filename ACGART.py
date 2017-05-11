# -*- coding: UTF-8 -*- 
import httplib
import json
import threading
import os.path
import Queue
import platform
import time
import argparse

myQueue = Queue.Queue(0)
threadWorker = 6
ACGHost = "beauty.xukeliapp.work"
iPhone5URLPath = "/_uploadfiles/iphone5/640/"
ReqeustHeaders = {"User-Agent": "NewBeautyFree/1.2.2 (iPhone; iOS 10.3.1; Scale/2.00)", "Cookie":"__cfduid=d86602b13317745b45fc082a7f25cc1571494310830"}
SaveDiskPath = ""
SaveHImageDiskPath = ""
under18ImageList = []





def fetchUnder18ImageList(token):
    conn = httplib.HTTPConnection(ACGHost)
    index = 1
    while True:
        conn.request("GET","/json_daily.php?device=iphone5&page={}&version=a.1.2.2&token={}000000000000".format(index,token[:10]), headers=ReqeustHeaders)
        r1 = conn.getresponse()
        print "List Page: {}".format(index)
        print "Under18ImageList Response:", r1.status, r1.reason
        data1 = r1.read()
        print "From Http GET Data Length:",len(data1)
        s=json.loads(data1)
        datas = s['data']
        if(len(datas) == 0 ):
            print "+-------------------------------+"
            print "Total Under18Image Pages: {}".format(index-1)
            print "Under18ImageList count:", len(under18ImageList)
            print "+-------------------------------+"
            break
        for data in datas:
            under18ImageList.extend(data["imgs"])
        index += 1
        print "================================="

        


def fetchImageList(token):
    conn = httplib.HTTPConnection(ACGHost)
    allImgs = []
    index = 1
    while True:
        conn.request("GET","/json_daily.php?device=iphone5&page={}&version=a.1.2.2&token={}".format(index,token), headers=ReqeustHeaders)
        r1 = conn.getresponse()
        print "List Page: {}".format(index)
        print "List Response:", r1.status, r1.reason
        data1 = r1.read()
        print "From Http GET Data Length:",len(data1)
        
        fileData = data1
        s=json.loads(fileData)
        datas = s['data']

        if(len(datas) == 0 ):
            print "+----------------------------+"
            print "AllPages count: {}".format(index-1)
            print "AllImages count:", len(allImgs)
            print "+----------------------------+"
            return allImgs
        
        for data in datas:
            allImgs.extend(data["imgs"])
        index += 1

        print "================================="
	


def checkPlatformAndSavePath():
    system = platform.system() 
    global SaveDiskPath
    global SaveHImageDiskPath
    if system == 'Windows':
        SaveDiskPath = '\\ACGART\\'
        SaveHImageDiskPath = '\\ACGART\\H\\'
    else:
        SaveDiskPath = './ACGART/'
        SaveHImageDiskPath = './ACGART/H/'
        
    print "System: %s,Save images to %s, H images to %s" % (system, SaveDiskPath, SaveHImageDiskPath)
    if not os.path.isdir(SaveDiskPath):
        print SaveDiskPath , "Not Exist"
        os.mkdir(SaveDiskPath)
    if not os.path.isdir(SaveHImageDiskPath):
        print SaveHImageDiskPath, "Not Exist"
        os.mkdir(SaveHImageDiskPath)


def downjpg(FileName,retries=3):
    savePath = FileName;
    isHImage = True
    # 判断H图，默认都是H图
    if FileName in under18ImageList:
        isHImage = False
    print "DownLoad", FileName, "isH", isHImage
    
    if isHImage:
        savePath = SaveHImageDiskPath +FileName
        print 'H image save path is :', savePath
    else:
        savePath = SaveDiskPath +FileName
        print 'image save path is :', savePath
        
    if os.path.isfile(savePath):
        print FileName, "Exist"
    else:
        try:
            inConn = httplib.HTTPConnection(ACGHost)
            inConn.request("GET",iPhone5URLPath+FileName, headers=ReqeustHeaders)
            imageRes = inConn.getresponse()
            imageData = imageRes.read()
            File = file(savePath,"wb")
            File.write(imageData)
            File.close()
            inConn = httplib.HTTPConnection(ACGHost)
            inConn.request("GET",iPhone5URLPath+FileName, headers=ReqeustHeaders)
            imageRes = inConn.getresponse()
            imageData = imageRes.read()
            File = file(savePath,"wb")
            File.write(imageData)
            File.close()
            optimizeImg(savePath)
        except Exception,e:
            print e.message
            if retries > 0:
                time.sleep(1)
                return downjpg(FileName,retries=retries-1)
            else:
                print "Pic: {} download failed!".format(FileName)
    

		        

class MyDownloadThread(threading.Thread):
	def __init__(self, input):
		super(MyDownloadThread, self).__init__()
		self._jobq = input
	def run(self):
		while self._jobq.qsize()>0:
			job = self._jobq.get()
			downjpg(job)
			if self._jobq.qsize() == 1:
				print 'Download complete, you got all pictures!（´∀｀*) '


def optimizeImg(File):
    system = platform.system() 
    script = os.path.join(os.path.abspath('.'),'pingo.exe')
    if (system == 'Windows' and os.path.isfile(savePath)):
        os.system('{} -s5 {}'.format(script,File))
    else:
        pass

if __name__ == '__main__':
    print "begin...."
    
    global token
    parser = argparse.ArgumentParser()
    parser.add_argument('token',help="token for scrapy, eg: 9132210801044103780693")
    args = parser.parse_args()
    token = args.token
    #print token
    
	
    
    allImgs = fetchImageList(token)
    
    fetchUnder18ImageList(token)
    
    checkPlatformAndSavePath()
    for i in allImgs:
    	myQueue.put(i)
    print "job myQueue size ", myQueue.qsize()
    for x in range(threadWorker):
    	MyDownloadThread(myQueue).start()
    
    
