# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 08:55:46 2021

@author: kingl
"""

#import relevant packages
import datetime

##dependencies for function call
import pandas as pd

##function
from functions.stat_scraper_1 import *

def data_export(uploaded_file):
    
    #read in the excel file of interest, given by the user
    input_table = uploaded_file
    
    #data cleaning of input file
    ##toss observations with no MaxPreps link or game date
    input_part = input_table[input_table['MaxPreps Link'].notna() & input_table['Game Date'].notna()].reset_index(drop = True)
    ##change format of game date to match MaxPreps data
    input_part['Game Date'] = input_part['Game Date'].astype(str).apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').strftime('%m/%d'))
    
    #scrape stats for all players
    input_stats = stat_scraper_1(input_part['MaxPreps Link'])
    
    #merge stats with this week's data, dropping and renaming columns as necessary
    input_merge = pd.merge(input_part, input_stats, left_on = ['MaxPreps Link', 'Game Date'], right_on = ['Player', 'Date'], how = 'left').drop(['Player', 'Date'], axis=1).rename(columns = {'Result_x': 'Result', 'Result_y': 'Scraped_Result'}).drop(['Game Date', 'MaxPreps Link', 'Opponent'], axis = 1)
    
    #merge back to the main page of data, goal of this is to create output file identical to google sheet format
    final_merge = pd.merge(input_table, input_merge, how = 'left')
    
    #cleaning of final export file
    final_merge[['Result', 'Record', 'Stats/Notes']] = final_merge[['Scraped_Result', 'Current_Record', 'Stats_Condensed']]
    final_merge['Record'] = '(' + final_merge['Record'] + ')'
    export = final_merge.drop(['Scraped_Result', 'Current_Record', 'Stats_Condensed'], axis = 1)
    
    #return the export file
    return(export)