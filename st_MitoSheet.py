from mitosheet.streamlit.v1 import spreadsheet
import streamlit as st
import pandas as pd

if not hasattr(st.session_state, "df_mito"):
    st.session_state["df_mito"]= pd.DataFrame()

st.subheader("Data Analytics by Mito / mitoを使ったデータ分析")
upload_file = st.file_uploader('***You can analyze data using Mito. Upload your favorite files.***\n\n***mitoを使ったデータ分析が出来ます。お好きなファイルをアップロードしてください。***', type=['csv', 'xlsx'])
if upload_file is not None:
    if upload_file.name.endswith("csv"):
        st.session_state.df_mito=pd.read_csv(upload_file)
    elif upload_file.name.endswith("xlsx"):
        st.session_state.df_mito=pd.read_excel(upload_file)
    final_df,code=spreadsheet(st.session_state.df_mito)

    st.write(final_df)
    st.code(code)