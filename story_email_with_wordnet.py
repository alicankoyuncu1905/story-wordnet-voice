import smtplib
import os
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from datetime import datetime
import pytz
from gtts import gTTS
from googletrans import Translator
from dotenv import load_dotenv
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet

# NLTK verilerini indir (ilk çalıştırmada gerekli)
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')

# Ortam değişkenlerini yükle
load_dotenv()

# Gmail bilgileri
EMAIL = os.getenv("EMAIL", "alicankoyuncu1905@gmail.com")
PASSWORD = os.getenv("PASSWORD", "fhvtmqncdcvznauo")
RECIPIENT = os.getenv("RECIPIENT", "ahmetakoyuncu@gmail.com")

# Hikaye dosyasının yolu
FILE_PATH = r"C:\Users\alican.koyuncu\OneDrive - Aydinli\Masaüstü\Gizemstories\alican.txt"
AUDIO_PATH = "story_audio.mp3"

# Türkiye saat dilimi
IST = pytz.timezone("Europe/Istanbul")

# Çevirici başlat
translator = Translator()

# Hikayeyi dosyadan yükle
def load_story():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return f.read()

# Metni Türkçe’ye çevir
def translate_to_turkish(text):
    translated = translator.translate(text, src="en", dest="tr")
    return translated.text

# Metni sese çevir (İngilizce)
def text_to_audio(text):
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(AUDIO_PATH)
    print(f"🎙️ Audio file created: {AUDIO_PATH}")

# NLP ile daha fazla dinamik kelime listesi oluştur (WordNet ile)
def get_vocabulary(story):
    # Metni kelimelere ayır ve etiketle
    tokens = word_tokenize(story.lower())
    tagged = pos_tag(tokens)

    # Durdurma kelimelerini çıkar
    stop_words = set(stopwords.words('english'))
    # Önemli kelimeleri seç (isimler: NN, fiiller: VB, sıfatlar: JJ)
    important_words = [word for word, pos in tagged if (pos.startswith('NN') or pos.startswith('VB') or pos.startswith('JJ')) and word not in stop_words and word.isalpha()]

    # Kelime frekanslarını hesapla
    word_freq = nltk.FreqDist(important_words)
    # En sık 10 kelimeyi al
    top_words = [word for word, freq in word_freq.most_common(10)]

    # Kelimeler için tanım ve çeviri al
    vocab = {}
    for word in top_words:
        try:
            # WordNet ile İngilizce tanım al
            synsets = wordnet.synsets(word)
            definition = synsets[0].definition() if synsets else f"A common English word: {word}"
            # Türkçe çeviri
            turkish = translator.translate(word, src="en", dest="tr").text
            vocab[word] = {"definition": definition, "turkish": turkish}
        except Exception as e:
            print(f"⚠️ Could not get details for '{word}': {e}")
            vocab[word] = {"definition": f"A common English word: {word}", "turkish": "Bilinmiyor"}
    
    return vocab

# Hikayeyi e-posta ile gönder (Helvetica fontu + geniş kelime listesi)
def send_story():
    try:
        # Hikayeyi yükle
        story_en = load_story()
        print("📄 English story content loaded:")
        print(story_en)

        # Türkçe çeviriyi yap
        story_tr = translate_to_turkish(story_en)
        print("📝 Turkish translation:")
        print(story_tr)

        # Dinamik kelime listesini al
        vocabulary = get_vocabulary(story_en)
        print("📚 Vocabulary extracted (up to 10 words):")
        print(vocabulary)

        # İngilizce metni sese çevir
        text_to_audio(story_en)

        # Kelime listesi HTML formatında
        vocab_html = "<h4>Vocabulary</h4><ul>"
        for word, details in vocabulary.items():
            vocab_html += f"<li><b>{word}</b>: {details['definition']} (Türkçe: {details['turkish']})</li>"
        vocab_html += "</ul>"

        # Helvetica fontu ile HTML içeriği
        html = f"""
        <html>
        <head>
            <style>
                body, p, h3, h4, li {{
                    font-family: 'Helvetica', 'Arial', sans-serif;
                    font-size: 16px;
                }}
                b {{
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <h3>🌟 Today's English Story</h3>
            <p><b>English:</b><br>{story_en}</p>
            <p><b>Türkçe Çeviri:</b><br>{story_tr}</p>
            {vocab_html}
            <p>Sesli versiyonu (İngilizce) ekte bulabilirsiniz.</p>
        </body>
        </html>
        """

        # E-posta oluştur
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = RECIPIENT
        msg["Subject"] = "🌟 Today's English Story with Translation, Voice, and Vocabulary"

        # HTML metni ekle
        msg.attach(MIMEText(html, "html"))

        # Ses dosyasını ekle
        with open(AUDIO_PATH, "rb") as audio_file:
            audio = MIMEAudio(audio_file.read(), _subtype="mpeg")
            audio.add_header("Content-Disposition", "attachment", filename="story_audio.mp3")
            msg.attach(audio)

        # E-postayı gönder
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        print(f"✅ Email sent successfully at {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}")

        # Geçici ses dosyasını sil
        os.remove(AUDIO_PATH)
        print(f"🗑️ Audio file {AUDIO_PATH} removed")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Görev zamanlayıcı
def schedule_task():
    schedule.every().day.at("08:00").do(send_story)
    print("⏰ Scheduler started. Waiting for 08:00 IST daily...")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    send_story()  # İlk testi hemen yap
    schedule_task()  # Zamanlayıcıyı başlat
