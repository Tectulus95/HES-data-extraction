"""The provided methods are designed to turn the tab-seperated HAMLA and HES files provided by the US national
archive at https://catalog.archives.gov/id/4616225 into Geopandas DataFrames with EPSG:4326 encoded coordinates
"""
import os
from os import walk

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

from utils import makedict, toCoord, progress

def hamla_data_extraction(filepath: str, withCoords: bool = True) -> tuple:
    """Extracts data from a hamla text file and turns it into a (geo)pandas dataframe

    Parameters
    ----------
    filepath: str
        Path to the hamla text file
    withCoords: bool
        If True the returned DataFrame will not be transformed into a GeoDataFrame and not contatin
        geographic data and only identify its hamlet by USID

    Returns
    -------
    DataFrame/GeoDataFrame
        (Geo)DataFrame created from the HES data
    str
        Name of the file
    """
    filename = os.path.split(filepath)[1]
    f = open(filepath, "r")
    length = sum(1 for _ in f)
    f.seek(0)
    line = f.readline()
    columns = [word.rstrip() for word in line.split("\t")]
    line = f.readline()
    hamletlist = []
    f.seek(0)
    for i, line in enumerate(f.readlines()):
        if i > 0:
            entries = [word.rstrip() for word in line.split("\t")]
            entries = [word.strip() for word in entries]
            hamletlist.append(makedict(columns, entries))
            progress("Parsing data into DataFrame", i, length)
    f.close()
    hamlet_info = pd.DataFrame(hamletlist)
    hamlet_info["USID"] = pd.Series(dtype='str')
    for i, row in hamlet_info.iterrows():
        USID = row["CHAM"] + row["PHAM"] + row["DHAM"] + row["VHAM"] + row["HHAM"]
        hamlet_info.at[i, "USID"] = USID
        progress(f"USID {USID}", i, len(hamlet_info))
    hamlet_info["POPUL"] = pd.to_numeric(hamlet_info["POPUL"])
    hamlet_info["SECUR"] = pd.to_numeric(hamlet_info["SECUR"])
    hamlet_info["DEVEL"] = pd.to_numeric(hamlet_info["DEVEL"])
    hamlet_info["CLASX"] = pd.to_numeric(hamlet_info["CLASX"])
    hamlet_info["CONFX"] = pd.to_numeric(hamlet_info["CONFX"])
    hamlet_info["VISIT"] = pd.to_numeric(hamlet_info["VISIT"])
    hamlet_info["USID"] = pd.to_numeric(hamlet_info["USID"])
    for column in hamlet_info.columns:
        if column not in ["POPUL", "SECUR", "DEVEL", "CLASX", "CONFX", "VISIT", "USID", "DATE"]:
            hamlet_info[column] = hamlet_info[column].astype("string")
    if not withCoords:
        hamlet_info = hamlet_info.drop(columns=["CHAM", "PHAM", "DHAM", "VHAM", "HHAM", "POINT", " +PCN", " +SC0", "NAME", "XNAME", "VSZ"])
    else:
        hamlet_info = gpd.GeoDataFrame(hamlet_info)
        coords = []
        for i, row in hamlet_info.iterrows():
            coords.append(toCoord(row["POINT"]))
            progress("Converting coordinates", i, len(hamlet_info))
        point_coords =[]
        for i, entry in enumerate(coords):
            if entry is not None:
                point_coords.append(Point(entry[1], entry[0]))
            else: point_coords.append(None)
            progress("Inverting coordinates", i, len(coords))
        
        s = gpd.GeoSeries(point_coords, crs="EPSG:4326")
        hamlet_info["coords"] = s
        hamlet_info = hamlet_info.set_geometry("coords")
    return(hamlet_info, filename)

def hes_70_71_data_extraction(directory: str, withCoords: bool = True) -> tuple:
    """Extracts data from a HES 70 text file and turns it into a (geo)pandas dataframe

    Parameters
    ----------
    directory: str
        Path to the HES text files per year
    withCoords: bool
        If True the returned DataFrame will not be transformed into a GeoDataFrame and not contatin
        geographic data and only identify its hamlet or village by USID

    Returns
    -------
    DataFrame/GeoDataFrame
        (Geo)DataFrame created from the HES hamlet data
    DataFrame/GeoDataFrame
        (Geo)DataFrame created from the HES village data
    str
        Name of the file
    """
    pdlist = []
    filenames = next(walk(directory), (None, None, []))[2]
    filenames = sorted(filenames)
    name = os.path.split(directory)[1]
    for i, filename in enumerate(filenames):
        print(f"File {i+1} of {len(filenames)}: {filename}")
        filepath = os.path.join(directory,filename)
        f = open(filepath, "r")
        length = sum(1 for _ in f)
        f.seek(0)
        line = f.readline()
        columns = [word.rstrip() for word in line.split("\t")]
        line = f.readline()
        hamletlist = []
        f.seek(0)
        for j, line in enumerate(f.readlines()):
            if j > 0:
                entries = [word.rstrip() for word in line.split("\t")]
                entries = [word.strip() for word in entries]
                hamletlist.append(makedict(columns, entries))
                progress("Parsing data into DataFrame", j, length)
        f.close()
        pdlist.append(pd.DataFrame(hamletlist))
        pdlist[i]["entryid"] = pd.Series(dtype='str')
        pdlist[i]["USID"] = pd.Series(dtype='str')
        for j, row in pdlist[i].iterrows():
            USID = row["CORPS"] + row["PROV"] + row["DIST"] + row["VILG"] + row["HAM"]
            entryid = USID + row.iloc[6]
            pdlist[i].at[j, "USID"] = USID
            pdlist[i].at[j, "entryid"] = entryid
            progress("Writing IDs", j, len(pdlist[i]))
        if i > 1:
            pdlist[i] = pdlist[i].drop(columns=["CORPS", "PROV", "DIST", "VILG", "HAM", " +PCN"])
    outputframehamlets = pdlist[0]
    outputframevillages = pdlist[1]
    print("Merging dataframes")
    for i in range(2, len(pdlist)):
        outputframehamlets = pd.merge(outputframehamlets, pdlist[i], on="entryid", how='left')
        outputframevillages = pd.merge(outputframevillages, pdlist[i], on="entryid", how='left')
    outputframehamlets["HPOPUL"] = pd.to_numeric(outputframehamlets["HPOPUL"])
    outputframehamlets["HPERM"] = pd.to_numeric(outputframehamlets["HPERM"])
    outputframehamlets["HTEMP"] = pd.to_numeric(outputframehamlets["HTEMP"])
    outputframevillages["VNHPOP"] = pd.to_numeric(outputframevillages["VNHPOP"])
    outputframevillages["VHPOP"] = pd.to_numeric(outputframevillages["VHPOP"])
    outputframevillages["VPERM"] = pd.to_numeric(outputframevillages["VPERM"])
    outputframevillages["VTEMP"] = pd.to_numeric(outputframevillages["VTEMP"])
    outputframevillages["VTPOP"] = pd.to_numeric(outputframevillages["VTPOP"])
    outputframevillages["VHCNT"] = pd.to_numeric(outputframevillages["VHCNT"])
    for column in outputframehamlets.columns:
        if column not in ["HPOPUL", "HPERM", "HTEMP", "USID"]:
            outputframehamlets[column] = outputframehamlets[column].astype("string")
    for column in outputframevillages.columns:
        if column not in ["VNHPOP", "VHPOP", "VPERM", "VTEMP", "VTPOP", "VHCNT", "USID"]:
            outputframevillages[column] = outputframevillages[column].astype("string")

    if not withCoords:
        outputframehamlets = outputframehamlets.drop(columns=["CORPS", "PROV", "DIST", "VILG", "HAM", " +PCN", "HPOINT", "entryid"])
        outputframevillages = outputframevillages.drop(columns=["CORPS", "PROV", "DIST", "VILG", "HAM", " +PCN", "VPOINT", "entryid"])
    
    else:
        outputframehamlets = gpd.GeoDataFrame(outputframehamlets)
        hcoords = []
        for i, row in outputframehamlets.iterrows():
            hcoords.append(toCoord(row["HPOINT"]))
            progress("Converting coordinates", i, len(outputframehamlets))
        h_point_coords =[]
        for i, entry in enumerate(hcoords):
            if entry is not None:
                h_point_coords.append(Point(entry[1], entry[0]))
            else: h_point_coords.append(None)
            progress("Inverting coordinates", i, len(hcoords))
        
        s1 = gpd.GeoSeries(h_point_coords, crs="EPSG:4326")
        outputframehamlets["coords"] = s1
        outputframehamlets = outputframehamlets.set_geometry("coords")

        outputframevillages = gpd.GeoDataFrame(outputframevillages)
        vcoords = []
        for i, row in outputframevillages.iterrows():
            vcoords.append(toCoord(row["VPOINT"]))
            progress("Converting coordinates", i, len(outputframevillages))
        v_point_coords =[]
        for i, entry in enumerate(vcoords):
            if entry is not None:
                v_point_coords.append(Point(entry[1], entry[0]))
            else: v_point_coords.append(None)
            progress("Inverting coordinates", i, len(vcoords))
        
        s2 = gpd.GeoSeries(v_point_coords, crs="EPSG:4326")
        outputframevillages["coords"] = s1
        outputframevillages = outputframevillages.set_geometry("coords")

    return outputframehamlets, outputframevillages, name