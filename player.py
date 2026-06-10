from yt_dlp import YoutubeDL

def get_audio_stream(url):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return info['url']