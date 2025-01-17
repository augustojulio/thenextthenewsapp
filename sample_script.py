import feedparser
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline # Hugging Face - AI to summarize text

from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Escopos necessários para fazer upload de vídeos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# part 1: Coleta de Informações e Fontes
# Testing with one feed
result = []
feed_url = "https://www.theverge.com/rss/index.xml"
feed = feedparser.parse(feed_url)
# Add a list of feed_urls to test with multiple feeds
# Get the first 2 entries from each feed url

for entry in feed.entries[:5]:
    result.append(f"Título: {entry.title}\nLink: {entry.link}\nResumo: {entry.summary}\n")

# print(result)

# Modelo e tokenizer compatíveis com textos longos para sumarização
model_name = "allenai/led-base-16384"

# Carregar o tokenizer e o modelo
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Configurar o pipeline
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# part 2: Resumo Automático de Notícias
# Função de sumarização
def resumir_texto(texto):
    max_tokens = 16384  # Limite do modelo
    palavras = texto.split()

    if len(palavras) > max_tokens:
        texto = " ".join(palavras[:max_tokens])  # Truncar para o máximo suportado

    # Gerar resumo
    resumo = summarizer(texto, max_length=500, min_length=50, do_sample=False)[0]["summary_text"]
    return resumo

noticia = result[0]
resumo = resumir_texto(noticia)
# print(resumo)
print("############")

# # part 3: Criação do Áudio (Texto para Fala (TTS)) do resumo da notícia
# # texto = "Este é um resumo das principais tendências de tecnologia."
texto = resumo
tts = gTTS(text=texto, lang='pt')
# tts = gTTS(text=texto, lang='en')
tts.save("resumo.mp3")

# part 4: Geração de Vídeo com Imagem de Fundo e Áudio
# Carregar imagens e áudio
imagem = ImageClip("fundo.jpg").with_duration(10)
audio = AudioFileClip("resumo.mp3")

# Adicionar texto
fonte="./arial/ARIAL.TTF"
texto_clipe = TextClip(text="Resumo de Tecnologia", font=fonte, font_size=70, color='white', horizontal_align='center', duration=5)
# texto_clipe = texto_clipe.set_position("center").with_duration(10)

# Combinar tudo
video = CompositeVideoClip([imagem, texto_clipe])
video = video.with_audio(audio)

# Salvar vídeo
video.write_videofile("video_tecnologia.mp4", fps=24)

# part 5: Upload automático do Vídeo para o YouTube
def authenticate_youtube():
    # Realize o fluxo de autenticação
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret_xxxxxxxxxxx.json",  # Substitua pelo caminho do JSON das credenciais OAuth
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
                "categoryId": "28"  # Categoria: Science & Technology
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(video_file)
    )
    response = request.execute()
    print("Upload concluído! ID do vídeo:", response["id"])

upload_video("video_tecnologia.mp4", "Resumo de Tecnologia da Semana", "Confira as últimas tendências em tecnologia.")