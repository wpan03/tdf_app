import streamlit as st
import pandas as pd
import base64


def reshape_dataframe(df):
    """
    Only keep columns with created projects information in the dataframe
    and reshape those columns to a single column

    Parameters
    ----------
    df : pd.DataFrame
        a dataframe with format from general tab of OCP spreadsheet 

    Returns
    -------
    df : pd.DataFrame
    the reshpaed dataframe
    """

    filter_col = [col for col in df if col.startswith('Projects Created')]
    df = df[filter_col]
    df = df.dropna(axis=1, how='all')
    df = df.melt().dropna(axis=0)
    return df


def merge_df(all_sheet, update_2018=True):
    """
    merge the created project id in each tab

    Parameters
    ----------
    all_sheet: the output of pd.Excelfile()

    update_2018: bool
    Determine whether the input stage 1 excel is in 2018 updated format


    Returns
    -------
    df : pd.DataFrame
    a dataframe contains all project ids from stage 1 excel sheet
    """

    store = []
    sheets = all_sheet.sheet_names

    if update_2018:
        for i in range(len(sheets)):
            if i == 0:
                df = all_sheet.parse(i, skiprows=[0])
                df = reshape_dataframe(df)
                df_select = df.loc[:, ['value']].reset_index(drop=True)
                df_select.columns = ['Projects Created']
            elif i == 1:
                df = all_sheet.parse(i)
                for i in list(df.columns):
                    if 'Created' in i:
                        select1 = i
                        df_select = df[[select1]]
                        df_select.columns = ['Projects Created']
                        break
            elif i == 2:
                df = all_sheet.parse(i)
                df_select = df[['Created Project ID']]
                df_select.columns = ['Projects Created']
            elif i >= 3:
                df = all_sheet.parse(i)
                df_select = df[['Projects Created']]

            store.append(df_select)

    else:
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
    """
    break cell with multiple projects to one project per cell and drop duplicate project id

    Parameters
    ----------
    df: pd.DataFrame
    output of the function merge_df

    delimiter: str
    What delimiter stage 1 coder uses to separate project

    Returns
    -------
    df: pd.DataFrame
    """

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


def get_create_ocp(file, delimiter, update_2018):
    """Integrate merge_df and clean_merge"""

    all_sheet = pd.ExcelFile(file)
    df_merged = merge_df(all_sheet, update_2018)
    df_clean = clean_merge(df_merged, delimiter)

    return df_clean


def make_page_title():
    """Title in the transferred created subpage"""

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
    """Create a text input area in the subpage and
    break the input text to separate lines based on delimiter"""

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
    """The main function that runs in the subpage"""

    make_page_title()

    uploaded_file = st.file_uploader(
        "Choose a the stage 1 excel file", type="xlsx")
    country = st.text_input('Country')
    delimiter = st.text_input('What delimiter stage 1 RA use to separate project id?', ',')
    update_2018 = st.checkbox('Is this excel in 2018 updated format?', value=True)

    if st.button('Start Transfer!'):
        df_ocp = get_create_ocp(uploaded_file, delimiter, update_2018)
        df_ocp['source'] = 'OCP'
        df_ocp['country'] = country
        df_ocp = df_ocp[['source', 'country', 'Projects Created']]

        st.markdown(get_table_download_link(df_ocp), unsafe_allow_html=True)
        st.text('Congratulations!')
        st.text("You transferred about {} projects".format(df_ocp.shape[0]))

    break_line_area(delimiter)
