import streamlit as st
import json
import requests
from typing import Optional

# Constants from your API code
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "34d17c26-a986-4b87-a228-81e15a1ecc86"
FLOW_ID = "41708703-20f2-4d0d-8e7a-2a7e7b621b03"
APPLICATION_TOKEN = st.secrets["APPLICATION_TOKEN"]

# Your TWEAKS dictionary
TWEAKS = {
    "ChatInput-RgtFO": {},
    "ParseData-XbI0A": {},
    "Prompt-6dcqx": {},
    "OpenAIModel-sPgyc": {},
    "ChatOutput-f75Z7": {},
    "AstraDB-Bk2ax": {},
    "OpenAIEmbeddings-H7bHs": {}
}

# Crowe website styling
st.set_page_config(
    page_title="Crowe Malaysia Assistant",
    page_icon="🏢",
    layout="centered"
)

# Custom CSS matching Crowe's branding
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .stMarkdown {
        color: #333333;
    }
    .stButton button {
        background-color: #BE0D34;
        color: white;
    }
    .stButton button:hover {
        background-color: #8B0A26;
    }
    h1, h2, h3 {
        color: #BE0D34;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #f5f5f5;
    }
    .assistant-message {
        background-color: #fef2f4;
        border-left: 5px solid #BE0D34;
    }
    .category-header {
        color: #BE0D34;
        font-size: 1.1rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .sample-prompt-container {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
    .prompt-button {
        width: 100%;
        text-align: left;
        padding: 0.5rem;
        margin: 0.2rem 0;
        background-color: white;
        border: 1px solid #dee2e6;
        border-radius: 0.3rem;
        cursor: pointer;
    }
    .prompt-button:hover {
        background-color: #fef2f4;
        border-color: #BE0D34;
    }
    </style>
""", unsafe_allow_html=True)

def run_flow(message: str,
    endpoint: str = FLOW_ID,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = TWEAKS) -> dict:
    
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if tweaks:
        payload["tweaks"] = tweaks
        
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header with Crowe styling and logo
st.image("logo.png", width=200)
st.title("Crowe Malaysia Advisory Assistant")

# Welcome message
st.markdown("""
    <div style='background-color: #fef2f4; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; border-left: 5px solid #BE0D34;'>
        Welcome to Crowe Malaysia's AI Assistant. I can help you with information about taxation, IPO services, and investing in Malaysia.
    </div>
""", unsafe_allow_html=True)

# Sample prompts organized by category
sample_prompts = {
    "Taxation": [
        "What are the key take aways for corporate tax in 2024",
        "What is the new Indirect Tax rate"
    ],
    "IPO": [
        "What are the key accounting challenges when it comes to an IPO",
        "How can Crowe help my company with an IPO"
    ],
    "Investing in Malaysia": [
        "What is the cost of forming a business in Malaysia",
        "What are the tax incentives available when investing in Malaysia"
    ]
}

# Display categorized sample prompts
st.markdown("### Explore our services:")
for category, prompts in sample_prompts.items():
    st.markdown(f"<div class='category-header'>{category}</div>", unsafe_allow_html=True)
    for prompt in prompts:
        if st.button(prompt, key=f"sample_{prompt}"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Processing your request..."):
                    response = run_flow(prompt)
                    try:
                        if isinstance(response, dict):
                            message = (response.get('outputs', [])[0]
                                     .get('outputs', [])[0]
                                     .get('results', {})
                                     .get('message', {})
                                     .get('data', {})
                                     .get('text', 'No response received'))
                            
                            st.markdown(message)
                            st.session_state.messages.append({"role": "assistant", "content": message})
                        else:
                            st.error("I apologize, but I couldn't process your request at the moment.")
                    except Exception as e:
                        st.error("I apologize, but something went wrong. Please try again.")
                        st.write("Technical details:", str(e))

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"""
            <div class='chat-message {message["role"]}-message'>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Processing your request..."):
            response = run_flow(prompt)
            try:
                if isinstance(response, dict):
                    message = (response.get('outputs', [])[0]
                             .get('outputs', [])[0]
                             .get('results', {})
                             .get('message', {})
                             .get('data', {})
                             .get('text', 'No response received'))
                    
                    st.markdown(message)
                    st.session_state.messages.append({"role": "assistant", "content": message})
                else:
                    st.error("I apologize, but I couldn't process your request at the moment.")
            except Exception as e:
                st.error("I apologize, but something went wrong. Please try again.")
                st.write("Technical details:", str(e))

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666666; font-size: 0.8rem;'>
        © 2025 Crowe Malaysia PLT. All rights reserved.<br>
        A member of Crowe Global
    </div>
""", unsafe_allow_html=True)

# Clear chat button in sidebar
if st.sidebar.button("Clear Conversation", key="clear"):
    st.session_state.messages = []
    st.rerun()
