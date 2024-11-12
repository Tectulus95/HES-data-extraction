# HES data extraction

## Introduction

The US national archives [collection of Vietnam War electronic data files](https://www.archives.gov/research/military/vietnam-war/electronic-data-files) provides a huge number of electronic resources dating back to the 1960s and 1970s.

In the context of my bachelor's thesis the goal of this repository is to document my approach in extracting and transforming the data into a format that is easily usable with modern tools and lay the foundation for enabling a data driven approach to research the US war in Vietnam.

### Geopandas DataFrames from tab-separated text files

As a first step I have transformed the HAMLA and HES files provided [by the national archive](https://catalog.archives.gov/id/4616225) into Geopandas DataFrames with EPSG:4326 encoded coordinates. Through the "toShapefile.py" script it's possible to save them as Shapefiles for further use in GIS software.

### Hamlets as entities

The approach of simply turning the provided data into DataFrames without further work introduces several problems. Firstly the provided tables contain massive redundancies in the information identifying hamlets. Every entry reproduces the hamlet ID, location and, for the HAMLA datasets, name. Furthermore, due to presumed errors in inputting the data, some locations and hamlet names are inconsistent.

Additionally, the data differences between the HAMLA and HES70/71 tables complicate a direct comparison between them.

In order to have relatively consistent hamlet level data over time (at least in the columns that can be compared between versions) I have decided to implement a relational model that maps datapoints onto hamlet entities.

## Requirements

**Python 3.11**

- `geopandas 1.0.1`
- `mgrs 1.5.0`
- `pandas 2.2.3`

## Directory strucure

`hesDataExtraction/hamlatextfiles`\
Provides the tab separated HAMLA files which were in use from 1967 to mid-1969.

`hesDataExtraction/hestextfiles`\
Provides the tab separated HES files which were in use from mid-1969 to early 1974. The files are split into periodical sets which are grouped in directories named after the operative timeframe.

`hesDataExtraction/masterfile`\
Holds the HES masterfile separated out into its constituent tables. Table 6 is used to extract the hamlet reference data and position.

`hesDataExtraction/hamlets_shp`\
ESRI shapefile of the hamlet reference data extracted from the masterfile.

`dataExploration`\
Provides the Flask application for interactively exploring the data.

## Scripts

`hesDataExtraction/hesDataExtraction.py`\
Provides the methods for extracting the data from HES and HAMLA text files and turning them into Pandas DataFrames.

`hesDataExtraction/hamletTable.py`\
Provides the methods to extract the hamlet data from the masterfile, find the most common coordinates for each hamlet and turn the data into a DataFrame or GeoDataFrame with one entry per hamlet.

`hesDataExtraction/toShapefile.py`\
Uses the methods provided by hesDataExtraction to save HES and HAMLA data as ESRI shapefiles.

`hesDataExtraction/toShapefile.py`\
Uses the methods provided by hesDataExtraction to write the HES and HAMLA data into a SQLite database for use with the reference data shapefile.

`hesDataExtraction/utils`\
Provides a number of common utility methods.

## Files not provided in this repository

I have provided as many output files as possible with this repository, however due to the gitHub file size limit I was unable to upload the following files:

- `hesshapefiles`
- `hes_data.db` 

Both can be created by the `toShapefile.py` and `toEntrylist.py` respectively. All required files are provided in this repository.

**Note:** The hesshapefiles directory has a size of ca. 7.6GB.

# How to get it running

1. Install the dependencies from requirements.txt
1. Run hamletTable.py to generate the shapefile containing the hamlet information
1. Run toEntrylist.py to generate the database of HAMLA and HES entries
1. Run InteractiveGeoDataExplorer.py and open the indicated url in your browser

This repository is still under development.
