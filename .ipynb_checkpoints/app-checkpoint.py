# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 09:23:45 2021

@author: kingl
"""

import streamlit as st
import pandas as pd
import base64
from data_export import *

# format app to fill screen width
st.set_page_config(layout="wide")

# set main title of application
st.title('MaxPreps High School Football Score and Stat Scraper')

uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")

def scrape_fun():
    try:
        final_output = data_export(output_df)
        st.write('Scores and Stats File: ')
        st.dataframe(final_output)
        st.markdown(get_table_download_link(final_output), unsafe_allow_html=True)
        return
    except:
        st.write('Output could not be generated for the file input.')
        
def get_table_download_link(df):
    """Generates a link allowing the data in a given pandas dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="export.csv">Download .csv file</a>'
    return(href)

if uploaded_file:
    uploaded_df = pd.ExcelFile(uploaded_file)
    uploaded_sheet_names = list(pd.read_excel(uploaded_df, sheet_name = None).keys())
    
    sheet = st.selectbox('Sheets: ',
                         uploaded_sheet_names)
    
    st.write("Your sheet is: ", sheet)
    
    output_df = pd.read_excel(uploaded_df, sheet_name = sheet)

    st.dataframe(output_df)
    
    if st.button('Get Scores and Stats'):
        scrape_fun()
    
    