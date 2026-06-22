import streamlit as st

# Home page rendering function
def show_home():
    st.set_page_config(page_title="LangChain Portal", page_icon="🚀", layout="wide")
    
    # Custom CSS for homepage
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #0d2b1d, #091711);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        margin: 0;
        font-weight: 800;
        font-size: 2.6rem;
        background: linear-gradient(90deg, #10b981, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .card-box {
        background: rgba(255, 255, 255, 0.02);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
        height: 190px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease-in-out;
    }
    .card-box:hover {
        transform: translateY(-4px);
        border-color: rgba(16, 185, 129, 0.25);
        background: rgba(255, 255, 255, 0.04);
    }
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #f8fafc;
    }
    .card-desc {
        font-size: 0.92rem;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 0.5rem;
        flex-grow: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 LangChain & Google Gemini Portal</h1>
        <p style="color: #94a3b8; font-size: 1.15rem; margin-top: 0.5rem; margin-bottom: 0;">
            Explore the core features of LangChain and Google Gemini through interactive, step-by-step educational mini-apps.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🛠️ Select a Learning Module")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # Module 1
        st.markdown("""
        <div class="card-box">
            <div>
                <div class="card-title">🏛️ 1. World Capital Finder</div>
                <div class="card-desc">
                    A basic introduction to LangChain and LLMs. Learn how to invoke Google Gemini with simple prompt inputs and format the results as clean text output.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Capital Finder ➡️", key="btn_llm", use_container_width=True):
            st.switch_page("1_llm.py")
            
        st.write("") # Spacer
        
        # Module 3
        st.markdown("""
        <div class="card-box">
            <div>
                <div class="card-title">🔗 3. LangChain Chains Explained</div>
                <div class="card-desc">
                    Understand the 4 fundamental chain structures in LangChain: Normal Chains, Sequential Chains, Parallel Chains, and Conditional Chains (routing based on output).
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Chains Explained ➡️", key="btn_chains", use_container_width=True):
            st.switch_page("3_chains.py")

    with col2:
        # Module 2
        st.markdown("""
        <div class="card-box">
            <div>
                <div class="card-title">🎬 2. Movie Info Finder</div>
                <div class="card-desc">
                    Learn about Structured JSON Output parsing. This demo uses a JsonOutputParser to parse unstructured LLM completions into structured Python dictionaries.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Movie Finder ➡️", key="btn_movie", use_container_width=True):
            st.switch_page("2_movie_info.py")
            
        st.write("") # Spacer
        
        # Module 4
        st.markdown("""
        <div class="card-box">
            <div>
                <div class="card-title">🇵🇰 4. RAG Pakistan Tourism Assistant</div>
                <div class="card-desc">
                    A full implementation of Retrieval-Augmented Generation (RAG). Learn how to load documents, embed them using Google GenAI, index in an InMemoryVectorStore, and construct grounded prompts.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Pakistan RAG Assistant ➡️", key="btn_rag", use_container_width=True):
            st.switch_page("4_rag_tourism.py")

# Navigation setup
pages = [
    st.Page(show_home, title="Home Portal", icon="🏠", default=True),
    st.Page("1_llm.py", title="1. World Capital Finder", icon="🏛️"),
    st.Page("2_movie_info.py", title="2. Movie Info Finder", icon="🎬"),
    st.Page("3_chains.py", title="3. LangChain Chains Explained", icon="🔗"),
    st.Page("4_rag_tourism.py", title="4. RAG Pakistan Tourism Assistant", icon="🇵🇰"),
]

# Run navigation
pg = st.navigation(pages)
pg.run()
