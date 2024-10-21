""" flask_example.py

    Required packages:
    - flask
    - folium

    Usage:

    Start the flask server by running:

        $ python flask_example.py

    And then head to http://127.0.0.1:5000/iframe in your browser to see the map displayed

"""

from flask import Flask, render_template_string

import folium
import pandas as pd
import geopandas as gpd

import hamlet_export

def create_map():
    m = folium.Map(tiles="esri.WorldTopoMap", location=(14, 106), zoom_start=7)
    return m

def update_map(m):
    colors = {
        "00":"white",
        "SE":"green",
        "SS":"yellow",
        "CO":"orange",
        "VC":"red",
        "":"white",
        None:"white"
        }
    qdate = pd.date_range("5-1-1968", periods=1, freq="MS")
    folium.GeoJson(
        hamlet_export.dynamic_gdf(qdate),
        name = "Hamlet Markers",
        marker=folium.CircleMarker(radius=4, fill_color="orange", fill_opacity=0.4, color="black", weight=1),
        tooltip=folium.GeoJsonTooltip(fields=["Hamlet Nam", "POPUL", "SCSTA", "CLASX"]),
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


@app.route("/")
def fullscreen():
    """Simple example of a fullscreen map."""
    m = create_map()
    m = update_map(m)
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



if __name__ == "__main__":
    app.run(debug=True)
