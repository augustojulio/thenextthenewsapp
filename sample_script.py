import feedparser
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline # Hugging Face - AI to summarize text

from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required to upload videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# part 1: Information Collection and Sources
# Testing with one feed
result = []
feed_url = "https://www.theverge.com/rss/index.xml"
feed = feedparser.parse(feed_url)
# Add a list of feed_urls to test with multiple feeds
# Get the first 2 entries from each feed url

for entry in feed.entries[:5]:
    result.append(f"Título: {entry.title}\nLink: {entry.link}\nResumo: {entry.summary}\n")

# print(result)

# Long text-friendly model and tokenizer for summarization
model_name = "allenai/led-base-16384"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Configure the pipeline
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# part 2: Automatic News Summary
# Summarization function
def resumir_texto(texto):
    max_tokens = 16384  # Model limit
    palavras = texto.split()

    if len(palavras) > max_tokens:
        texto = " ".join(palavras[:max_tokens])  # Truncate to maximum supported

    # Generate the summary
    resumo = summarizer(texto, max_length=500, min_length=50, do_sample=False)[0]["summary_text"]
    return resumo

noticia = result[0]
resumo = resumir_texto(noticia)
# print(resumo)
print("############")

# # part 3: Creating Audio (Text to Speech (TTS)) of the news summary
# # texto = "This is a summary of the main technology trends."
texto = resumo
tts = gTTS(text=texto, lang='pt')
# tts = gTTS(text=texto, lang='en')
tts.save("resumo.mp3")

# part 4: Video Generation with Background Image and Audio
# Upload images and audio
imagem = ImageClip("fundo.jpg").with_duration(10)
audio = AudioFileClip("resumo.mp3")

# Add text
fonte="./arial/ARIAL.TTF"
texto_clipe = TextClip(text="Technology Summary", font=fonte, font_size=70, color='white', horizontal_align='center', duration=5)
# texto_clipe = texto_clipe.set_position("center").with_duration(10)

# Combine everything
video = CompositeVideoClip([imagem, texto_clipe])
video = video.with_audio(audio)

# Save the video
video.write_videofile("video_tecnologia.mp4", fps=24)

# part 5: Automatically Upload Video to YouTube
def authenticate_youtube():
    # Perform the authentication flow
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret_xxxxxxxxxxx.json",  # Replace with the path to your OAuth credentials JSON
        SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

def upload_video(video_file, title, description):
    youtube = authenticate_youtube()

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["tecnologia", "insights"],
                "categoryId": "28"  # Category: Science & Technology
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    print("Upload complete! Video ID:", response["id"])

upload_video("video_tecnologia.mp4", "Technology Summary of the Week", "Check out the latest technology trends.")