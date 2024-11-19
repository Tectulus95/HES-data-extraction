import datetime
import os
import sys
dirname = os.path.dirname(__file__)
parentdir = "".join(dirname.split()[0:-1])
sys.path.append(os.path.join(parentdir, 'hesDataExtraction'))

import geopandas as gpd
from numpy import datetime64, float32, int32, str_, nan
import pandas as pd
from shapely.geometry import Point

from utils import progress, toCoord

con = sqlite3.connect(os.path.join(dirname, "sitra_data.db"))

fileFolder = os.path.join(dirname, "Files")

sitraFiles = [
	os.path.join(fileFolder, "SITRA.TR.6668.txt"),
	os.path.join(fileFolder, "SITRA.TR.69.txt"),
	os.path.join(fileFolder, "SITRA.TR.70.txt"),
	os.path.join(fileFolder, "SITRA.TR.7173.txt")
	]

columnDict = {}

def sitraFilterAndEport():
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
	df = df[df["UTM"]!=""]
	df.reset_index(inplace=True)
	df["ISO date"] = pd.Series(data=datetime)
	print("Converting to GeoDataFrame")
	df["geometry"] = gpd.GeoSeries(crs="EPSG:4326")
	df = gpd.GeoDataFrame(df, geometry="geometry")
	print("Writing coordinates")
	for i, row in df.iterrows():
		coords = toCoord(row["UTM"])
		if coords is not None:
			df.at[i, "geometry"] = Point(coords[1], coords[0])
		progress("Writing coordinates and dates", i, len(df))
		try:
			entrydate = datetime.datetime.strptime(f"19{row["DATE"]}", "%Y%m%d")
			df.at[i, "ISO date"] = entrydate
		except:
			pass
	savepath = os.path.join(parentdir, 'HES.gpkg')

	print("Saving")
	df.to_file(savepath, layer="SITRA", driver="GPKG")

def main():
	sitraFilterAndEport()

if __name__ == "__main__":
	main()