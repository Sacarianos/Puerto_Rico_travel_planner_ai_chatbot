import streamlit as st
import os
import dotenv
import uuid

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler

from rag_methods import (
    initialize_vector_store, itinerary_planner, find_weather_forecast,
    rank_appropriate_locations, find_info_on_location, update_preferences, lock_location, ask_travel_dates, ask_interests
)

# 🔹 Load API Keys
dotenv.load_dotenv()

# 🔹 Streamlit Page Configuration
st.set_page_config(
    page_title="Puerto Rico Travel Chatbot",
    layout="centered",
    page_icon="🇵🇷",
    initial_sidebar_state="expanded"
)

st.title("🌴 The Hitchhiker's Guide to Puerto Rico")
st.write("Your AI-powered travel assistant for exploring Puerto Rico! 🏝️")

# --- Session Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
    ]

# --- Sidebar API Key Input ---
with st.sidebar:
    st.subheader("🔐 API Key Setup")
    openai_api_key = st.text_input(
        "Enter your OpenAI API Key",
        type="password",
        key="openai_api_key",
    )

#  Stop execution if API key is missing (Prevents vector store error)
if not openai_api_key:
    st.warning("⬅️ Please enter a valid OpenAI API Key to continue.")
    st.stop()


#  Initialize Vector Store (AFTER OpenAI Key is Set)
if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = initialize_vector_store()

#  Initialize Memory (PERSIST Memory Across Messages)
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
    ]
# --- Initialize LLM ---
llm = ChatOpenAI(
    model_name="gpt-4-turbo",
    temperature=0,
    streaming=True,
    openai_api_key=openai_api_key
)

# --- Define Tools ---
tools = [
    Tool(
        name="itinerary_planner",
        func=itinerary_planner,
        description="Generates a travel itinerary using ranked RAG retrieval based on user interests and travel dates."
    ),
    Tool(
        name="find_weather_forecast",
        func=find_weather_forecast,
        description="Get the weather forecast for a specific location."
    ),
    Tool(
        name="rank_appropriate_locations",
        func=rank_appropriate_locations,
        description="Find the best locations based on user preferences."
    ),
    Tool(
        name="find_info_on_location",
        func=find_info_on_location,
        description="Retrieve details about a specific location."
    ),
    Tool(
        name="ask_travel_dates", 
        func=ask_travel_dates, 
        description="Ask user for travel dates."
    ),
    Tool(
        name="ask_interests", 
        func=ask_interests, 
        description="Ask user for travel interests."
    ),
    Tool(
        name="lock_location", 
        func=lock_location, 
        description="Lock a location in the itinerary."
    ),
]

# --- Initialize Memory for Conversation ---


# --- Define Chat Prompt ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are 'The Hitchhiker's Guide to Puerto Rico', a travel assistant.
        Your job is to help users plan trips by:
        - Asking for travel dates and storing them
        - Asking for interests and storing them
        - Suggesting locations based on interests
        - Locking locations if the user confirms
        - Providing a finalized itinerary when asked

        Keep track of the conversation history and follow up where needed.
    """),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# --- Create AI Agent ---
agent = create_tool_calling_agent(llm, tools, prompt)

# --- Wrap in an Executor ---
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    memory=st.session_state["memory"],
    handle_parsing_errors=True
)

#  Custom Streaming Callback
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container):
        self.container = container
        self.full_response = ""

    def on_llm_new_token(self, token: str, **kwargs):
        """Receive and display tokens as they arrive"""
        self.full_response += token
        self.container.markdown(self.full_response + "▌")  # Cursor effect

    def on_llm_end(self, response, **kwargs):
        """Final update when streaming completes"""
        self.container.markdown(self.full_response)

# --- Chat Display ---
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User Input Handling ---
user_input = st.chat_input("Ask me anything about your trip to Puerto Rico!")

if user_input and isinstance(user_input, str) and user_input.strip():
    #  Append user input to chat history BEFORE processing
    st.session_state["messages"].append({"role": "user", "content": user_input})

    #  Display user message in chat
    with st.chat_message("user"):
        st.markdown(user_input)

    #  Streaming AI Response with Callback
    with st.chat_message("assistant"):
        response_container = st.empty()
        stream_handler = StreamHandler(response_container)

        #  Invoke the Agent with Streaming Callback
        response = agent_executor.invoke(
            {"input": user_input},
            config={"callbacks": [stream_handler]}
        )

    #  Store cleaned assistant response
    st.session_state["messages"].append({"role": "assistant", "content": stream_handler.full_response.strip()})
