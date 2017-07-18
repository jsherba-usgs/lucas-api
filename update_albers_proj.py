from osgeo import osr, gdal, ogr
import sys

gtif = gdal.Open( "/home/jsherba-pr/Downloads/data/It0001-Ts2011-sc.tif", gdal.GA_Update)
source_proj = gtif.GetProjectionRef()

print (source_proj)

target_proj = source_proj.replace('"Albers"', '"Albers_Conic_Equal_Area"')


'''print (target_proj)

targetSR = osr.SpatialReference()

targetSR.ImportFromWkt(target_proj)

gtif.SetProjection(targetSR.ExportToWkt())


print(gtif.GetProjectionRef())
gtif.FlushCache()
gtif = None'''