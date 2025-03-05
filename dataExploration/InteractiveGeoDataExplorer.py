""" Runs the flask server for interacting with the data in the browser.

    Run this file and then head to http://127.0.0.1:5000 in your browser to see the map displayed

"""
from datetime import datetime
from json import dumps
import os

from flask import Flask, make_response, render_template_string, render_template, request
import geopandas as gpd
from numpy._core.defchararray import isdecimal
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

@app.route('/')
def landing_page():
    return render_template("index.html")

@app.route('/get_geojson/<dString>')
def get_geojson(dString):
    d = datetime.strptime(dString, "%m%Y")
    qdate = pd.date_range(d, periods=1, freq="MS")
    gdf = hamlet_export.dynamic_gdf_hamlets(qdate)
    hesDict = gdf.to_geo_dict()
    response = make_response((umsgpack.packb(hesDict), {'content-type': 'application/octet-stream'}))
    return response

@app.route('/get_thor/<dString>')
def get_thor(dString):
    d = datetime.strptime(dString, "%m%Y")
    qdate = pd.date_range(d, periods=2, freq="MS")
    gdf = hamlet_export.dynamic_gdf_thor(qdate)
    data = []
    for i, row in gdf.iterrows():
        totalWeight = row["WEAPONTYPEWEIGHT"] * row["NUMWEAPONSDELIVERED"]
        data.append({"lat": row["TGTLATDD_DDD_WGS84"], "lon": row["TGTLONDDD_DDD_WGS84"], "wgt": row["WEAPONTYPEWEIGHT"], "total_weight": totalWeight})
    thorDict = {"data": data}
    response = make_response((umsgpack.packb(thorDict), {'content-type': 'application/octet-stream'}))
    return response

@app.route('/get_sitra/<dString>')
def get_sitra(dString):
    d = datetime.strptime(dString, "%m%Y")
    qdate = pd.date_range(d, periods=2, freq="MS")
    gdf = hamlet_export.dynamic_gdf_sitra(qdate)
    sitraDict = gdf.to_geo_dict()
    response = make_response((umsgpack.packb(sitraDict), {'content-type': 'application/octet-stream'}))
    return response

@app.route('/map', methods=['GET','POST'])
def js_map():
    #hamlets = get_geojson("011967")
    if request.method == 'POST':
        content = request.form
        return render_template("map_template.html", dirname=dirname, x=float(content['x']), y=float(content['y']), level = 14)
    else:
        return render_template("map_template.html", dirname=dirname, x=106, y=13, level = 7)

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
    name = hamladf["Hamlet Name"].iloc[0]
    location = hamlet_export.hamlet_location(usid)
    #p = figure(x_axis_type="datetime", width=600, height=400)
    fig1 = px.bar(hamladf, x='DATE', y='CLASX', range_x=[datetime.fromisoformat("1967-01-01"), datetime.fromisoformat("1969-06-30")], range_y=[0, 500])
    fig1_json = dumps(fig1, cls=utils.PlotlyJSONEncoder)
    fig2 = px.bar(hamladf, x='DATE', y='POPUL', range_x=[datetime.fromisoformat("1967-01-01"), datetime.fromisoformat("1969-06-30")])
    fig2_json = dumps(fig2, cls=utils.PlotlyJSONEncoder)
    fig3 = px.bar(hamladf, x='DATE', y="SCSTA", category_orders={"SCSTA": ["SE", "SS", "CO", "VC", ""]}, labels={None: "None"}, range_x=[datetime.fromisoformat("1967-01-01"), datetime.fromisoformat("1969-06-30")])
    fig3_json = dumps(fig3, cls=utils.PlotlyJSONEncoder)
    fig4 = px.bar(hesdf, x='DATE', y='HCAT', category_orders={"HCAT": ["A", "B", "C", "D", "E", "V", "N", "X", "P"]}, range_x=[datetime.fromisoformat("1970-01-01"), datetime.fromisoformat("1974-01-31")])
    fig4_json = dumps(fig4, cls=utils.PlotlyJSONEncoder)
    fig5 = px.bar(hesdf, x='DATE', y='HPOPUL', range_x=[datetime.fromisoformat("1970-01-01"), datetime.fromisoformat("1974-01-31")])
    fig5_json = dumps(fig5, cls=utils.PlotlyJSONEncoder)
    fig6 = px.bar(hesdf, x='DATE', y="HTEMP",  range_x=[datetime.fromisoformat("1970-01-01"), datetime.fromisoformat("1974-01-31")])
    fig6_json = dumps(fig6, cls=utils.PlotlyJSONEncoder)

    hamladf = pd.DataFrame(hamladf.drop(columns=["USID", "Hamlet Name", "GVN Serial Number", "UTM Coordinates", "geometry"]))
    hesdf = pd.DataFrame(hesdf.drop(columns=["USID", "Hamlet Name", "GVN Serial Number", "UTM Coordinates", "geometry"]))

    #print(fig1_json)
    return render_template(
        "dashboard_template.html",
        fig1_json = fig1_json,
        fig2_json = fig2_json,
        fig3_json = fig3_json,
        fig4_json = fig4_json,
        fig5_json = fig5_json,
        fig6_json = fig6_json,
        hamla_json = hamladf.to_json(orient='split', date_format='iso'),
        hes_json = hesdf.to_json(orient='split', date_format='iso'),
        name = name,
        usid = usid,
        x = location.x,
        y = location.y)

@app.route('/search')
def searchpage():
    return render_template(
        "search_template.html")

@app.route('/usid_search', methods=['POST'])
def usidSearch():
    content = request.json
    searchString = content['search_string']
    if searchString.isdecimal():
        df = hamlet_export.hamlets[int(searchString) == hamlet_export.hamlets["USID"]]
    else:
        df = hamlet_export.hamlets[hamlet_export.hamlets["Hamlet Name"].str.contains(searchString)]
    df = df[df["geometry"] != None]
    return df.to_geo_dict()

@app.route("/get_events", methods=['POST'])
def get_events():
    content = request.json
    df = hamlet_export.events_in_radius(int(content['usid']), content['event_gdf'], float(content['radius']))
    if content['event_gdf'] == 'thor':
        responseDict = df.sort_values(by=['MSNDATE']).to_geo_dict()
    else:
        responseDict = df.sort_values(by=['Date']).to_geo_dict()
    #response = make_response((umsgpack.packb(responseDict), {'content-type': 'application/octet-stream'}))
    return responseDict

if __name__ == "__main__":
    app.run(debug=False)
