import streamlit as st
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage
import streamlit_antd_components as sac
from langchain_core.runnables import RunnableConfig
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import os

def agent():
    st.title("Simple Agent")
    st.write("**using the Agent feature of Langchain. The current tools are duckduckgo-search and llm-math-chain.Please set your favorite tool.**")
    search = DuckDuckGoSearchRun()

    attrs=["messages_agent","kwargs_agent"]
    for attr in attrs:
        if attr not in st.session_state:
            st.session_state[attr] = []
    if "Clear_agent" not in st.session_state:
        st.session_state.Clear_agent = False

    msgs = StreamlitChatMessageHistory(key="special_app_key")
    memory = ConversationBufferMemory(memory_key="history", return_messages=True, chat_memory=msgs)

    kwargs_agent = {
        "system_message": SystemMessage(content="You are an AI chatbot having a conversation with a human.", additional_kwargs={}),
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="history")],
    }

    for message in st.session_state.messages_agent:
        if not message["role"]=="system":
            if message["role"]=="user":
                with st.chat_message(message["role"], avatar = "😊"):
                    st.markdown(message["content"])
            elif message["role"]=="assistant":
                with st.chat_message(message["role"], avatar = "👩‍🎓"):
                    st.markdown(message["content"])

    if user_prompt := st.chat_input("Send a message"):
        if not st.session_state.openai_api_key:
            sac.alert(label='warning', description='Please add your OpenAI API key to continue.', color='red', banner=[False, True], icon=True, size='lg')
            st.stop()

        llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-4o",openai_api_key=st.session_state.openai_api_key)
        llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=False)

        tools = [
            Tool(
                name = "ddg-search",
                func=search.run,
                description="useful for when you need to answer questions about current events.. You should ask targeted questions"
            ),
            Tool(
                name="Calculator",
                func=llm_math_chain.run,
                description="useful for when you need to answer questions about math"
            ),
        ]

        agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, kwargs=kwargs_agent,verbose=False,memory=memory)

        st.session_state.messages_agent.append({"role": "user", "content": user_prompt})
        with st.chat_message("user", avatar = "😊"):
            st.markdown(user_prompt)
        
        with st.chat_message("assistant" , avatar = "👩‍🎓"):
            st_callback = StreamlitCallbackHandler(st.container())
            cfg = RunnableConfig()
            cfg["callbacks"] = [st_callback]
            response = agent.invoke(user_prompt, cfg)
            response = response["output"]
            st.write(response)
        st.session_state.messages_agent.append({"role": "assistant", "content": response})
        st.session_state.Clear_agent = True

    if st.session_state.Clear_agent:
        if st.button('clear chat history'):
            st.session_state.messages_agent = []
            response = ""
            msgs.clear()
            memory.clear()
            st.session_state.Clear_agent = False
            st.rerun()

if __name__ == "__main__":
    with st.sidebar:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
        new_openai_api_key = st.text_input("OpenAI API Key", value = st.session_state.openai_api_key,type="password")
        apply_api_key = st.button("Apply API Key")
        if apply_api_key:
            st.session_state.openai_api_key = new_openai_api_key
    agent()