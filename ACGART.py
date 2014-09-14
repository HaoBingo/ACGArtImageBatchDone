# -*- coding: UTF-8 -*- 
import httplib
import json
import threading
import os.path
import Queue

myQueue = Queue.Queue(0)
threadWorker = 10
ACGHost = "acg.sugling.in"
iPhone5URLPath = '/_uploadfiles/iphone5/640/'
ReqeustHeaders = {"User-Agent": "ACGArt/4.4.11 CFNetwork/672.1.15 Darwin/14.0.0", "Accept":"*/*"}
SaveDiskPath = 'D:\\ACGART\\'
SaveHImageDiskPath = 'D:\\ACGART\\H\\'
under18ImageList = []


def fetchUnder18ImageList():
	conn = httplib.HTTPConnection(ACGHost)
	conn.request("GET","/json_daily.php?device=iphone5&pro=yes&user=yes&sexyfilter=yes&version=m.4.4.11", headers=ReqeustHeaders)
	r1 = conn.getresponse()
	print "Under18ImageList Response:", r1.status, r1.reason
	data1 = r1.read()
	print "From Http GET Data Length:",len(data1)
	s=json.loads(data1)
	datas = s['data']
	for data in datas:
		under18ImageList.extend(data["imgs"])
	print "Under18ImageList count:", len(under18ImageList)


def fetchImageList():
	conn = httplib.HTTPConnection(ACGHost)
	conn.request("GET","/json_daily.php?device=iphone5&pro=yes&user=yes&sexyfilter=no&version=m.4.4.11", headers=ReqeustHeaders)
	r1 = conn.getresponse()
	print "List Response:", r1.status, r1.reason
	data1 = r1.read()
	print "From Http GET Data Length:",len(data1)
	# print "JSON:",json.dumps(data1)
	# print "Data", data1
	# f = file("ACGART.txt","w")
	# f.write(data1)
	# f.close()
	# file_object = open('ACGART.txt')
	# try:
	#      fileData = file_object.read()
	# finally:
	#      file_object.close( )
	# print "Data", fileData
	fileData = data1
	s=json.loads(fileData)
	datas = s['data']
	# print "IMAGE DAYS Data length :",len(datas);
	# print datas[0]
	# print datas[0]["imgs"]
	allImgs = []
	# allImgs.extend(datas[0]["imgs"])
	# allImgs.extend(datas[1]["imgs"])
	for data in datas:
		allImgs.extend(data["imgs"])
	print "AllImages count:", len(allImgs)
	return allImgs

def checkDiskPath():
	if not os.path.isdir(SaveDiskPath):
		print SaveDiskPath , "Not Exist"
		os.mkdir(SaveDiskPath)
	if not os.path.isdir(SaveHImageDiskPath):
		print SaveHImageDiskPath, "Not Exist"
		os.mkdir(SaveHImageDiskPath)

def downjpg(FileName):
	savePath = FileName;
	isHImage = True
	if FileName in under18ImageList:
		isHImage = False
	print "DownLoad", FileName, "isH", isHImage

	if isHImage:
		savePath = SaveHImageDiskPath +FileName
	else:
		savePath = SaveDiskPath +FileName

	if os.path.isfile(savePath):
		print FileName, "Exist"
	else:
		inConn = httplib.HTTPConnection(ACGHost)
		inConn.request("GET",iPhone5URLPath+FileName, headers=ReqeustHeaders)
		imageRes = inConn.getresponse()
		imageData = imageRes.read()
		File = file(savePath,"wb")
		File.write(imageData)
		File.close()

class MyDownloadThread(threading.Thread):
	def __init__(self, input):
		super(MyDownloadThread, self).__init__()
		self._jobq = input
	def run(self):
		while self._jobq.qsize()>0:
			job = self._jobq.get()
			downjpg(job)

if __name__ == '__main__':
	print "begin...."
	allImgs = fetchImageList()
	fetchUnder18ImageList();
	checkDiskPath()
	for i in allImgs:
		myQueue.put(i)
	print "job myQueue size ", myQueue.qsize()
	for x in range(threadWorker):
		MyDownloadThread(myQueue).start()

