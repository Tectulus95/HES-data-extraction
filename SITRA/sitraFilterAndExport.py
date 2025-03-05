import datetime
import os
import sys

from shapely import union
dirname = os.path.dirname(__file__)
parentdir = "".join(dirname.split()[0:-1])
sys.path.append(os.path.join(parentdir, 'hesDataExtraction'))
from time import time

import geopandas as gpd
from numpy import datetime64, float32, int32, str_, nan
import pandas as pd
from shapely.geometry import Point, Polygon, LineString, MultiPoint

from utils import progress, toCoord

#con = sqlite3.connect(os.path.join(dirname, "sitra_data.db"))

fileFolder = os.path.join(dirname, "Files")

sitraFiles = [
	os.path.join(fileFolder, "SITRA.TR.6668.txt"),
	os.path.join(fileFolder, "SITRA.TR.69.txt"),
	os.path.join(fileFolder, "SITRA.TR.70.txt"),
	os.path.join(fileFolder, "SITRA.TR.7173.txt")
	]

columnDict = {}

def sitraFilterAndExport(onlyCoords = False, ctrlGroup = False):
	with open(os.path.join(fileFolder, "SITRA.TR.LAY.txt")) as f:
		lines = f.readlines()
		for line in lines[2:78]:
			valuelist = line.split("\t")
			valuelist = list(filter(None, valuelist))
			dictlist = [valuelist[3], valuelist[4], valuelist[5]]
			columnDict[valuelist[1]] = dictlist

	sitraList = []
	print("Exporting 4 files")
	for i, file in enumerate(sitraFiles):
		with open(file) as f:
			lines = f.readlines()
			for j, line in enumerate(lines):
				linedict = {}
				for key in columnDict:
					linedict[key] = line[int(columnDict.get(key)[1])-1:int(columnDict.get(key)[2])].strip()
					if columnDict.get(key)[0] == "Number":
						try:
							linedict[key] = int(linedict[key])
						except:
							linedict[key] = None
				sitraList.append(linedict)
				progress(f"Exporting for File {i+1}", j, len(lines))

	df = pd.DataFrame(sitraList)
	print("Filtering Data")
	if onlyCoords:
		df = df[df["UTM"]!=""]
	if ctrlGroup:
		df["control"] = pd.Series()
		for i, row in df.iterrows():
			df.at[i, "control"] = str(row["DATE"]) + row["DATAT"] + row["SERAL"] + str(row["CORP"]) + str(row["PART"])
			progress("Writing control group", i, len(df))
	df.reset_index(inplace=True)
	df["ISO date"] = pd.Series(data=datetime)
	print("Converting to GeoDataFrame")
	df["geometry"] = gpd.GeoSeries(crs="EPSG:4326")
	df = gpd.GeoDataFrame(df, geometry="geometry")
	for i, row in df.iterrows():
		coords = toCoord(row["UTM"])
		if coords is not None:
			df.at[i, "geometry"] = Point(coords[1], coords[0])
		progress("Writing coordinates and dates", i, len(df))
		try:
			entrydate = pd.to_datetime(f'19{row["DATE"]}', format="%Y%m%d")
			df.at[i, "ISO date"] = entrydate
		except:
			pass
	savepath = os.path.join(parentdir, 'HES.gpkg')

	print("Saving")
	df.to_file(savepath, layer="SITRA", driver="GPKG")
	return df

def sitraSimplified(df):
	simpList = []
	code = df.at[0, "control"]
	recordDict = {}
	#control_values = df["control"].unique()
	for i, row in df.iterrows():
		if row["DATAT"] != "W" and not (row["DATAT"] == "S" and row["SERAL"][0] == "C"):
			if row["control"] != code:
				if bool(recordDict):
					if len(coords) > 1:
						mpt = MultiPoint(coords)
						recordDict["geometry"] = mpt.convex_hull
					elif len(coords) == 1:
						recordDict["geometry"] = Point(tuple(coords))
					else:
						geometry = None
					simpList.append(recordDict)
				code = row["control"]
				recordDict = {}
				recordDict["Control"] = code
				recordDict["Date"] = row["ISO date"]
				coords = []
				recordDict["Killed"] = 0
				recordDict["Wounded"] = 0
				recordDict["Captured"] = 0
			if row["geometry"] is not None: coords.append((row["geometry"].x, row["geometry"].y))
			if row["LSCAT"] == "J":
				recordDict["Killed"] += int(row["NODES"])
				recordDict["Wounded"] += int(row["NODAM"])
				recordDict["Captured"] += int(row["NOCAP"])
		progress("Writing Dictionaries", i, len(df))
	simpFrame = gpd.GeoDataFrame(simpList, crs="EPSG:4326")
	simpFrame.drop_duplicates(subset=["Control"], inplace=True)
	simpFrame.reset_index(inplace=True, drop=True)
	savepath = os.path.join(parentdir, 'HES.gpkg')
	simpFrame.to_file(savepath, layer="SITRA_simplified", driver="GPKG")


def main():
	sitra = sitraFilterAndExport(ctrlGroup=True)
	#loadpath = os.path.join(parentdir, 'HES.gpkg')
	#sitra = gpd.read_file(loadpath, layer='SITRA')
	sitraSimplified(sitra)

if __name__ == "__main__":
	main()