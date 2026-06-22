import os
import certifi
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return None
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import streamlit as st
from streamlit_config import init_google_api_key

# Setup
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()
init_google_api_key()

# UI Styling
st.title("🎬 Movie Info Finder")
st.markdown("Enter a movie name below to get detailed information about it!")

movie_name = st.text_input("Movie Name", placeholder="e.g. Avatar")

def get_movie_info(movie):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            temperature=0.2,
        )
    except Exception as e:
        if "API key" in str(e):
            return {"error": "⚠️ Google API key not set. Set GOOGLE_API_KEY environment variable or Streamlit secret."}
        raise
    
    parser = JsonOutputParser()
    
    prompt = PromptTemplate(
        template="You are a movie expert. Provide the following information about the movie '{movie}'.\n"
                 "{format_instructions}\n"
                 "If the movie is not found or ambiguous, try to provide the closest match.",
        input_variables=["movie"],
        partial_variables={
            "format_instructions": "Return a JSON object with exactly these keys: "
                                   "'title' (string), "
                                   "'reviews_summary' (string: a brief summary of critical and audience reviews), "
                                   "'rating' (string: e.g. 8.8/10), "
                                   "'release_year' (string: e.g. 2010), "
                                   "'release_date' (string: e.g. July 16, 2010), "
                                   "'genres' (list of strings), "
                                   "'box_office' (string: e.g. $836.8 million), "
                                   "'star_cast' (list of strings)."
        },
    )
    
    chain = prompt | llm | parser
    
    try:
        return chain.invoke({"movie": movie})
    except Exception as e:
        return {"error": str(e)}

if movie_name:
    with st.spinner(f"Fetching details for '{movie_name}'..."):
        info = get_movie_info(movie_name)
        
        if "error" in info:
            st.error(f"Failed to retrieve information: {info['error']}")
        else:
            st.write("---")
            st.header(f"🍿 {info.get('title', movie_name.title())}")
            
            # Key metrics layout
            def wrap_metric(label, value):
                st.markdown(f"""
                <div style="padding: 5px 0; margin-bottom: 10px;">
                    <div style="font-size: 0.9rem; opacity: 0.8;">{label}</div>
                    <div style="font-size: 1.2rem; font-weight: 600; line-height: 1.4; word-wrap: break-word;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
                
            col1, col2, col3 = st.columns(3)
            with col1:
                wrap_metric("⭐ Rating", info.get('rating', 'N/A'))
                wrap_metric("📆 Release Year", info.get('release_year', 'N/A'))
            with col2:
                wrap_metric("🗓️ Release Date", info.get('release_date', 'N/A'))
                wrap_metric("💰 Box Office", info.get('box_office', 'N/A'))
            with col3:
                genres = info.get('genres', [])
                wrap_metric("🎭 Genres", ", ".join(genres) if genres else 'N/A')
            
            st.write("---")
            
            # Reviews and Cast layout
            col5, col6 = st.columns([2, 1])
            with col5:
                st.markdown("### 📝 Reviews Summary")
                st.info(info.get('reviews_summary', 'No review summary available.'))
            with col6:
                st.markdown("### ⭐ Star Cast")
                for actor in info.get('star_cast', []):
                    st.markdown(f"- {actor}")
