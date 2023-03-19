import yaml
import folium
import pandas as pd
import geopandas as gpd
from branca.colormap import linear

# Cost of living index https://www.theglobaleconomy.com/rankings/cost_of_living_wb/
# Flights price Skyscanner
# Average cost per day 

# Constants
DAYS = 9
PATH_TO_WORLD = 'world/ne_110m_admin_0_countries.shp'
PATH_TO_DATA = 'data.yml'
CAPTION_FP = 'Flights price for November, just one way (€)'
CAPTION_CL = 'Cost of living index (€)'
CAPTION_BG = 'Budget for {} days (€)'.format(DAYS)

# Read the data
world = gpd.read_file(PATH_TO_WORLD)
with open(PATH_TO_DATA, 'r') as f:
    data = yaml.safe_load(f)
df = pd.DataFrame(data).transpose()
df.index.name = 'NAME'
df = df.reset_index()

# Normalize cost of living index by the cost of living in Spain
df['cost_living_index'] = df['cost_living_index'] / df[df['NAME'] == 'Spain']['cost_living_index'].values[0]

# Round the cost of living index to 2 decimals
df['cost_living_index'] = df['cost_living_index'].round(2)

# Multiply the cost per day by the number of days
df['cost_per_day'] = df['cost_per_day'] * DAYS

# Round the cost per day to 1 decimals
df['cost_per_day'] = df['cost_per_day'].round(1)

# Change the cost per day label to budget
df = df.rename(columns={'cost_per_day': 'budget'})

# Merge the data with the world map
merged = world.merge(df, on='NAME')

m = folium.Map(location=[0, 0], zoom_start=2)

# Define the colormap for the flights price
cmap_fp = linear.YlOrRd_09.scale(min(df['flights_price']), max(df['flights_price'])) 

# Add the Flights cost price GeoJSON layer 
folium.GeoJson(
    merged,
    name='flights_price',
    style_function=lambda x: {'fillColor': cmap_fp(x['properties']['flights_price']), 'color': 'black', 'weight': 2, 'fillOpacity': 0.6},
    tooltip=folium.features.GeoJsonTooltip(fields=['NAME', 'flights_price', 'cost_living_index', 'budget'], aliases=['Country', 'Flights price', 'Cost of living', 'Budget']),
).add_to(m)

# Add a caption 
cmap_fp.caption = CAPTION_FP
cmap_fp.add_to(m)

# Define the colormap for the cost of living
cmap_col = linear.YlOrRd_09.scale(min(df['cost_living_index']), max(df['cost_living_index']))

# Add the Cost of living GeoJSON layer
folium.GeoJson(
    merged,
    name='cost_living_index',
    style_function=lambda x: {'fillColor': cmap_col(x['properties']['cost_living_index']), 'color': 'black', 'weight': 2, 'fillOpacity': 0.6},
    tooltip=folium.features.GeoJsonTooltip(fields=['NAME', 'flights_price', 'cost_living_index', 'budget'], aliases=['Country', 'Flights price', 'Cost of living', 'Budget']),
).add_to(m)

# Add a caption 
cmap_col.caption = CAPTION_CL 
cmap_col.add_to(m)

 
# Define the colormap for the budget
cmap_bg = linear.YlOrRd_09.scale(min(df['budget']), max(df['budget']))

# Add the Budget GeoJSON layer
folium.GeoJson(
    merged,
    name='budget',
    style_function=lambda x: {'fillColor': cmap_bg(x['properties']['budget']), 'color': 'black', 'weight': 2, 'fillOpacity': 0.6},
    tooltip=folium.features.GeoJsonTooltip(fields=['NAME', 'flights_price', 'cost_living_index', 'budget'], aliases=['Country', 'Flights price', 'Cost of living', 'Budget']),
).add_to(m)
 
# Add a caption 
cmap_bg.caption = CAPTION_BG

cmap_bg.add_to(m)


# Add layer control
folium.LayerControl().add_to(m)

# Add limits to the map
m.fit_bounds(m.get_bounds())

# Save the map
m.save('map.html')