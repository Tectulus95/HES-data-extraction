""" Runs the flask server for interacting with the data in the browser.

    Run this file and then head to http://127.0.0.1:5000 in your browser to see the map displayed

"""
from datetime import datetime
from json import dumps
import os

import bokeh
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
from flask import Flask, render_template_string, render_template
import geopandas as gpd
import pandas as pd
from plotly import utils
import plotly.express as px

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
    gdf = hamlet_export.dynamic_gdf(qdate)
    gdf.rename(columns={"Hamlet Nam": "Hamlet Name"})
    return gdf.to_json()

@app.route('/')
def js_map():
    json = get_geojson("011967")
    return render_template("map_template.html", geojson=json)


@app.route("/usid/<usid>")
def hamlet_data(usid):
    hamladf, hesdf = hamlet_export.hamlet_history(usid)
    print(hamladf.head())
    name = hamladf["Hamlet Nam"].iloc[0]
    #p = figure(x_axis_type="datetime", width=600, height=400)
    fig1 = px.line(hamladf, x='DATE', y='CLASX')
    fig1_json = dumps(fig1, cls=utils.PlotlyJSONEncoder)
    fig2 = px.line(hamladf, x='DATE', y='POPUL')
    fig2_json = dumps(fig2, cls=utils.PlotlyJSONEncoder)
    #print(fig1_json)
    return render_template_string(
        """
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>



<h3>Line Graph Representations {{name | safe}}</h3>

<!-- scatter plot goes in this div -->
<div id='fig1_div'><div>
<div id='fig2_div'><div>

<script type="text/javascript">

        
        var fig1_graph = {{fig1_json | safe}};
        var fig2_graph = {{fig2_json | safe}};

        fig1 = document.getElementById('fig1_div');
        fig2 = document.getElementById('fig2_div');

        
        Plotly.plot(fig1, fig1_graph);
        Plotly.plot(fig2, fig2_graph);

</script>
        """,
        fig1_json = fig1_json,
        fig2_json = fig2_json,
        name = name)



if __name__ == "__main__":
    app.run(debug=True)
