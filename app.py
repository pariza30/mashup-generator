from flask import Flask, render_template, request
import os, zipfile, smtplib, yt_dlp
from email.message import EmailMessage
from moviepy.audio.io.AudioFileClip import AudioFileClip
from pydub import AudioSegment

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
CLIP_DIR = "clips"
OUTPUT_FILE = "final_output.mp3"


# ---------------------------------------
# DOWNLOAD SONGS
# ---------------------------------------
def download_songs(singer, count):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/song_%(autonumber)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{count}:{singer} official song"])


# ---------------------------------------
# CREATE CLIPS
# ---------------------------------------
def create_clips(duration):
    os.makedirs(CLIP_DIR, exist_ok=True)

    for file in os.listdir(DOWNLOAD_DIR):
        path = os.path.join(DOWNLOAD_DIR, file)

        audio = AudioFileClip(path)
        wav_path = path + ".wav"
        audio.write_audiofile(wav_path, logger=None)
        audio.close()

        sound = AudioSegment.from_file(wav_path)
        clip = sound[:duration * 1000]

        clip.export(os.path.join(CLIP_DIR, "clip_" + file + ".mp3"), format="mp3")

        os.remove(wav_path)


# ---------------------------------------
# MERGE CLIPS
# ---------------------------------------
def merge_clips():
    combined = AudioSegment.empty()

    for file in sorted(os.listdir(CLIP_DIR)):
        combined += AudioSegment.from_file(os.path.join(CLIP_DIR, file))

    combined.export(OUTPUT_FILE, format="mp3")


# ---------------------------------------
# CREATE ZIP
# ---------------------------------------
def create_zip():
    os.makedirs("output", exist_ok=True)
    zip_path = "output/mashup.zip"

    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(OUTPUT_FILE)

    return zip_path


# ---------------------------------------
# SEND EMAIL
# ---------------------------------------
def send_email(receiver_email, zip_path):

    sender_email = "pkandol_be23@thapar.edu"
    app_password = "poaadlxrnbldmjdu"

    msg = EmailMessage()
    msg["Subject"] = "Your Mashup File 🎵"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Enjoy your auto-generated mashup!")

    with open(zip_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename="mashup.zip"
        )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)


# ---------------------------------------
# ROUTE
# ---------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            singer = request.form.get("singer")
            email = request.form.get("email")

            # numeric inputs
            try:
                videos = int(request.form.get("videos"))
                duration = int(request.form.get("duration"))
            except:
                return "❌ Videos and duration must be numbers."

            # validation
            if videos <= 10:
                return "❌ Number of videos must be greater than 10."

            if duration <= 20:
                return "❌ Duration must be greater than 20 seconds."

            # clean old files
            for folder in [DOWNLOAD_DIR, CLIP_DIR]:
                if os.path.exists(folder):
                    for f in os.listdir(folder):
                        os.remove(os.path.join(folder, f))

            # process
            download_songs(singer, videos)
            create_clips(duration)
            merge_clips()
            zip_path = create_zip()
            send_email(email, zip_path)

            return "✅ Mashup created & sent to email!"

        except Exception as e:
            return f"❌ Error: {str(e)}"

    return render_template("index.html")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

