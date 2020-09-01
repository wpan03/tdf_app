import pandas as pd
import base64
import streamlit as st


def reshape_dataframe(df):
    """
    Only keep columns with amended projects information in the dataframe
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
    filter_col = [col for col in df if col.startswith('Projects Amended')]
    df = df[filter_col]
    df = df.dropna(axis=1, how='all')
    df = df.melt().dropna(axis=0)
    return df


def merge_df(all_sheet, update_2018):
    """
    merge the amended project id in each tab

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
            # General
            if i == 0:
                df = all_sheet.parse(i, skiprows=[0])
                df = reshape_dataframe(df)
                df_select = df.loc[:, ['value']].reset_index(drop=True)
                df_select.columns = ['Projects Amended']
            # Project Revisions
            elif i == 1:
                df = all_sheet.parse(i)
                for i in list(df.columns):
                    if 'Amended' in i:
                        select1 = i
                        df_select = df[[select1]]
                        df_select.columns = ['Projects Amended']
                        break
            # Project List
            elif i == 2:
                df = all_sheet.parse(i)
                for i in list(df.columns):
                    if 'Existing' in i:
                        select2 = i
                        df_select = df[[select2]]
                        df_select.columns = ['Projects Amended']
                        break
            # years tab
            elif i >= 2:
                df = all_sheet.parse(i)
                for i in list(df.columns):
                    if 'Amend' in i:
                        select3 = i
                        df_select = df[[select3]]
                        df_select.columns = ['Projects Amended']
                        break

            store.append(df_select)

    else:
        for i in range(len(sheets)):
            if i == 0:
                df = all_sheet.parse(i, skiprows=[0])
                for i in list(df.columns):
                    if 'Amended' in i:
                        select1 = i
                df_select = df[[select1]]
                df_select.columns = ['Projects Amended']
            elif i == 1:
                df = all_sheet.parse(i)
                for i in list(df.columns):
                    if 'Existing' in i:
                        select2 = i
                df_select = df[[select2]]
                df_select.columns = ['Projects Amended']
            elif i >= 2:
                df = all_sheet.parse(i)
                for i in list(df.columns):
                    if 'Amend' in i:
                        select3 = i
                df_select = df[[select3]]
                df_select.columns = ['Projects Amended']

            store.append(df_select)
    df_merged = pd.concat(store).dropna().reset_index(drop=True)
    return df_merged


def clean_df(df, delimiter):
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
    df['Projects Amended'] = df['Projects Amended'].astype(str)
    special = df['Projects Amended'].str.split(delimiter).notnull()
    df.loc[special, 'Projects Amended'] = df[special]['Projects Amended'].str.split(delimiter)
    df = df.explode('Projects Amended')

    df['Projects Amended'] = df['Projects Amended'].astype(str)
    special1 = df['Projects Amended'].str.strip().notnull()
    df.loc[special1, 'Projects Amended'] = df[special1]['Projects Amended'].str.strip()

    df_clean = df.drop_duplicates('Projects Amended').reset_index(drop=True)
    return df_clean


def get_amend(all_sheet, delimiter, update_2018):
    """extracting id from stage 1 spreadsheet"""

    df_merged = merge_df(all_sheet, update_2018)
    df_clean = clean_df(df_merged, delimiter)

    return df_clean


def make_page_title():
    """Make the title for the page"""

    st.header('Transfer Amended OCP Project')
    ocp_amend_requirement = st.checkbox('ocp amend requirment')
    if ocp_amend_requirement:
        st.markdown("+ The tab in the excel file should have following order: General Tab, Project List, and Year Tab.")
        st.markdown("+ There should be one line above the header in the general tab")
        st.markdown("+ There should be no line above the header in the project list and year tab")


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string"""

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def split_text_area(delimiter):
    """Create a text input area in the subpage and
    break the input text to separate lines based on delimiter"""

    st.subheader('Break text to different line')
    text_input = st.text_input('text')
    text_input_list = text_input.split(delimiter)
    if st.button('Split!'):
        for i in text_input_list:
            st.write(i)


def read_stage2(file):
    """Read Stage 2 Spreadsheet"""

    all_stage2_sheet = pd.ExcelFile(file)
    stage2_sheet = st.selectbox('Which tab in the stage 2 spreadsheet?', all_stage2_sheet.sheet_names)
    df_st2 = pd.read_excel(file, sheet_name=stage2_sheet)
    df_st2.columns = df_st2.columns.str.lower()

    return df_st2


def transfer_amend():
    make_page_title()

    stage1 = st.file_uploader("Choose a the stage 1 excel file", type="xlsx")
    stage2 = st.file_uploader("Choose a stage 2 excel file", type="xlsx")
    delimiter = st.text_input('What delimiter stage 1 RA use to separate project id?', ',')
    update_2018 = st.checkbox('Is this excel in 2018 updated format?', value=True)

    if (stage1 != None) and (stage2 != None):

        # Load stage1 spreadsheet
        all_sheet = pd.ExcelFile(stage1)

        # Read Stage 2 Spreadsheet
        df_st2 = read_stage2(stage2)
        country = st.selectbox('Which Country?', df_st2['country'].unique())

        if st.button('Start Transfer!'):
            # Run the function
            df_amend = get_amend(all_sheet, delimiter, update_2018)

            # Get rid of repeated id in stage 2
            id = [s for s in list(df_st2.columns) if "id" in s][0]
            stage2_list = df_st2[df_st2['country'] == country][id].reset_index(drop=True).astype(str)
            df_not_repeat = df_amend[~df_amend['Projects Amended'].isin(stage2_list)].reset_index(drop=True)

            # Export spread sheet
            df_not_repeat['Source'] = 'OCP'
            df_not_repeat['Country'] = country

            st.markdown(get_table_download_link(df_not_repeat), unsafe_allow_html=True)
            st.text('Congratulations!')
            st.text(f'You get rid of {df_amend.shape[0] - df_not_repeat.shape[0]} repeated projects')
            st.text(f"You finally transferred about {df_not_repeat.shape[0]} projects")

    split_text_area(delimiter)
