import streamlit as st

st.number_input("Test", value = 1., help = "Test")

st.checkbox("Test", value = True, help = "Test")

st.slider("Test", min_value=1, max_value=10, value=5, step=1, help = "Test")

st.expander("Test", help = "Test") #Doesn't Work
