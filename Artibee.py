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
ACGHost = "artibee.xukeliapp.work"
iPhone5URLPath = "/_uploadfiles/iphone5/640/"
ReqeustHeaders = {"User-Agent": "ArtibeeFree/1.2.2 (iPhone; iOS 10.3.1; Scale/2.00)"}
SaveDiskPath = ""
SaveHImageDiskPath = ""
under18ImageList = []




def fetchUnder18ImageList(token):
    conn = httplib.HTTPConnection(ACGHost)
    index = 1
    while True:
        conn.request("GET","/json_daily.php?device=iphone5&page={}&version=a.1.2.2&token={}000000000000".format(index,token[:10]), headers=ReqeustHeaders)
        r1 = conn.getresponse()
        print("List Page: {}".format(index))
        print("Under18ImageList Response: {0} {1}".format(r1.status, r1.reason))
        data1 = r1.read()
        print("From Http GET Data Length: {0}".format(len(data1)))
        s=json.loads(data1)
        datas = s['data']
        if(len(datas) == 0 ):
            print("+-------------------------------+")
            print("Total Under18Image Pages: {0}".format(index-1))
            print("Under18ImageList count: {0}".format(len(under18ImageList)))
            print("+-------------------------------+")
            break
        for data in datas:
            under18ImageList.extend(data["imgs"])
        index += 1
        print("=================================")




def fetchImageList(token):
    conn = httplib.HTTPConnection(ACGHost)
    allImgs = []
    index = 1
    while True:
        conn.request("GET","/json_daily.php?device=iphone5&page={}&version=a.1.2.2&token={}".format(index,token), headers=ReqeustHeaders)
        r1 = conn.getresponse()
        print("List Page: {0}".format(index))
        print("List Response: {0} {1}".format(r1.status, r1.reason))
        data1 = r1.read()
        print("From Http GET Data Length: {0}".format(len(data1)))

        fileData = data1
        s=json.loads(fileData)
        datas = s['data']

        if(len(datas) == 0 ):
            print("+----------------------------+")
            print("AllPages count: {0}".format(index-1))
            print("AllImages count: {0}".format(len(allImgs)))
            print("+----------------------------+")
            return allImgs

        for data in datas:
            allImgs.extend(data["imgs"])
        index += 1

        print("=================================")



def checkSavePath():
    system = platform.system()
    global SaveDiskPath
    global SaveHImageDiskPath

    abspath = os.path.abspath(".")
    SaveDiskPath = os.path.join(abspath,"Artibee")
    SaveHImageDiskPath = os.path.join(SaveDiskPath,"H")


    print("System: {0},Save images to {1}, H images to {2}".format(system, SaveDiskPath, SaveHImageDiskPath))
    if not os.path.isdir(SaveDiskPath):
        print("{0} Not Exist".format(SaveDiskPath))
        os.mkdir(SaveDiskPath)
    if not os.path.isdir(SaveHImageDiskPath):
        print("{0} Not Exist".format(SaveHImageDiskPath))
        os.mkdir(SaveHImageDiskPath)


def downjpg(FileName,retries=3):
    global flag
    savePath = FileName;
    isHImage = True
    # 判断H图，默认都是H图
    if FileName in under18ImageList:
        isHImage = False
    print("DownLoad {0} isH {1}".format(FileName,isHImage))

    if isHImage:
        savePath = os.path.join(SaveHImageDiskPath,FileName)
        print("H image save path is : {0}".format(savePath))
    else:
        if flag != 1:
            savePath = os.path.join(SaveDiskPath,FileName)
            print("image save path is : {0}".format(savePath))
        else:
            return

    if os.path.isfile(savePath):
        print("{0} Exist".format(FileName))
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
            print(e.message)
            if retries > 0:
                time.sleep(1)
                return downjpg(FileName,retries=retries-1)
            else:
                print("Pic: {} download failed!".format(FileName))




class MyDownloadThread(threading.Thread):
	def __init__(self, input):
		super(MyDownloadThread, self).__init__()
		self._jobq = input
	def run(self):
		while self._jobq.qsize()>0:
			job = self._jobq.get()
			downjpg(job)
			if self._jobq.qsize() == 1:
				print("Download complete, you got all pictures!（´∀｀*) ")


def optimizeImg(File):
    system = platform.system()
    script = os.path.join(os.path.abspath("."),"pingo.exe")
    if (system == "Windows" and os.path.isfile(script)):
        os.system("{} -s5 {}".format(script,File))
    else:
        pass

if __name__ == "__main__":
    print("Begin....")

    parser = argparse.ArgumentParser()
    parser.add_argument('token',help="token for scrapy, eg: 9132210801044105040315")
    parser.add_argument('-f','--flag',help="1 or 0,only download H imgs,Deafult false",default = 0,type=int)
    args = parser.parse_args()
    token = args.token
    flag = args.flag

    if flag == 1:
        print("Only download H images !")

    allImgs = fetchImageList(token)
    fetchUnder18ImageList(token)

    checkSavePath()
    for i in allImgs:
    	myQueue.put(i)
    print("job myQueue size {0}".format(myQueue.qsize()))
    for x in range(threadWorker):
    	MyDownloadThread(myQueue).start()
