import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, Point
from shapely.geometry.collection import GeometryCollection
import matplotlib.pyplot as plt
from bokeh.io import curdoc, output_file, show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, GeoJSONDataSource, HoverTool, LogColorMapper, LogTicker, ColorBar
from bokeh.layouts import column
from bokeh.palettes import Inferno as palette

##################################################################
# In this file we created the DataFrame that is to be used in the WorldMap.py
# program, by combining together several different data sets.
# I couldn't find one data set that had the polygons of every single country,
# so I have to pick and choose and merge them together.
# This was only run to choose the final data set to use so this file shouldn't ever be
# needed again.
##################################################################

FINAL_FILE = "final_dataset.csv"


def get_geometry_coords(geo_object):
    """
    Finds the x and y coordinates of a geometry object and returns them as two lists in the
    correct form to be plotted using Bokeh.
    Input: A Shapely geometry object.
    Returns: A tuple containing the lists of the input object's x and y coordinates, respectively.

    Each list is in the form:
    [[ [coordinates], [coordinates of hole 1], [coordinates of hole 2], [etc...] ]]
    """

    if geo_object is None:
        return ([0], [0])

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


def plot_data_set(dataset):
    """
    Plots one of the polygon datasets.

    This was used to figure out which parts of which data set I want to combine
    together by comparing them to each other.

    Input: The number of the dataset you want to display (as the index in the array below).
    """

    #################################################
    # Data set 0
    #################################################
    # To replace: (Country in this data set, country from another data set)
    #             (Western Sahara + Morocco, Morocco)
    #             (Somaliland + Somalia, Somalia)
    #             (Turkis Republic of Northern Cyprus + Cyprus, Cyprus)
    #             (France, France + territories)
    #             (Maldives, Maldives from set 2)
    geodata_file0 = "../database/ne_50m_admin_0_countries.shp"

    #################################################
    # Data set 1
    #################################################
    # To replace: (Country in this data set, country from another data set)
    geodata_file1 = "../database/0/99bfd9e7-bb42-4728-87b5-07f8c8ac631c2020328-1-1vef4ev.lu5nk.shp"

    #################################################
    # Data set 2 - GOOD SET
    #################################################
    # Use this data set as the base.
    # To replace: (Country in this data set, country from another data set)
    #             (Western Sahara + Morocco, Morocco) --> need to merge the two instead
    #             (Serbia, Serbia + Kosovo) --> from set 0
    #             (Sudan, Sudan + South Sudan) -- from set 1
    # Names to change: Swaziland, Brunei
    geodata_file2 = "../database/1/TM_WORLD_BORDERS-0.3.shp"

    files = [geodata_file0, geodata_file1, geodata_file2]
    hovers = ['@{NAME_EN}', '@{CNTRY_NAME}', '@{NAME}']

    # since the following steps are the same for all datasets, we just need the
    # index of the file in the list above
    # geodataframe of country shapely objects
    geodata = gpd.read_file(files[dataset])
    geodata = add_patch_coords(geodata)
    geodata.drop(columns='geometry', inplace=True)

    plot = figure(plot_width=1300, plot_height=680,
                  title="Data set " + str(dataset))
    plot.multi_polygons('xs', 'ys', source=geodata,
                        line_color="black", fill_alpha=0.3)

    country_hover = HoverTool(tooltips=hovers[dataset], name='Hover (country)')
    plot.add_tools(country_hover)

    show(plot)

    return geodata


def fix_polygons():
    """
    Picks certain country Polygons from the three different datasets and creates from them
    a single, final dataset.

    I used file0 as the base dataset since that was the one with Kosovo/Serbia and Sudan/South
    Sudan correctly separated. I then replaced some countries' Polygons with those from
    the other files because they looked better.
    """

    file0 = "../database/ne_50m_admin_0_countries.shp"  # the base data set
    file1 = "../database/0/99bfd9e7-bb42-4728-87b5-07f8c8ac631c2020328-1-1vef4ev.lu5nk.shp"
    file2 = "../database/1/TM_WORLD_BORDERS-0.3.shp"

    geodata0 = gpd.read_file(
        file0)[['NAME_EN', 'ISO_A3', 'geometry']]  # good dataframe
    geodata1 = gpd.read_file(file1)
    geodata2 = gpd.read_file(file2)[['ISO3', 'NAME', 'geometry']]
    geodata2.crs = geodata0.crs

    # merge morocco and western sahara polygons
    # extract good serbia geometry
    morocco = geodata0[geodata0['NAME_EN'] == 'Morocco']['geometry'].squeeze()
    morocco_index = geodata0[geodata0['NAME_EN'] ==
                             'Morocco'].index.tolist()  # row index of serbia
    # extract good serbia geometry
    sahara = geodata0[geodata0['NAME_EN'] ==
                      'Western Sahara']['geometry'].squeeze()
    geodata0.at[morocco_index[0], 'geometry'] = morocco.union(
        sahara)  # assign new serbia
    geodata0 = geodata0.drop(
        geodata0[geodata0['NAME_EN'] == 'Western Sahara'].index)

    # merge somalia and somaliland polygons
    # extract good serbia geometry
    somalia = geodata0[geodata0['NAME_EN'] == 'Somalia']['geometry'].squeeze()
    somalia_index = geodata0[geodata0['NAME_EN'] ==
                             'Somalia'].index.tolist()  # row index of serbia
    # extract good serbia geometry
    somaliland = geodata0[geodata0['NAME_EN']
                          == 'Somaliland']['geometry'].squeeze()
    geodata0.at[somalia_index[0], 'geometry'] = somalia.union(
        somaliland)  # assign new serbia polygon
    geodata0 = geodata0.drop(
        geodata0[geodata0['NAME_EN'] == 'Somaliland'].index)

    # replace maldives with polygons from set 2
    maldives_index = geodata0[geodata0['NAME_EN'] ==
                              'Maldives'].index.tolist()  # row index of serbia
    # the following line of code doesn't work if you try to assign a variable containing the multipolygon
    # see here: https://stackoverflow.com/questions/56018427/geopandas-set-geometry-valueerror-for-multipolygon-equal-len-keys-and-value
    geodata0.loc[maldives_index[0], 'geometry'] = geodata2.loc[geodata2['NAME']
                                                               == 'Maldives', 'geometry'].values  # assign new serbia polygon

    # replace kiribati with polygons from set 2
    kiribati_index = geodata0[geodata0['NAME_EN'] ==
                              'Kiribati'].index.tolist()  # row index of serbia
    geodata0.loc[kiribati_index[0], 'geometry'] = geodata2.loc[geodata2['NAME']
                                                               == 'Kiribati', 'geometry'].values  # assign new serbia polygon

    return geodata0


def add_population(df_final):
    """
    Adds the population data to the final data set. Only meant to be called after
    fix_polygons().
    """

    def get_population_density(row):
        if row['geometry'].area == 0 or row['geometry'] is None:
            return 0
        else:
            # get population / area and convert to km^2
            return row['2019'] / row['geometry'].area * 10**6

    df_pop = pd.read_csv(
        "../database/API_SP.POP.TOTL_DS2_en_csv_v2_1976634.csv", header=2)

    df_final = df_final.merge(df_pop[['Country Code', 'Country Name', '2019']],
                              how='outer', left_on='ISO_A3', right_on='Country Code')
    # change any None geometries to actual geometry objects...
    df_copy = df_final['geometry'].apply(
        lambda x: x if x else GeometryCollection())
    # ...so next line doesn't throw error
    # change to CRS which gives most accurate area values
    df_copy = df_copy.to_crs({'proj': 'cea'})
    df_final['pop_density'] = df_final['2019'] / df_copy.area * 10**6
    # df_final['geometry'] = df_final['geometry'].to_crs(epsg=3857) # change to CRS back to longitude/latitude

    return df_final


def create_polygon_dataset():
    df = fix_polygons()
    df = add_population(df)
    df.to_file(FINAL_FILE)  # write the good polygons to a shapefile
    # column names get truncated here, but I don't know how to fix it

    return df


#df = create_polygon_dataset()


'''
geodata0 = plot_data_set(0)
geodata1 = plot_data_set(1)
geodata2 = plot_data_set(2)




data = gpd.read_file(FINAL_FILE)
data = add_patch_coords(data)
data.drop(columns='geometry', inplace=True)

plot = figure(plot_width=1300, plot_height=680, title="Map")
plot.multi_polygons('xs', 'ys', source=data[:239], line_color='black')

show(plot)

'''
