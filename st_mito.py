import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from mitosheet.streamlit.v1 import spreadsheet

st.header("MitoSheet Demo")

df = sns.load_dataset('tips')

# Display the dataframe in a Mito spreadsheet
final_dfs, code = spreadsheet(df)

# Display the final dataframes created by editing the Mito component
# This is a dictionary from dataframe name -> dataframe
st.write(final_dfs)

# Display the code that corresponds to the script
st.code(code)