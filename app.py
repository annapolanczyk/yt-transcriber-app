import streamlit as st
import subprocess
import whisper
import json
import os
import cv2
import time
from googletrans import Translator

# --- Ustawienia ---
st.set_page_config(page_title="YT Transcriber & Translator", layout="wide")
st.title("🎬 YouTube Video Transcriber & Translator 🇬🇧➡️🇵🇱")

output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# --- Formularz użytkownika ---
with st.form("yt_form"):
    url = st.text_input("Wklej link do filmu na YouTube", "")
    model_size = st.selectbox("Wybierz model Whisper", ["tiny", "base", "small", "medium", "large"], index=1)
    interval = st.number_input("Interwał zrzutów ekranu (sekundy)", min_value=10, max_value=600, value=60, step=10)
    submitted = st.form_submit_button("🔄 Rozpocznij transkrypcję")

if submitted and url:
    progress = st.progress(0)
    progress.progress(5)

    with st.spinner("📥 Pobieranie filmu..."):
        video_path = os.path.join(output_folder, "video.mp4")
        command = ["yt-dlp", url, "--format", "best[ext=mp4]", "--output", video_path, "--write-info-json"]
        subprocess.run(command, check=True)
        progress.progress(20)

        info_json = os.path.join(output_folder, "video.info.json")
        if os.path.exists(info_json):
            with open(info_json, 'r', encoding='utf-8') as f:
                video_info = json.load(f)
            st.success(f"Tytuł filmu: {video_info.get('title', 'Nieznany')}")
        else:
            st.warning("Nie udało się odczytać tytułu filmu.")

    with st.spinner("🧠 Transkrypcja audio z Whisper..."):
        model = whisper.load_model(model_size)
        result = model.transcribe(video_path)
        transcript_en = result["text"]
        transcript_path = os.path.join(output_folder, "transcription_en.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_en)
        st.text_area("📄 Transkrypcja (EN)", transcript_en, height=300)
        progress.progress(50)

    with st.spinner("🌍 Tłumaczenie na polski..."):
        chunks = [transcript_en[i:i+2000] for i in range(0, len(transcript_en), 2000)]
        translator = Translator()
        translated_chunks = []
        for chunk in chunks:
            translation = translator.translate(chunk, src='en', dest='pl').text
            translated_chunks.append(translation)
            time.sleep(1)
        transcript_pl = " ".join(translated_chunks)
        translation_path = os.path.join(output_folder, "transcription_pl.txt")
        with open(translation_path, "w", encoding="utf-8") as f:
            f.write(transcript_pl)
        st.text_area("📄 Tłumaczenie (PL)", transcript_pl, height=300)
        progress.progress(75)

    with st.spinner("🖼️ Tworzenie zrzutów ekranu..."):
        screenshots_dir = os.path.join(output_folder, "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        st.info(f"🎞️ Długość filmu: {int(duration)} sekund (⏱️ Szacowany czas przetwarzania: {int(duration / 2)} sekund)")

        screenshot_count = 0
        for t in range(0, int(duration), interval):
            frame_number = int(t * fps)
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = video.read()
            if success:
                screenshot_path = os.path.join(screenshots_dir, f"screenshot_{t:04d}.png")
                cv2.imwrite(screenshot_path, frame)
                screenshot_count += 1
        video.release()
        st.success(f"Zapisano {screenshot_count} zrzutów ekranu w folderze: {screenshots_dir}")
        progress.progress(100)

    st.balloons()
    st.success("🎉 Wszystko gotowe! Sprawdź folder output.")
