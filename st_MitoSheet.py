from mitosheet.streamlit.v1 import spreadsheet
import streamlit as st
import pandas as pd

def mito():
    if not hasattr(st.session_state, "df_mito"):
        st.session_state["df_mito"]= pd.DataFrame()

    st.title("Data Analytics by Mito")
    upload_file = st.file_uploader('**You can analyze data using Mito. Upload your favorite files.**', type=['csv', 'xlsx'])
    if upload_file is not None:
        if upload_file.name.endswith("csv"):
            st.session_state.df_mito=pd.read_csv(upload_file)
        elif upload_file.name.endswith("xlsx"):
            st.session_state.df_mito=pd.read_excel(upload_file)
        final_df,code=spreadsheet(st.session_state.df_mito)

        st.write(final_df)
        st.code(code)

if __name__ == "__main__":
    mito()