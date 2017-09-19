import sqlite3
import pyspatialite.dbapi2 as db
import json, pprint



def spatialite_conn(landcarbondb):
	#Add paths to app_rasterstore
	conn = db.connect(landcarbondb)
	c = conn.cursor()
	return c, conn


def get_max_location_id(connection):
	c = connection[0]
	c.execute("SELECT MAX(id) FROM `app_location`")
	max_id = c.fetchall()

	return max_id

def add_to_rasterstore(connection, json_file_in, layer_name):
	c = connection[0]
	conn = connection[1]

	with open(json_file_in) as data_file:
		data = json.load(data_file)


	if get_max_location_id(connection)[0][0] is None:
		id = 0
	else:
		id = int(get_max_location_id(connection)[0][0]) + 1


	for features in data["features"]:

		properties = features["properties"]["name"]
		#properties = features["properties"]["Name"]
		#properties = features["properties"]["GRIDCODE"]

		coordinates = features["geometry"]["coordinates"]

		if features["geometry"]['type']=='MultiPolygon':

			polygons =  '{"type":"MultiPolygon","crs":{"type":"name","properties":{"name":"EPSG:4326"}},"coordinates":%s}' % coordinates
		else:
			polygons = '{"type":"MultiPolygon","crs":{"type":"name","properties":{"name":"EPSG:4326"}},"coordinates":[%s]}' % coordinates


		layers = layer_name
		#slug = properties.split(" County")[0]
		slug = properties
		label = properties

		c.execute("INSERT INTO `app_location` (`id`,`layers`,`slug`,`label`,geom) VALUES (?,?,?,?,GeomFromGeoJSON(?))", (id, layers, slug, label, polygons))
		#c.execute("INSERT INTO `app_location` (`id`,`layers`,`slug`,geom) VALUES (?,?,?,GeomFromText(?,4326))", (number, layers, slug, geometry))
		conn.commit()
		id+=1
	conn.close()


json_file_in = r"/home/ubuntu/projects/lucas-api/landcarbon/media/location/islands.json"
landcarbondb = r"/home/ubuntu/projects/lucas-api/landcarbon.db"
layer_name = 'hi_islands'

connection = spatialite_conn(landcarbondb)

add_to_rasterstore(connection, json_file_in, layer_name)
print("done")
