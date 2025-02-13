import os
import json
import requests
import dotenv
import streamlit as st
from pinecone import Pinecone as PineconeClient
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from geopy.distance import geodesic

# 🔹 Load API Keys
dotenv.load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 🔹 User Preferences Storage
user_preferences = {
    "travel_dates": None,
    "interests": [],
    "locked_locations": [],
}


# 🔹 Initialize Pinecone Vector Store
vector_store = None  # Declare as global variable

def initialize_vector_store():
    """Initialize LangChain's Pinecone Vector Store with OpenAI embeddings."""
    global vector_store

    if vector_store is None:  # Prevent re-initialization
        openai_api_key = st.session_state.get("openai_api_key", os.getenv("OPENAI_API_KEY"))
        
        if not openai_api_key:
            raise ValueError("⚠️ OpenAI API Key is required to initialize vector store.")

        # Initialize Pinecone Client
        pc = PineconeClient(api_key=PINECONE_API_KEY)  
        index_name = "puerto-rico-travel"
        
        # Ensure the index exists before using it
        if index_name not in [i.name for i in pc.list_indexes()]:
            raise ValueError(f"⚠️ Pinecone index '{index_name}' does not exist. Create it first.")

        index = pc.Index(index_name)  # Connect to existing index

        # Initialize OpenAI Embeddings
        embedding = OpenAIEmbeddings(api_key=openai_api_key, model="text-embedding-ada-002")

        # Initialize LangChain's Pinecone Vector Store (✅ Corrected)
        vector_store = PineconeVectorStore(index=index, embedding=embedding, text_key="text")
    
    return vector_store




# 🔹 Fetch Weather Forecast
def find_weather_forecast(location: str):
    """Fetches weather forecast for a location."""
    formatted_location = f"{location},PR,US"
    travel_dates = user_preferences.get("travel_dates", "your trip")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={formatted_location}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        return f"Weather in {location} on {travel_dates}: {data['weather'][0]['description']}, {data['main']['temp']}°C, Humidity: {data['main']['humidity']}%"
    else:
        return f"Could not fetch weather for {location}."

# 🔹 Rank Locations Based on Preferences
def rank_appropriate_locations(user_prompt: str = None):
    """Ranks locations based on user preferences."""
    if not user_prompt:
        interests = ", ".join(user_preferences.get("interests", []))
        user_prompt = f"Best places for {interests} in Puerto Rico"

    results = vector_store.similarity_search_with_score(user_prompt, k=5)
    ranked_results = sorted(results, key=lambda x: (
        x[0].metadata.get("rating", 0),
        x[0].metadata.get("review_count", 0)
    ), reverse=True)

    return [{"name": item[0].metadata["name"], "rating": item[0].metadata["rating"]} for item in ranked_results]

# 🔹 Get Info on a Specific Location
def find_info_on_location(location: str):
    """Retrieves information about a specific location."""
    print(vector_store)
    results = vector_store.similarity_search_with_score(location, k=1)
    if not results:
        return "No information found."

    place = results[0][0].metadata
    contact_info = json.loads(place.get("contact", "{}"))
    google_maps_url = contact_info.get("google_maps_url", "No directions available.")

    return f"{place['name']} - {place['description']} (Rating: {place.get('rating', 'N/A')}, {place.get('review_count', 'N/A')} reviews). More info: {place['url']} Directions: {google_maps_url}"

# 🔹 Generate an Itinerary
def itinerary_planner(days: int = 5):
    """Generates a travel itinerary based on user preferences."""
    travel_dates = user_preferences.get("travel_dates", "upcoming trip")
    interests = user_preferences.get("interests", [])

    if not interests:
        return "Please provide your interests before generating an itinerary."

    user_query = f"Best places for {', '.join(interests)} in Puerto Rico"
    ranked_places = rank_appropriate_locations(user_query)

    if not ranked_places:
        return "I couldn't find enough locations matching your interests."

    daily_itinerary = {f"Day {i+1}": [] for i in range(days)}
    
    for i, place in enumerate(ranked_places):
        day_index = i % days  
        daily_itinerary[f"Day {day_index+1}"].append(place)

    itinerary = f"**Itinerary for {travel_dates}**\n\n"
    
    for day, places in daily_itinerary.items():
        itinerary += f"**{day}:**\n"
        for place in places:
            itinerary += f"  - {place['name']} (⭐ {place['rating']})\n"
        itinerary += "\n"

    return itinerary

# 🔹 Update User Preferences
def update_preferences(key, value):
    """Updates user preferences for travel planning."""
    if key == "interests" and isinstance(value, str):
        if value not in user_preferences[key]:
            user_preferences[key].append(value)
    elif key == "locked_locations" and isinstance(value, str):
        if value not in user_preferences[key]:
            user_preferences[key].append(value)
    else:
        user_preferences[key] = value
    return f"Updated {key}: {user_preferences[key]}"

# 🔹 Lock a Location
def lock_location(location: str):
    """Locks a location in the user's itinerary."""
    user_preferences["locked_locations"].append(location)
    return f"{location} has been locked in your itinerary."


def ask_travel_dates(_: str = None):
    return "What are your travel dates? I’ll remember them for later."

def set_travel_dates(dates: str):
    user_preferences["travel_dates"] = dates
    return f"Got it! Your travel dates are set to {dates}."

def ask_interests(_: str = None):
    return "What are your travel interests? (e.g., hiking, history, beaches)"

def set_interests(interests: list):
    user_preferences["interests"].extend(interests)
    return f"Added {', '.join(interests)} to your interests."
