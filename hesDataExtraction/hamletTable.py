import os
from zipfile import ZipFile

import pandas as pd
import geopandas as gpd
from pandas import DataFrame

from utils import makedict, toCoord, progress

dirname = os.path.dirname(__file__)

def get_most_common(df: DataFrame, USID: str, column: str) -> str:
    hamlet = df.loc[df['USID']==USID]
    coords =  hamlet['UTM Coordinates'].value_counts()
    if coords.size > 1:
        print(hamlet["Hamlet Name"].iloc[0], USID, coords.index.get_level_values(0))

with ZipFile(os.path.join(dirname, "masterfile/HES_Individual_Tables.zip")) as masterfile:
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
#        hamlet_info.to_csv("hamlets_master.csv")

USIDs = hamlet_info.USID.drop_duplicates()
for i, USID in USIDs.items():
    get_most_common(hamlet_info, USID, "UTM Coordinates")
