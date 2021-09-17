# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 10:25:55 2021

@author: kingl
"""

#import relevant packages
import requests as rq
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

def stat_scraper_1(player_url, year = '21-22'):
    
    #read in csv for relevant stats
    stat_lookup = pd.read_csv('https://raw.githubusercontent.com/kingla6/recruit-score-scraper/main/support-data/stat_lookup.csv')
    
    #initialize empty dataframe for all player stats
    all_player_stats = pd.DataFrame(columns = ['Player', 'Date', 'Result', 'Opponent', 'Current_Record', 'Table', 'Stat', 'Value'])

    #loop over all player urls
    for p in player_url:

        #change player url to the stats page
        p_cleaned = p.replace('default', 'football/stats')
        #set the relevant url, must do in parts then join together
        url_parts = [p_cleaned, '#year=', year]
        url = ''.join(url_parts)
        #use get to access the url and save the page
        page = rq.get(url)
        #save the html content of the page
        soup = bs(page.content, 'html.parser')

        #continue to next iteration if no football page
        try:
            #initialize the html page for the current season of player stats
            season_page = soup.find_all('div', class_ = 'item')[1]
        except:
            continue

        #extract current record for player's team
        record = season_page.find('dd').getText()

        #continue to next iteration if no stats for current season
        if season_page.find_all('span', class_ = 'pagination-item')[1].getText().split(' ')[1] != year:
            continue

        #initialize html for stat tables of current season, which has been confirmed as the year of interest
        season_stats = season_page.find('div', class_ = "stats-grids")

        #continue to next iteration if season stats have nonetype issue 
        #(this needs to be looked into further, affects a couple observations in testing)
        if season_stats is None:
            continue

        #initialize empty dataframe for all player stat tables to be stored in
        player_stats = pd.DataFrame(columns = ['Date', 'Result', 'Opponent', 'Table', 'Stat', 'Value'])

        #double loop allows us to isolate each table to extract data
        for i in season_stats.find_all('div'):
            for j in i.find_all('div'):

                #extract html elements for each table
                table_name = j.find_all('h4')
                n_col = len(j.find_all('a', href = '#'))
                col_names = j.find_all('a', href = '#')
                n_val = len(j.find('tbody').find_all('td'))
                vals = j.find('tbody').find_all('td')

                #extract text from html elements
                for a in table_name:
                    table_name_text = a.getText()
                col_name_text = []
                for b in col_names:
                    col_name_text.append(b.getText())
                vals_text = []
                for c in vals:
                    vals_text.append(c.getText())

                #reshape the values to store in a table with the column names
                vals_text_reshape = np.reshape(vals_text, (int(n_val/n_col), n_col))

                #combine all pieces into singular dataframe
                data = pd.DataFrame(data = vals_text_reshape, columns = col_name_text)
                data.insert(loc = 3, column = 'Table', value = table_name_text)

                #convert dataframe from wide to long
                data_long = pd.melt(data, 
                                    id_vars = ['Date', 'Result', 'Opponent', 'Table'], 
                                    var_name = 'Stat', 
                                    value_name = 'Value')

                #append data from current table to main table for current player
                player_stats = player_stats.append(data_long, ignore_index = True)

        #general cleaning of main player table
        ##add column for player url
        player_stats.insert(loc = 0, column = 'Player', value = [p]*len(player_stats))
        ##add column for team record
        player_stats.insert(loc = 4, column = 'Current_Record', value = [record]*len(player_stats))
        ##re-sorting stats by game date while maintaining order MaxPreps table display order
        player_stats.reset_index(level=0, inplace=True)
        player_stats = player_stats.sort_values(by=['Date', 'index']).drop(['index'], axis=1).reset_index(drop = True)

        #might want to think about selecting the most recent game for each player 
        #(code to do so is below, make sure you sub this into the appending to all_player_stats)
        ##recent_player_stats = player_stats[player_stats.Date == max(player_stats.Date)].reset_index(drop = True)

        #append stats for current player into all player df
        all_player_stats = all_player_stats.append(player_stats).reset_index(drop = True) #recent_player_stats for only most recent game appended

    #drop statistics from table that players did not record
    all_player_stats = all_player_stats.drop(all_player_stats[all_player_stats.Value.isin(['0', '.0', ''])].index).reset_index(drop = True).reset_index(drop = False)

    #update table to have only the stats of interest
    all_player_stats_update = pd.merge(all_player_stats, stat_lookup, on = ['Table', 'Stat']).sort_values(by=['index']).drop(['index','Table','Stat','Order','Side of Ball'], axis=1).reset_index(drop = True)

    #condensing player stats down to one row per game
    all_player_stats_alter = all_player_stats_update.loc[:]
    all_player_stats_alter['Stat_Value'] = all_player_stats_alter['Value'] + ' ' + all_player_stats_alter['New Stat']
    all_player_stats_condensed = all_player_stats_alter.groupby(['Player', 'Date', 'Result', 'Opponent', 'Current_Record'],sort = False)['Stat_Value'].apply(', '.join).reset_index().rename(columns={'Stat_Value': 'Stats_Condensed'})        
    #return final stat table for all players
    return(all_player_stats_condensed)