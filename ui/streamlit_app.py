import streamlit as st
import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="FinAssist", layout="wide")

st.title("🐱 FinAssist: AI Support Agent")
st.markdown("*Prototype for Automated Support & Evaluation Pipeline*")

# Sidebar for controls
st.sidebar.header("Developer Controls")
debug_mode = st.sidebar.checkbox("Show Debug & Metrics", value=True)

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about late fees, refunds, or payment splits..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking & Evaluating..."):
            try:
                response = requests.post(f"{API_URL}/chat", json={"query": prompt})
                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    # --- THE "SENIOR" SHOWCASE ---
                    # If Debug Mode is on, show the Evaluation Metrics side-by-side
                    if debug_mode:
                        st.divider()
                        col1, col2, col3 = st.columns(3)
                        
                        metrics = data["evaluation"]
                        
                        # Color coding metrics
                        faith_color = "normal"
                        if metrics["faithfulness_score"] < 0.7: faith_color = "off"
                        elif metrics["faithfulness_score"] > 0.9: faith_color = "inverse"
                        
                        col1.metric(label="🛡️ Faithfulness Score", value=f"{metrics['faithfulness_score']:.2f}")
                        col2.metric(label="🎯 Relevance Score", value=f"{metrics['relevance_score']:.2f}")
                        
                        with col3:
                            st.caption("Auto-Evaluation Reasoning:")
                            st.info(metrics["reasoning"])
                        
                        with st.expander("🔍 View Retrieved Context (Source Data)"):
                            for i, ctx in enumerate(data["context"]):
                                st.text(f"Chunk {i+1}: {ctx}")

                else:
                    st.error("API Error")
            except Exception as e:
                st.error(f"Connection failed: {e}")