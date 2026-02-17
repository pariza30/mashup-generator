from flask import Flask, render_template, request
import os, zipfile, smtplib, yt_dlp
from email.message import EmailMessage
from moviepy.audio.io.AudioFileClip import AudioFileClip

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
# CREATE CLIPS (MoviePy only)
# ---------------------------------------
def create_clips(duration):
    os.makedirs(CLIP_DIR, exist_ok=True)

    for file in os.listdir(DOWNLOAD_DIR):
        path = os.path.join(DOWNLOAD_DIR, file)

        audio = AudioFileClip(path).subclip(0, duration)

        clip_path = os.path.join(CLIP_DIR, "clip_" + file + ".mp3")
        audio.write_audiofile(clip_path, logger=None)
        audio.close()


# ---------------------------------------
# MERGE CLIPS
# ---------------------------------------
def merge_clips():
    clips = []

    for file in sorted(os.listdir(CLIP_DIR)):
        clips.append(AudioFileClip(os.path.join(CLIP_DIR, file)))

    final = clips[0]

    for clip in clips[1:]:
        final = final.append(clip)

    final.write_audiofile(OUTPUT_FILE, logger=None)


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

    sender_email = "yourgmail@gmail.com"
    app_password = "your_app_password"

    msg = EmailMessage()
    msg["Subject"] = "Your Mashup File"
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

            try:
                videos = int(request.form.get("videos"))
                duration = int(request.form.get("duration"))
            except:
                return "Videos and duration must be numbers."

            if videos <= 10:
                return "Number of videos must be greater than 10."

            if duration <= 20:
                return "Duration must be greater than 20 seconds."

            # clean old files
            for folder in [DOWNLOAD_DIR, CLIP_DIR]:
                if os.path.exists(folder):
                    for f in os.listdir(folder):
                        os.remove(os.path.join(folder, f))

            download_songs(singer, videos)
            create_clips(duration)
            merge_clips()
            zip_path = create_zip()
            send_email(email, zip_path)

            return "Mashup created and sent to email!"

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html")


# Render port config
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
