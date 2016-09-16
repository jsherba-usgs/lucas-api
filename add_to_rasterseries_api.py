import sqlite3
from ssim_api.ssim_query_functions import query_projects, project_summary

#Collect run control data
sqlite_file = r"/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon/media/Hawaii_Assessment_Final_GIF/Hawaii LandCarbon Assessment.ssim"

projects = query_projects(sqlite_file)
project_id = projects["ProjectID"].iloc[0]
project_id =(project_id,)
projectsummary = project_summary(sqlite_file, project=project_id)[0]
projectsummary = projectsummary[projectsummary.RunStatus == 3]

#Create Raster Seres
conn = sqlite3.connect('/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon.db')
c = conn.cursor()

table_name = 'app_rasterseries'
id = 1
for index, row in projectsummary.iterrows():
    scenario = row['ScenarioID']
    iterations = range(row['MinimumIteration'], row["MaximumIteration"]+1)
    begin = str(row["MinimumTimestep"]) + "-01-01 00:00:00"
    end = str(row["MaximumTimestep"]) + "-01-01 00:00:00"
    for iteration in iterations:
		iteration = '{:0>4}'.format(iteration)
		slug = 'scenario-'+str(scenario)+'-spatial-it'+iteration+'-sc'

		print(id,iteration,slug, begin, end)
		c.execute("INSERT INTO `app_rasterseries` (`id`,`name`,`slug`,`begin`,`end`) VALUES (?,?,?,?,?)", (id, 'NULL', slug, begin, end))
		conn.commit()
		id += 1
	 
conn.close()
