import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.memory import StreamlitChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tracers.run_collector import RunCollectorCallbackHandler
import streamlit_antd_components as sac
import requests
import base64
import os
from st_img_pastebutton import paste
from io import BytesIO

def encode_image(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    return base64.b64encode(file_bytes).decode('utf-8')

def analyze_image(prompt):
    image_base64=encode_image(st.session_state.uploaded_file)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.session_state.openai_api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": f"{prompt} Let's think step by step to get the correct answer."
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{image_base64}",
                  "detail": "high"
                }
              }
            ]
          }
        ],
        "max_tokens": 4000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = response.json()

    if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
        return response_data["choices"][0]["message"]["content"]
    else:
        return "No analysis available for the image."


def vision():
    st.title("ChatGPT-Vision")
    st.write("**You can analyze images. Please upload an image and ask a question.**")

    clopboard_file = paste(label="paste from clipboard",key="image_clipboard")

    if clopboard_file is not None:
        header, encoded = clopboard_file.split(",", 1)
        binary_data = base64.b64decode(encoded)
        bytes_data = BytesIO(binary_data)
        st.session_state.uploaded_file = bytes_data
        st.image(bytes_data, caption="Uploaded Image", width =500)

    attrs=["messages_vision","agent_kwargs_vision"]
    for attr in attrs:
        if attr not in st.session_state:
            st.session_state[attr] = []
    if "Clear_vision" not in st.session_state:
        st.session_state.Clear_vision = False

    agent_kwargs_vision = {
        "system_message": SystemMessage(content="You are an AI chatbot having a conversation with a human.There may come a time when you are asked a question about photography. The photo has already been uploaded. Use the tool appropriately and answer the question. \
            Instead of directly returning the results obtained from using the tools, you are expected to use those results to respond to the user's questions. DO YOUR BEST TO PROVIDE APPROPRIATE ANSWERS TO USER QUESTIONS!!", additional_kwargs={}),
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="history_vision")],
    }
    msgs = StreamlitChatMessageHistory(key="vision")
    memory = ConversationBufferMemory(memory_key="history_vision",return_messages=True, chat_memory=msgs)
    tools = [
        Tool(
            name="image_analysis",
            func=analyze_image,
            description="Useful when you need to answer a question about an image of some kind. image is already uploaded. Pass the appropriate prompt to ask about IMAGE. \
                Prompt is very important and must be in line with the user's intentions. Instead of directly returning the results obtained from using the tools, you are expected to use those results to respond to the user's questions." ,
            return_direct=False
        )
        ]
    

    for message in st.session_state.messages_vision:
        if not message["role"]=="system":
            if message["role"]=="assistant":
                with st.chat_message(message["role"],avatar = "👁️"):
                    st.markdown(message["content"],unsafe_allow_html=True)
            else:
                with st.chat_message(message["role"], avatar="😊"):
                    st.markdown(message["content"],unsafe_allow_html=True)

    if user_prompt_vision := st.chat_input("Send a message"):

        if st.session_state.openai_api_key == "":
            sac.alert(label='warning', description='Please add your OpenAI API key to continue.', color='red', banner=[False, True], icon=True, size='lg')
            st.stop()

        llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-4-turbo-preview",openai_api_key=st.session_state.openai_api_key)
        agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS,verbose=False,agent_kwargs=agent_kwargs_vision,memory=memory)
    
        st.session_state.messages_vision.append({"role": "user", "content": user_prompt_vision})
        with st.chat_message("user", avatar="😊"):
            st.markdown(user_prompt_vision.replace("\n","<br>").replace("$","\\$").replace("#","\\#").replace("_","\\_"),unsafe_allow_html=True)
        with st.chat_message("assistant",avatar="👁️"):
            st_callback_vision = StreamlitCallbackHandler(st.container())
            run_collector = RunCollectorCallbackHandler()
            cfg = RunnableConfig()
            cfg["callbacks"] = [st_callback_vision, run_collector]
            response_vison = agent.invoke(user_prompt_vision, cfg)
            response_vison = response_vison["output"]
            st.markdown(response_vison.replace("\n","  \n"),unsafe_allow_html=True)

        st.session_state.messages_vision.append({"role": "assistant", "content": response_vison})
        st.session_state.Clear_vision = True
                
    if st.session_state.Clear_vision:
        if st.button('clear chat history'):
            st.session_state.messages_vision = []
            response_vison = ""
            msgs.clear()
            memory.clear()
            st.session_state.Clear_vision = False 
            st.rerun()

if __name__ == "__main__":
    if not hasattr(st.session_state, "openai_api_key"):
        try:
            st.session_state.openai_api_key = os.environ["OPENAI_API_KEY"]
        except:
            st.session_state.openai_api_key = ""
    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if not openai_api_key == "":
            st.session_state.openai_api_key = openai_api_key
        st.write("if you are running the app locally,  \nthere is no need to enter the key  \nif it is already set as an environment variable.")
    vision()