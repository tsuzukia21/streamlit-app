import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import math
import tiktoken
from operator import itemgetter
from tiktoken.core import Encoding
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import pyperclip
encoding: Encoding = tiktoken.encoding_for_model("gpt-4o")

def _get_openai_type(msg):
    if msg.type == "human":
        return "user"
    if msg.type == "ai":
        return "assistant"
    if msg.type == "chat":
        return msg.role
    return msg.type

def clear_chat():
    st.session_state.messages = []
    st.session_state.Clear = False
    st.session_state.total_tokens=0
    st.session_state.memory.clear()
    st.session_state.done = True
    st.rerun()

def show_messages(messages, memory, edit, new_message=None):
    st.session_state.total_tokens = 0
    st.session_state.disable_copy = False
    i = 0
    memory.clear()
    for msg in messages:
        streamlit_type = _get_openai_type(msg)
        avatar = "🤖" if streamlit_type == "assistant" else "😊"
        with st.chat_message(streamlit_type, avatar=avatar):
            if streamlit_type == "user":
                st.session_state.total_tokens += len(encoding.encode(msg.content))
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.markdown(msg.content.replace("\n","  \n"), unsafe_allow_html=True)
                if edit:
                    with col2:
                        key = st.button("edit", key=f"edit_{i}")
                        if key:
                            st.session_state.edit = True
                            st.session_state.disable_copy = True
                    if st.session_state.edit:
                        st.session_state.new_message = st.text_area("Please save after editing.", value=msg.content)
                        save = st.button("save", key=f"save_{i}")
                        if save:
                            st.session_state.edit = False
                            messages = modify_message(messages, i, memory)
                            st.session_state.save = True
                            st.session_state.disable_copy = False
                else:
                    with col2:
                        key = st.button("edit", key=f"dummy_{i}")

            else:
                st.session_state.total_tokens += len(encoding.encode(msg.content))
                col1, col2 = st.columns([9, 1])
                with col1:
                    st.markdown(msg.content.replace("\n", "  \n"), unsafe_allow_html=True)
                if i == len(messages) - 1:
                    with col2:
                        copy_button = st.button("copy",disabled=st.session_state.disable_copy)
                        if copy_button:
                            pyperclip.copy(st.session_state.last_response)
        memory.chat_memory.add_message(msg)
        i += 1
    if new_message:
        st.session_state.total_tokens += len(encoding.encode(new_message))
        with st.chat_message("user", avatar="😊"):
            col1, col2 = st.columns([9, 1])
            with col1:
                st.markdown(new_message.replace("\n","  \n"), unsafe_allow_html=True)
            
def check_token():
    if st.session_state.total_tokens>20000:
        percent=math.floor(st.session_state.total_tokens/200)
        st.error(f'Error: The amount of text exceeds the limit by {percent}%. \nPlease delete unnecessary parts or reset the conversation.', icon="🚨")
        if st.button('clear chat history'):
            clear_chat()
        st.stop()
    if len(st.session_state.messages) > 30:
        if st.button('clear chat history'):
            clear_chat()
        st.error('Error: The number of conversations has exceeded the limit. Please reset the conversation.', icon="🚨")
        st.stop()

def modify_message(messages, i, memory):
    memory.clear()
    del messages[i:]
    for msg in messages:
        memory.chat_memory.add_message(msg)
    return messages

def temperareture_update():
    st.session_state.temperature = st.session_state.new_temperature

def system_prompt_update():
    st.session_state.system_prompt = st.session_state.new_system_prompt

def st_chat():
    st.title("Streamlit Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if not hasattr(st.session_state, "temperature"):
        st.session_state.temperature = 0.7
    attrs=["edit","save","stop","Clear"]
    for attr in attrs:
        if attr not in st.session_state:
            st.session_state[attr] = False
    if "done" not in st.session_state:
        st.session_state.done = True
    if "total_token" not in st.session_state:
        st.session_state.total_token= 0
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are an helpful AI assistant."
    attrs=["last_response","full_response","prompt"]
    for attr in attrs:
        if attr not in st.session_state:
            st.session_state.attr = ""
    if "engine_index" not in st.session_state:
        st.session_state.engine_index= 0

    st.write("**You can converse with the selected model. You can pause the conversation midway and edit the conversation history.**")

    with st.expander("option"):
        st.selectbox("model",("gpt-4o","gpt-4o-mini","claude-3.5-sonnet","gemini-1.5-pro"),help="You can select the model.",index=st.session_state.engine_index,key="engine")
        st.text_area("system prompt",value=st.session_state.system_prompt,help="You can provide a prompt to the system. This is only effective at the first message transmission.",key="new_system_prompt",on_change=system_prompt_update)
        st.slider(label="temperature",min_value=0.0, max_value=1.0,value=st.session_state.temperature,help="Controls the randomness of the generated text.",key="new_temperature",on_change=temperareture_update)

    if st.session_state.engine == "gpt-4o":
        if not st.session_state.openai_api_key:
            st.error("Please enter the OpenAI API Key.")
            st.stop()
        model = ChatOpenAI(model=st.session_state.engine,api_key=st.session_state.openai_api_key,temperature=st.session_state.temperature)
        st.session_state.engine_index = 0
    elif st.session_state.engine == "gpt-4o-mini":
        if not st.session_state.openai_api_key:
            st.error("Please enter the OpenAI API Key.")
            st.stop()
        model = ChatOpenAI(model=st.session_state.engine,api_key=st.session_state.openai_api_key,temperature=st.session_state.temperature)
        st.session_state.engine_index = 1
    elif st.session_state.engine == "claude-3.5-sonnet":
        if not st.session_state.anthropic_api_key:
            st.error("Please enter the Anthropic API Key.")
            st.stop()
        model = ChatAnthropic(model_name="claude-3-5-sonnet-20240620",anthropic_api_key=st.session_state.anthropic_api_key,temperature=st.session_state.temperature)
        st.session_state.engine_index = 2
    elif st.session_state.engine == "gemini-1.5-pro":
        if not st.session_state.google_api_key:
            st.error("Please enter the Google API Key.")
            st.stop()
        model = ChatGoogleGenerativeAI(model="gemini-1.5-pro-exp-0801",google_api_key=st.session_state.google_api_key,temperature=st.session_state.temperature)
        st.session_state.engine_index = 3

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", st.session_state.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
    st.session_state.memory.load_memory_variables({})
    chain = (
        RunnablePassthrough.assign(
            history=RunnableLambda(st.session_state.memory.load_memory_variables) | itemgetter("history")
        )
        | prompt_template
        | model
    )

    show_messages(messages=st.session_state.messages,memory=st.session_state.memory,edit=True)
    if not st.session_state.done:
        st.session_state.memory.chat_memory.add_user_message(st.session_state.prompt)
        st.session_state.memory.chat_memory.add_ai_message(st.session_state.full_response)
        st.session_state.messages = st.session_state.memory.buffer
        # st.session_state.Clear = True
        st.session_state.done = True
        st.session_state.save = False
        st.rerun()
    
    if prompt := st.chat_input(placeholder="Send a message"):
        st.session_state.Clear = False
        st.session_state.done = False
        st.session_state.prompt = prompt
        st.session_state.edit = False
        st.session_state.total_tokens+=len(encoding.encode(prompt))
        check_token()
        st.session_state.full_response = ""

        with st.chat_message("user",avatar="😊"):
            col1,  col2 = st.columns([9,  1])
            with col1:
                st.markdown(prompt.replace("\n","  \n"),unsafe_allow_html=True)
        with st.chat_message("assistant", avatar="🤖"):
            col1,  col2 = st.columns([9,  1])
            with col1:
                message_placeholder = st.empty()
                message_placeholder.markdown("thinking...")
            with col2:
                st.session_state.stop = st.button("stop")
            with col1:
                for chunk in chain.stream({"input": prompt}):
                    if not st.session_state.stop:
                        st.session_state.full_response += chunk.content
                        message_placeholder.markdown(st.session_state.full_response.replace("\n","  \n") + "▌",unsafe_allow_html=True)              
                st.session_state.done = True
                message_placeholder.markdown(st.session_state.full_response.replace("\n","  \n"),unsafe_allow_html=True)
                st.session_state.last_response=st.session_state.full_response.replace("\n", "\\n").replace('"', '\\"')
                st.session_state.memory.save_context({"input": prompt}, {"output": st.session_state.full_response})
                st.session_state.messages = st.session_state.memory.buffer
        st.session_state.Clear = True
        st.rerun()

    if st.session_state.save:
        st.session_state.Clear = False
        st.session_state.done = False
        prompt = st.session_state.new_message
        st.session_state.prompt = prompt
        show_messages(messages=st.session_state.messages,memory=st.session_state.memory,edit=False,new_message=prompt)
        check_token()
        st.session_state.full_response = ""
        with st.chat_message("assistant", avatar="🤖"):
            col1,  col2 = st.columns([9,  1])
            with col1:
                message_placeholder = st.empty()
                message_placeholder.markdown("thinking...")
            with col2:
                st.session_state.stop = st.button("stop")
            with col1:
                for chunk in chain.stream({"input": prompt}):
                    if not st.session_state.stop:
                        st.session_state.full_response += chunk.content
                        message_placeholder.markdown(st.session_state.full_response.replace("\n","  \n") + "▌",unsafe_allow_html=True)              
                st.session_state.done = True
                message_placeholder.markdown(st.session_state.full_response.replace("\n","  \n"),unsafe_allow_html=True)
                st.session_state.last_response = st.session_state.full_response.replace("\n", "\\n").replace('"', '\\"')
                st.session_state.memory.save_context({"input": prompt}, {"output": st.session_state.full_response})
                st.session_state.messages = st.session_state.memory.buffer

        st.session_state.Clear = True
        st.session_state.save = False
        st.rerun()
    
    if st.session_state.Clear:
        with st.container():
            clear_button = st.button("clear chat history",type="primary")
            if clear_button:
                clear_chat()

if __name__ == "__main__":
    st_chat()