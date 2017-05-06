#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os.path, re, json, sys
import PhotoScan

class PointCloudGenerator(object):
	def __init__(self, input_dir, output_dir, project_name=None, scale_list = None, filetype = "tif"):
		self.input_dir = input_dir
		if project_name is None:
			self.project_name = os.path.basename(input_dir)
		else:
			self.project_name = project_name
		self.output_dir = output_dir
		self.filetype = filetype
		

		# alignPhotos Parameters
		self.accuracy = PhotoScan.HighestAccuracy
		self.preselection = PhotoScan.GenericPreselection
		self.keypoint_limit = 100000
		self.tiepoint_limit = 10000

		# setScales Parameters
		self.scale_list = scale_list
		self.markerType = PhotoScan.CircularTarget12bit
		self.tolerance = 50
		
		# buildDenseCloud Parameters
		# self.quality = PhotoScan.UltraQuality
		self.quality = PhotoScan.HighQuality
		self.filter = PhotoScan.AggressiveFiltering


		self.doc = PhotoScan.app.document
		self.doc.clear()
		self.chunk = self.doc.addChunk()
		PTN_PHOTOS =r".+\." + filetype + "$"
		self.ptn_photos = re.compile(PTN_PHOTOS)

	def _getPhotoPathes(self, input_dir):
		dirEntry = os.scandir(input_dir)
		pathes = []
		for item in dirEntry:
			# print(item.name)
			m = self.ptn_photos.match(item.name)
			if item.is_dir():
				pathes.extend(self._getPhotoPathes(item.path))
			elif m is not None:
				filename = os.path.normpath(os.path.join(input_dir,item.name))
				pathes.append(filename)
		# print(pathes)
		return pathes

	def addPhotos(self, input_dir):
		pathes = self._getPhotoPathes(input_dir)
		self.chunk.addPhotos(pathes)

	def alignPhotos(self):
		print("AlignPhotos: Start")
		self.chunk.matchPhotos(accuracy=self.accuracy, preselection=self.preselection, keypoint_limit = self.keypoint_limit, tiepoint_limit= self.tiepoint_limit)
		self.chunk.alignCameras()
		print("AlignPhotos: Finished")
	def setScales(self):
		print("SetScales: Start")
		if self.scale_list is None:
			return
		self.chunk.detectMarkers(type=self.markerType, tolerance=self.tolerance)
		markers = self.chunk.markers
		
		tmpMLabelNum = sorted(list(set([item for sublist in self.scale_list for item in sublist[0:2]])))
		tmpMLabel = {marker.label:marker.key for marker in markers}
		mLabelNum2Key = {}
		for mNum in tmpMLabelNum:
			label = "target "+str(mNum)
			if label in tmpMLabel.keys():
				mLabelNum2Key[mNum] = tmpMLabel[label]
		
		for m1, m2, length, accuracy in self.scale_list:
			if (mLabelNum2Key[m1] is None) or (mLabelNum2Key[m2] is None):
				continue
			marker1 = markers[mLabelNum2Key[m1]]
			marker2 = markers[mLabelNum2Key[m2]]
			scalebar = self.chunk.addScalebar(marker1, marker2)
			scalebar.reference.accuracy = accuracy
			scalebar.reference.distance = length
		print("SetScales: Finished")

	def buildDenseCloud(self):
		print("BuildDenseCloud: Start")
		self.chunk.buildDenseCloud(quality=self.quality, filter=self.filter)
		print("BuildDenseCloud: Finished")
	def saveProject(self, output_dir):
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)
		path = os.path.join(output_dir, self.project_name + ".psx")
		self.doc.save(path, [self.chunk])
	def exportPointCloud(self,output_dir):
		path = os.path.join(output_dir, self.project_name + ".txt")
		self.chunk.exportPoints(path, PhotoScan.DataSource.DenseCloudData, normals = True, colors = True, format = PhotoScan.PointsFormat.PointsFormatXYZ)
	def generatePointCloud(self):
		self.addPhotos(self.input_dir)
		self.setScales()
		self.saveProject(self.output_dir)
		self.alignPhotos()
		self.saveProject(self.output_dir)
		self.buildDenseCloud()
		self.saveProject(self.output_dir)
		self.exportPointCloud(self.output_dir)

def batch(input_dir, output_dir, infofile = "info.json"):
	info_path = os.path.normpath(os.path.join(input_dir, infofile))
	with open(info_path, "r") as f:
		info = json.load(f)
		specimens = info["input"]
		scale_list = info["scale"]
	# print(info)
	for key, value in specimens.items():
		input_dir_specimen = os.path.normpath(os.path.join(input_dir, value["path"]))
		output_dir_specimen = os.path.normpath(os.path.join(output_dir, value["path"]))
		if not os.path.exists(output_dir_specimen):
			os.makedirs(output_dir_specimen)
		project_name = key
		projectPath = os.path.join(output_dir_specimen, project_name + ".psx")
		print(projectPath)
		existProject = os.path.isfile(projectPath)
		if not existProject:
			existOutputDir = os.path.isdir(output_dir_specimen)
			if not existOutputDir:
				os.mkdir(output_dir_specimen)
			pcGen = PointCloudGenerator(input_dir_specimen, output_dir_specimen, project_name, scale_list, "CR2")
			pcGen.generatePointCloud()

def main():
	argvs = sys.argv
	argc = len(argvs)
	print(argvs)
	if argc == 3:
		batch(argvs[1], argvs[2])
	else:
		print("Usage: This script needs 'input_dir' and 'output_dir' pathes.")
	# batch( r"//norin61-nas.ut-biomet.org/home/Soybean/Tanashi_2016_output/20160708")

if __name__ == '__main__':
    main()

