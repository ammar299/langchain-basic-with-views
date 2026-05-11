import os
import certifi
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.runnables import RunnableParallel, RunnableBranch
from pydantic import BaseModel, Field
from typing import Literal

# Setup Environment
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

# Initialize LLM using your setup
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    temperature=0.0
)

# UI Styling
st.set_page_config(page_title="LangChain Chains Explained", page_icon="🔗", layout="wide")
st.title("🔗 Understanding LangChain Chains")
st.markdown("This app explains the 4 fundamental types of chains in LangChain: **Normal, Sequential, Parallel, and Conditional**, adapted to use Google Gemini.")

tabs = st.tabs(["1️⃣ Normal Chain", "2️⃣ Sequential Chain", "3️⃣ Parallel Chain", "4️⃣ Conditional Chain"])

# ----------------------------------------
# 1. Normal Chain
# ----------------------------------------
with tabs[0]:
    st.header("1. Normal Chain")
    st.markdown("""
    **What it is:** The most basic chain. It simply connects a Prompt Template, an LLM, and an Output Parser in a straight line.
    
    `PromptTemplate` ➡️ `LLM` ➡️ `StrOutputParser`
    """)
    
    st.divider()
    question = st.text_input("Ask a simple question:", value="What is the capital of France?")
    
    if st.button("Run Normal Chain"):
        with st.spinner("Running..."):
            parser = StrOutputParser()
            template = PromptTemplate.from_template("You are a helpful assistant. Answer the question: {question}")
            
            # Building the chain using the pipe (|) syntax
            chain = template | llm | parser
            
            result = chain.invoke({"question": question})
            st.success(result)

# ----------------------------------------
# 2. Sequential Chain
# ----------------------------------------
with tabs[1]:
    st.header("2. Sequential Chain")
    st.markdown("""
    **What it is:** Connects multiple chains together where the output of one chain automatically becomes the input for the next.
    
    `Prompt 1` ➡️ `LLM` ➡️ `Parser 1` ➡️ `Prompt 2` ➡️ `LLM` ➡️ `Parser 2`
    """)
    
    st.divider()
    topic = st.text_input("Enter a topic for summary and key points:", value="Generative AI")
    
    if st.button("Run Sequential Chain"):
        with st.spinner("Step 1 (Summary) ➡️ Step 2 (Key Points)..."):
            parser = StrOutputParser()
            
            # Step 1
            seq_template1 = PromptTemplate.from_template("Give me a short summary on topic: {topic}")
            # Step 2 (takes {summary} as input from Step 1)
            seq_template2 = PromptTemplate.from_template("Based on the summary, give me 5 key points on it:\n{summary}")
            
            # Building the sequential chain
            seq_chain = seq_template1 | llm | parser | seq_template2 | llm | parser
            
            result = seq_chain.invoke({"topic": topic})
            st.success(result)

# ----------------------------------------
# 3. Parallel Chain
# ----------------------------------------
with tabs[2]:
    st.header("3. Parallel Chain")
    st.markdown("""
    **What it is:** Runs multiple chains at the same time (in parallel) and combines their outputs into a single dictionary object. It is very fast because the LLM calls happen simultaneously!
    
    ```text
             /➡️ Chain 1 (Summary) \\
    Input ➡️                        ➡️ Merged Output
             \\➡️ Chain 2 (Key Pts) /
    ```
    """)
    
    st.divider()
    topic_par = st.text_input("Enter a topic to generate summary and key points simultaneously:", value="Quantum Computing", key="par_input")
    
    if st.button("Run Parallel Chain"):
        with st.spinner("Running chains simultaneously in parallel..."):
            parser = StrOutputParser()
            
            par_template1 = PromptTemplate.from_template("Give me a very short summary on topic: {topic}")
            par_template2 = PromptTemplate.from_template("Give me 3 key points on topic: {topic}")
            
            par_chain1 = par_template1 | llm | parser
            par_chain2 = par_template2 | llm | parser
            
            # Combine them in parallel
            parallel_chain = RunnableParallel({
                "summary": par_chain1,
                "key_points": par_chain2
            })
            
            mer_template = PromptTemplate.from_template("""
Combine the following information into a comprehensive output:
                                             
Summary: {summary}
Key Points: {key_points}
            """)
            mer_chain = mer_template | llm | parser
            
            # The parallel output dictionary automatically fulfills the {summary} and {key_points} in mer_chain
            final_chain = parallel_chain | mer_chain
            
            result = final_chain.invoke({"topic": topic_par})
            st.success(result)

# ----------------------------------------
# 4. Conditional Chain (Routing)
# ----------------------------------------
with tabs[3]:
    st.header("4. Conditional Chain (Routing)")
    st.markdown("""
    **What it is:** Evaluates an input and routes it to different chains based on conditions.
    """)
    
    st.divider()
    review = st.text_area("Enter a movie review:", value="It was okay—some good moments, but nothing particularly memorable. Just an average watch.")
    
    if st.button("Run Conditional Chain"):
        with st.spinner("Detecting sentiment and routing..."):
            # We use Pydantic for strict output formatting so we can route effectively
            class ReviewSentiment(BaseModel):
                sentiment: Literal["positive", "negative", "neutral"] = Field(description="The sentiment of the movie review")

            str_parser = StrOutputParser()
            pydantic_parser = PydanticOutputParser(pydantic_object=ReviewSentiment)
            
            con_template1 = PromptTemplate.from_template("""
Give me the sentiment of the movie review: {review}
{format_instruction}
            """, partial_variables={"format_instruction": pydantic_parser.get_format_instructions()})
            
            # Chain 1: Determines sentiment
            review_chain = con_template1 | llm | pydantic_parser
            
            # Templates for routing
            pos_template = PromptTemplate.from_template("The review is positive so write a short appreciation:\n{review}")
            neg_template = PromptTemplate.from_template("The review is negative so write a short critique:\n{review}")
            neu_template = PromptTemplate.from_template("The review is neutral so write a short balanced remark:\n{review}")
            default_template = PromptTemplate.from_template("I could not detect the clear sentiment. Provide a neutral response:\n{review}")
            
            # RunnableBranch evaluates the sentiment dictionary and routes to the right template
            branch_chain = RunnableBranch(
                (lambda x: x.sentiment == "positive", pos_template | llm | str_parser),
                (lambda x: x.sentiment == "negative", neg_template | llm | str_parser),
                (lambda x: x.sentiment == "neutral", neu_template | llm | str_parser),
                default_template | llm | str_parser
            )
            
            # Combining the sentiment detector and the router
            final_con_chain = review_chain | branch_chain
            
            # Let's show both outputs step-by-step for clarity!
            sentiment_result = review_chain.invoke({"review": review})
            st.info(f"**🧠 Step 1 (Detection):** The LLM detected the sentiment as **{sentiment_result.sentiment.upper()}**")
            
            result = final_con_chain.invoke({"review": review})
            st.success(f"**🔀 Step 2 (Routing):** Based on the sentiment, here is the generated response:\n\n{result}")
