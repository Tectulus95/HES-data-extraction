from os import walk

import hamlaDataExtraction

def hamla():
    hesDirectory = "hamlatextfiles\\"
    filenames = next(walk(hesDirectory), (None, None, []))[2]
    for i, filename in enumerate(filenames):
        print(f"File {i+1} of {len(filenames)}")
        df, name = hamlaDataExtraction.hamla_data_extraction(hesDirectory + filename)
        name = "hesshapefiles\\" + name.rstrip(".txt") + ".shp"
        df.to_file(name)

def hes():
    hesDirectory = "C:hestextfiles\\"
    directories = next(walk(hesDirectory), (None, [], None))[1]
    for i, directory in enumerate(directories):
        print(f"Directory {i+1} of {len(directories)}")
        hamdf, vildf, name = hamlaDataExtraction.hes_70_71_data_extraction(f"{hesDirectory}{directory}\\")
        hamdf.to_file(f"hesshapefiles\\hes_hamlets{name}.shp")
        vildf.to_file(f"hesshapefiles\\hes_villages{name}.shp")

hamla()
hes()