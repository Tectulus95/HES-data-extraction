from datetime import datetime
import os
from os import walk
#import sqlite3

import pandas as pd
import geopandas as gpd

import hesDataExtraction
from utils import progress

dirname = os.path.dirname(__file__)
parentdir = "".join(dirname.split()[0:-1])

#con = sqlite3.connect("hes_data.db")
savepath = os.path.join(parentdir, 'HES.gpkg')

def hamla():
    hesDirectory = os.path.join(dirname, "hamlatextfiles")
    filenames = next(walk(hesDirectory), (None, None, []))[2]
    DataFrames = []
    for i, filename in enumerate(filenames):
        print(f"HAMLA file {i+1} of {len(filenames)}")
        df, name = hesDataExtraction.hamla_data_extraction(os.path.join(hesDirectory, filename), False)
        for j, row in df.iterrows():
            df.at[j, "DATE"] = datetime.strptime(f"19{row["DATE"]}", "%Y%m")
            progress("Parsing Dates", j, len(df))
        df["DATE"] = pd.to_datetime(df["DATE"])
        DataFrames.append(df)
    for i in range(1, len(DataFrames)):
        DataFrames[0] = pd.concat([DataFrames[0], DataFrames[i]])
    DataFrames[0] = DataFrames[0].reset_index(drop=True)
    #DataFrames[0].to_sql("hamla", con, if_exists='replace')
    gpd.GeoDataFrame(DataFrames[0]).to_file(savepath, layer="HAMLA", driver="GPKG")
    return DataFrames[0]

def hes():
    hesDirectory = os.path.join(dirname, "hestextfiles")
    directories = next(walk(hesDirectory), (None, [], None))[1]
    HDataFrames = []
    VDataFrames = []
    for i, directory in enumerate(directories):
        print(f"HES directory {i+1} of {len(directories)}")
        hamdf, vildf, name = hesDataExtraction.hes_70_71_data_extraction(os.path.join(hesDirectory, directory), False)
        for j, row in hamdf.iterrows():
            hamdf.at[j, "DATE"] = datetime.strptime(f"19{row["HDATE"]}", "%Y%m")
            progress("Parsing Dates Hamlets", j, len(hamdf))
        HDataFrames.append(hamdf)
        for j, row in vildf.iterrows():
            vildf.at[j, "DATE"] = datetime.strptime(f"19{row["VDATE"]}", "%Y%m")
            progress("Parsing Dates Villages", j, len(vildf))
        VDataFrames.append(vildf)
    for i in range(1, len(HDataFrames)):
        HDataFrames[0] = pd.concat([HDataFrames[0], HDataFrames[i]])
    for i in range(1, len(VDataFrames)):
        VDataFrames[0] = pd.concat([VDataFrames[0], VDataFrames[i]])
    HDataFrames[0] = HDataFrames[0].reset_index(drop=True)
    HDataFrames[0].dropna(how='all', axis=1, inplace=True)
    #HDataFrames[0].to_sql("hes_ham", con, if_exists='replace')
    gpd.GeoDataFrame(HDataFrames[0]).to_file(savepath, layer="HES_hamlets", driver="GPKG")
    VDataFrames[0] = VDataFrames[0].reset_index(drop=True)
    VDataFrames[0].dropna(how='all', axis=1, inplace=True)
    #VDataFrames[0].to_sql("hes_vil", con, if_exists='replace')
    gpd.GeoDataFrame(VDataFrames[0]).to_file(savepath, layer="HES_villages", driver="GPKG")
    return HDataFrames[0], VDataFrames[0]

def main():
    hamla()
    hes()

if __name__ == "__main__":
    main()