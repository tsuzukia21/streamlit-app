from streamlit_cookies_controller import CookieController
import streamlit as st

st.set_page_config('Cookie QuickStart', '🍪', layout='wide')

controller = CookieController()

# Set a cookie
controller.set('cookie_name', 'testing')
controller.set('index', 0)

# Get all cookies
cookies = controller.getAll()
st.write(cookies)

# Get a cookie
cookie = controller.get('cookie_name')
st.write(cookie)

# Remove a cookie
# controller.remove('cookie_name')
