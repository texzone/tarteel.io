import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import cartopy
import cartopy.io.shapereader as shpreader
import cartopy.crs as ccrs
import pandas as pd

"""
Data Prep
"""
# === Read in demographics CSV ===
# This csv was from the SQL restapi_demographics_table
names = ['id', 'session_id', 'platform', 'gender', 'age', 'ethnicity',
         'country', 'timestamp', 'qiraah']
demo_df = pd.read_csv('demographics.csv', delimiter=';', header=None, names=names)

# === Cleanup ===
# Make all genders same
demo_df['gender'] = demo_df['gender'].str.lower()
# Convert arabic to eng.
demo_df.loc[demo_df['gender'] == 'ذكر', 'gender'] = 'male'

# === Country Counts ===
demo_country_df = demo_df['ethnicity'].value_counts().to_frame()
# Add normalized column for colors
country_counts = demo_country_df.values
norm_values = country_counts / np.linalg.norm(country_counts)
demo_country_df['norm_value'] = norm_values

"""
Plot Prep
"""
# === Country DB ===
shpfilename = shpreader.natural_earth(resolution='110m',
                                      category='cultural',
                                      name='admin_0_countries')
reader = shpreader.Reader(shpfilename)
countries = reader.records()

# === Plotting ===
# Colors
cmap = cm.YlGn
# Prepare plot
fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
ax.add_feature(cartopy.feature.BORDERS, linestyle='-', alpha=.5)
ax.set_extent([-150, 60, -25, 60])
# Iterate over all countries in df
# Country code attr.: 'WB_A2'
for country in countries:
    country_code = country.attributes['WB_A2']
    try:
        country_count = demo_country_df.ethnicity[country_code]
        country_color = cmap(demo_country_df.norm_value[country_code])

        ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                          facecolor=country_color,
                          label=country_code)
    except KeyError:
        ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                          facecolor=cmap(0),
                          label=country_code)

# Colorbar
sm = cm.ScalarMappable(cmap=cmap)
sm._A = country_counts
cb = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.05)
cb.ax.set_xlabel('Number of Users')

plt.title("Tarteel's Demographic Breakdown")
plt.show()
fig.savefig('tarteel_dmg.png')
