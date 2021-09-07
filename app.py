# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 09:23:45 2021

@author: kingl
"""

# import relevant packages and functions
import streamlit as st
import pandas as pd
import base64
from functions.data_export import *

# format app to fill screen width
st.set_page_config(layout="wide")

# set main title of application
st.title('MaxPreps High School Football Score and Stat Scraper')

# allow user to upload an excel file to be scraped
uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")

# function to scrape data upon click of a button
def scrape_fun():
    try:
        # save the data_export output for the file that was input
        final_output = data_export(output_df)
        # display the export file
        st.write('Scores and Stats File: ')
        st.dataframe(final_output)
        # provide a link to download the file
        st.markdown(get_table_download_link(final_output), unsafe_allow_html=True)
        return
    except:
        # if no file output, print error message
        st.write('Output could not be generated for the file input. Make sure columns are present for MaxPreps Link and Game Date in the file of interest.')

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
    st.dataframe(output_df)
    
    # if the scrape button is clicked, execute the scrape function
    if st.button('Get Scores and Stats'):
        scrape_fun()
    
    