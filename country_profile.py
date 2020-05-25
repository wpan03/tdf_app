import pandas as pd 
import streamlit as st
import plotly.express as px

def get_profile():
    st.title('Country Profile')

    file = st.file_uploader("Choose an export csv file", type="csv")

    if file != None:

        df_raw  = pd.read_csv(file)
        
        def clean_df(df):
            """Only keep China-donated active, non-umbrella and official proejcts"""
            df = df[df['donor'] == 'China']
            df = df[df['umbrella_project'] == False]
            df = df[df['flow_class'].isin(['ODA-like','OOF-like','Vague (Official Finance)'])]
            df_clean = df[df['active'] == 'Active']
            return df_clean

        df = clean_df(df_raw)
        
        st.write('There are {} projects'.format(df.shape[0]))
        st.write('Total transaction amount is {} dollars'.format(df['usd_defl'].sum()))
        
        selectbox = st.selectbox(
        'Which category you want to see?',
        ('flow_class', 'intent', 'crs_sector_name')
        )
        
        summary = df[selectbox].value_counts().reset_index()
        summary.columns = [selectbox, 'count']
        st.write(summary)
        
        fig = px.bar(summary, x=selectbox, y='count')

        st.plotly_chart(fig)
    

    
    

