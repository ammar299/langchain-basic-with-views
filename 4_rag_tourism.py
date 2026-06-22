import os
import certifi
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return None
import streamlit as st
from streamlit_config import init_google_api_key
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

# Setup Environment
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()
init_google_api_key()

# Initialize LLMs & Embeddings
@st.cache_resource
def get_llm():
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview", 
            temperature=0.2
        )
    except Exception as e:
        if "API key" in str(e):
            st.error("⚠️ Google API key not set. Please set GOOGLE_API_KEY environment variable or add it to Streamlit Secrets.")
            st.stop()
        raise

# Static Pakistan Tourism Corpus
TOURISM_DATABASE = [
    # Lahore
    Document(
        page_content="Lahore, Punjab: The cultural heart of Pakistan. Major sights include the majestic Badshahi Mosque, the historic Lahore Fort (Shahi Qila) featuring the Sheesh Mahal, and the colorful Wazir Khan Mosque. The Shalimar Gardens, a UNESCO World Heritage site, showcases Mughal garden architecture.",
        metadata={"destination": "Lahore, Punjab", "category": "Mughal Heritage & Sights"}
    ),
    Document(
        page_content="Lahore, Punjab: Food culture is legendary here. Visit the Fort Road Food Street at night for spectacular views of Badshahi Mosque and delicious Lahori Karahi, Siri Paye, and Hareesa. Explore Anarkali Bazaar for historical street shopping and traditional snacks.",
        metadata={"destination": "Lahore, Punjab", "category": "Food & Shopping"}
    ),
    
    # Karachi
    Document(
        page_content="Karachi, Sindh: Pakistan's largest city and economic hub. Key attractions include Clifton Beach (popular for camel rides), the white-marble Mazar-e-Quaid (Mausoleum of Muhammad Ali Jinnah), the Italian-gothic Mohatta Palace, and the waterfront food street Port Grand.",
        metadata={"destination": "Karachi, Sindh", "category": "Coastline & Landmarks"}
    ),
    Document(
        page_content="Karachi, Sindh: Famous for its diverse food scene. Burns Road is the ultimate food destination for authentic Karachi Nihari, Bun Kababs, Haleem, and Biryani. The city is also known for its lively night markets and shopping centers like Clifton and Tariq Road.",
        metadata={"destination": "Karachi, Sindh", "category": "Food & Culture"}
    ),
    
    # Islamabad
    Document(
        page_content="Islamabad, Capital Territory: The modern, green capital city. Faisal Mosque, one of the largest mosques in the world, is situated at the foot of the Margalla Hills. Visit Daman-e-Koh and the Monal restaurant for a panoramic view of the entire city. Rawal Lake and Shakarparian Park offer peaceful nature escapes.",
        metadata={"destination": "Islamabad", "category": "Scenic & Landmarks"}
    ),
    
    # Peshawar
    Document(
        page_content="Peshawar, Khyber Pakhtunkhwa: One of the oldest cities in South Asia. Walk through the bustling Qissa Khwani Bazaar (Storytellers' Market), visit the Peshawar Museum to view ancient Buddhist Gandhara art, and eat the famous Charsi Tikka or Kabuli Pulao in local bazaars.",
        metadata={"destination": "Peshawar, KPK", "category": "History & Food"}
    ),
    
    # Hunza Valley
    Document(
        page_content="Hunza Valley, Gilgit-Baltistan: Famous for its high peaks, lush apricot gardens, and long-lived locals. Main attractions include Karimabad town, the ancient Baltit Fort and Altit Fort, the bright blue Attabad Lake (popular for boating), and the sharp, towering Passu Cones. Local specialties include apricot cake and walnut cakes.",
        metadata={"destination": "Hunza, Gilgit-Baltistan", "category": "Nature & Forts"}
    ),
    
    # Skardu
    Document(
        page_content="Skardu, Gilgit-Baltistan: The gateway to the world's highest peaks, including K2. Key spots include Shangrila Resort (Lower Kachura Lake), the vast Deosai National Park (the second-highest plateau in the world, known for Himalayan brown bears and wildflowers), and the cold sand dunes of Sarfaranga Desert.",
        metadata={"destination": "Skardu, Gilgit-Baltistan", "category": "Mountains & Lakes"}
    ),
    
    # Swat Valley
    Document(
        page_content="Swat Valley, Khyber Pakhtunkhwa: Referred to as the 'Switzerland of the East'. Top destinations include the Malam Jabba ski resort (featuring skiing and a chairlift), Kalam Valley, the dense pine forests of Ushu, and the pristine, turquoise Mahodand Lake.",
        metadata={"destination": "Swat, KPK", "category": "Resorts & Nature"}
    ),
    
    # Murree & Nathia Gali
    Document(
        page_content="Murree & Nathia Gali, Punjab/KPK: Popular hill stations close to Islamabad. Murree's Mall Road is famous for shopping and chairlifts. Nathia Gali in the Galyat region offers quiet forest hiking trails (like Pipeline Track), pine-scented mountain air, and cool summer temperatures.",
        metadata={"destination": "Murree & Galyat", "category": "Hill Stations"}
    ),
    
    # Neelum Valley
    Document(
        page_content="Neelum Valley, Azad Kashmir: A stunning 144 km long bow-shaped valley. Key locations are Keran, Sharda (home to Sharda Peeth, ancient ruins of a historic Hindu temple/university), Kel, and the scenic village of Arang Kel (reached via chairlift and short hike). Ratti Gali Lake is a high-altitude alpine lake in the valley.",
        metadata={"destination": "Neelum Valley, Kashmir", "category": "Valleys & Alpine Lakes"}
    ),
    
    # Multan & Bahawalpur
    Document(
        page_content="Multan & Bahawalpur, Punjab: Multan is the 'City of Saints,' famous for the blue-tiled Sufi Shrine of Shah Rukn-e-Alam, blue pottery, and Sohan Halwa. Nearby Bahawalpur features the grand Noor Mahal (palace of the Nawabs) and the colossal Derawar Fort in the Cholistan Desert.",
        metadata={"destination": "Multan & Bahawalpur", "category": "Sufi Heritage & Palaces"}
    ),
    
    # Taxila
    Document(
        page_content="Taxila, Punjab: A UNESCO World Heritage site and a center of the ancient Gandhara civilization. Explore ruins of Buddhist monasteries like Julian, the archaeological remains of Sirkap city, and the Taxila Museum containing a vast collection of stone sculpture and coins.",
        metadata={"destination": "Taxila, Punjab", "category": "Archaeology & Gandhara"}
    ),
    
    # Mohenjo-daro
    Document(
        page_content="Mohenjo-daro, Sindh: An archaeological site of the Indus Valley Civilization dating back to 2500 BCE. It showcases advanced ancient urban planning, a highly structured brick drainage system, the Great Bath, and historic assembly halls, reflecting ancient engineering.",
        metadata={"destination": "Mohenjo-daro, Sindh", "category": "Ancient Civilizations"}
    ),
    
    # Kumrat Valley
    Document(
        page_content="Kumrat Valley, Khyber Pakhtunkhwa: A pristine hidden valley in Upper Dir. Known for its dense towering deodar and pine forests, the roaring Panjkora River, Jahaz Banda meadows, and the beautiful alpine Katora Lake surrounded by snowy mountains.",
        metadata={"destination": "Kumrat Valley, KPK", "category": "Meadows & Pine Forests"}
    ),
    
    # Gorakh Hill
    Document(
        page_content="Gorakh Hill, Sindh: A hill station situated at an elevation of 5,688 feet in the Kirthar Mountains. Known as the 'Murree of Sindh,' it experiences cold temperatures in winter. Tourists visit for stunning sunrise views, sunset photography, and stargazing.",
        metadata={"destination": "Gorakh Hill, Sindh", "category": "Desert Hill Station"}
    ),
    
    # Hingol National Park
    Document(
        page_content="Hingol National Park, Balochistan: Pakistan's largest national park. It lies along the Makran Coastal Highway. Famous for its mud volcanoes, the pristine Kund Malir Beach, and bizarre rock formations like the 'Princess of Hope' and the Hingol Sphinx.",
        metadata={"destination": "Hingol, Balochistan", "category": "Canyons & Beaches"}
    ),
    
    # Quetta & Ziarat
    Document(
        page_content="Quetta & Ziarat, Balochistan: Quetta is known for dry fruits, Hanna Lake, and traditional food like Sajji. Nearby Ziarat houses the world's second-largest Juniper Forest and the historic Ziarat Residency, a wooden building where Quaid-e-Azam spent his last days.",
        metadata={"destination": "Ziarat & Quetta, Balochistan", "category": "Juniper Forests & Culture"}
    ),
    
    # NEW: Fairy Meadows (Gilgit-Baltistan)
    Document(
        page_content="Fairy Meadows, Gilgit-Baltistan: Lush green pastures situated at the base of Nanga Parbat (8,126 meters, the 'Killer Mountain'). It offers breathtaking views of the mountain's north face and Raikot Glacier. Reached via a thrilling jeep ride from Raikot Bridge on Karakoram Highway, followed by a 3-4 hour hike.",
        metadata={"destination": "Fairy Meadows, Gilgit-Baltistan", "category": "Lakes & Trekking"}
    ),
    
    # NEW: Khunjerab Pass (Gilgit-Baltistan)
    Document(
        page_content="Khunjerab Pass, Gilgit-Baltistan: The highest paved international border crossing in the world (4,693 meters), connecting Pakistan and China. It is home to the Karakoram National Park, which protects endangered snow leopards, Himalayan ibex, and Marco Polo sheep. The world's highest ATM is located here.",
        metadata={"destination": "Khunjerab Pass, Gilgit-Baltistan", "category": "High Borders & Wildlife"}
    ),
    
    # NEW: Gilgit City (Gilgit-Baltistan)
    Document(
        page_content="Gilgit City, Gilgit-Baltistan: The administrative capital of Gilgit-Baltistan. Key sights include the Kargah Buddha, a 7th-century rock carving on a cliffside, and the Danyore Suspension Bridge. It serves as a major hub for mountaineering expeditions heading to Karakoram and Hindu Kush ranges.",
        metadata={"destination": "Gilgit City, Gilgit-Baltistan", "category": "Towns & Rock Carvings"}
    ),
    
    # NEW: Naran & Kaghan Valley (KPK)
    Document(
        page_content="Naran & Kaghan Valley, Khyber Pakhtunkhwa: Famous alpine valleys. Key attractions are Lake Saif-ul-Malook, associated with the folklore of a prince and a fairy, Babusar Top (a high mountain pass at 13,691 feet connecting to Gilgit), Lulusar Lake, and the white waters of Kunhar River (popular for rafting).",
        metadata={"destination": "Naran & Kaghan, KPK", "category": "Alpine Lakes & Passes"}
    ),
    
    # NEW: Chitral & Kalash Valley (KPK)
    Document(
        page_content="Chitral & Kalash Valley, Khyber Pakhtunkhwa: Located in the Hindu Kush range near Tirich Mir peak. Famous for the Kalash Valleys (Bumburet, Rumbur, Birir) where the Kalash people preserve their unique polytheistic culture, dress, and annual spring festival 'Chilam Joshi'.",
        metadata={"destination": "Chitral & Kalash, KPK", "category": "Unique Culture & Festivals"}
    ),
    
    # NEW: Gwadar (Balochistan)
    Document(
        page_content="Gwadar, Balochistan: A port city known for its deep sea port, the Hammerhead headland, and pristine desert-ocean beaches. Nearby Ormara Beach offers stunning sand cliffs. Astola Island (Island of the Seven Hills) lies off the coast of Pasni, boasting crystal-clear water and marine life ideal for scuba diving.",
        metadata={"destination": "Gwadar, Balochistan", "category": "Beaches & Deep Sea Port"}
    ),
    
    # NEW: Mehrgarh (Balochistan)
    Document(
        page_content="Mehrgarh, Balochistan: A Neolithic archaeological site dating back to 7000 BCE, located on the Kachi Plain. It is one of the earliest sites with evidence of farming (wheat and barley) and herding (sheep, goats, cattle) in South Asia, pre-dating the Indus Valley Civilization.",
        metadata={"destination": "Mehrgarh, Balochistan", "category": "Ancient Civilizations"}
    ),
    
    # NEW: Banjosa Lake & Toli Peer (Azad Kashmir)
    Document(
        page_content="Banjosa Lake & Toli Peer, Azad Kashmir: Located near Rawalakot. Banjosa Lake is a scenic artificial lake surrounded by dense pine forests. Toli Peer is a hilltop meadow situated at an altitude of 8,800 feet, offering panoramic views of Azad Kashmir's rolling green hills and distant mountain peaks.",
        metadata={"destination": "Banjosa & Toli Peer, Kashmir", "category": "Meadows & Lakes"}
    ),
    
    # NEW: Ganga Choti (Azad Kashmir)
    Document(
        page_content="Ganga Choti, Azad Kashmir: A scenic peak in the Bagh District, standing at an elevation of 9,989 feet. It is a popular spot for hiking, trekking, and overnight camping, offering breathtaking views of snow-covered Pir Panjal ranges and surrounding valleys.",
        metadata={"destination": "Ganga Choti, Kashmir", "category": "Peaks & Camping"}
    )
]

# Cache the vector store setup
@st.cache_resource
def get_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(TOURISM_DATABASE)
    return vector_store

# UI Styling
# Injecting Custom CSS for premium styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}
.rag-header {
    background: linear-gradient(135deg, #112a1d, #06140e);
    padding: 2rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    margin-bottom: 2rem;
}
.rag-header h1 {
    margin: 0;
    font-weight: 800;
    background: linear-gradient(90deg, #10b981, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.rag-card {
    background: rgba(255, 255, 255, 0.02);
    padding: 1.25rem;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 1rem;
    transition: all 0.2s ease-in-out;
}
.rag-card:hover {
    transform: translateY(-2px);
    border-color: rgba(16, 185, 129, 0.25);
    background: rgba(255, 255, 255, 0.04);
}
.step-badge {
    background: linear-gradient(90deg, #10b981, #059669);
    color: white;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.75rem;
    display: inline-block;
    margin-bottom: 0.5rem;
}
.doc-badge {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.5rem;
}
.cat-badge {
    background: rgba(168, 85, 247, 0.15);
    border: 1px solid rgba(168, 85, 247, 0.3);
    color: #c084fc;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.5rem;
}
.score-badge {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #60a5fa;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("""
<div class="rag-header">
    <h1>🇵🇰 RAG Pakistan Tourism Assistant</h1>
    <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 0.5rem; margin-bottom: 0;">
        Implementing <strong>Retrieval-Augmented Generation (RAG)</strong> to answer travel questions using custom tourist guides for Pakistan's major cities, northern areas, and hidden gems.
    </p>
</div>
""", unsafe_allow_html=True)

# Explanatory Steps Accordion
with st.expander("🎓 Learn the 4 Short Steps of RAG in this Project", expanded=True):
    st.markdown("""
    This application implements RAG using a four-step pipeline:
    1. **Document Loading**: We start with a static database of travel guides for Pakistan's cities and towns (Lahore, Karachi, Hunza, Skardu, Neelum, Ziarat, etc.).
    2. **Embedding & Storage**: Text chunks are converted into 3072-dimensional vectors using Gemini's `gemini-embedding-001` model and stored in an `InMemoryVectorStore`.
    3. **Similarity Retrieval**: When you submit a question, the vector database finds the top 2 guide entries most semantically similar to your question.
    4. **Augmented Generation**: The matching guidelines are retrieved and injected into a prompt template as "Context". Gemini uses *only* this context to draft the final response.
    """)

# Load vector store and LLM
vector_store = get_vector_store()
llm = get_llm()

# Layout
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("🤖 Ask the AI Travel Assistant")
    st.markdown("Ask a question about Pakistan's major cities, remote valleys, archaeological sites, or hill stations.")
    
    # Sample questions helper
    sample_queries = [
        "Where can I see the Princess of Hope rock formation?",
        "What are the main attractions to visit in Hunza Valley?",
        "What is the historical significance of Sharda Peeth in Neelum Valley?",
        "Where is the best place to eat authentic Nihari in Karachi?",
        "Which national park in Skardu is home to Himalayan brown bears?",
        "Where can I go skiing in Swat Valley?",
        "What is there to do in Ziarat?",
        "Tell me about the historical palaces in Bahawalpur.",
        "How do you get to Fairy Meadows and see Nanga Parbat?",
        "What animals are protected in Khunjerab Pass near the China border?",
        "What is the historical significance of Mehrgarh in Balochistan?",
        "Tell me about Lake Saif-ul-Malook and Babusar Top.",
        "What is unique about Chitral and Kalash Valleys?",
        "Where is Astola Island located and what can you do there?",
        "Tell me about Banjosa Lake and Toli Peer in Kashmir."
    ]
    selected_sample = st.selectbox("Or choose a sample question:", ["-- Select a question --"] + sample_queries)
    
    default_val = selected_sample if selected_sample != "-- Select a question --" else "What are the main attractions to visit in Hunza Valley?"
    user_query = st.text_input("Enter your travel query:", value=default_val)
    
    run_button = st.button("Run RAG Pipeline 🚀", type="primary")
    
    st.write("---")
    
    # Section to Dynamically Add custom documents
    st.subheader("➕ Add custom guidelines to the RAG Database")
    st.markdown("You can expand the knowledge base dynamically by adding custom tourist tips below!")
    
    with st.form("add_doc_form", clear_on_submit=True):
        new_city = st.text_input("Destination / City Name", placeholder="e.g. Gwadar, Balochistan")
        new_category = st.text_input("Category", placeholder="e.g. Port & Sights")
        new_content = st.text_area("Content Guideline", placeholder="Write travel advice, rules, or details about the location...")
        
        submitted = st.form_submit_button("Add to Knowledge Base 📂")
        if submitted:
            if new_city and new_category and new_content:
                full_text = f"{new_city}: {new_content}"
                new_doc = Document(
                    page_content=full_text,
                    metadata={"destination": new_city, "category": new_category}
                )
                vector_store.add_documents([new_doc])
                st.toast(f"✅ Added {new_city} to the vector store!", icon="📁")
                st.success(f"Added custom guide for **{new_city}** successfully! You can now query about it.")
            else:
                st.error("Please fill in all fields before submitting.")

with right_col:
    if run_button and user_query:
        st.subheader("🔍 RAG Step-by-Step Execution")
        
        with st.spinner("Processing RAG pipeline..."):
            # Step 1: Retrieval
            retrieved_docs_with_scores = vector_store.similarity_search_with_score(user_query, k=2)
            
            # Step 1 Card
            st.markdown("""
            <div class="step-badge">Step 1: Similarity Retrieval</div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"Found **{len(retrieved_docs_with_scores)}** matching documents in the vector store:")
            
            for doc, score in retrieved_docs_with_scores:
                dest = doc.metadata.get("destination", "Unknown")
                cat = doc.metadata.get("category", "General")
                st.markdown(f"""
                <div class="rag-card">
                    <span class="doc-badge">📍 {dest}</span>
                    <span class="cat-badge">📂 {cat}</span>
                    <span class="score-badge">🎯 Score: {score:.4f}</span>
                    <p style="margin-top: 0.5rem; margin-bottom: 0; font-size: 0.95rem; line-height: 1.4;">
                        {doc.page_content}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Step 2: Context Formatting & Prompt Construction
            context_text = "\n\n".join([doc.page_content for doc, _ in retrieved_docs_with_scores])
            
            prompt_template = PromptTemplate.from_template("""You are an expert travel assistant. Answer the user's question using ONLY the provided context. If the context does not contain the answer, say "I'm sorry, but that information is not available in my tourism knowledge base." Do not make up information.

Context:
{context}

Question: {question}
Answer:""")
            
            formatted_prompt = prompt_template.format(context=context_text, question=user_query)
            
            st.markdown("""
            <div class="step-badge">Step 2: Prompt Construction</div>
            """, unsafe_allow_html=True)
            
            with st.expander("Show filled prompt template sent to Gemini"):
                st.text_area("Formatted Prompt", value=formatted_prompt, height=220, disabled=True)
                
            # Step 3: LLM Response Generation
            st.markdown("""
            <div class="step-badge">Step 3: Response Generation</div>
            """, unsafe_allow_html=True)
            
            # Run LLM and parse output to extract only the text
            chain = llm | StrOutputParser()
            response_text = chain.invoke(formatted_prompt)
            
            st.markdown("### 🌴 AI Travel Agent Response:")
            st.success(response_text)
            
    else:
        # Show database explorer when no query is run
        st.subheader("🗄️ Explore RAG Knowledge Base")
        st.markdown("Here are the currently loaded guides in the `InMemoryVectorStore`:")
        
        # Pull all documents from vector store using the underlying stores
        all_docs = list(vector_store.store.values())
        
        for idx, doc in enumerate(all_docs):
            metadata = doc.get("metadata", {})
            dest = metadata.get("destination", "Unknown")
            cat = metadata.get("category", "General")
            content = doc.get("text", "")
            st.markdown(f"""
            <div class="rag-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                    <div>
                        <span class="doc-badge">📍 {dest}</span>
                        <span class="cat-badge">📂 {cat}</span>
                    </div>
                    <span style="font-size: 0.75rem; color: #64748b;">ID: Doc {idx+1}</span>
                </div>
                <p style="margin: 0; font-size: 0.9rem; color: #cbd5e1; line-height: 1.4;">
                    {content}
                </p>
            </div>
            """, unsafe_allow_html=True)
