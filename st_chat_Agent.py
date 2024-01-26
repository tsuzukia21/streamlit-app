import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler
from langchain.tools import DuckDuckGoSearchRun
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType, initialize_agent, load_tools,Tool
from langchain.callbacks import StreamlitCallbackHandler
from langchain import LLMMathChain
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage
import openai
import streamlit_antd_components as sac

def agent():
    st.title("Agent by Streamlit")

    if st.session_state.openai_api_key == "":
        sac.alert(label='warning', description='Please add your OpenAI API key to continue.', color='red', banner=[False, True], icon=True, size='lg')
        st.stop()
    
    search = DuckDuckGoSearchRun()

    attrs=["messages_agent","agent_kwargs"]
    for attr in attrs:
        if attr not in st.session_state:
            st.session_state[attr] = []
    if "Clear" not in st.session_state:
        st.session_state.Clear = False

    agent_kwargs = {
        "system_message": SystemMessage(content="You are an AI chatbot having a conversation with a human.", additional_kwargs={}),
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="history")],
    }
    msgs = StreamlitChatMessageHistory(key="special_app_key")
    memory = ConversationBufferMemory(memory_key="history", return_messages=True, chat_memory=msgs)

    llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-3.5-turbo",openai_api_key=st.session_state.openai_api_key)
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
    agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, agent_kwargs=agent_kwargs,verbose=False,memory=memory)

    # Display chat messages_agent from history on app rerun
    for message in st.session_state.messages_agent:
        if not message["role"]=="system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"],unsafe_allow_html=True)

    if user_prompt := st.chat_input("Send a message"):
        st.session_state.messages_agent.append({"role": "user", "content": user_prompt})
        st.chat_message("user").write(user_prompt)
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            response = agent.run(user_prompt, callbacks=[st_callback])
            st.write(response)
        st.session_state.messages_agent.append({"role": "assistant", "content": response})
        st.session_state.Clear = True # チャット履歴のクリアボタンを有効にする

    # チャット履歴をクリアするボタンが押されたら、メッセージをリセット
    if st.session_state.Clear:
        if st.button('clear chat history'):
            st.session_state.messages_agent = [] # メッセージのリセット
            response = ""
            msgs.clear()
            memory.clear()
            st.session_state.Clear = False # クリア状態をリセット
            st.experimental_rerun() # 画面を更新

if __name__ == "__main__":
    agent()