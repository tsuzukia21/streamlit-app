import streamlit as st
import streamlit_antd_components as sac
import os
from home import home
from st_chat_ChatGPT import chat
from st_chat_Agent import agent
from st_MitoSheet import mito
from st_transcribe import transcribe

st.set_page_config(layout='wide', page_title='streamlit-antd-components')

with st.sidebar.container():
    menu = sac.menu([
        sac.MenuItem('home', icon='house-fill'),
        sac.MenuItem('chat', icon='emoji-smile-fill'),
        sac.MenuItem('agent', icon='person'),
        sac.MenuItem('transcribe', icon='music-note'),
        sac.MenuItem('mitosheet', icon='table'),
        ])

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="open_api_key", type="password")
    if openai_api_key == "":
        try:
            st.session_state.openai_api_key = os.environ["OPENAI_API_KEY"]
        except:
            st.session_state.openai_api_key = ""

if menu == 'home':
    home()
elif menu == 'chat':
    chat()
elif menu == 'agent':
    agent()
elif menu == 'transcribe':
    transcribe()
elif menu == 'mitosheet':
    mito()