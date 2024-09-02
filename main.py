import streamlit as st
import streamlit_antd_components as sac
import os
from home import home
from st_chat import st_chat
from st_chat_Agent import agent
from st_chat_vision import vision
from st_MitoSheet import mito
from st_transcribe import transcribe
from st_rag_langgraph import st_rag_langgraph
from streamlit_cookies_controller import CookieController
import time

st.set_page_config(layout="wide", page_title="tsuzukia's app")

if not hasattr(st.session_state, "openai_api_key"):
    st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
if not hasattr(st.session_state, "anthropic_api_key"):
    st.session_state.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not hasattr(st.session_state, "google_api_key"):
    st.session_state.google_api_key = os.getenv("GOOGLE_API_KEY")
if not hasattr(st.session_state, "tavily_api_key"):
    st.session_state.tavily_api_key = os.getenv("TAVILY_API_KEY")

if not hasattr(st.session_state, "index"):
    st.session_state.controller = CookieController()
    cookies= st.session_state.controller.getAll()
    time.sleep(0.1)
    try:
        st.session_state.index = cookies.get("index")
    except AttributeError:
        st.session_state.index = 1
    if st.session_state.index is None:
        st.session_state.index = 1
    if st.session_state.index == 1:
        st.session_state.menu = 'home'
    elif st.session_state.index == 2:
        st.session_state.menu = 'chat'
    elif st.session_state.index == 3:
        st.session_state.menu = 'agent'
    elif st.session_state.index == 4:
        st.session_state.menu = 'vision'
    elif st.session_state.index == 5:
        st.session_state.menu = 'transcribe'
    elif st.session_state.index == 6:
        st.session_state.menu = 'mitosheet'
    elif st.session_state.index == 7:
        st.session_state.menu = 'Adaptive RAG'

with st.sidebar.container() as st.session_state.sidebar:
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
    ],index=st.session_state.index,key='menu')

    new_openai_api_key = st.text_input("OpenAI API Key", value = st.session_state.openai_api_key,type="password")
    new_anthropic_api_key = st.text_input("Anthropic API Key", value = st.session_state.anthropic_api_key, type="password")
    new_google_api_key = st.text_input("Google API Key", value = st.session_state.google_api_key,type="password")
    new_tavily_api_key = st.text_input("Tavily API Key", value = st.session_state.tavily_api_key, type="password")
    apply_api_key = st.button("Apply API Key")
    if apply_api_key:
        st.session_state.openai_api_key = new_openai_api_key
        st.session_state.anthropic_api_key = new_anthropic_api_key
        st.session_state.google_api_key = new_google_api_key
        st.session_state.tavily_api_key = new_tavily_api_key

if menu:
    if st.session_state.menu == 'home':
        home()
        st.session_state.index = 1
    elif st.session_state.menu == 'chat':
        st_chat()
        st.session_state.index = 2
    elif st.session_state.menu == 'agent':
        agent()
        st.session_state.index = 3
    elif st.session_state.menu == 'vision':
        vision()
        st.session_state.index = 4
    elif st.session_state.menu == 'transcribe':
        transcribe()
        st.session_state.index = 5
    elif st.session_state.menu == 'mitosheet':
        mito()
        st.session_state.index = 6
    elif st.session_state.menu == 'Adaptive RAG':
        st_rag_langgraph()
        st.session_state.index = 7
    st.session_state.controller.set('index', st.session_state.index)
    