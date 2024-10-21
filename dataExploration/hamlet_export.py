import os
from datetime import datetime
import sqlite3

import geopandas as gpd
import pandas as pd

dirname = os.path.dirname(__file__)

con = sqlite3.connect("hes_data.db")

hamlets = gpd.read_file("hamlets_shp/hamlets.shp")
hamla = pd.read_sql("SELECT * from hamla", con, index_col="index", parse_dates=["DATE"])
hamla["USID"] = pd.to_numeric(hamla["USID"])
#hes = read_df_with_dtypes(os.path.join(dirname, "hes_data/hes_ham.csv"))
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
    else:
        df = pd.merge(right=hamla[hamla["DATE"].isin(daterange)], left=hamlets, on="USID", how="right")
        df["DATE"] = df["DATE"].astype("string")
        df = gpd.GeoDataFrame(df)
    return df
