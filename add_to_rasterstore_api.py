import sqlite3
import pyspatialite.dbapi2 as db
from ssim_api.ssim_query_functions import query_spatial_files_stateclass

#Collect state_class paths
sqlite_file = r"/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon/media/Hawaii_Assessment_Final_GIF/Hawaii LandCarbon Assessment.ssim"
scenario_id = (6370,)
iteration = range(1, 21)
timestep=range(2001,2062)
stateclass_paths = query_spatial_files_stateclass(sqlite_file, scenario_id=None, iteration=None, timestep=timestep)

#Add paths to app_rasterstore
conn = db.connect('/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon.db')
c = conn.cursor()

table_name = 'app_rasterstore'
#id = 1
#image = 'Hawaii_Assessment_Final_GIF/Hawaii LandCarbon Assessment.ssim.output/Scenario-6370/Spatial/It0001-Ts2001-sc.tif'
width = 555
height = 398
#event = '2001-01-01'
srs ='PROJCS[\"NAD83 / UTM zone 4N\",GEOGCS[\"NAD83\",DATUM[\"North_American_Datum_1983\",SPHEROID[\"GRS 1980\",6378137,298.2572221010002,AUTHORITY[\"EPSG\",\"7019\"]],AUTHORITY[\"EPSG\",\"6269\"]],PRIMEM[\"Greenwich\",0],UNIT[\"degree\",0.01745quit32925199433],AUTHORITY[\"EPSG\",\"4269\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",-159],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"26904\"]]'
minval = '1.0'
maxval = '10.0'
nodata = -9999.0
xpixsize = '1000.0'
ypixsize = '1000.0'
name = 'NULL'
#slug = 's6368-it0001-ts2001-sc'
units = 'NULL'
series_id = 'NULL'
#iteration = 1
geometry = 'POLYGON((-159.834808 18.790113,-154.573079 18.739518,-154.468468 22.324861,-159.854614 22.386072,-159.834808 18.790113))'

id = 1

image_path = 'Hawaii_Assessment_Final_GIF/'

for index, row in stateclass_paths.iterrows():
    scenario = row['Scenario']
    iteration_str = row['Iteration']
    iteration = str(iteration_str)
    timestep = row['Timestep']
    event = str(timestep)+'-01-01'
    image = image_path+row['Path']
    slug = 's'+str(scenario)+'-it'+iteration_str+'-ts'+timestep+'-sc'
    print(scenario, iteration, event, image,slug)
    c.execute("INSERT INTO `app_rasterstore` (`id`,`image`,`width`,`height`,`event`,`srs`,`minval`,`maxval`,`nodata`,`xpixsize`,`ypixsize`,`name`,`slug`,`units`,`series_id`,`iteration`,geom) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,GeomFromText(?,4326))", (id, image, width, height, event, srs, minval, maxval, nodata, xpixsize, ypixsize, name, slug, units, series_id, iteration, geometry))
    conn.commit()
    id +=1
conn.close()
