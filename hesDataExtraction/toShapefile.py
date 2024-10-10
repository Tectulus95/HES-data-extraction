import os
from os import walk

import hamlaDataExtraction

dirname = os.path.dirname(__file__)

def hamla():
    hesDirectory = os.path.join(dirname, "hamlatextfiles")
    filenames = next(walk(hesDirectory), (None, None, []))[2]
    for i, filename in enumerate(filenames):
        print(f"HAMLA file {i+1} of {len(filenames)}")
        df, name = hamlaDataExtraction.hamla_data_extraction(hesDirectory + filename)
        name = os.path.join(dirname, "hesshapefiles", name.rstrip(".txt") + ".shp")
        df.to_file(name)

def hes():
    hesDirectory = os.path.join(dirname, "hestextfiles")
    directories = next(walk(hesDirectory), (None, [], None))[1]
    for i, directory in enumerate(directories):
        print(f"HES directory {i+1} of {len(directories)}")
        hamdf, vildf, name = hamlaDataExtraction.hes_70_71_data_extraction(os.path.join(hesDirectory, directory))
        hamdf.to_file(os.path.join(dirname, f"hesshapefiles/hes_hamlets{name}.shp"))
        vildf.to_file(os.path.join(dirname, f"hesshapefiles/hes_villages{name}.shp"))

hamla()
hes()