import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, Point
from shapely.geometry.collection import GeometryCollection
import matplotlib.pyplot as plt
from bokeh.io import curdoc, output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, GeoJSONDataSource, HoverTool, LogColorMapper, LogTicker, ColorBar
from bokeh.layouts import column

from create_dataframe import add_patch_coords

geodata_file0 = "../database/df_merged.csv"
df0 = gpd.read_file(geodata_file0)

df0 = add_patch_coords(df0)
df0.drop(columns='geometry', inplace=True)

hover = HoverTool(
    tooltips=[('NAME', '@Country/Region'), ('ISO3', '@ISO3_CODE')])

plot_width = 1300
plot_height = int(plot_width / 1.7647)
plot = figure(plot_width=plot_width, plot_height=plot_height,  # width / height = 1.7647
              title="Population density (people/km squared)", toolbar_location='left', tools=[hover, 'box_zoom', 'reset'])
countries_glyph = plot.multi_polygons(
    "xs", "ys", source=df0, line_color='black')


layout = column(plot)
curdoc().add_root(layout)
