import sqlite3
import pyspatialite.dbapi2 as db
from ssim_api.ssim_query_functions import query_spatial_files_stateclass, query_projects, project_summary
from osgeo import osr, gdal, ogr

def update_albers_proj(path):
	print(path)
	rootpath = '/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon/media/'
	tifpath = rootpath+path
	gtif = gdal.Open(tifpath, gdal.GA_Update)
	source_proj = gtif.GetProjectionRef()

	print (source_proj)

	target_proj = source_proj.replace('"Albers"', '"Albers_Conic_Equal_Area"')

	print (target_proj)

	targetSR = osr.SpatialReference()

	targetSR.ImportFromWkt(target_proj)

	gtif.SetProjection(targetSR.ExportToWkt())

	print(gtif.GetProjectionRef())
	gtif.FlushCache()
	gtif = None

def stateclass_paths(sqlite_file, scenario_id, iteration, timestep):
#Collect state_class paths
	#scenario_id = (1120,1201,1202,1203)
	stateclass_paths = query_spatial_files_stateclass(sqlite_file, scenario_id=scenario_id, iteration=iteration, timestep=timestep)
	return stateclass_paths

def spatialite_conn(landcarbondb):
	#Add paths to app_rasterstore
	conn = db.connect(landcarbondb)
	c = conn.cursor()
	return c, conn

def add_to_rasterstore(connection, path_to_spatial_files, stateclass_paths, series_ids=None):
	c = connection[0]
	conn = connection[1]
	table_name = 'app_rasterstore'
	width = 730
	height = 1233
	#srs ='PROJCS["North_America_Albers_Equal_Area_Conic",GEOGCS["GCS_North_American_1983",DATUM["North_American_Datum_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["longitude_of_center",-96],PARAMETER["Standard_Parallel_1",20],PARAMETER["Standard_Parallel_2",60],PARAMETER["latitude_of_center",40],UNIT["Meter",1],AUTHORITY["EPSG","102008"]]'
	#srs= 'PROJCS["WGS 84 / UTM zone 10N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-123],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","32610"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
	#srs = 'PROJCS[\"NAD83 / UTM zone 4N\",GEOGCS[\"NAD83\",DATUM[\"North_American_Datum_1983\",SPHEROID[\"GRS 1980\",6378137,298.2572221010002,AUTHORITY[\"EPSG\",\"7019\"]],AUTHORITY[\"EPSG\",\"6269\"]],PRIMEM[\"Greenwich\",0],UNIT[\"degree\",0.01745quit32925199433],AUTHORITY[\"EPSG\",\"4269\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",-159],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AUTHORITY[\"EPSG\",\"26904\"]]'
	#srs = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
	srs='PROJCS["NAD_1983_Albers",GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9108"]],AUTHORITY["EPSG","4269"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["meters",1]]'
	minval = '1.0'
	maxval = '12.0'
	nodata = -9999.0
	xpixsize = '1000.0'
	ypixsize = '1000.0'
	name = 'NULL'
	units = 'NULL'
	geometry = 'POLYGON((-125.260128026 31.3005985283,-113.749295773 31.3005985283,-113.749295773 43.5754794945,-125.260128026 43.5754794945,-125.260128026 31.3005985283))'
	id = int(get_max_rasterstore_id(connection)[0][0]) + 1
	image_path = path_to_spatial_files

	for index, row in stateclass_paths.iterrows():
		scenario = row['Scenario']
		iteration_str = row['Iteration']
		iteration = str(iteration_str)
		timestep = row['Timestep']
		event = str(timestep)+'-01-01'
		image = image_path+row['Path']
		update_albers_proj(image)
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

def summary(sqlite_file, project_id = None):
	if project_id:
		projectsummary = project_summary(sqlite_file, project=project_id)[0]
	else: 
		print(sqlite_file)
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

def get_max_rasterseries_id(connection):
	c = connection[0]
	table_name = 'app_rasterseries'
	c.execute("SELECT MAX(id) FROM `app_rasterseries`")
	max_id = c.fetchall()
	
	return max_id


def get_max_rasterstore_id(connection):
	c = connection[0]
	table_name = 'app_rasterseries'
	c.execute("SELECT MAX(id) FROM `app_rasterstore`")
	max_id = c.fetchall()
	
	return max_id

def add_to_rasterseries(projectsummary, connection, scenario_id):
	c = connection[0]
	conn = connection[1]
	table_name = 'app_rasterseries'
	id = int(get_max_rasterseries_id(connection)[0][0]) + 1
	print(id)
	series_ids = {}

	for index, row in projectsummary.iterrows():
	    scenario = row['ScenarioID']
	    print(scenario)
	    print(scenario_id)
	    if int(scenario) in scenario_id:
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

sqlite_file = r"/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon/media/California_Climate_Assessment_Model_v3.0.37.ssim"
landcarbondb = r"/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon.db"

project_id = (4008,)
scenario_id = (1120,1201,1202,1203)
iteration = range(1, 11)
timestep=range(2001,2102)
path_to_spatial_files = 'California_Climate_Assessment_ Model_v3.0.37/'

print("start")
projectsummary = summary(sqlite_file, project_id=project_id)
print(projectsummary)
connection = sqlite_conn(landcarbondb)

series_ids = add_to_rasterseries(projectsummary, connection, scenario_id)

stateclass_paths = stateclass_paths(sqlite_file, scenario_id, iteration, timestep)

connection = spatialite_conn(landcarbondb)

add_to_rasterstore(connection, path_to_spatial_files, stateclass_paths, series_ids=series_ids)
print("done")