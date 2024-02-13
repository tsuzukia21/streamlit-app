import streamlit as st
import streamlit_antd_components as sac
import os
from home import home
from st_chat_ChatGPT import chat
from st_chat_Agent import agent
from st_chat_vision import vision
from st_MitoSheet import mito
from st_transcribe import transcribe

st.set_page_config(layout="wide", page_title="tsuzukia's app")

if not hasattr(st.session_state, "openai_api_key"):
    try:
        st.session_state.openai_api_key = os.environ["OPENAI_API_KEY"]
    except:
        st.session_state.openai_api_key = ""

with st.sidebar.container():
    editing = sac.Tag('editing', color='green')
    menu = sac.menu([
        sac.MenuItem('pages', type='group', children=[
        sac.MenuItem('home', icon='house-fill'),
        sac.MenuItem('chat', icon='emoji-smile-fill'),
        sac.MenuItem('agent', icon='person'),
        sac.MenuItem('vision', icon='eye-fill'),
        sac.MenuItem('transcribe', icon='music-note',tag=editing),
        sac.MenuItem('mitosheet', icon='table')]),
        sac.MenuItem('link', type='group', children=[
        sac.MenuItem('Github', icon='github', href='https://github.com/tsuzukia21'),
        sac.MenuItem('X', icon='twitter-x', href='https://twitter.com/tsuzukia_prgm'),
        sac.MenuItem('Zenn', icon='book', href='https://zenn.dev/tsuzukia')]),
        sac.MenuItem(type='divider'),
    ],index=1)

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key == "":
        st.session_state.openai_api_key = openai_api_key
    st.write("if you are running the app locally,  \nthere is no need to enter the key  \nif it is already set as an environment variable.")

if menu == 'home':
    home()
elif menu == 'chat':
    chat()
elif menu == 'agent':
    agent()
elif menu == 'vision':
    vision()
elif menu == 'transcribe':
    transcribe()
elif menu == 'mitosheet':
    mito()