import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, Point
import matplotlib.pyplot as plt
from bokeh.io import curdoc, output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, GeoJSONDataSource, HoverTool, LogColorMapper, LogTicker, ColorBar
from bokeh.layouts import column
from bokeh.palettes import Inferno as palette

def get_geometry_coords(geo_object):
    """
    Finds the x and y coordinates of a geometry object and returns them as two lists in the
    correct form to be plotted using Bokeh.
    Input: A Shapely geometry object.
    Returns: A tuple containing the lists of the input object's x and y coordinates, respectively.

    Each list is in the form:
    [[ [coordinates], [coordinates of hole 1], [coordinates of hole 2], [etc...] ]]
    """

    xs = []
    ys = []
    
    if geo_object.geom_type == 'MultiPolygon':
        for p in geo_object:
            polygon_x = []
            polygon_y = []
            x = p.exterior.coords.xy[0]
            y = p.exterior.coords.xy[1]
            polygon_x.append(list(x))
            polygon_y.append(list(y))
            for hole in list(p.interiors):
                hole_x = hole.coords.xy[0]
                hole_y = hole.coords.xy[1]
                polygon_x.append(list(hole_x))
                polygon_y.append(list(hole_y))
            xs.append(list(polygon_x))
            ys.append(list(polygon_y))
    elif geo_object.geom_type == 'Polygon':
        polygon_x = []
        polygon_y = []
        x = geo_object.exterior.coords.xy[0]
        y = geo_object.exterior.coords.xy[1]
        polygon_x.append(list(x))
        polygon_y.append(list(y))
        for hole in list(geo_object.interiors):
            hole_x = hole.coords.xy[0]
            hole_y = hole.coords.xy[1]
            polygon_x.append(list(hole_x))
            polygon_y.append(list(hole_y))
        xs.append(list(polygon_x))
        ys.append(list(polygon_y))
    elif geo_object.geom_type == 'Point':
        xs = geo_object.x
        ys = geo_object.y

    return (xs, ys)

def add_patch_coords(geodataframe):
    x_patches, y_patches = [], []

    for country in geodataframe['geometry'].tolist():
        coords = get_geometry_coords(country)
        x_patches.append(coords[0])
        y_patches.append(coords[1])

    geodataframe['xs'] = x_patches
    geodataframe['ys'] = y_patches

    return geodataframe

def get_population_density(row, pop):
    if row['geometry'] is not None:
        return row[pop] / row['geometry'].area
    else:
        return None

def remove_none(row):
    if row['geometry'] is None:
        return Polygon()
    else:
        return row['geometry']


geodata_file = "../database/ne_50m_admin_0_countries.shp"
geodata = gpd.read_file(geodata_file) # geodataframe of country shapely objects
geodata = add_patch_coords(geodata)

pop_data_file = "../database/API_SP.POP.TOTL_DS2_en_csv_v2_1976634.csv"
pop_data = pd.read_csv(pop_data_file, header=2)


merge_data = geodata.merge(pop_data[['Country Code', 'Country Name', '2019']],
                      how='outer', left_on='ISO_A3', right_on='Country Code')
merge_data['pop_density'] = merge_data.apply(get_population_density, pop='2019', axis=1) 
#merge_data['geometry'] = merge_data.apply(remove_none, axis=1) 

merge_data.drop(columns='geometry', inplace=True)


#source = GeoJSONDataSource(geojson=merge_data.to_json())
color_mapper = LogColorMapper(palette=list(reversed(palette[256])))

plot = figure(plot_width=1300, plot_height=680, title="Map")
plot.multi_polygons("xs", "ys", source=merge_data[:241], line_color="black",
                fill_color={'field': 'pop_density', 'transform': color_mapper})

color_bar = ColorBar(color_mapper=color_mapper, ticker=LogTicker(),
                     label_standoff=12, border_line_color=None, location=(0,0))
plot.add_layout(color_bar, 'right')

country_hover = HoverTool(tooltips='@{NAME}', name='Hover (country)')
plot.add_tools(country_hover)

#show(plot)


layout = column(plot)
curdoc().add_root(layout)




