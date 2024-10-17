import os
from zipfile import ZipFile

import pandas as pd
from pandas import DataFrame
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point

from utils import makedict, toCoord, progress

dirname = os.path.dirname(__file__)

def get_most_common(df: DataFrame, USID: str, columns: list[str]) -> dict:
    """Finds the most common entry in the indicated columns for a given hamlet

    Parameters
    ----------
    df: DataFrame
        Result of hamlets_master_from_zip
    USID: str
        USID of the requested hamlet
    columns: list[str]
        List of columns to be included

    Returns
    -------
    dict
    """
    hamlet = df.loc[df['USID']==USID]
    return_dict = {}
    return_dict["USID"] = USID
    for column in columns:
        value =  hamlet[column].value_counts()
        most_common = ''
        if value.size > 1:
            i = 0
            while i < value.size:
                x = value.index.get_level_values(0)[i]
                if "000000" not in x and x != '':
                    most_common = x
                    break
                else:
                    i += 1
        else:
            most_common = value.index.get_level_values(0)[0]
        return_dict[column] = most_common
    return return_dict

def hamlets_master_from_zip(rel_path: str, save: bool = False) -> DataFrame:
    """Turn the B6 table of the master file into a DataFrame

    Parameters
    ----------
    rel_path: str
        Relative path to the folder containing the master zip file
    save: bool
        Save resulting DataFrame as .csv file

    Returns
    -------
    DataFrame
    """
    with ZipFile(os.path.join(dirname, rel_path, "HES_Individual_Tables.zip")) as masterfile:
        with masterfile.open("HES_table_B-06.txt", "r") as hamlets_descriptive:
            length = sum(1 for _ in hamlets_descriptive)
            hamlets_descriptive.seek(0)
            columns = hamlets_descriptive.readline().decode().strip("\n").split("|")
            hamletlist = []
            for i, line in enumerate(hamlets_descriptive.readlines()):
                try:
                    entries = [word.rstrip() for word in line.decode().strip("\n").split("|")]
                    entries = [word.strip() for word in entries]
                    hamletlist.append(makedict(columns, entries))
                except:
                    pass
                progress("Parsing data into DataFrame", i, length-1)
            hamlet_info = pd.DataFrame(hamletlist)
            if save:
                hamlet_info.to_csv(os.path.join(dirname, rel_path, "hamlets_master.csv"))
    return hamlet_info

def get_hamlet_locations(hamlet_info: DataFrame, save: bool = False, rel_path: str = None) -> DataFrame:
    """Create DataFrame of the most common entries for hamlets

    Parameters
    ----------
    hamlet_info: DataFrame
        Input DataFrame of hamlet master file data
    save: bool
        Save resulting DataFrame as .csv file
    rel_path: str
        Relative path to the desired output folder if save is set to true

    Returns
    -------
    DataFrame
    """
    USIDs = hamlet_info.USID.drop_duplicates().reset_index(drop=True)
    print(USIDs.head())
    print(USIDs.size)
    hamlet_dict_list = []
    for i in range(USIDs.size):
        USID = USIDs.iloc[i]
        hamlet_dict = get_most_common(hamlet_info, USID, ["Hamlet Name", "UTM Coordinates", "GVN Serial Number"])
        hamlet_dict_list.append(hamlet_dict)
        progress("Extracting Hamlet Information", i, USIDs.size)

    df = pd.DataFrame(hamlet_dict_list)
    if save:
        df.to_csv(os.path.join(dirname, rel_path, "hamlet_table.csv"))
    return df

def to_GeoDataFrame(hamlet_info: DataFrame, save: bool = False) -> GeoDataFrame:
    """Add EPSG:4326 coordinates from the mgrs coordinates and return a GeoDataFrame

    Parameters
    ----------
    hamlet_info: DataFrame
        Input DataFrame of hamlets
    save: bool
        Save resulting DataFrame as .csv file

    Returns
    -------
    DataFrame
    """
    hamlet_info = gpd.GeoDataFrame(hamlet_info)
    coords = []
    for i, row in hamlet_info.iterrows():
        coords.append(toCoord(row["UTM Coordinates"]))
        progress("Converting coordinates", i, len(hamlet_info))
    point_coords = []
    for i, entry in enumerate(coords):
        if entry is not None:
            point_coords.append(Point(entry[1], entry[0]))
        else:
            point_coords.append(None)
        progress("Inverting coordinates", i, len(coords))

    s = gpd.GeoSeries(point_coords, crs="EPSG:4326")
    hamlet_info["coords"] = s
    hamlet_info = hamlet_info.set_geometry("coords")
    if save:
        if not os.path.isdir("hamlets_shp"):
            os.mkdir("hamlets_shp")
        hamlet_info.to_file("hamlets_shp/hamlets.shp")
    return (hamlet_info)

def main():
    df = hamlets_master_from_zip("masterfile", True)
    hamlet_table = get_hamlet_locations(df, True, "masterfile")
    hamlet_gdf = to_GeoDataFrame(hamlet_table, True)

if __name__ == "__main__":
    main()