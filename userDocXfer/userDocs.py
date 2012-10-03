import os
import sys
import zipfile
import threading
import argparse

from time import sleep

#define the program args
parser = argparse.ArgumentParser(description='Zip files from specific dirs with specific extensions')
parser.add_argument('-d','--dir', help='comma separated dirs to search.  ex:  "c:\\workspace,c:\\users"', required=True)
parser.add_argument('-e','--ext', help='comma separated file extensions.  ex: ".doc,.txt,.png"', required=True)
parser.add_argument('-p','--keeppath', help='should it retain the full path in the zip? "y" for yes, "n" for no', default = 'y')
parser.add_argument('-v','--verbose',action="store_true", help='display logs of what is going on')
args = vars(parser.parse_args())

#array of paths to recurse through
rootPaths = args['dir'].split(",")

#dir to output the zip file
outputDir = './'

#write the zipfile with the name userDocs.zip
zf = zipfile.ZipFile('userDocs.zip', mode='w')

#file extensions to add to the archive
extensions = args['ext'].split(",")

#Determine if the full path should be retained in the zip
retainFullPath = args['keeppath'].lower() == 'y'

# Wrap the thread in a class
class singlePathThread(threading.Thread):
    def __init__(self, rootDir):
        if args['verbose']:
            print("starting new thread for: " + rootDir)
        self.rootDir = rootDir
        threading.Thread.__init__(self)
    def run(self):
        recurseAndAdd(self.rootDir)

#walk through a dir and its subdirs then add the correct files to a zip
def recurseAndAdd(rootDir):
    for root, subFolders, files in os.walk(rootDir):
        for fileName in files:
            # split the extension from the path and normalise it to lowercase.
            ext = os.path.splitext(fileName)[-1].lower()
            if ext in extensions:
                if args['verbose']:
                    print("adding filename: " + fileName)
                #maintain the dir structure in the zip
                if retainFullPath:
                    zf.write(root + "\\" +  fileName)
                #put everything in the top level    
                else:
                    zf.write(root + "\\" +  fileName, arcname=fileName)



#Create a separate thread for each path
startedThreads = []                    
for path in rootPaths:
    dirThread = singlePathThread(path)
    #run the final thread as a blocking thread
    if rootPaths[-1] == path:
        dirThread.run()
    else:
        dirThread.start()
        startedThreads.append(dirThread)

#if the last thread was faster than the rest, make sure the rest are not still running before closing the zip resource
for startedThread in startedThreads:
    while startedThread.isAlive():
        sleep(1)        

#relase the lock on the zip
zf.close()

