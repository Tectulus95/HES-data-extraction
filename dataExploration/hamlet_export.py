"""Provides the data handling methods for the flask server.
"""
import os
from datetime import datetime
import sqlite3

import geopandas as gpd
import pandas as pd

dirname = os.path.dirname(__file__)

con = sqlite3.connect("hes_data.db")

print("Loading Hamlet GeoData")

hamlets = gpd.read_file("hamlets_shp/hamlets.shp")
print("Loading HAMLA data")
hamla = pd.read_sql("SELECT * from hamla", con, index_col="index", parse_dates=["DATE"])
hamla["USID"] = pd.to_numeric(hamla["USID"])
print("Loading HES data")
hes = pd.read_sql("SELECT * from hes_ham", con, index_col="index", parse_dates=["DATE"])
hes["USID"] = pd.to_numeric(hes["USID_y"])
#hes["DATE"] = pd.to_datetime(hes["DATE"])

#print(hamla.dtypes)

#qdate = datetime.strptime("1968/05", "%Y/%m")
qdate = pd.date_range("1-1-1968", periods=1, freq="MS")

#df = pd.merge(right=hamla[hamla["DATE"].isin(qdate)], left=hamlets, on="USID", how="right")

def dynamic_gdf(daterange = None):
    if daterange is None:
        df = pd.merge(right=hamla, left=hamlets, on="USID", how="right")
        df["DATE"] = df["DATE"].astype("string")
        df = gpd.GeoDataFrame(df)
    elif daterange[-1] < datetime.strptime("07/1969", "%m/%Y"):
        df = pd.merge(right=hamla[hamla["DATE"].isin(daterange)], left=hamlets, on="USID", how="right")
        df["DATE"] = df["DATE"].astype("string")
        df = gpd.GeoDataFrame(df)
    else:
        df = pd.merge(right=hes[hes["DATE"].isin(daterange)], left=hamlets, on="USID", how="right")
        df["DATE"] = df["DATE"].astype("string")
        df = gpd.GeoDataFrame(df)
    return df

def hamlet_history(usid):
    usid = int(usid)
    hamladf = pd.merge(left=hamlets[hamlets["USID"]==usid], right=hamla, on="USID", how="left")
    hesdf = pd.merge(left=hamlets[hamlets["USID"]==usid], right=hes, on="USID", how="left")
    return hamladf, hesdf
