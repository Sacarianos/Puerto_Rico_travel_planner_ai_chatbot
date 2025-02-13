# 🇵🇷 Puerto Rico Travel Planner AI Chatbot

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-blue?logo=github)](https://github.com/Sacarianos/Puerto_Rico_travel_planner_ai_chatbot)

## ✈️ Overview
**The Hitchhiker's Guide to Puerto Rico** is an AI-powered travel assistant that helps users plan trips to Puerto Rico. It uses OpenAI's GPT-4-turbo, Pinecone for vector search, and Streamlit for an interactive UI. The chatbot provides personalized itineraries, location recommendations, and travel insights based on user preferences.

## 🚀 Features
- ✅ **Conversational Chatbot**: AI-powered assistant that understands user inputs.
- ✅ **Customizable Itineraries**: Plans trips based on travel dates and interests.
- ✅ **Live Weather Updates**: Fetches real-time weather for locations in Puerto Rico.
- ✅ **Location Search**: Retrieves details about historical sites, beaches, and activities.
- ✅ **Memory Persistence**: Remembers user choices (locked locations, interests, etc.).
- ✅ **Streaming Responses**: Generates real-time AI responses dynamically.

## 🛠️ Setup Instructions
### 1️⃣ Clone the Repository
```sh
 git clone https://github.com/Sacarianos/Puerto_Rico_travel_planner_ai_chatbot.git
 cd Puerto_Rico_travel_planner_ai_chatbot
```

### 2️⃣ Create a Virtual Environment (Recommended)
```sh
python -m venv env
source env/bin/activate  # On macOS/Linux
env\Scripts\activate    # On Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a `.env` file and add the following keys:
```ini
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

### 5️⃣ Run the Application
```sh
streamlit run app.py
```

## 📌 How It Works
1. **Enter your OpenAI API key** in the sidebar.
2. **Start a conversation** – ask about locations, weather, or create an itinerary.
3. **Lock locations** to add them to your trip plan.
4. **Modify your preferences** anytime (change interests, add/remove locations).
5. **Receive AI-generated recommendations** based on your travel style.

## 🔍 Project Structure
```
Puerto_Rico_travel_planner_ai_chatbot/
│── app.py               # Streamlit chatbot UI
│── rag_methods.py       # RAG functions (retrieval-augmented generation)
│── requirements.txt     # Dependencies
│── .env                 # API keys (not included in repo)
│── main.ipynb           # Core development and testing notebook for the AI Chatbot capabilities.
└── README.md            # Project documentation
```

## 📌 Tech Stack
- **Frontend:** Streamlit
- **AI Model:** OpenAI GPT-4-turbo
- **Vector Database:** Pinecone
- **Embedding Model:** OpenAI Ada-002
- **Weather API:** OpenWeatherMap

## 🤝 Contributing
1. **Fork the repo** and create a new branch.
2. **Make your changes** and test them locally.
3. **Submit a pull request** – we welcome contributions!

## 📜 License
This project is licensed under the **MIT License**.

---

🔥 **Made with ❤️ for travelers exploring Puerto Rico!** 🌴✈️


