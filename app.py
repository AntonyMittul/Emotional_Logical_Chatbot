import streamlit as st
from main import ChatService, ChatState
from supabase import create_client, Client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="NEURA - AI Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def get_chat_service():
    return ChatService()

supabase = get_supabase_client()
chat_service = get_chat_service()

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0;
        }

        .stApp {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        [data-testid="stSidebar"] * {
            color: #e4e4e7 !important;
        }

        .sidebar-title {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff !important;
            margin-bottom: 10px;
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        }

        .chat-container {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px;
            margin: 20px auto;
            max-width: 900px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            min-height: 70vh;
        }

        .header-container {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }

        .main-title {
            font-size: 48px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            letter-spacing: -1px;
        }

        .subtitle {
            font-size: 18px;
            color: #64748b;
            font-weight: 400;
            margin-top: 10px;
        }

        .current-chat-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
            margin-top: 15px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .message-container {
            display: flex;
            margin-bottom: 24px;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-bubble {
            padding: 16px 20px;
            border-radius: 20px;
            max-width: 70%;
            word-wrap: break-word;
            font-size: 15px;
            line-height: 1.6;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            position: relative;
        }

        .user-container {
            justify-content: flex-end;
        }

        .user-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }

        .assistant-container {
            justify-content: flex-start;
        }

        .assistant-bubble {
            background: #f8fafc;
            color: #1e293b;
            border: 1px solid #e2e8f0;
            margin-right: auto;
            border-bottom-left-radius: 4px;
        }

        .message-role {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            opacity: 0.7;
        }

        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            margin-bottom: 10px;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        [data-testid="stSidebar"] .stButton > button {
            background: rgba(102, 126, 234, 0.2);
            border: 1px solid rgba(102, 126, 234, 0.3);
            color: #ffffff !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(102, 126, 234, 0.3);
            border-color: rgba(102, 126, 234, 0.5);
        }

        .chat-history-item {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .chat-history-item:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(102, 126, 234, 0.5);
            transform: translateX(5px);
        }

        .stTextInput > div > div > input {
            border-radius: 12px;
            border: 2px solid #e2e8f0;
            padding: 12px 16px;
            font-size: 15px;
            transition: all 0.3s ease;
        }

        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #94a3b8;
        }

        .empty-state-icon {
            font-size: 64px;
            margin-bottom: 20px;
            opacity: 0.5;
        }

        .empty-state-text {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 10px;
        }

        .empty-state-subtext {
            font-size: 14px;
            opacity: 0.7;
        }

        hr {
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin: 20px 0;
        }

        .stSpinner > div {
            border-top-color: #667eea !important;
        }

        [data-testid="stChatInput"] {
            border-radius: 16px;
            border: 2px solid #e2e8f0;
            background: white;
        }

        [data-testid="stChatInput"]:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .sidebar-section {
            margin-bottom: 30px;
        }

        .sidebar-section-title {
            font-size: 14px;
            font-weight: 600;
            color: #94a3b8 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "current_chat_id" not in st.session_state:
    st.session_state["current_chat_id"] = None
if "current_chat_name" not in st.session_state:
    st.session_state["current_chat_name"] = "New Chat"

def load_chat_from_db(chat_id: str):
    try:
        chat_response = supabase.table("chats").select("*").eq("id", chat_id).single().execute()
        messages_response = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at").execute()

        if chat_response.data and messages_response.data:
            st.session_state["current_chat_id"] = chat_id
            st.session_state["current_chat_name"] = chat_response.data["name"]
            st.session_state["messages"] = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages_response.data
            ]
    except Exception as e:
        st.error(f"Error loading chat: {e}")

def save_chat_to_db():
    if not st.session_state["messages"]:
        st.warning("Cannot save an empty chat.")
        return

    try:
        with st.spinner("Saving chat..."):
            if st.session_state["current_chat_id"]:
                chat_id = st.session_state["current_chat_id"]
                supabase.table("chats").update({
                    "updated_at": datetime.now().isoformat()
                }).eq("id", chat_id).execute()
            else:
                generated_name = chat_service.generate_chat_name_llm(st.session_state["messages"])

                chat_response = supabase.table("chats").insert({
                    "name": generated_name
                }).execute()

                chat_id = chat_response.data[0]["id"]
                st.session_state["current_chat_id"] = chat_id
                st.session_state["current_chat_name"] = generated_name

                for msg in st.session_state["messages"]:
                    supabase.table("messages").insert({
                        "chat_id": chat_id,
                        "role": msg["role"],
                        "content": msg["content"]
                    }).execute()

            st.success(f"Chat saved: **{st.session_state['current_chat_name']}**")
            st.rerun()
    except Exception as e:
        st.error(f"Error saving chat: {e}")

def new_chat():
    st.session_state["messages"] = []
    st.session_state["current_chat_id"] = None
    st.session_state["current_chat_name"] = "New Chat"

def get_all_chats():
    try:
        response = supabase.table("chats").select("*").order("updated_at", desc=True).execute()
        return response.data
    except:
        return []

with st.sidebar:
    st.markdown('<div class="sidebar-title">🧠 NEURA</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Actions</div>', unsafe_allow_html=True)
    if st.button("✨ New Chat"):
        new_chat()
        st.rerun()

    if st.button("💾 Save Chat"):
        save_chat_to_db()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Chat History</div>', unsafe_allow_html=True)
    chats = get_all_chats()
    if chats:
        for chat in chats:
            if st.button(f"💬 {chat['name']}", key=f"chat_{chat['id']}"):
                load_chat_from_db(chat['id'])
                st.rerun()
    else:
        st.caption("No saved chats yet")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
        <div style="padding: 15px; background: rgba(102, 126, 234, 0.1); border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.2);">
            <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #ffffff !important;">About NEURA</div>
            <div style="font-size: 13px; line-height: 1.6; color: #cbd5e1 !important;">
                An intelligent AI companion that adapts to your needs:
                <br><br>
                🧠 <b>Logical Mode</b> - Facts and analysis
                <br>
                💜 <b>Emotional Mode</b> - Empathy and support
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

st.markdown(f"""
    <div class="header-container">
        <div class="main-title">NEURA</div>
        <div class="subtitle">Your Intelligent AI Companion</div>
        <div class="current-chat-badge">{st.session_state['current_chat_name']}</div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state["messages"]:
    st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-text">Start a conversation</div>
            <div class="empty-state-subtext">I'm here to help with logical analysis or emotional support</div>
        </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="message-container user-container">
                    <div class="message-bubble user-bubble">
                        <div class="message-role">You</div>
                        {msg["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="message-container assistant-container">
                    <div class="message-bubble assistant-bubble">
                        <div class="message-role">NEURA</div>
                        {msg["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Type your message..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.spinner("NEURA is thinking..."):
        state_to_invoke = {"messages": st.session_state["messages"], "message_type": None}

        try:
            state = chat_service.invoke(state_to_invoke)
            st.session_state["messages"] = state["messages"]

            if st.session_state["current_chat_id"]:
                last_msg = state["messages"][-1]
                supabase.table("messages").insert({
                    "chat_id": st.session_state["current_chat_id"],
                    "role": "user",
                    "content": prompt
                }).execute()
                supabase.table("messages").insert({
                    "chat_id": st.session_state["current_chat_id"],
                    "role": last_msg["role"],
                    "content": last_msg["content"]
                }).execute()
                supabase.table("chats").update({
                    "updated_at": datetime.now().isoformat()
                }).eq("id", st.session_state["current_chat_id"]).execute()

        except Exception as e:
            st.error(f"Error: {e}")
            if st.session_state["messages"]:
                st.session_state["messages"].pop()

    st.rerun()
