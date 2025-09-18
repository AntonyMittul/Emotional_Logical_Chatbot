from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI  # Gemini API wrapper

# Load environment variables
load_dotenv()

# Initialize Gemini Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Message classifier schema
class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify whether the message requires an emotional (therapist) or logical response"
    )

# Define state
class State(TypedDict):
    messages: list
    message_type: str | None

def classify_message(state: State):
    last_message = state['messages'][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
           "role": "system",
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            """
        },
        {"role": "user", "content": last_message['content']}
    ])
    return {"message_type": result.message_type}

def therapist_agent(state: State):
    last_message = state['messages'][-1]
    messages = [
        {"role": "system",
         "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""},
        {"role": "user", "content": last_message['content']}
    ]
    reply = llm.invoke(messages)
    return {"messages": state["messages"] + [{"role": "assistant", "content": reply.content}]}

def logical_agent(state: State):
    last_message = state['messages'][-1]
    messages = [
        {"role": "system",
         "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses."""},
        {"role": "user", "content": last_message['content']}
    ]
    reply = llm.invoke(messages)
    return {"messages": state["messages"] + [{"role": "assistant", "content": reply.content}]}

def router(state: State):
    message_type = state.get('message_type', 'logical')
    if message_type == 'emotional':
        return {"next": "therapist_agent"}
    return {"next": "logical_agent"}

# Build graph
graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("therapist_agent", therapist_agent)
graph_builder.add_node("logical_agent", logical_agent)
graph_builder.add_node("router", router)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get('next'),
    {"therapist_agent": "therapist_agent", "logical_agent": "logical_agent"}
)

graph_builder.add_edge("therapist_agent", END)
graph_builder.add_edge("logical_agent", END)

graph = graph_builder.compile()

# Interactive chatbot
def run_chatbot():
    state = {"messages": [], "message_type": None}
    
    while True:
        user_input = input("Message: ")
        if user_input.lower() == "exit":
            print("Bye 👋")
            break

        state['messages'] = state.get('messages', []) + [{"role": "user", "content": user_input}]
        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state['messages'][-1]
            print(f"Assistant: {last_message['content']}")

if __name__ == "__main__":
    run_chatbot()
