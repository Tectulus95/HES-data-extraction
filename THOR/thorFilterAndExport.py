import os
import sys
dirname = os.path.dirname(__file__)
parentdir = "".join(dirname.split()[0:-1])
sys.path.append(os.path.join(parentdir, 'hesDataExtraction'))

import geopandas as gpd
from numpy import datetime64, float32, int32, str_
import pandas as pd
from shapely.geometry import Point

from utils import progress

def thor_to_db():
	print("Loading csv")
	dtypedict = {
		"THOR_DATA_VIET_ID": int32,
		"COUNTRYFLYINGMISSION": str_,
		"MILSERVICE": str_,
		"SOURCEID": int32,
		"SOURCERECORD": str_,
		"VALID_AIRCRAFT_ROOT": str_,
		"TAKEOFFLOCATION": str_,
		"TGTLATDD_DDD_WGS84": float32,
		"TGTLONDDD_DDD_WGS84": float32,
		"TGTTYPE": str_,
		"NUMWEAPONSDELIVERED": int32,
		"TIMEONTARGET": float32,
		"WEAPONTYPE": str_,
		"WEAPONTYPECLASS": str_,
		"WEAPONTYPEWEIGHT": int32,
		"AIRCRAFT_ORIGINAL": str_,
		"AIRCRAFT_ROOT": str_,
		"AIRFORCEGROUP": str_,
		"AIRFORCESQDN": str_,
		"CALLSIGN": str_,
		"FLTHOURS": int32,
		"MFUNC": str_,
		"MFUNC_DESC": str_,
		"MISSIONID": str_,
		"NUMOFACFT": int32,
		"OPERATIONSUPPORTED": str_,
		"PERIODOFDAY": str_,
		"UNIT": str_,
		"TGTCLOUDCOVER": str_,
		"TGTCONTROL": str_,
		"TGTCOUNTRY": str_,
		"TGTID": str_,
		"TGTORIGCOORDS": str_,
		"TGTORIGCOORDSFORMAT": str_,
		"TGTWEATHER": str_,
		"ADDITIONALINFO": str_,
		"GEOZONE": str_,
		"ID": int32,
		"MFUNC_DESC_CLASS": str_,
		"NUMWEAPONSJETTISONED": int32,
		"NUMWEAPONSRETURNED": int32,
		"RELEASEALTITUDE": float32,
		"RELEASEFLTSPEED": float32,
		"RESULTSBDA": str_,
		"TIMEOFFTARGET": float32,
		"WEAPONSLOADEDWEIGHT": int32
		}
	thor = pd.read_csv(os.path.join(dirname, 'thor_data_vietnam.csv'), dtype=dtypedict, parse_dates=["MSNDATE"])
	print("Filtering DataFrame")

	thorRel = thor[(thor["TGTCOUNTRY"] == "SOUTH VIETNAM") & (thor["NUMWEAPONSDELIVERED"] > 0) & (thor["WEAPONTYPEWEIGHT"] > 0)].dropna(subset="TGTLATDD_DDD_WGS84")
	thorRel["MSNDATE"] = pd.to_datetime(thorRel["MSNDATE"], format='ISO8601')
	thorRel["geometry"] = gpd.GeoSeries(crs="EPSG:4326")
	thorRel = gpd.GeoDataFrame(thorRel, geometry='geometry')
	j = 0
	for i, row in thorRel.iterrows():
		point = Point(row["TGTLONDDD_DDD_WGS84"], row["TGTLATDD_DDD_WGS84"])
		thorRel.at[i, "geometry"] = point
		j += 1
		progress("Writing coords", j, len(thorRel))
	print("Writing to Geopackage file")
	savepath = os.path.join(parentdir, 'HES.gpkg')
	thorRel.to_file(savepath, driver='GPKG', layer='THOR')

def main():
	thor_to_db()

if __name__ == "__main__":
    main()
