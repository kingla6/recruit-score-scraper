# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 15:16:17 2021

@author: kingl
"""

#import relevant packages
import requests as rq
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

def stat_scraper(player_url, year = '21-22'):
    
    #initialize empty dataframe for all player stats
    all_player_stats = pd.DataFrame(columns = ['Player', 'Date', 'Result', 'Opponent', 'Stats_Condensed'])

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

        #continue to next iteration if no stats for current season
        if season_page.find_all('span', class_ = 'pagination-item')[1].getText().split(' ')[1] != year:
            continue

        #initialize html for stat tables of current season, which has been confirmed as the year of interest
        season_stats = season_page.find('div', class_ = "stats-grids")

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
        ##re-sorting stats by game date while maintaining order MaxPreps table display order
        player_stats.reset_index(level=0, inplace=True)
        player_stats = player_stats.sort_values(by=['Date', 'index']).drop(['index'], axis=1).reset_index(drop = True)
        ##drop statistics from table that player did not record
        player_stats = player_stats.drop(player_stats[player_stats.Value.isin(['0', '.0', ''])].index).reset_index(drop = True)

        #condensing player stats down to one row per game
        player_stats_alter = player_stats.loc[:]
        player_stats_alter['Stat_Value'] = player_stats_alter['Stat'] + ': ' + player_stats_alter['Value']
        player_stats_alter_stat_value_df = player_stats_alter.groupby(['Player', 'Date', 'Result', 'Opponent', 'Table'],
                                                                      sort = False)['Stat_Value'].apply(', '.join).reset_index()
        player_stats_alter_stat_value_df['Stats_Condensed'] = player_stats_alter_stat_value_df['Table'] + ' - ' + player_stats_alter_stat_value_df['Stat_Value']
        player_stats_condensed = player_stats_alter_stat_value_df.groupby(['Player', 'Date', 'Result', 'Opponent'], sort = False)['Stats_Condensed'].apply('; '.join).reset_index()

        #might want to think about selecting the most recent game for each player 
        #(code to do so is below, make sure you sub this into the appending to all_player_stats)
        ##recent_player_stats_condensed = player_stats_condensed[player_stats_condensed.Date == max(player_stats_condensed.Date)]

        #append final condensed stats for current player into all player df
        all_player_stats = all_player_stats.append(player_stats_condensed).reset_index(drop = True) #recent_player_stats_condensed for only most recent game appended
        
    #return final stat table for all players
    return(all_player_stats)