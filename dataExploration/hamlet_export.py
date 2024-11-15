"""Provides the data handling methods for the flask server.
"""
from lib2to3.pgen2 import driver
import os
from datetime import date, datetime, timedelta
import sqlite3

import geopandas as gpd
import pandas as pd

dirname = os.path.dirname(__file__)
parentdir = "".join(dirname.split()[0:-1])
loadpath = os.path.join(parentdir, 'HES.gpkg')

con = sqlite3.connect(loadpath)

print("Loading Hamlet GeoData")

hamlets = gpd.read_file(loadpath, layer='Hamlets')
print("Loading HAMLA data")
start = datetime.now()
hamla = pd.DataFrame(gpd.read_file(loadpath, layer='HAMLA'))
end = datetime.now()
print(f"Time elapsed: {end-start}")
print("Loading HES data")
start = datetime.now()
hes = pd.DataFrame(gpd.read_file(loadpath, layer='HES_hamlets'))
hes["USID"] = pd.to_numeric(hes["USID_y"])
end = datetime.now()
print(f"Time elapsed: {end-start}")
print("Loading THOR data")
start = datetime.now()
thor = gpd.read_file(loadpath, layer='THOR')
end = datetime.now()
print(f"Time elapsed: {end-start}")

#print(hamla.dtypes)

#qdate = datetime.strptime("1968/05", "%Y/%m")
qdate = pd.date_range("1-1-1968", periods=1, freq="MS")

#df = pd.merge(right=hamla[hamla["DATE"].isin(qdate)], left=hamlets, on="USID", how="right")

def dynamic_gdf_hamlets(daterange = None):
    if daterange is None:
        df = pd.merge(right=hamla, left=hamlets, on="USID", how="right")
        df["DATE"] = df["DATE"].astype("string")
        df = gpd.GeoDataFrame(df)
    elif daterange[-1] < datetime.strptime("07/1969", "%m/%Y"):
        df = pd.merge(right=hamla[hamla["DATE"].isin(daterange)], left=hamlets, on="USID", how="right")
        df["DATE"] = df["DATE"].astype("string")
        df = df[["Hamlet Name", "USID", "POPUL", "SCSTA", "geometry"]]
        df = gpd.GeoDataFrame(df)
    else:
        df = pd.merge(right=hes[hes["DATE"].isin(daterange)], left=hamlets, on="USID", how="right")
        df["DATE"] = df["DATE"].astype("string")
        df = df[["Hamlet Name", "USID", "HPOPUL", "HCAT", "geometry"]]
        df = gpd.GeoDataFrame(df)
    return df

def dynamic_gdf_thor(daterange = None):
    if daterange is None:
        df = thor
        df = gpd.GeoDataFrame(df)
    else:
        df = thor[(thor["MSNDATE"] >= daterange[0]) & (thor["MSNDATE"] < (daterange[0] + timedelta(days=32)).replace(day=1))]
        df = gpd.GeoDataFrame(df)
    df["MSNDATE"] = df["MSNDATE"].astype("string")
    return df

def hamlet_history(usid):
    usid = int(usid)
    hamladf = pd.merge(left=hamlets[hamlets["USID"]==usid], right=hamla, on="USID", how="left")
    hesdf = pd.merge(left=hamlets[hamlets["USID"]==usid], right=hes, on="USID", how="left")
    return hamladf, hesdf

def main():
    d = datetime.strptime("021968", "%m%Y")
    qdate = pd.date_range(d, periods=1, freq="MS")
    df = dynamic_gdf_thor(qdate)
    print(df.head())

if __name__ == "__main__":
    main()
