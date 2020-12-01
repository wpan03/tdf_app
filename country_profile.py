import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st


def get_overview(df):
    info_name = ["Total Number of Projects", "Total Transaction Amount(current usd)"]
    info_value = [df.shape[0], df["usd_current"].sum()]
    df_overview = pd.DataFrame({"name": info_name, "value": info_value})
    return df_overview


def table(df, col):
    abs_count = df[col].value_counts()
    rel_count = np.round(abs_count.values / df.shape[0], 3)

    return pd.DataFrame({col: abs_count.index.values,
                         'count': abs_count.values,
                         'percentage': rel_count})


def group_select_box(key):
    return st.selectbox('How would you like to break down the project',
                        ('flow_class', 'flow', 'crs_sector_name', 'status'), key=key)


def total_transaction_amount_plot(df, select):
    df_trans = df.groupby(select).sum()['usd_current'].reset_index()
    df_trans['percentage'] = np.round(df_trans["usd_current"] / (df[["usd_current"]].sum().values.item()), 3)
    df_trans.sort_values("usd_current", ascending=False, inplace=True)
    fig_trans_group = px.bar(df_trans, x=select, y="usd_current",
                             hover_data=[select, 'usd_current', 'percentage'],
                             title="Total Transaction Amount in Each Category")
    return fig_trans_group


def year_slider(the_min=2000, the_max=2020, key=None):
    return st.slider('', the_min, the_max, value=[the_min, the_max], key=key)


def year_filter(df_input, year_range, include_year_undef=False):
    df = df_input.copy()
    df['year'] = df['year'].fillna(0)
    year_min = year_range[0]
    year_max = year_range[1]
    df = df[(df['year'] >= year_min) & (df['year'] <= year_max) | (df['year'] == 0)]
    if include_year_undef:
        df = df.query('year != 0')
    return df


def seg_type_widget(key):
    seg_type = st.selectbox("What variables do you want to plot separately?",
                            ("None", 'crs_sector_name', 'flow_class', 'status'),
                            key=key)
    return seg_type


def graph_type_widget(key):
    graph_type = st.radio("What type of graph do you want to plot", ('line', 'bar'), key=key)
    return graph_type


def cat_filter(df_input,crs_select, flow_class_select):
    df = df_input.copy()
    df = df[(df['crs_sector_name'].isin(crs_select)) & (df['flow_class'].isin(flow_class_select))].reset_index()
    return df


def plot_over_time(df, col, break_by, graph_type):
    if break_by == "None":
        df_time = df.groupby('year').agg(count=('project_id', 'count'),
                                         usd_current=('usd_current', 'sum')).reset_index()
        if graph_type == 'line':
            fig_time = px.line(df_time, x='year', y=col, color=None)
        elif graph_type == 'bar':
            fig_time = px.bar(df_time, x='year', y=col)
    else:
        df_time = df.groupby(['year', break_by]).agg(count=('project_id', 'count'),
                                                     usd_current=('usd_current', 'sum')).reset_index()
        if graph_type == 'line':
            fig_time = px.line(df_time, x='year', y=col, color=break_by)
        elif graph_type == 'bar':
            fig_time = px.bar(df_time, x='year', y=col, color=break_by)

    return fig_time


def country_profile():
    st.title('Country Profile')

    uploaded_file = st.file_uploader("Choose an export csv file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        official_finance = st.checkbox('Only Select Official Finance')
        if official_finance:
            df = df.query('is_official_finance == 1').reset_index(drop=True)

        st.header("Overview")
        df_overview = get_overview(df)
        st.dataframe(df_overview)

        st.header("3 Most Important Projects")
        df_most_value = df.sort_values('usd_current', ascending=False, ignore_index=True)[
            ['project_id', 'title', 'usd_current']].head(3)
        st.table(df_most_value)

        st.header("Information By Category")
        st.subheader("Filter")
        st.markdown("#### By Year")
        year_range = year_slider()
        include_year_undefine = st.checkbox('Include Year Undefined')
        df_select = year_filter(df, year_range, include_year_undefine)

        st.subheader("Number of Projects")
        group_option_1 = group_select_box("first time")
        df_count_group = table(df_select, group_option_1)
        fig_count_group = px.bar(df_count_group, x=group_option_1, y="count",
                                 hover_data=[group_option_1, 'count', 'percentage'],
                                 title="Number of Projects in Each Category")
        st.plotly_chart(fig_count_group)

        st.subheader("Transaction Amount")
        group_option_2 = group_select_box("second time")
        fig_trans_group = total_transaction_amount_plot(df_select, group_option_2)
        st.plotly_chart(fig_trans_group)

        st.header("Information Overtime")
        st.text("Note: projects with undefined year are excluded.")

        st.subheader('Filter')
        st.markdown('#### CRS Sector')
        crs_select = st.multiselect("", options=list(df['crs_sector_name'].unique()),
                                    default=list(df['crs_sector_name'].unique()))
        st.markdown('#### flow class')
        flow_class_select = st.multiselect("", options=list(df['flow_class'].unique()),
                                           default=list(df['flow_class'].unique()))
        df_cat_select = cat_filter(df,crs_select, flow_class_select)

        st.subheader("Number of Projects")
        seg_type_1 = seg_type_widget(key='first')
        graph_type_1 = graph_type_widget(key='first')
        fig_count_time = plot_over_time(df_cat_select, 'count', seg_type_1, graph_type_1)
        fig_count_time.update_layout(title="Number of Projects Over Time")
        st.plotly_chart(fig_count_time)

        st.subheader("Transaction Amount")
        seg_type_2 = seg_type_widget(key='second')
        graph_type_2 = graph_type_widget(key='second')
        fig_count_usd = plot_over_time(df_cat_select, 'usd_current', seg_type_2, graph_type_2)
        fig_count_usd.update_layout(title="Transaction Amount Over Time")
        st.plotly_chart(fig_count_usd)
