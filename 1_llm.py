import os
import certifi
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return None
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
from streamlit_config import init_google_api_key

# Setup
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()
init_google_api_key()

# UI Styling
st.title("🏛️ World Capital Finder")
st.markdown("Enter a country name below to find its capital city.")

country = st.text_input("Country Name", placeholder="e.g. France")

def get_capital(country_name):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", # Using 1.5 flash for stability
            temperature=0,
        )
        
        # 1. Use a clean string parser to remove the metadata/signatures
        chain = llm | StrOutputParser()
        
        prompt = f"What is the capital of {country_name}? Respond with only the name of the city."
        return chain.invoke(prompt)
    except Exception as e:
        if "API key" in str(e):
            return "⚠️ Error: Google API key not set. Set GOOGLE_API_KEY environment variable or Streamlit secret."
        return f"Error: {e}"

if country:
    with st.spinner("Searching..."):
        result = get_capital(country)
        
        # 2. Use st.info or st.metric for a "beautiful" UI look
        st.write("---")
        st.subheader(f"Results for {country.title()}")
        st.success(f"The capital city is **{result}**")
        
        # Optional: Add a fun fact or visual element
        st.balloons()
