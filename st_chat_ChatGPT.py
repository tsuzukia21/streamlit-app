from openai import OpenAI
import streamlit as st
import streamlit_antd_components as sac
import os

def chat():
    st.title("Simple Chatbot by OpenAI")
    st.write("**it is a simple chatbot made only with OpenAI and Streamlit libraries. You can set system prompts, model, and temperature as options.**")
    client = OpenAI(api_key=st.session_state.openai_api_key)

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if "Clear" not in st.session_state:
        st.session_state.Clear = False
   
    if "temprature" not in st.session_state:
        st.session_state.temprature = 0.7
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are an AI chatbot having a conversation with a human."

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role":"system", "content":st.session_state.system_prompt}]

    with st.expander("Options"):
        st.selectbox("Model", ("gpt-4o", "gpt-4o-mini"), help="Choose the AI model to use. 'gpt-4o' is the latest model with more advanced capabilities, while 'gpt-4o-mini' is an older but still powerful version.", key="openai_model")
        st.text_area("System Prompt", value="You are an AI chatbot having a conversation with a human.", help="Can only be set at the time of the first message sent.Set the initial prompt for the AI system which sets the context of the conversation. This can influence how the AI responds.", key="system_prompt")
        st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, help="Adjust the creativity of the AI's responses. A lower temperature means more deterministic and predictable responses, while a higher temperature results in more varied and sometimes more creative responses.", key="temperature")

    for message in st.session_state.messages:
        if not message["role"]=="system":
            if message["role"]=="user":
                with st.chat_message(message["role"], avatar = "😊"):
                    st.markdown(message["content"])
            elif message["role"]=="assistant":
                with st.chat_message(message["role"], avatar = "🤖"):
                    st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        if not st.session_state.openai_api_key:
            sac.alert(label='warning', description='Please add your OpenAI API key to continue.', color='red', banner=[False, True], icon=True, size='lg')
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar = "😊"):
            st.markdown(prompt)

        with st.chat_message("assistant" , avatar = "🤖"):
            message_placeholder = st.empty()
            full_response = ""
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.Clear = True

    if st.session_state.Clear:
        if st.button('clear chat history'):
            st.session_state.messages = []
            full_response = ""
            st.session_state.Clear = False 
            st.rerun()

if __name__ == "__main__":
    with st.sidebar:
        st.session_state.openai_api_key = os.getenv("OPENAI_API_KEY")
        new_openai_api_key = st.text_input("OpenAI API Key", value = st.session_state.openai_api_key,type="password")
        apply_api_key = st.button("Apply API Key")
        if apply_api_key:
            st.session_state.openai_api_key = new_openai_api_key
    chat()