# HES data extraction

## Introduction

The US national archives [collection of Vietnam War electronic data files](https://www.archives.gov/research/military/vietnam-war/electronic-data-files) provides a huge number of electronic resources dating back to the 1960s and 1970s.

In the context of my bachelor's thesis the goal of this repository is to document my approach in extracting and transforming the data into a format that is easily usable with modern tools and lay the foundation for enabling a data driven approach to research the US war in Vietnam.

## Geopandas DataFrames from tab-separated text files

As a first step I have transformed the HAMLA and HES files provided [by the national archive](https://catalog.archives.gov/id/4616225) into Geopandas DataFrames with EPSG:4326 encoded coordinates. Through the "toShapefile.py" script it's possible to save them as Shapefiles for further use in GIS software.

## Hamlets as entities

The approach of simply turning the provided data into DataFrames without further work introduces several problems. Firstly the provided tables contain massive redundancies in the information identifying hamlets. Every entry reproduces the hamlet ID, location and, for the HAMLA datasets, name. Furthermore, due to presumed errors in inputting the data, some locations and hamlet names are inconsistent.

Additionally, the data differences between the HAMLA and HES70/71 tables complicate a direct comparison between them.

In order to have relatively consistent hamlet level data over time (at least in the columns that can be compared between versions) I have decided to implement a relational model that maps datapoints onto hamlet entities.