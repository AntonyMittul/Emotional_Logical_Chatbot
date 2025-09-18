import streamlit as st
from main import graph

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")

# Session state to keep track of conversation
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "message_type" not in st.session_state:
    st.session_state["message_type"] = None

st.title("🤖 NEURA (Emotional and Logical AI Chatbot)")

# Display previous messages
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # Run through LangGraph
    state = {"messages": st.session_state["messages"], "message_type": None}
    state = graph.invoke(state)

    # Save response
    st.session_state["messages"] = state["messages"]

    # Display assistant message
    last_message = state["messages"][-1]
    st.chat_message("assistant").markdown(last_message["content"])
