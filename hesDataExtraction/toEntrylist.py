from datetime import datetime
import os
from os import walk

import pandas as pd

import hamlaDataExtraction
from utils import progress

dirname = os.path.dirname(__file__)

def hamla():
    hesDirectory = os.path.join(dirname, "hamlatextfiles")
    filenames = next(walk(hesDirectory), (None, None, []))[2]
    DataFrames = []
    for i, filename in enumerate(filenames):
        print(f"HAMLA file {i+1} of {len(filenames)}")
        df, name = hamlaDataExtraction.hamla_data_extraction(os.path.join(hesDirectory, filename), False)
        for j, row in df.iterrows():
            df.at[j, "DATE"] = datetime.strptime(f"19{row["DATE"]}", "%Y%m")
            progress("Parsing Dates", j, len(df))
        DataFrames.append(df)
    for i in range(1, len(DataFrames)):
        DataFrames[0] = pd.concat([DataFrames[0], DataFrames[i]])
    DataFrames[0] = DataFrames[0].reset_index(drop=True)
    DataFrames[0].to_csv("hamla.csv")
    return DataFrames[0]

hamla()