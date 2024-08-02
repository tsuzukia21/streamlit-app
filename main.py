import streamlit as st
import streamlit_antd_components as sac
import os
from home import home
from st_chat_ChatGPT import chat
from st_chat_Agent import agent
from st_chat_vision import vision
from st_MitoSheet import mito
from st_transcribe import transcribe
from st_rag_langgraph import st_rag_langgraph

st.set_page_config(layout="wide", page_title="tsuzukia's app")

with st.sidebar.container():
    editing = sac.Tag('editing', color='green')
    menu = sac.menu([
        sac.MenuItem('pages', type='group', children=[
        sac.MenuItem('home', icon='house-fill'),
        sac.MenuItem('chat', icon='emoji-smile-fill'),
        sac.MenuItem('agent', icon='person'),
        sac.MenuItem('vision', icon='eye-fill'),
        sac.MenuItem('transcribe', icon='music-note'),
        sac.MenuItem('mitosheet', icon='table'),
        sac.MenuItem('Adaptive RAG', icon='book'),
        ]),
        sac.MenuItem('link', type='group', children=[
        sac.MenuItem('Github', icon='github', href='https://github.com/tsuzukia21'),
        sac.MenuItem('X', icon='twitter-x', href='https://twitter.com/tsuzukia_prgm'),
        sac.MenuItem('Zenn', icon='book', href='https://zenn.dev/tsuzukia')]),
        sac.MenuItem(type='divider'),
    ],index=1)

with st.sidebar:
    if not hasattr(st.session_state, "openai_api_key"):
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
    if not hasattr(st.session_state, "tavily_api_key"):
        st.session_state.tavily_api_key = os.getenv("TAVILY_API_KEY")
    new_openai_api_key = st.text_input("OpenAI API Key", value = st.session_state.openai_api_key,type="password")
    new_tavily_api_key = st.text_input("Tavily API Key", value = st.session_state.tavily_api_key, type="password")
    apply_api_key = st.button("Apply API Key")
    if apply_api_key:
        st.session_state.openai_api_key = new_openai_api_key
        st.session_state.tavily_api_key = new_tavily_api_key

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
elif menu == 'Adaptive RAG':
    st_rag_langgraph()