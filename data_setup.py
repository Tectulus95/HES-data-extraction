import os
import sys

dirname = os.path.dirname(__file__)
sys.path.append(os.path.join(dirname, 'hesDataExtraction'))
sys.path.append(os.path.join(dirname, 'THOR'))

import hamletTable
import toEntrylist
import downloadThor
import thorFilterAndExport

def main():
    print("Exporting Hamlets to Geopackage")
    df = hamletTable.hamlets_master_from_zip("masterfile")
    hamlet_table = hamletTable.get_hamlet_locations(df)
    hamlet_gdf = hamletTable.to_GeoDataFrame(hamlet_table, True)
    print("Exporting HAMLA and HES data to Geopackage")
    toEntrylist.hamla()
    toEntrylist.hes()
    print("Downloading THOR data")
    downloadThor.download_thor()
    print("Exporting THOR data to Geopackage")
    thorFilterAndExport.thor_to_db()

if __name__ == "__main__":
    main()