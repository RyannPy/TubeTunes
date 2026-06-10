from yt_dlp import YoutubeDL


def get_playlist(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return info