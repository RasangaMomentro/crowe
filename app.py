import streamlit as st
import json
import requests
from typing import Optional

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "34d17c26-a986-4b87-a228-81e15a1ecc86"
FLOW_ID = "41708703-20f2-4d0d-8e7a-2a7e7b621b03"
APPLICATION_TOKEN = st.secrets["APPLICATION_TOKEN"]
TWEAKS = {
    "ChatInput-RgtFO": {}, "ParseData-XbI0A": {}, "Prompt-6dcqx": {},
    "OpenAIModel-sPgyc": {}, "ChatOutput-f75Z7": {}, "AstraDB-Bk2ax": {},
    "OpenAIEmbeddings-H7bHs": {}
}

st.set_page_config(page_title="Crowe Malaysia Assistant", page_icon="🏢", layout="centered")

st.markdown("""
    <style>
    .stApp {background-color: #ffffff;}
    .stMarkdown {color: #333333;}
    .stButton button {
        background-color: rgba(247, 247, 248);
        color: black;
        border: 1px solid #e5e5e5;
        border-radius: 0.75rem;
        width: 100%;
        text-align: center;
        padding: 0.75rem;
        margin-bottom: 1rem;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        font-size: 0.9rem;
    }
    .stButton button:hover {
        background-color: #ffffff;
        border-color: #FDB813;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="column"] {padding: 0.5rem;}
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {background-color: #f5f5f5;}
    .assistant-message {
        background-color: #fffbeb;
        border-left: 5px solid #FDB813;
    }
    </style>
""", unsafe_allow_html=True)

def run_flow(message: str, endpoint: str = FLOW_ID, output_type: str = "chat",
            input_type: str = "chat", tweaks: Optional[dict] = TWEAKS) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
        "tweaks": tweaks
    }
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if "messages" not in st.session_state:
    st.session_state.messages = []

st.image("logo.png", width=200)
st.title("Crowe Malaysia Advisory Assistant")

st.markdown("""
    <div style='background-color: #fffbeb; padding: 1rem; border-radius: 0.5rem; 
    margin-bottom: 2rem; border-left: 5px solid #FDB813;'>
        Welcome to Crowe Malaysia's AI Assistant. I can help you with information 
        about taxation, IPO services, and investing in Malaysia, based on the wealth of knowledge available at Crowe
    </div>
""", unsafe_allow_html=True)

categories = {
    "Taxation": [
        "What are the key take aways for corporate tax in 2024",
        "What is the new Indirect Tax rate"
    ],
    "IPO": [
        "What are the key accounting challenges in an IPO",
        "How can Crowe help my company with an IPO"
    ],
    "Investing in Malaysia": [
        "What is the cost of forming a business in Malaysia",
        "What are the tax incentives for investing in Malaysia"
    ]
}

# Examples section
st.markdown("""
    <div style='text-align: center; margin: 2rem 0 1rem 0;'>
        <h2 style='color: #333333; font-size: 1.5rem;'>Examples</h2>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='
        background-color: #f7f7f8;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 2rem;
    '>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

for (col, (category, prompts)) in zip([col1, col2, col3], categories.items()):
    with col:
        st.markdown(f"<div style='font-weight: bold; margin-bottom: 1rem; color: #333333;'>{category}</div>", 
                   unsafe_allow_html=True)
        for prompt in prompts:
            if st.button(prompt, key=f"sample_{prompt}"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                response = run_flow(prompt)
                try:
                    if isinstance(response, dict):
                        message = (response.get('outputs', [])[0]
                                 .get('outputs', [])[0]
                                 .get('results', {})
                                 .get('message', {})
                                 .get('data', {})
                                 .get('text', 'No response received'))
                        st.session_state.messages.append({"role": "assistant", "content": message})
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# Chat display and input
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"""
            <div class='chat-message {message["role"]}-message'>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = run_flow(prompt)
    try:
        if isinstance(response, dict):
            message = (response.get('outputs', [])[0]
                     .get('outputs', [])[0]
                     .get('results', {})
                     .get('message', {})
                     .get('data', {})
                     .get('text', 'No response received'))
            st.session_state.messages.append({"role": "assistant", "content": message})
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")
    st.rerun()

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666666; font-size: 0.8rem;'>
        © 2025 Crowe Malaysia PLT. All rights reserved.<br>
        A member of Crowe Global
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("Clear Conversation", key="clear"):
    st.session_state.messages = []
    st.rerun()
