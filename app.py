# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 09:23:45 2021

@author: kingl
"""

# import relevant packages and functions
import streamlit as st
import pandas as pd
import base64
import requests
from PIL import Image # import Image from pillow to open images
from functions.data_export import *

# format app to fill screen width
st.set_page_config(layout="wide")

# set main title of application
st.markdown("<h1 style='text-align: center;'>MaxPreps High School Football Score and Stat Scraper</h1>", unsafe_allow_html=True)

# create sidebar with multiple options
sidebar = st.sidebar.selectbox("Navigation", ("Main", "Application", "Instructions"))

# load images that will be present in the app
vandy = Image.open(requests.get("https://github.com/kingla6/recruit-score-scraper/raw/main/images/vandy.png", stream=True).raw)
instructions_1 = Image.open(requests.get("https://github.com/kingla6/recruit-score-scraper/raw/main/images/instructions_1.png", stream=True).raw)
instructions_2 = Image.open(requests.get("https://github.com/kingla6/recruit-score-scraper/raw/main/images/instructions_2.png", stream=True).raw)
instructions_3 = Image.open(requests.get("https://github.com/kingla6/recruit-score-scraper/raw/main/images/instructions_3.png", stream=True).raw)
instructions_4 = Image.open(requests.get("https://github.com/kingla6/recruit-score-scraper/raw/main/images/instructions_4.png", stream=True).raw)

# code for main page
if sidebar == 'Main':
    
    # Page Content
    st.markdown("<h2 style='text-align: center;'>Main Page</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Through the navigation sidebar, the application and instructions pages can be accessed.</h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>For documentation, code, and all other relevant files, see the <a href='https://github.com/kingla6/recruit-score-scraper'>project repo</a>.</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1]) # this allows us to center the image by selecting col2 in next line
    col2.image(vandy, use_column_width=True)
    st.markdown("<h4 style='text-align: center;'>Developed by Logan King, Graduate Recruiting Assistant - Vanderbilt Football</h4>", unsafe_allow_html=True)

# code for application page
if sidebar == 'Application':
    
    # Page Header
    st.markdown("<h2 style='text-align: center;'>Application Page</h2>", unsafe_allow_html=True)
    
    # allow user to upload an excel file to be scraped
    uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")
    
    # function to scrape data upon click of a button
    def scrape_fun():
        try:
            # save the data_export output for the file that was input
            final_output = data_export(output_df)
            # display the export file
            st.write('Scores and Stats File: ')
            # st.dataframe(final_output) sheet cannot currently be displayed bc of issues with pandas and st.dataframe https://discuss.streamlit.io/t/after-upgrade-to-the-latest-version-now-this-error-id-showing-up-arrowinvalid/15794
            # provide a link to download the file
            st.markdown(get_table_download_link(final_output), unsafe_allow_html=True)
            return
        except:
            # if no file output, print error message
            st.error('Output could not be generated for the input file. Make sure columns are present and formatted correctly for MaxPreps Link and Game Date in the sheet of interest.')
    
    # download link function found at: https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806        
    def get_table_download_link(df):
        """Generates a link allowing the data in a given pandas dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="export.csv">Download .csv file</a>'
        return(href)
    
    # when a file is uploaded, execute the following
    if uploaded_file:
        # read in the excel file
        uploaded_df = pd.ExcelFile(uploaded_file)
        # get a list of sheet names from the excel file
        uploaded_sheet_names = list(pd.read_excel(uploaded_df, sheet_name = None).keys())
        # allow the user to select a sheet
        sheet = st.selectbox('Sheets: ',
                             uploaded_sheet_names)
        st.write("Your sheet is: ", sheet)
        # read the sheet that was selected and display the sheet
        output_df = pd.read_excel(uploaded_df, sheet_name = sheet)
        # st.dataframe(output_df) sheet cannot currently be displayed bc of issues with pandas and st.dataframe https://discuss.streamlit.io/t/after-upgrade-to-the-latest-version-now-this-error-id-showing-up-arrowinvalid/15794
        
        # if the scrape button is clicked, execute the scrape function
        if st.button('Get Scores and Stats'):
            scrape_fun()
  
# code for instructions page
if sidebar == 'Instructions':
    
    # Header
    st.markdown("<h2 style='text-align: center;'>Instructions Page</h2>", unsafe_allow_html=True)
    
    # display instructions and images
    st.markdown("<h2 style='text-align: left;'>1. Download Gametracker File</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left;'>Be sure to download the file as an .xlsx file as shown below:</h3>", unsafe_allow_html=True)
    st.image(instructions_1)

    st.markdown("<h2 style='text-align: left;'>2. Load file into application and select desired sheet</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left;'>Once the sheet loads, click the button to collect scores and stats for that week.</h3>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: left;'><em>This can take several minutes, so do NOT hit back or refresh in the browser!</em></h4>", unsafe_allow_html=True)
    st.image(instructions_2)
    
    st.markdown("<h2 style='text-align: left;'>3. Download the .csv file using the link that appears</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left;'>Congratulations, you've gotten all scores and stats for the players on MaxPreps this week!</h3>", unsafe_allow_html=True)
    st.image(instructions_3)
    
    st.markdown("<h2 style='text-align: left;'>Errors</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left;'>If you input a sheet without the necessary columns to collect data, the following error will appear:</h3>", unsafe_allow_html=True)
    st.image(instructions_4)