#!/bin/bash

cd /Users/annapolanczyk/WEBAPP

# 1. Tworzenie środowiska jeśli nie istnieje
if [ ! -d "venv" ]; then
  echo "🔧 Tworzę środowisko wirtualne..."
  python3 -m venv venv
fi

# 2. Aktywacja środowiska
echo "🧪 Aktywuję środowisko venv..."
source venv/bin/activate

# 3. Instalacja bibliotek
echo "📦 Instaluję wymagane biblioteki..."
pip install --upgrade pip
pip install streamlit yt-dlp openai-whisper googletrans==4.0.0-rc1 opencv-python

# 4. Uruchomienie aplikacji
echo "🚀 Uruchamiam aplikację Streamlit..."
streamlit run app.py

