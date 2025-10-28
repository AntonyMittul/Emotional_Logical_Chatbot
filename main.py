from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
import os
import json
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

# ----------------------- PERSISTENCE UTILITIES -----------------------
CHAT_HISTORY_DIR = "chat_history"

def ensure_chat_history_dir():
    """Ensures the chat history directory exists."""
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

def list_saved_chats() -> list[str]:
    """Lists all saved chat filenames (without the .json extension)."""
    ensure_chat_history_dir()
    return sorted([f.replace(".json", "") for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith(".json")])

# Pydantic schema for keyword extraction
class ChatNameGenerator(BaseModel):
    chat_name: str = Field(
        ...,
        description="A concise, keyword-based title (max 3 words) for the conversation."
    )

# ----------------------- CORE CHAT SERVICE -----------------------

# Define state (TypedDict is placed globally as it's used for the Graph definition)
class ChatState(TypedDict):
    messages: list
    message_type: str | None

class ChatService:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        # Load environment variables
        load_dotenv()
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.graph = self._build_graph()

    # --- Utility Methods ---

    def generate_chat_name_llm(self, messages: list) -> str:
        """Generates a keyword-based name for the chat history using LLM."""
        name_llm = self.llm.with_structured_output(ChatNameGenerator)
        
        history_text = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages[-5:])

        prompt = [
            {"role": "system", 
             "content": "Analyze the following conversation history and generate a short, keyword-based title (maximum 3 words) that summarizes the main topic or emotion. The title must be suitable as a filename. Do not include quotes or special characters."},
            {"role": "user", "content": f"Conversation History:\n{history_text}"}
        ]
        
        try:
            result = name_llm.invoke(prompt)
            safe_name = "".join(c for c in result.chat_name if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")
            return safe_name if safe_name else datetime.now().strftime("Chat_%Y-%m-%d_%H%M%S")
        except Exception as e:
            print(f"Error generating chat name: {e}")
            return datetime.now().strftime("Chat_%Y-%m-%d_%HM%S")
        
    def save_chat_history(self, messages: list, chat_name: str | None = None) -> str:
        """Saves the chat history to a JSON file, generating a name if none is provided."""
        ensure_chat_history_dir()
        
        if not chat_name:
            chat_name = self.generate_chat_name_llm(messages)

        final_name = chat_name

        file_path = os.path.join(CHAT_HISTORY_DIR, f"{final_name}.json")
        
        # Handle filename collision by appending an index
        counter = 1
        original_name = final_name
        while os.path.exists(file_path):
            final_name = f"{original_name}_{counter}"
            file_path = os.path.join(CHAT_HISTORY_DIR, f"{final_name}.json")
            counter += 1
        
        with open(file_path, 'w') as f:
            json.dump(messages, f, indent=4)
            
        return final_name

    @staticmethod
    def load_chat_history(chat_name: str) -> list | None:
        """Loads a chat history from a JSON file."""
        file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    @staticmethod
    def list_saved_chats() -> list[str]:
        return list_saved_chats()


    # --- Graph Node Methods (Bound to instance) ---
    def _classify_message(self, state: ChatState):
        classifier_llm = self.llm.with_structured_output(self._get_classifier_schema())
        last_message = state['messages'][-1]

        result = classifier_llm.invoke([
            {"role": "system",
             "content": """Classify the user message as either:
                - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
                - 'logical': if it asks for facts, information, logical analysis, or practical solutions
                """
            },
            {"role": "user", "content": last_message['content']}
        ])
        return {"message_type": result.message_type}

    def _therapist_agent(self, state: ChatState):
        last_message = state['messages'][-1]
        messages = [
            {"role": "system",
             "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                            Show empathy, validate their feelings, and help them process their emotions.
                            Ask thoughtful questions to help them explore their feelings more deeply.
                            Avoid giving logical solutions unless explicitly asked."""},
            {"role": "user", "content": last_message['content']}
        ]
        reply = self.llm.invoke(messages)
        return {"messages": state["messages"] + [{"role": "assistant", "content": reply.content}]}

    def _logical_agent(self, state: ChatState):
        last_message = state['messages'][-1]
        messages = [
            {"role": "system",
             "content": """You are a purely logical assistant. Focus only on facts and information.
                Provide clear, concise answers based on logic and evidence.
                Do not address emotions or provide emotional support.
                Be direct and straightforward in your responses."""},
            {"role": "user", "content": last_message['content']}
        ]
        reply = self.llm.invoke(messages)
        return {"messages": state["messages"] + [{"role": "assistant", "content": reply.content}]}
    
    @staticmethod
    def _router(state: ChatState):
        message_type = state.get('message_type', 'logical')
        if message_type == 'emotional':
            return {"next": "therapist_agent"}
        return {"next": "logical_agent"}

    @staticmethod
    def _get_classifier_schema():
        class MessageClassifier(BaseModel):
            message_type: Literal["emotional", "logical"] = Field(
                ...,
                description="Classify whether the message requires an emotional (therapist) or logical response"
            )
        return MessageClassifier

    # --- Graph Builder ---

    def _build_graph(self):
        graph_builder = StateGraph(ChatState)

        # Nodes are instance methods, note the use of self.method_name
        graph_builder.add_node("classifier", self._classify_message)
        graph_builder.add_node("therapist_agent", self._therapist_agent)
        graph_builder.add_node("logical_agent", self._logical_agent)
        graph_builder.add_node("router", self._router)

        graph_builder.add_edge(START, "classifier")
        graph_builder.add_edge("classifier", "router")

        graph_builder.add_conditional_edges(
            "router",
            lambda state: state.get('next'),
            {"therapist_agent": "therapist_agent", "logical_agent": "logical_agent"}
        )

        graph_builder.add_edge("therapist_agent", END)
        graph_builder.add_edge("logical_agent", END)

        return graph_builder.compile()
    
    # --- Public Execution Method ---
    
    def invoke(self, state: dict) -> dict:
        """Invokes the chat workflow with the given state."""
        return self.graph.invoke(state)


# Interactive chatbot (Kept for console compatibility)
def run_chatbot():
    # Instantiate the service here
    chat_service = ChatService()
    state = None
    
    while True:
        saved_chats = chat_service.list_saved_chats()
        print("\n--- NEURA Chatbot ---")
        if saved_chats:
            print("--- Load/View Saved Chats ---")
            for i, chat_name in enumerate(saved_chats):
                print(f"[{i+1}] {chat_name}")
            print("[N] Start New Chat")
            print("[Q] Quit Program")
            
            choice = input("Enter number to load, 'N' for new, or 'Q' to quit: ").lower()
            
            if choice == 'q':
                return
            
            if choice == 'n':
                state = {"messages": [], "message_type": None}
                print("\nStarting new chat. Type 'exit' to save and quit.")
                break
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(saved_chats):
                    chat_name_to_load = saved_chats[idx]
                    messages = chat_service.load_chat_history(chat_name_to_load)
                    if messages:
                        state = {"messages": messages, "message_type": None}
                        print(f"\nLoaded chat: {chat_name_to_load}. Messages:")
                        for msg in messages:
                            print(f"{msg['role'].capitalize()}: {msg['content']}")
                        if input("\nContinue this chat? (y/n): ").lower() == 'y':
                            break
                        else:
                            state = None
                            continue
                    else:
                        print("Error loading chat.")
                else:
                    print("Invalid choice.")
            else:
                print("Invalid input.")
        else:
            state = {"messages": [], "message_type": None}
            print("No saved chats found. Starting new chat. Type 'exit' to save and quit.")
            break
            
    if state is None:
        return

    while True:
        user_input = input("Message: ")
        
        if user_input.lower() == "exit":
            if state["messages"]:
                print("\n--- Saving Chat ---")
                generated_name = chat_service.generate_chat_name_llm(state["messages"])
                
                save_name_override = input(f"Chat name determined: {generated_name}. Enter a new name or press Enter to confirm: ")
                if not save_name_override:
                    save_name_override = generated_name
                    
                saved_name = chat_service.save_chat_history(state["messages"], save_name_override)
                print(f"Chat saved as: {saved_name}.json in {CHAT_HISTORY_DIR}/")
            
            print("Bye 👋")
            break

        state['messages'] = state.get('messages', []) + [{"role": "user", "content": user_input}]
        
        try:
            state = chat_service.invoke(state)
        except Exception as e:
            print(f"An error occurred during graph execution: {e}")
            state['messages'].pop() 
            continue

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state['messages'][-1]
            print(f"Assistant: {last_message['content']}")

if __name__ == "__main__":
    run_chatbot()