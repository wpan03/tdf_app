import streamlit as st
import pandas as pd
import base64


def reshape_dataframe(df):
    """
    Only keep columns with created projects information in the dataframe

    Parameters
    ----------
    df : pd.DataFrame
        a dataframe with format from general tab of OCP spreadsheet 

    Returns
    -------
    df : pd.DataFrame
    the shrinked dataframe 
    """
    filter_col = [col for col in df if col.startswith('Projects Created')]
    df = df[filter_col]
    df = df.dropna(axis=1, how='all')
    df = df.melt().dropna(axis=0)
    return df

def merge_df(all_sheet):
    """merge the created project id in each tab"""

    store = []
    sheets = all_sheet.sheet_names

    for i in range(len(sheets)):
        if i == 0:
            df = all_sheet.parse(i, skiprows=[0])
            df = reshape_dataframe(df)
            df_select = df.loc[:, ['value']].reset_index(drop=True)
            df_select.columns = ['Projects Created']
        elif i == 1:
            df = all_sheet.parse(i)
            df_select = df[['Created Project ID']]
            df_select.columns = ['Projects Created']
        elif i >= 2:
            df = all_sheet.parse(i)
            df_select = df[['Projects Created']]

        store.append(df_select)
        
    df_merged = pd.concat(store).dropna().reset_index(drop=True) 

    return df_merged

def clean_merge(df, delimiter):

        # break projects in one cell to one project per row
        df['Projects Created'] = df['Projects Created'].astype(str)
        special = df['Projects Created'].str.split(delimiter).notnull()
        df.loc[special, 'Projects Created'] = df[special]['Projects Created'].str.split(
            delimiter)
        df = df.explode('Projects Created')

        # Format each cell
        df['Projects Created'] = df['Projects Created'].astype(str)
        special1 = df['Projects Created'].str.strip().notnull()
        df.loc[special1, 'Projects Created'] = df[special1]['Projects Created'].str.strip()

        # Drop duplicate
        df_clean = df.drop_duplicates(
            'Projects Created').reset_index(drop=True)

        return df_clean

def get_create_ocp(file, delimiter):

    all_sheet = pd.ExcelFile(file)
    df_merged = merge_df(all_sheet)
    df_clean = clean_merge(df_merged, delimiter)

    return df_clean

def make_page_title():

    st.subheader('Transfer OCP Created Project')

    ocp_create_requirement = st.checkbox('ocp create requirment')
    if ocp_create_requirement:
        st.markdown(
            "+ The tab in the excel file should have following order: General Tab, Project List, and Year Tab.")
        st.markdown(
            "+ There should be one line above the header in the general tab")
        st.markdown(
            "+ There should be no line above the header in the project list and year tab")

def break_line_area(delimiter):

    st.subheader('Break text to different line')
    text_input = st.text_input('text')
    text_input_list = text_input.split(delimiter)
    if st.button('Split!'):
        for i in text_input_list:
            st.write(i)

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string"""

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def ocp_transfer_created():
    
    make_page_title()

    uploaded_file = st.file_uploader(
        "Choose a the stage 1 excel file", type="xlsx")
    country = st.text_input('Country')
    delimiter = st.text_input('What delimiter stage 1 RA use to separate project id?', ',')

    if st.button('Start Transfer!'):
        df_ocp = get_create_ocp(uploaded_file, delimiter)
        df_ocp['source'] = 'OCP'
        df_ocp['country'] = country
        df_ocp = df_ocp[['source', 'country', 'Projects Created']]


        st.markdown(get_table_download_link(df_ocp), unsafe_allow_html=True)
        st.text('Congratulations!')
        st.text("You transferred about {} projects".format(df_ocp.shape[0]))

    break_line_area(delimiter)
