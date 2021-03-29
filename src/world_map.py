import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, Point
import matplotlib.pyplot as plt
from bokeh.io import curdoc, output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, GeoJSONDataSource, HoverTool, LogColorMapper, LogTicker, ColorBar, CheckboxGroup, FuncTickFormatter, FixedTicker, HoverTool, BoxZoomTool, ResetTool, ToolbarBox, Toolbar
from bokeh.layouts import column
from bokeh.palettes import Inferno, Cividis, Viridis8, Viridis6, Viridis
import numpy as np

from create_dataframe import add_patch_coords


def patch_colors(df_countries):
    """
    Determines the color of each patch based on the population density of that patch.
    """

    # population density ranges:
    #   0 - 10      0
    #   10 - 25     1
    #   25 - 50     2
    #   50 - 75     3
    #   75 - 100    4
    #   100 - 150   5
    #   150 - 300   6
    #   300 - 1000  7
    #   1000+       8

    palette = ['#f7f4f9', '#e7e1ef', '#d4b9da', '#c994c7',
               '#df65b0', '#e7298a', '#ce1256', '#980043', '#67001f']
    # palette = ['#fcfbfd','#efedf5','#dadaeb','#bcbddc','#9e9ac8','#807dba','#6a51a3','#54278f','#3f007d']
    density_ranges = ['≤ 10', '10 - 25', '25 - 50', '50 - 75', '75 - 100', '100 - 150',
                      '150 - 300', '300 - 1000', '1000+']
    df_countries['color'] = ''
    df_countries['legend'] = ''

    for row, data in df_countries.iterrows():
        density = data['density']
        if density <= 10:
            df_countries.loc[row, 'color'] = palette[0]
            df_countries.loc[row, 'legend'] = density_ranges[0]
        elif density <= 25:
            df_countries.loc[row, 'color'] = palette[1]
            df_countries.loc[row, 'legend'] = density_ranges[1]
        elif density <= 50:
            df_countries.loc[row, 'color'] = palette[2]
            df_countries.loc[row, 'legend'] = density_ranges[2]
        elif density <= 75:
            df_countries.loc[row, 'color'] = palette[3]
            df_countries.loc[row, 'legend'] = density_ranges[3]
        elif density <= 100:
            df_countries.loc[row, 'color'] = palette[4]
            df_countries.loc[row, 'legend'] = density_ranges[4]
        elif density <= 150:
            df_countries.loc[row, 'color'] = palette[5]
            df_countries.loc[row, 'legend'] = density_ranges[5]
        elif density <= 300:
            df_countries.loc[row, 'color'] = palette[6]
            df_countries.loc[row, 'legend'] = density_ranges[6]
        elif density <= 1000:
            df_countries.loc[row, 'color'] = palette[7]
            df_countries.loc[row, 'legend'] = density_ranges[7]
        elif density > 1000:
            df_countries.loc[row, 'color'] = palette[8]
            df_countries.loc[row, 'legend'] = density_ranges[8]

    return df_countries


#################################################
# Plot countries
#################################################
df_countries = gpd.read_file("final_dataset/final_dataset.shp")
#print("\n", 1, df_countries[df_countries["SOV_A3"] == "USA"])
df_countries = add_patch_coords(df_countries)
#print("\n", 2, df_countries[df_countries["SOV_A3"] == "USA"])

df_countries.drop(columns='geometry', inplace=True)
#print("\n", 3, df_countries[df_countries["SOV_A3"] == "USA"])

df_countries['pop_densit'] = df_countries['pop_densit']

max_pop_density = df_countries.loc[df_countries['pop_densit']
                                   != np.inf, 'pop_densit'].squeeze().max()
min_pop_density = df_countries['pop_densit'].min()
color_mapper = LogColorMapper(palette=list(reversed(Viridis[256])),
                              low=min_pop_density, high=max_pop_density)

plot_width = 1300
plot_height = int(plot_width / 1.7647)
plot = figure(plot_width=plot_width, plot_height=plot_height,  # width / height = 1.7647
              title="Population density (people/km squared)", toolbar_location='left')
#plot.axis.visible = False
countries_glyph = plot.multi_polygons("xs", "ys", source=df_countries[:239], line_color="black",
                                      fill_color={'field': 'pop_densit', 'transform': color_mapper})

ticker = FixedTicker(
    ticks=[1, 2, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000])

color_bar = ColorBar(color_mapper=color_mapper, location=(
    0, 0), major_tick_line_color='black', ticker=ticker, label_standoff=10)

plot.add_layout(color_bar, 'right')


plot.add_tools(HoverTool(
    renderers=[countries_glyph], tooltips='@{NAME_EN}', name='Hover (country)'))


#################################################
# Plot capitals
#################################################
df_capitals = pd.read_csv("../database/df_capitals.csv")

capitals_glyph = plot.circle(x='CapitalLongitude', y='CapitalLatitude', source=df_capitals,
                             fill_color='red', line_color='red', size=4.5)

capitals_tooltips = """ 
    <div>
        <div>
            <span style="font-size: 12px;">@CapitalName_x, @{Country/Region}</span>
        </div>
    </div>
"""

plot.add_tools(
    HoverTool(renderers=[capitals_glyph], tooltips=capitals_tooltips))

capitals_checkbox = CheckboxGroup(labels=['Show capitals'], active=[0])


def show_capitals_callback(active):
    """
    Callback function for the 'Show capitals' checkbox. If the checkbox is active, show the countries' capitals and hover tool. Otherwise,
    hide them.
    """

    if active:
        capitals_glyph.visible = True
    else:
        capitals_glyph.visible = False


capitals_checkbox.on_click(show_capitals_callback)

plot.background_fill_color = '#f0f0f0'

layout = column(capitals_checkbox, plot)
curdoc().add_root(layout)
