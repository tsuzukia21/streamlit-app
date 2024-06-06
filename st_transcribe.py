from openai import OpenAI
import streamlit as st
import streamlit_antd_components as sac

def transcribe():
    st.title("Transcribe by Streamlit")
    if st.session_state.openai_api_key == "":
        sac.alert(label='warning', description='Please add your OpenAI API key to continue.', color='red', banner=[False, True], icon=True, size='lg')
        st.stop()
    client = OpenAI(api_key=st.session_state.openai_api_key)

    upload_file = st.file_uploader('Please select the file you want to transcribe. \nDue to API limitations, files over 25MB cannot be transcribed.\
                                Please reduce the file size by splitting it or similar methods.', type=['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav'])
    if upload_file is not None:
        st.subheader('File Details')
        file_details = {'FileName': upload_file.name, 'FileType': upload_file.type, 'FileSize': upload_file.size}
        st.write(file_details)
        if upload_file.size > 25000000:
            st.error('Error: The file exceeds 25MB. Due to API limitations, files over 25MB cannot be transcribed. Please reduce the file size by splitting it or similar methods.', icon="🚨")
        trans_start=st.button('Start Transcription')

        if trans_start:
            with st.spinner('**Transcribing audio...**'):
                trans = client.audio.transcriptions.create(model="whisper-1", file=upload_file).text
            st.success('**Transcription completed**')
            st.write("**Transcription Result**")
            st.write(trans)

if __name__ == "__main__":
    transcribe()