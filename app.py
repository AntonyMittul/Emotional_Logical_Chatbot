import streamlit as st
from main import graph

# ----------------------- PAGE CONFIG -----------------------
st.set_page_config(page_title="NEURA - AI Chatbot", page_icon="🤖", layout="wide")

# ----------------------- CUSTOM CSS -----------------------
st.markdown("""
    <style>
        .main {
            background-color: #f9f9fb;
        }
        .chat-container {
            margin-bottom: 10px;
            display: flex;
        }
        .chat-bubble {
            padding: 12px 16px;
            border-radius: 15px;
            max-width: 55%; /* Reduced width */
            word-wrap: break-word;
            font-size: 15px;
            line-height: 1.4;
        }
        .user-msg {
            background-color: transparent;
            margin-left: auto;
            text-align: justify;
        }
        .assistant-msg {
            background-color: transparent;
            margin-right: auto;
            text-align: justify;
        }
        .header {
            font-size: 26px;
            font-weight: bold;
            color: #2C3E50;
        }
        .subheader {
            font-size: 16px;
            color: #7F8C8D;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------- SESSION STATE -----------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "message_type" not in st.session_state:
    st.session_state["message_type"] = None

# ----------------------- HEADER -----------------------
st.markdown('<p class="header">🤖 NEURA</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Your AI assistant for <b>Therapeutical</b> and <b>Logical</b> responses.</p>', unsafe_allow_html=True)

# ----------------------- SIDEBAR -----------------------
with st.sidebar:
    st.title("ℹ️ About NEURA")
    st.write("""
    NEURA is an AI-powered chatbot that adapts its responses based on your needs:
    - 🧠 Logical mode: Provides facts, reasoning, and analysis.  
    - 💙 Emotional mode: Offers empathy, support, and guidance.  
    
    **Tip:** Type *exit* in console to stop the bot.
    """)
    st.markdown("---")
    st.caption("Built with Streamlit, LangGraph & Gemini API")

# ----------------------- CHAT HISTORY -----------------------
for msg in st.session_state["messages"]:
    role_class = "user-msg" if msg["role"] == "user" else "assistant-msg"
    st.markdown(f"""
        <div class="chat-container">
            <div class="chat-bubble {role_class}">{msg["content"]}</div>
        </div>
    """, unsafe_allow_html=True)

# ----------------------- CHAT INPUT -----------------------
if prompt := st.chat_input("Type your message..."):
    # Save and show user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.markdown(f"""
        <div class="chat-container">
            <div class="chat-bubble user-msg">{prompt}</div>
        </div>
    """, unsafe_allow_html=True)

    # Process with LangGraph
    with st.spinner("NEURA is thinking..."):
        state = {"messages": st.session_state["messages"], "message_type": None}
        state = graph.invoke(state)

    # Save assistant response
    st.session_state["messages"] = state["messages"]
    last_message = state["messages"][-1]

    # Show assistant response
    st.markdown(f"""
        <div class="chat-container">
            <div class="chat-bubble assistant-msg">{last_message["content"]}</div>
        </div>
    """, unsafe_allow_html=True)
