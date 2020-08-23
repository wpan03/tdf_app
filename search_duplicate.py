import streamlit as st
import pandas as pd
import tensorflow_hub as hub
import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import sentencepiece as spm


def filter_search(df, keyword, year_min=2000, year_max=2019, donor='China', Active=True):

    df = df[(df['year'] >= year_min) | (df['year'] == 0)]
    df = df[(df['year'] <= year_max) | (df['year'] == 0)]
    df = df[df['donor'] == donor]
    if Active is True:
        df = df[df['active'] == 'Active']
    result = df[df['description'].str.contains(keyword, na=False, case=False)| df['title'].str.contains(keyword, na=False, case=False)].reset_index(drop=True)
    return result

def load_model():
    module = hub.Module("https://tfhub.dev/google/universal-sentence-encoder-lite/2")
    return module

def process_to_IDs_in_sparse_format(sp, sentences):
    
    ids = [sp.EncodeAsIds(x) for x in sentences]
    max_len = max(len(x) for x in ids)
    dense_shape=(len(ids), max_len)
    values=[item for sublist in ids for item in sublist]
    indices=[[row,col] for row in range(len(ids)) for col in range(len(ids[row]))]
    return (values, indices, dense_shape)

def cosine(u, v):
    return np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))

def get_embedding(module, df):

    titles = df['title'].to_list()

    input_placeholder = tf.sparse_placeholder(tf.int64, shape=[None, None])
    encodings = module(
           inputs=dict(
               values=input_placeholder.values,
               indices=input_placeholder.indices,
               dense_shape=input_placeholder.dense_shape))
    
    with tf.Session() as sess:
        spm_path = sess.run(module(signature="spm_path"))

    sp = spm.SentencePieceProcessor()
    sp.Load(spm_path)

    values, indices, dense_shape = process_to_IDs_in_sparse_format(sp, titles)

    with tf.Session() as session:
        
        session.run([tf.global_variables_initializer(), tf.tables_initializer()])
        message_embeddings = session.run(
        encodings,
        feed_dict={input_placeholder.values: values,
                    input_placeholder.indices: indices,
                    input_placeholder.dense_shape: dense_shape})

    return message_embeddings


def find_most_likely_duplicate(df, project_id, embeddings):
    
    index = df[df['project_id'] == project_id].index[0]
    target = df.iloc[index, :]
    target_embed = embeddings[index]
    
    potentials = {}
    potential_titles = []
    
    for i in range(df.shape[0]):

        if i == index:
            continue
            
        comparison = df.iloc[i, :]
        com_embed = embeddings[i]
        title_score = cosine(target_embed, com_embed) * 0.3
        
        year_score = (np.abs((target['year'] - comparison['year'])) <=2) * 0.15
        flow_score = (target['flow'] == comparison['flow']) * 0.1
        official_score = (target['is_official_finance'] == comparison['is_official_finance']) * 0.1
        crs_score = (target['crs_sector_name'] == comparison['crs_sector_name']) * 0.1
        agency_score = (target['donor_agency'] == comparison['donor_agency']) * 0.05
        
        score = title_score + year_score + flow_score + crs_score + agency_score + official_score

        potentials[comparison['project_id']] = score
        potential_titles.append(comparison['title'])

    df_potentials = pd.DataFrame(potentials,index=[0]).T.reset_index()
    df_potentials.columns = ['id', 'score']
    df_potentials['title'] =  potential_titles
    df_potentials = df_potentials.sort_values('score', ascending=False).reset_index(drop=True)    
    
    
    return  df_potentials.head()

def write_useful_resources():

    st.subheader('Useful Sources')
    st.markdown("[TUFF 1.4 Guide](https://docs.google.com/document/d/1henyi4ixkRKMSH4k2Is9g-N5T8GeBWgEOINDzSaLE4c/edit)")
    st.markdown("[CRS Sector](https://www.oecd.org/dac/stats/documentupload/Budget%20identifier%20purpose%20codes_EN_Apr%202016.pdf)")
    st.markdown("[Google Translate](https://translate.google.com/)")
    st.markdown("[LIBOR](https://www.global-rates.com/interest-rates/libor/american-dollar/2017.aspx)")  

def open_project():

  if st.checkbox('open project in aiddata website'):
      project_id = st.number_input('project_id', value = 0)
      if project_id != 0:
          st.markdown("[Open Project](http://admin.china.aiddata.org/projects/{})".format(project_id))     

def search_duplicate(): 
  st.title('Search Duplicate')

  uploaded_file = st.file_uploader("Choose a export csv file", type="csv")

  if uploaded_file != None:
    df = pd.read_csv(uploaded_file)
    df['year'] = df.year.fillna(0)

    base = r'^{}'
    expr = '(?=.*{})'
    text_input = st.text_input('keyword', value='None')
    words = text_input.split(" ")
    search_input = base.format(''.join(expr.format(w) for w in words))

    active = False
    if st.checkbox('Only Active'):
        active = True

    year_min_max = st.slider('year', 2000, 2020, value=[2000, 2020])
    year_min = year_min_max[0]
    year_max = year_min_max[1]


    # Otherwise, 'a|b' will search strings that contain a or b
    result = filter_search(df, keyword=search_input, year_min=year_min, year_max=year_max, Active = active)
    result = result.sort_values('year').reset_index(drop=True)

    # Display Project_id, title, year
    st.subheader('Search Results')
    st.table(result[['project_id', 'year', 'title']])

    # See the description
    if st.checkbox('get description'):
        index = st.number_input('which one', value=-1)
        if index != -1:
            st.write(result.loc[index]['description'])
    
    st.header('Duplicate Suggestions')

    project_id = st.number_input('project_id', value=0)
      
    suggestion = st.button('make suggestions')
    if suggestion:
       module = load_model()
       embeddings = get_embedding(module, df)
       df_potential = find_most_likely_duplicate(df, project_id, embeddings)
       st.write('The original title is:', df[df['project_id'] == project_id]['title'].iloc[0])
       st.table(df_potential)


  st.header('Useful Sources')

  open_project()
  write_useful_resources()
  


