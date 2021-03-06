import pandas as pd
import numpy as np
import streamlit as st
import base64


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def merge():
    st.header('Merge according to project id')
    export_file = st.file_uploader("Choose an exported csv file", type="csv")
    stage2_file = st.file_uploader(
        'Choose the stage 2 / qa excel file', type='xlsx')

    if (export_file is not None) and (stage2_file is not None):
        stage2_sheet = pd.ExcelFile(stage2_file)
        sheet = st.selectbox(
            'Which tab in the stage 2 / qa spreadsheet?', stage2_sheet.sheet_names)
        df_stage2 = pd.read_excel(stage2_file, sheet_name=sheet)
        df_export = pd.read_csv(export_file, dtype={'year': 'string'})

        df_stage2.columns = df_stage2.columns.str.strip()
        the_id = [s for s in list(df_stage2.columns) if "id" in s.lower()][0]

        # Add info for year uncertain
        df_export['year'] = df_export['year'].fillna('')
        df_export['year_info'] = np.where(df_export['year_uncertain'] is True, '(uncertain)', '')
        df_export['year_acc'] = df_export['year'] + df_export['year_info']
        df_export.drop('year_info', axis=1, inplace=True)

        # Select Country
        country = st.multiselect('Which countries?', df_stage2['Country'].unique())
        df_stage2 = df_stage2[df_stage2['Country'].isin(country)]

        # Choose idenifier
        left_identifier = st.text_input('stage 2 / qa identifier', value=the_id)
        right_identifier = st.text_input(
            'export identifier', value='project_id')
        how_to_merge = st.text_input('how to merge', value='left')

        if st.button('merge'):
            df_merge = pd.merge(df_stage2, df_export, left_on=left_identifier,
                                right_on=right_identifier, how=how_to_merge)

            selections = ['project_id', 'year_acc', 'flow_class', 'flow', 'usd_current', 'Country']
            df_merge = df_merge[selections]
            st.markdown(get_table_download_link(
                df_merge), unsafe_allow_html=True)
