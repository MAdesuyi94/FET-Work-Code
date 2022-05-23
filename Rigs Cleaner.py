# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 13:18:16 2021

@author: Matthew.Adesuyi
"""

import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta

folder = "C:\\Users\\matthew.adesuyi\\OneDrive - Forum Energy Technologies\\Documents\\"
rigs_0 = pd.read_csv(folder+"env_csv-rigTimeSeries-dcf1f_2022-05-23.csv")
rigs_1 = pd.read_csv(folder+"rseg_rig_timeseries_view-246133.csv")
rigs_2 = pd.read_csv(folder+"rseg_rig_timeseries_view-236512.csv")
frac = pd.read_csv(folder+"env_csv-fracCrewsTimeSeries-fa74b_2022-05-23.csv")
rigs = pd.concat([rigs_0,rigs_1,rigs_2],ignore_index=True)
rigs.reset_index(inplace=True)
rigs.drop('index',axis=1,inplace=True)

def basin_assign(basin):
    env_list = ['ANADARKO', 'ARKOMA','APPALACHIAN', 'MIDLAND',
                'WESTERN GULF', 'DELAWARE', 'ARK-LA-TX', 'UINTA',
                'DENVER-JULESBURG', 'WILLISTON', 'ARDMORE', 'CHEROKEE PLATFORM',
                'PERMIAN OTHER', 'FORT WORTH', 'POWDER RIVER',
                'GREATER GREEN RIVER', 'SAN JUAN', 'MID-CONTINENT OTHER',
                'NORTH PARK', 'MARIETTA', 'WESTERN US OTHER', 'PICEANCE',
                'PALO DURO', 'BIGHORN', 'OTHER MONTANA', 'WIND RIVER',
                'BLACK WARRIOR','GOM OFFSHORE', 'ILLINOIS','SANTA MARIA', 'LOS ANGELES', 'SACRAMENTO',
                'MICHIGAN', 'VENTURA','FOREST CITY',
                'PARADOX', 'VALLEY AND RIDGE',
                'BRAVO DOME', 'RATON']
    fet_list = ['MidCon','MidCon','NorthEast','Permian','Eagleford','Permian',
                'Haynesville','Rockies','Rockies','Bakken','MidCon','MidCon',
                'Permian','MidCon','Rockies','Rockies','Rockies','MidCon',
                'Rockies','MidCon','California','Rockies','Permian','Rockies',
                'Rockies','Rockies','Other','Other','Other','California',
                'California','California','Other','California','MidCon',
                'Rockies','NorthEast','Permian','Rockies']
    for e,f in zip(env_list,fet_list):
        if basin == e:
            return(f)
        
frac['Basin'] = frac['RSBasin'].apply(basin_assign)
frac.loc[pd.isnull(frac['Basin']),'Basin'] = 'Other'
frac['DateDetected'] = pd.to_datetime(frac['DateDetected']).dt.date

rigs['Public or Private'] = rigs['ENV_Peer_Group'].apply(lambda x: 'Private' if x == 'Non-PE-Backed Private' else ('Private' if x == 'PE-Backed' else ('Private' if pd.isnull(x) else 'Public')))
rigs['Basin'] = rigs['ENVBasin'].apply(basin_assign)
rigs.loc[pd.isnull(rigs['Basin']),'Basin'] = 'Other'


date_range2 = pd.Series(pd.date_range('2014-01-01',end=date.today(),freq='10D'))
date_range2_end = date_range2 + timedelta(days=9)
date_range_2_total = pd.concat([date_range2,date_range2_end],axis=1).rename(columns={0:'Period Start',
                                                                                     1:'Period End'})
date_range_2_total['Period Start'] = pd.DatetimeIndex(date_range_2_total['Period Start']).date
date_range_2_total['Period End'] = pd.DatetimeIndex(date_range_2_total['Period End']).date
date_range = pd.period_range(start='2014-01-01',end=date.today(),freq='W-THU')
date_range = date_range.astype(str)
date_range = date_range.str.split('/').str[0]
date_range = pd.Series(date_range)
date_range = pd.to_datetime(date_range).dt.date
date_range_end = date_range + timedelta(days=6)
date_range_total = pd.concat([date_range,date_range_end],axis=1)
date_range_total.columns = ['Week Start','Week End']

def week_assign(day):
    date_start = date_range_total['Week Start'].tolist()
    date_end = date_range_total['Week End'].tolist()
    for s,e in zip(date_start,date_end):
        if day >=s:
            if day <= e:
                return(s)
                break
            
def ten_day_assign(day):
    date_start = date_range_2_total['Period Start'].tolist()
    date_end = date_range_2_total['Period End'].tolist()
    for s,e in zip(date_start,date_end):
        if day >=s:
            if day <= e:
                return(s)
                break

frac['Week Start'] = frac['DateDetected'].apply(week_assign)
frac['Ten Day Start'] = frac['DateDetected'].apply(ten_day_assign)
week_start = frac.pop('Week Start')
ten_day_start = frac.pop('Ten Day Start')
frac.insert(2,'Week Start',week_start)
frac.insert(2,'Ten Day Start',ten_day_start)
#frac.drop_duplicates(subset=['PadID','Week Start'],inplace=True,ignore_index=True)
    
def rig_date_check(rn,ws):
    if [rn,ws-timedelta(days=7)] in rigs_date_list:
        return('No')
    elif [rn,ws-timedelta(days=14)] in rigs_date_list:
        return('No')
    elif [rn,ws-timedelta(days=21)] in rigs_date_list:
        return('No')
    elif [rn,ws-timedelta(days=28)] in rigs_date_list:
        return('No')
    else:
        return('Yes')

rigs['EntryDate'] = pd.to_datetime(rigs['EntryDate']).dt.date
rigs['Week Start?'] = rigs['EntryDate'].apply(lambda x: True if x in date_range.tolist() else False)
rigs['FirstDay'] = pd.DatetimeIndex(rigs['FirstDay']).date
rigs = rigs.loc[rigs['Week Start?'] == True]
rigs.drop('Week Start?',axis=1,inplace=True)
rigs.rename(columns={'EntryDate':'Week Start'},inplace=True)
rig_count = rigs.groupby('Week Start').size()
latest_week = week_start.sort_values(ascending=False).reset_index().loc[0,'Week Start']
second_latest_week = rigs['Week Start'].drop_duplicates().sort_values(ascending=False).reset_index().loc[1,'Week Start']
latest_full_date = frac['DateDetected'].drop_duplicates().sort_values(ascending=False).reset_index().loc[5,'DateDetected']
rigs_by_date = rigs[['RigName_Number','Week Start']].drop_duplicates().reset_index(drop=True)
rigs_date_list = rigs_by_date.values.tolist()
rigs_by_date['New Rig'] = rigs_by_date.apply(lambda x: rig_date_check(x['RigName_Number'],x['Week Start']),axis=1)
#rigs_by_date['New Rig'] = rigs_by_date['New Rig'].apply(lambda x: 'No' if x == 'Yes' else 'Yes')

rigs['Latest Week'] = rigs['Week Start'].apply(lambda x: 'Yes' if x == latest_week else 'No')
rigs = rigs.merge(rigs_by_date,on=['RigName_Number','Week Start'])
frac['Second Latest Week'] = frac['Week Start'].apply(lambda x: 'Yes' if x == second_latest_week else 'No')
frac['Latest Full Date'] = frac['DateDetected'].apply(lambda x: 'Yes' if x == latest_full_date else 'No')
#frac_count = frac.groupby(['Week Start']).size()
frac_count = frac.groupby(['Ten Day Start','DateDetected']).size().groupby('Ten Day Start').median()
#frac_count.to_excel(folder+'Frac Count by Group.xlsx')
frac.to_csv(folder+"Frac Count Clean.csv",index=False)
rigs.to_csv(folder+"Rig Count Clean.csv",index=False)   
