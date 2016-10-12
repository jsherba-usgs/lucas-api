import sqlite3
import pyspatialite.dbapi2 as db
from ssim_api.ssim_query_functions import query_spatial_files_stateclass, query_projects, project_summary

def stateclass_paths(sqlite_file):
#Collect state_class paths
	scenario_id = (6370,)
	iteration = range(1, 21)
	timestep=range(2001,2062)
	stateclass_paths = query_spatial_files_stateclass(sqlite_file, scenario_id=None, iteration=None, timestep=timestep)
	return stateclass_paths

def spatialite_conn(landcarbondb):
	#Add paths to app_rasterstore
	conn = db.connect(landcarbondb)
	c = conn.cursor()
	return c, conn

def add_to_rasterstore(connection, stateclass_paths, series_ids=None):
	c = connection[0]
	conn = connection[1]
	table_name = 'app_rasterstore'
	width = 555
	height = 398
	srs ='PROJCS[\"NAD83 / UTM zone 4N\",GEOGCS[\"NAD83\",DATUM[\"North_American_Datum_1983\",SPHEROID[\"GRS 1980\",6378137,298.2572221010002,AUTHORITY[\"EPSG\",\"7019\"]],AUTHORITY[\"EPSG\",\"6269\"]],PRIMEM[\"Greenwich\",0],UNIT[\"degree\",0.01745quit32925199433],AUTHORITY[\"EPSG\",\"4269\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",-159],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"26904\"]]'
	minval = '1.0'
	maxval = '10.0'
	nodata = -9999.0
	xpixsize = '1000.0'
	ypixsize = '1000.0'
	name = 'NULL'
	units = 'NULL'
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
	    if series_ids:
	    	series_id = series_ids[scenario][iteration_str]
	    else:
	    	series_id = 'Null'
	    print(scenario, iteration, event, image,slug)
	    c.execute("INSERT INTO `app_rasterstore` (`id`,`image`,`width`,`height`,`event`,`srs`,`minval`,`maxval`,`nodata`,`xpixsize`,`ypixsize`,`name`,`slug`,`units`,`series_id`,`iteration`,geom) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,GeomFromText(?,4326))", (id, image, width, height, event, srs, minval, maxval, nodata, xpixsize, ypixsize, name, slug, units, series_id, iteration, geometry))
	    conn.commit()
	    id +=1
	conn.close()

def summary(sqlite_file):
	projects = query_projects(sqlite_file)
	project_id = projects["ProjectID"].iloc[0]
	project_id =(project_id,)
	projectsummary = project_summary(sqlite_file, project=project_id)[0]
	projectsummary = projectsummary[projectsummary.RunStatus == 3]
	return projectsummary

#Create Raster Seres
def sqlite_conn(landcarbondb):
	conn = sqlite3.connect(landcarbondb)
	c = conn.cursor()
	return c, conn

def add_to_rasterseries(projectsummary, connection):
	c = connection[0]
	conn = connection[1]
	table_name = 'app_rasterseries'
	id = 1
	series_ids = {}
	for index, row in projectsummary.iterrows():
	    scenario = row['ScenarioID']
	    iterations = range(row['MinimumIteration'], row["MaximumIteration"]+1)
	    begin = str(row["MinimumTimestep"]) + "-01-01 00:00:00"
	    end = str(row["MaximumTimestep"]) + "-01-01 00:00:00"
	    series_ids[scenario]={}
	    for iteration in iterations:
			iteration = '{:0>4}'.format(iteration)
			slug = 'scenario-'+str(scenario)+'-spatial-it'+iteration+'-sc'
			c.execute("INSERT INTO `app_rasterseries` (`id`,`name`,`slug`,`begin`,`end`) VALUES (?,?,?,?,?)", (id, 'NULL', slug, begin, end))
			conn.commit()
			series_ids[scenario][iteration] = id
			id += 1
		 
	conn.close()
	return series_ids

sqlite_file = r"/media/sf_jts_2016_09_01_LandCarbon_CDI/Hawaii_Assessment_Final_GIF/Hawaii LandCarbon Assessment.ssim"
landcarbondb = r'/home/ubuntu/projects/landcarbon-cdi/landcarbon.db'

projectsummary = summary(sqlite_file)

connection = sqlite_conn(landcarbondb)

series_ids = add_to_rasterseries(projectsummary, connection)

stateclass_paths = stateclass_paths(sqlite_file)

connection = spatialite_conn(landcarbondb)

add_to_rasterstore(connection, stateclass_paths, series_ids=series_ids)