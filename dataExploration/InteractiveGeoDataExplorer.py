""" Runs the flask server for interacting with the data in the browser.

    Run this file and then head to http://127.0.0.1:5000 in your browser to see the map displayed

"""
from datetime import datetime
from json import dumps
import os

from flask import Flask, make_response, render_template_string, render_template
import geopandas as gpd
import pandas as pd
from plotly import utils
import plotly.express as px
import umsgpack

import hamlet_export

dirname = os.path.dirname(__file__)

def load_and_filter_shp(filename, column, value):
    gdf = gpd.read_file(filename)
    output = gdf.loc[gdf[column]==value]
    return output

app = Flask(__name__)

@app.route('/get_geojson/<dString>')
def get_geojson(dString):
    d = datetime.strptime(dString, "%m%Y")
    qdate = pd.date_range(d, periods=1, freq="MS")
    gdf = hamlet_export.dynamic_gdf_hamlets(qdate)
    return gdf.to_json()

@app.route('/get_thor/<dString>')
def get_thor(dString):
    d = datetime.strptime(dString, "%m%Y")
    qdate = pd.date_range(d, periods=1, freq="MS")
    gdf = hamlet_export.dynamic_gdf_thor(qdate)
    data = []
    for i, row in gdf.iterrows():
        data.append({"lat": row["TGTLATDD_DDD_WGS84"], "lon": row["TGTLONDDD_DDD_WGS84"], "wgt": row["WEAPONTYPEWEIGHT"]})
    thorDict = {"max": 2000, "data": data}
    response = make_response((umsgpack.packb(thorDict), {'content-type': 'application/octet-stream'}))
    return response

@app.route('/')
def js_map():
    hamlets = get_geojson("011967")
    return render_template("map_template.html", hamlets=hamlets, dirname=dirname)

@app.route('/heatmap.min.js')
def heatmap():
    f = open(os.path.join(dirname, 'templates/heatmap.js-2.0.5/build/heatmap.min.js'))
    heatmap = f.read()
    f.close()
    response = make_response((heatmap, {'content-type': 'text/javascript; charset=utf-8'}))
    return response

@app.route('/leaflet-heatmap.js')
def leaflet_heatmap():
    f = open(os.path.join(dirname, 'templates/leaflet-heatmap.js'))
    heatmap = f.read()
    f.close()
    response = make_response((heatmap, {'content-type': 'text/javascript; charset=utf-8'}))
    return response

@app.route('/msgpack.min.js')
def msgpack():
    f = open(os.path.join(dirname, 'templates/msgpack.js-master/msgpack.min.js'))
    msgpack = f.read()
    f.close()
    response = make_response((msgpack, {'content-type': 'text/javascript; charset=utf-8'}))
    return response

@app.route("/usid/<usid>")
def hamlet_data(usid):
    hamladf, hesdf = hamlet_export.hamlet_history(usid)
    print(hamladf.head())
    name = hamladf["Hamlet Name"].iloc[0]
    #p = figure(x_axis_type="datetime", width=600, height=400)
    fig1 = px.line(hamladf, x='DATE', y='CLASX')
    fig1_json = dumps(fig1, cls=utils.PlotlyJSONEncoder)
    fig2 = px.line(hamladf, x='DATE', y='POPUL')
    fig2_json = dumps(fig2, cls=utils.PlotlyJSONEncoder)
    #print(fig1_json)
    return render_template(
        "dashboard_template.html",
        fig1_json = fig1_json,
        fig2_json = fig2_json,
        name = name)

if __name__ == "__main__":
    app.run(debug=True)
