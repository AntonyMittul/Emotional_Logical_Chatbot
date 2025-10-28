import streamlit as st
from main import ChatService, ChatState, CHAT_HISTORY_DIR 
import os
from datetime import datetime

# ----------------------- PAGE CONFIG -----------------------
st.set_page_config(page_title="NEURA - AI Chatbot", page_icon="🤖", layout="wide")

# ----------------------- INITIALIZE SERVICE -----------------------
@st.cache_resource
def get_chat_service():
    """Instantiate ChatService once and cache it."""
    return ChatService()

chat_service = get_chat_service()

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
            max-width: 55%; 
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
if "current_chat_name" not in st.session_state:
    st.session_state["current_chat_name"] = "New Chat"


# ----------------------- HELPER FUNCTIONS FOR UI -----------------------
def new_chat_session():
    st.session_state["messages"] = []
    st.session_state["current_chat_name"] = "New Chat"

def handle_load_chat(chat_name):
    # Use the static method on ChatService
    messages = ChatService.load_chat_history(chat_name)
    if messages:
        st.session_state["messages"] = messages
        st.session_state["current_chat_name"] = chat_name
    else:
        st.error(f"Could not load chat: {chat_name}")

def perform_save_auto():
    """Automatically generates a name and saves the current chat."""
    if not st.session_state["messages"]:
        st.warning("Cannot save an empty chat.")
        return
    
    with st.spinner("Generating chat name and saving..."):
        # Use simple message list for auto-naming
        generated_name = chat_service.generate_chat_name_llm(st.session_state["messages"])
        
        # Use the service instance method
        saved_name = chat_service.save_chat_history(st.session_state["messages"], generated_name)
        
        st.session_state["current_chat_name"] = saved_name
        st.success(f"Chat saved as: **{saved_name}**.json in {CHAT_HISTORY_DIR}/")
        st.rerun() 

# ----------------------- HEADER -----------------------
st.markdown('<p class="header">🤖 NEURA</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Your AI assistant for <b>Therapeutical</b> and <b>Logical</b> responses. Current Chat: <b>' + st.session_state["current_chat_name"] + '</b></p>', unsafe_allow_html=True)

# ----------------------- SIDEBAR (Chat History) -----------------------
with st.sidebar:
    st.title("ℹ️ About NEURA")
    st.write("""
    NEURA is an AI-powered chatbot that adapts its responses based on your needs:
    - 🧠 Logical mode: Provides facts, reasoning, and analysis.  
    - 💙 Emotional mode: Offers empathy, support, and guidance.  
    
    **Tip:** For the console version, type *exit* to save and stop the bot.
    """)
    st.markdown("---")
    
    st.header("Chat History")
    
    st.button("➕ New Chat", on_click=new_chat_session, use_container_width=True)
    
    if st.button("💾 Save Current Chat", use_container_width=True):
        perform_save_auto()
        
    st.markdown("---")
    
    # Use the static method on ChatService
    saved_chats = ChatService.list_saved_chats()
    if saved_chats:
        st.caption("Load a Previous Chat")
        for chat_name in saved_chats:
            if st.button(chat_name, key=f"load_{chat_name}", use_container_width=True):
                handle_load_chat(chat_name)
                st.rerun()

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
    # The prompt is used directly as the user message
    user_message = prompt
    
    # Save and show user message
    st.session_state["messages"].append({"role": "user", "content": user_message})
    st.markdown(f"""
        <div class="chat-container">
            <div class="chat-bubble user-msg">{prompt}</div>
        </div>
    """, unsafe_allow_html=True)

    # Process with ChatService instance
    with st.spinner("NEURA is thinking..."):
        # The service expects the state in a dict, so we pass current session messages.
        state_to_invoke = {"messages": st.session_state["messages"], "message_type": None}
        
        try:
            state = chat_service.invoke(state_to_invoke)
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            if st.session_state["messages"]:
                st.session_state["messages"].pop()
            st.stop()

    # Update session state with the response
    st.session_state["messages"] = state["messages"]
    last_message = state["messages"][-1]

    # Show assistant response
    st.markdown(f"""
        <div class="chat-container">
            <div class="chat-bubble assistant-msg">{last_message["content"]}</div>
        </div>
    """, unsafe_allow_html=True)