#!/usr/bin/env python
'''
Script to display a summary of files in the directory.
Displays number of files, filename and summary of frameranges

USAGE:
python lss.py -d \path\to\dir

BUGs:
1. Doesnt support if the filename has underscore before the framenumber
'''
__author__ = 'Rakesh Ramesh'

import glob
import re, os
import argparse
from itertools import groupby
from collections import Counter



sequencetypes = ['*.rgb', '*.exr', ".jpg"]
nonSequenceTypes = ['*.xml', '*.info']

def getFilesByExtension(ext_type):
	'''seperating files based on extension type'''
	filesList = []
	for files in ext_type:
		filesList.extend(glob.glob(files))
	return filesList

def frameRangeSummary(nums):
	'''gets the summary of frame numbers'''
	ranges = []
	for n in nums:
		if not ranges or n > ranges[-1][-1] + 1:
			ranges += [],
		ranges[-1][1:] = n,
	return ['-'.join(map(str, r)) for r in ranges]

def extractFilenameAndFrame(seqFiles):
	extension = []
	filenameAndFrame = []
	for seqFile in seqFiles:
		extension.append(seqFile.rsplit(".", 1))
	for fname in extension:
		filenameAndFrame.append([item[::-1] for item in fname[0][::-1].split('.', 1)][::-1])
	return filenameAndFrame

def getFrameNumbers(seqFiles):
	frameNumberList = []
	filenameAndFramenumberList = extractFilenameAndFrame(seqFiles)
	for i in filenameAndFramenumberList:
		frameNumberList.append(i[1])
	return frameNumberList

def seperateRGB(seqFiles):
	'''
	Returns a dictionary with key as sequence filename with no extension and frame number
	and values as a list of respective sequence files
	'''
	filenameAndFrame = extractFilenameAndFrame(seqFiles)
	fnameAndFramesDict={}
	seqFilename =[]
	for i in filenameAndFrame:
		seqFilename.append(i[0])
	seqFilename = list(set(seqFilename))
	for j in seqFilename:
		fnameAndFramesDict[j]=[i for i in seqFiles if j in i]
	return fnameAndFramesDict
	
def convertFramerange(seqInfo):
	'''
	Returns a dictionary with key as sequence filename with no extension and frame number
	and values as framerange summary
	'''
	seqfilecount = []
	padding =[]
	for key, value in seqInfo.iteritems():
		frameNumbers = getFrameNumbers(value)
		padding.append(len(frameNumbers[0]))
		seqInfo[key] = frameRangeSummary(map(int, frameNumbers))
		seqfilecount.append(len(value))
	return seqInfo, [seqfilecount, padding]

def countOccurences(files):
	return dict(Counter(files))

def getExtension(seqFiles):
	return seqFiles[0].split(".")[-1]

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--directory', dest = 'dir', help='enter a path', action='store')
	args = parser.parse_args()
	if os.path.exists(args.dir):
		os.chdir(args.dir)

	sequenceFiles = getFilesByExtension(sequencetypes)

	nonSequenceFiles = getFilesByExtension(nonSequenceTypes)
	nonSeqFilesCounter = countOccurences(nonSequenceFiles)

	seperatedseq = seperateRGB(sequenceFiles)
	fileseqAndFrameRangeSummary, seqfileinfo = convertFramerange(seperatedseq)

	i=0
	for key, value in fileseqAndFrameRangeSummary.iteritems():
		print '%s' %(str(seqfileinfo[0][i])) + '%27s' %(key) + ".%0" + str(seqfileinfo[1][i]) + "." + getExtension(sequenceFiles) + '%30s' %(" ".join(str(x) for x in value))
		i+=1
	for x in nonSeqFilesCounter:
		print '%s %34s' %(nonSeqFilesCounter[x], x)