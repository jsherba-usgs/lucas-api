# **********************************************************
# Example usage of the query_spatial_files_stateclass() function
# **********************************************************

# setup
import sqlite3, sys
from ssim_api.ssim_query_functions import db_query_stateclass, db_query_transitiongroup, db_query_stock, project_summary
## To do add stratum and secondary stratum id and name programatically to strata and secondary strata tables.

# define .ssim connection
sqlite_file = r"/home/jsherba-pr/Projects/landcarbon-cdi/landcarbon/media/California_Climate_Assessment_Model_v3.0.37.ssim"



# define query vals
project_id = (4008,)
table_name_dic = {"stateclass":"STSim_OutputStratumState", "stock": "SF_OutputStock", "transition": "STSim_OutputStratumTransition"}
group_by_dic = {"stateclass": [("IDScenario", "Timestep","Iteration", "StateLabelX","StateLabelY", "Stratum", "SecondaryStratum")],
                "stock":[("IDScenario", "Timestep","StockType", "Iteration", "StateClass", "Stratum"), ("IDScenario", "Timestep","StockType", "Iteration","StateClass", "SecondaryStratum"), ("IDScenario", "Timestep","StockType", "Iteration","StateClass")],
                "transition":[("IDScenario", "Timestep","Iteration", "TransitionGroup", "Stratum", "AgeMin", "AgeMax"),("IDScenario", "Timestep","Iteration", "TransitionGroup", "SecondaryStratum", "AgeMin", "AgeMax"), ("IDScenario", "Timestep","Iteration", "TransitionGroup","AgeMin", "AgeMax")]}


summary = project_summary(sqlite_file, project=project_id)
stateclasstable= summary[7]
statelabeltable = summary[1]
stratatable  = summary[5]
secondary_stratatable= summary[6]
transition_groupstable= summary[3]
stocks_groupstable= summary[4]
print(summary)

stateclasstable = stateclasstable.set_index('Name').to_dict()
statelabeltable = statelabeltable.set_index('Name').to_dict()
stratatable = stratatable.set_index('Name').to_dict()
secondary_stratatable = secondary_stratatable.set_index('Name').to_dict()
transition_groupstable = transition_groupstable.set_index('Name').to_dict()
#stocks_groupstable= stocks_groupstable.set_index('Name').to_dict()
percentiles=[95]
#percentiles = range(6,21) + range(80,95)
print (percentiles)
def add_percentile_stateclass(table_type, table_name_dic, group_by_dic):
    for p in percentiles:
        group_by = group_by_dic[table_type][0]
        percentile = ("Iteration",p)
        df = db_query_stateclass(sqlite_file, project_id=project_id, scenario_id = None, state_label_x=None, iteration=None, stratum=None, secondary_stratum=None, group_by=group_by, percentile = percentile)
        print('query_done')

        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()

        for index, row in df.iterrows():
            if row.StateLabelX == "Agriculture":
                    stateclass = stateclasstable['StateClassID'][str(row.StateLabelX) + ":Annual"]
            else:
                stateclass = stateclasstable['StateClassID'][str(row.StateLabelX) + ":All"]
            #stateclass =  stateclasstable['StateClassID'][str(row.StateLabelX)+":All"]
            scenario = int(row.IDScenario)
            iteration = 1000+p
            #iteration = 1050
            timestep= int(row.Timestep)
            statex = int(statelabeltable['StateLabelXID'][row.StateLabelX])
            statey = 7118
            stratum = int(stratatable['StratumID'][row.Stratum])
            secstratum = int(secondary_stratatable['SecondaryStratumID'][row.SecondaryStratum])
            agemin=0
            agemax=0
            
            amount = float(row['pc(sum, '+str(p)+')'])
            #amount = float(row['pc(sum, 50)'])
            try:
                c.execute("INSERT INTO {tn} VALUES ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}, {col7}, {col8}, {col9}, {col10}, {col11}, {col12})". \
                          format(tn=table_name_dic[table_type], col1=scenario, col2= iteration, col3 = timestep, col4 = stratum, col5 =secstratum, col6=stateclass, col7= statex, col8= statey, col9 = agemin, col10=agemax, col11="NULL", col12=amount ))
            except sqlite3.IntegrityError:
                print("error")

        print(str(p))

        conn.commit()

        conn.close()

    print("alldone")

def add_strata_all_stock(table_type, table_name_dic, group_by_dic):

    group_by = group_by_dic[table_type][0]

    df = db_query_stock(sqlite_file, project_id=project_id, scenario_id = None, iteration=None, stratum=None, secondary_stratum=None, group_by=group_by, percentile = None)
    print('query_done')
    print(df.head())
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    for index, row in df.iterrows():
        stock =  stocks_groupstable['StockTypeID'][str(row.StockType)]
        scenario = int(row.IDScenario)
        iteration = int(row.Iteration)
        timestep= int(row.Timestep)
        stateclass = stateclasstable['StateClassID'][str(row.StateClass)]
        stratum = int(stratatable['StratumID'][row.Stratum])
        secstratum = 1
        amount = float(row['sum'])
        try:
            c.execute("INSERT INTO {tn} VALUES ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}, {col7}, {col8})". \
                      format(tn=table_name_dic[table_type], col1=scenario, col2= iteration, col3 = timestep, col4 = stratum, col5 =secstratum, col6=stateclass, col7 = stock, col8=amount ))
        except sqlite3.IntegrityError:
            print("error")

    conn.commit()

    conn.close()

    print("secondary_strata done")

    group_by = group_by_dic[table_type][1]

    df =  db_query_stock(sqlite_file, project_id=project_id, scenario_id = None, iteration=None, stratum=None, secondary_stratum=None, group_by=group_by, percentile = None)
    print('query_done')


    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    for index, row in df.iterrows():
        stock = stocks_groupstable['StockTypeID'][str(row.StockType)]
        scenario = int(row.IDScenario)
        iteration = int(row.Iteration)
        timestep = int(row.Timestep)
        stateclass = stateclasstable['StateClassID'][str(row.StateClass)]
        stratum = 1
        secstratum = int(secondary_stratatable['SecondaryStratumID'][row.SecondaryStratum])
        amount = float(row['sum'])
        try:
            c.execute("INSERT INTO {tn} VALUES ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}, {col7}, {col8})". \
                      format(tn=table_name_dic[table_type], col1=scenario, col2=iteration, col3=timestep, col4=stratum,
                             col5=secstratum, col6=stateclass, col7=stock, col8=amount))
        except sqlite3.IntegrityError:
            print("error")

    conn.commit()

    conn.close()

    print("strata done")

    group_by = group_by_dic[table_type][2]

    df = db_query_stock(sqlite_file, project_id=project_id, scenario_id = None, iteration=None, stratum=None, secondary_stratum=None, group_by=group_by, percentile = None)
    print('query_done')


    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    for index, row in df.iterrows():
        stock = stocks_groupstable['StockTypeID'][str(row.StockType)]
        scenario = int(row.IDScenario)
        iteration = int(row.Iteration)
        timestep = int(row.Timestep)
        stateclass = stateclasstable['StateClassID'][str(row.StateClass)]
        stratum = 1
        secstratum = 1
        amount = float(row['sum'])
        try:
            c.execute("INSERT INTO {tn} VALUES ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}, {col7}, {col8})". \
                      format(tn=table_name_dic[table_type], col1=scenario, col2=iteration, col3=timestep, col4=stratum,
                             col5=secstratum, col6=stateclass, col7=stock, col8=amount))
        except sqlite3.IntegrityError:
            print("error")

    conn.commit()

    conn.close()


    print("alldone")

def add_strata_all_transition(table_type, table_name_dic, group_by_dic):

    group_by = group_by_dic[table_type][0]

    df = db_query_transitiongroup(sqlite_file, project_id=project_id, scenario_id = None, iteration=None, stratum=None, secondary_stratum=None, group_by= group_by, percentile = None)
    print('query_done')

    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    for index, row in df.iterrows():
        transtition =  transition_groupstable['TransitionGroupID'][str(row.TransitionGroup)]
        scenario = int(row.IDScenario)
        iteration = int(row.Iteration)
        timestep= int(row.Timestep)
        stratum = int(stratatable['StratumID'][row.Stratum])
        secstratum = 1
        agemin = 0
        agemax = 0
        ageclass ="NULL"
        amount = float(row['sum'])
        try:
            c.execute("INSERT INTO {tn} VALUES ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}, {col7}, {col8}, {col9}, {col10})". \
                      format(tn=table_name_dic[table_type], col1=scenario, col2= iteration, col3 = timestep, col4 = stratum, col5 =secstratum, col6=transtition, col7 = agemin, col8=agemax, col9=ageclass, col10=amount))
        except sqlite3.IntegrityError:
            print("error")

    conn.commit()

    conn.close()

    print("secondary_strata done")

    group_by = group_by_dic[table_type][1]

    df = db_query_transitiongroup(sqlite_file, project_id=project_id, scenario_id = None, iteration=None, stratum=None, secondary_stratum=None, group_by= group_by, percentile = None)
    print('query_done')


    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    for index, row in df.iterrows():
        transtition = transition_groupstable['TransitionGroupID'][str(row.TransitionGroup)]
        scenario = int(row.IDScenario)
        iteration = int(row.Iteration)
        timestep = int(row.Timestep)
        stratum = 1
        secstratum = int(secondary_stratatable['SecondaryStratumID'][row.SecondaryStratum])
        agemin = 0
        agemax = 0
        ageclass = "NULL"
        amount = float(row['sum'])
        try:
            c.execute(
                "INSERT INTO {tn} VALUES ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}, {col7}, {col8}, {col9}, {col10})". \
                format(tn=table_name_dic[table_type], col1=scenario, col2=iteration, col3=timestep, col4=stratum,
                       col5=secstratum, col6=transtition, col7=agemin, col8=agemax, col9=ageclass, col10=amount))
        except sqlite3.IntegrityError:
            print("error")

    conn.commit()

    conn.close()

    print("strata done")

    group_by = group_by_dic[table_type][2]

    df = db_query_transitiongroup(sqlite_file, project_id=project_id, scenario_id=None, iteration=None, stratum=None, secondary_stratum=None, group_by=group_by, percentile=None)
    print('query_done')


    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    for index, row in df.iterrows():
        transtition = transition_groupstable['TransitionGroupID'][str(row.TransitionGroup)]
        scenario = int(row.IDScenario)
        iteration = int(row.Iteration)
        timestep = int(row.Timestep)
        stratum = 1
        secstratum = 1
        agemin = 0
        agemax = 0
        ageclass = "NULL"
        amount = float(row['sum'])
        try:
            c.execute(
                "INSERT INTO {tn} VALUES ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}, {col7}, {col8}, {col9}, {col10})". \
                    format(tn=table_name_dic[table_type], col1=scenario, col2=iteration, col3=timestep, col4=stratum,
                           col5=secstratum, col6=transtition, col7=agemin, col8=agemax, col9=ageclass, col10=amount))
        except sqlite3.IntegrityError:
            print("error")

    conn.commit()

    conn.close()



    print("alldone")

table_type = "stateclass" #stock transition
add_percentile_stateclass(table_type, table_name_dic, group_by_dic)

#table_type = "stock"
#add_strata_all_stock(table_type, table_name_dic, group_by_dic)

#table_type = "transition"
#add_strata_all_transition(table_type, table_name_dic, group_by_dic)