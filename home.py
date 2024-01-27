import streamlit as st
import streamlit_antd_components as sac

def home():
    st.title("Home😊")
    st.header("Welcome to tsuzukia's Streamlit app!")
    st.header("I am creating a Streamlit app for work, and I will share a part of it😊")
    st.divider()
    st.subheader("I also publish an engineering blog. Feel free to check it out! It's in Japanese, though.")
    st.markdown("""
        <style>
        a.custom-link {
            font-size: 24px;
            font-weight: bold;
        }
        </style>
        <a href="https://zenn.dev/tsuzukia" class="custom-link">zenn</a>
    """, unsafe_allow_html=True)
    st.image("img/zenn.png")
    st.divider()
    st.subheader("This wonderful menu is created using the following custom components.")
    st.markdown("""
        <style>
        a.custom-link {
            font-size: 24px;
            font-weight: bold;
        }
        </style>
        <a href="https://github.com/nicedouble/StreamlitAntdComponents" class="custom-link">nicedouble/StreamlitAntdComponents</a>
    """, unsafe_allow_html=True)
    st.image("img/streamlit_antd_components.png")



if __name__ == "__main__":
    home()