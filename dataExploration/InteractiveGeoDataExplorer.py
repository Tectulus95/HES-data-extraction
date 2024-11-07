""" flask_example.py

    Required packages:
    - flask
    - folium

    Usage:

    Start the flask server by running:

        $ python flask_example.py

    And then head to http://127.0.0.1:5000 in your browser to see the map displayed

"""

import bokeh
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from flask import Flask, render_template_string, render_template

import folium
import pandas as pd
import geopandas as gpd
import plotly.express as px
from plotly import utils
from json import dumps
from datetime import datetime
import hamlet_export

def create_map():
    m = folium.Map(tiles="esri.WorldTopoMap", location=(14, 106), zoom_start=7)
    return m

def update_map(m, date):
    colors = {
        "00":"white",
        "SE":"green",
        "SS":"yellow",
        "CO":"orange",
        "VC":"red",
        "":"white",
        None:"white"
        }
    qdate = pd.date_range(date, periods=1, freq="MS")
    folium.GeoJson(
        hamlet_export.dynamic_gdf(qdate),
        name = "Hamlet Markers",
        marker=folium.CircleMarker(radius=4, fill_color="orange", fill_opacity=0.4, color="black", weight=1),
        popup=folium.GeoJsonPopup(fields=["Hamlet Nam", "USID", "POPUL", "SCSTA", "CLASX"]),
        style_function=lambda x: {
            "fillColor": colors[x['properties']['SCSTA']],
            "radius": (x['properties']['POPUL'])/2000+3,
        }
    ).add_to(m)
    return m

def load_and_filter_shp(filename, column, value):
    gdf = gpd.read_file(filename)
    output = gdf.loc[gdf[column]==value]
    return output

app = Flask(__name__)


@app.route("/date/<date>")
def fullscreen(date):

    """Simple example of a fullscreen map."""
    date = datetime.strptime(f"19{date}", "%Y%m")
    m = create_map()
    m = update_map(m, date)
    folium.LayerControl().add_to(m)
    return m.get_root().render()


@app.route("/iframe")
def iframe():
    """Embed a map as an iframe on a page."""
    
    m = create_map()
    m = update_map(m)

    # set the iframe width and height
    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head></head>
                <body>
                    <h1>HES data for</h1>
                    {{ iframe|safe }}
                </body>
            </html>
        """,
        iframe=iframe,
    )


@app.route("/components")
def components():
    """Extract map components and put those on a page."""
    m = folium.Map(
        width=1440,
        height=720,
    )

    m.get_root().render()
    header = m.get_root().header.render()
    body_html = m.get_root().html.render()
    script = m.get_root().script.render()

    return render_template_string(
        """
            <!DOCTYPE html>
            <html>
                <head>
                    {{ header|safe }}
                </head>
                <body>
                    <h1>Using components</h1>
                    {{ body_html|safe }}
                    <script>
                        {{ script|safe }}
                    </script>
                </body>
            </html>
        """,
        header=header,
        body_html=body_html,
        script=script,
    )

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
