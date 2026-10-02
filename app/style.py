

import streamlit as st

from constants import ROOT_PATH


@st.cache_data
def style_css():
    with open(ROOT_PATH / 'app' / 'style.css') as css:
        style = css.read()
        return(style)

def set_style():
    st.markdown(f'<style>{style_css()}</style>', unsafe_allow_html = True)
