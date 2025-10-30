# NEURA Deployment Guide

## Prerequisites
- Python 3.13+
- A Supabase account (already configured in `.env`)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Streamlit (Recommended)
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

### Option 2: Console Mode
```bash
python main.py
```

## Features

- **Modern UI**: Beautiful gradient design with smooth animations
- **Supabase Integration**: All chats are saved to the cloud
- **Dual AI Modes**:
  - Logical mode for factual responses
  - Emotional mode for therapeutic support
- **Chat History**: Load and continue previous conversations
- **Auto-naming**: AI generates chat titles automatically

## Deployment Options

### Streamlit Cloud (Easiest)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add environment variables:
   - `GEMINI_API_KEY`
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_SUPABASE_ANON_KEY`
5. Deploy!

### Heroku
1. Create a `Procfile`:
```
web: streamlit run app.py --server.port=$PORT
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Railway
1. Connect your GitHub repository
2. Railway will auto-detect Streamlit
3. Add environment variables
4. Deploy!

## Database Schema

The app uses two Supabase tables:
- `chats`: Stores chat sessions
- `messages`: Stores individual messages

All tables have Row Level Security (RLS) enabled with public access for demo purposes.
