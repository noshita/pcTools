#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os.path, re, json, sys
import PhotoScan

class PointCloudGenerator(object):
	def __init__(self, input_dir, output_dir, project_name=None, filetype = "tif"):
		self.input_dir = input_dir
		if project_name is None:
			self.project_name = os.path.basename(input_dir)
		else:
			self.project_name = project_name
		self.output_dir = output_dir
		self.filetype = filetype
		self.accuracy = PhotoScan.HighestAccuracy
		self.preselection = PhotoScan.GenericPreselection
		self.keypoint_limit = 100000
		self.tiepoint_limit = 100000 
		# self.quality = PhotoScan.UltraQuality
		self.quality = PhotoScan.HighQuality
		self.doc = PhotoScan.app.document
		self.doc.clear()
		self.chunk = self.doc.addChunk()
		PTN_PHOTOS =r".+\." + filetype + "$"
		self.ptn_photos = re.compile(PTN_PHOTOS)
	def addPhotos(self, input_dir):
		tmpFiles = os.listdir(input_dir)
		pathes = []
		# print(tmpFiles)
		for file in tmpFiles:
			m = self.ptn_photos.match(file)
			if m is not None:
				filename = os.path.normpath(os.path.join(input_dir,file))
				pathes.append(filename)
		self.chunk.addPhotos(pathes)
	def alignPhotos(self):
		self.chunk.matchPhotos(accuracy=self.accuracy, preselection=self.preselection)
		self.chunk.alignCameras()
	def buildDenseCloud(self):
		self.chunk.buildDenseCloud(quality=self.quality)
	def saveProject(self, output_dir):
		path = os.path.join(output_dir, self.project_name + ".psx")
		self.doc.save(path, [self.chunk])
	def exportPointCloud(self,output_dir):
		path = os.path.join(output_dir, self.project_name + ".txt")
		self.chunk.exportPoints(path, PhotoScan.DataSource.DenseCloudData, normals = True, colors = True, format = "xyz")
	def generatePointCloud(self):
		self.addPhotos(self.input_dir)
		self.alignPhotos()
		self.buildDenseCloud()
		self.saveProject(self.output_dir)
		self.exportPointCloud(self.output_dir)

def batch(input_dir, infofile = "info.json"):
	info_path = os.path.normpath(os.path.join(input_dir, infofile))
	with open(info_path, "r") as f:
		info = json.load(f)
	# print(info)
	for key, value in info.items():
		input_dir_specimen = os.path.normpath(os.path.join(input_dir, value["path"]))
		output_dir_specimen = os.path.normpath(os.path.join(input_dir_specimen, "points"))
		project_name = key
		print(os.path.join(output_dir_specimen, project_name + ".psx"))
		existProject = os.path.isfile(os.path.join(output_dir_specimen, project_name + ".psx"))
		if not existProject:
			existOutputDir = os.path.isdir(output_dir_specimen)
			if not existOutputDir:
				os.mkdir(output_dir_specimen)
			pcGen = PointCloudGenerator(input_dir_specimen, output_dir_specimen, project_name)
			pcGen.generatePointCloud()

def main():
	argvs = sys.argv
	argc = len(argvs)
	if argc == 2:
		batch(argvs[1])
	else:
		print("Usage: This script needs input_dir path.")
	# batch( r"//norin61-nas.ut-biomet.org/home/Soybean/Tanashi_2016_output/20160708")

if __name__ == '__main__':
    main()

