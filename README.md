<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <img src="assets/tubetunes-logo-1024.png" alt="TubeTunes Logo" width="120" />
  <h1 align="center">TubeTunes</h1>

  <p align="center">
    A powerful CLI YouTube playlist audio player for your terminal
    <br />
    <br />
    <a href="https://github.com/RyannPy/TubeTunes/releases/latest"><img src="https://img.shields.io/github/v/release/RyannPy/TubeTunes?style=for-the-badge&color=brightgreen" alt="Latest Release" /></a>
    &nbsp;
    <a href="https://github.com/RyannPy/TubeTunes/releases/latest"><img src="https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge&logo=windows" alt="Platform" /></a>
    &nbsp;
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-orange?style=for-the-badge" alt="License" /></a>
    <br />
    <br />
    <a href="#getting-started"><strong>Get Started »</strong></a>
    <br />
    <br />
    <a href="#usage">View Examples</a>
    ·
    <a href="https://github.com/RyannPy/TubeTunes/issues/new?labels=bug">Report Bug</a>
    ·
    <a href="https://github.com/RyannPy/TubeTunes/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#features">Features</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#windows-installer-exe">Windows Installer (.exe)</a></li>
      </ul>
    </li>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#interactive-menu">Interactive Menu</a></li>
        <li><a href="#command-line-mode">Command-Line Mode</a></li>
        <li><a href="#playback-controls">Playback Controls</a></li>
      </ul>
    </li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

TubeTunes is a terminal-based YouTube playlist audio player that lets you enjoy your favorite playlists without leaving the command line. Built with Python, it leverages `yt-dlp` for audio extraction and `mpv` for high-quality playback, offering a clean, distraction-free listening experience.

**Why TubeTunes?**
* 🎯 **Terminal-native** — No browser tabs, no ads, just music
* ⚡ **Lightweight** — Minimal resource usage compared to web browsers
* 🎛️ **Full control** — Interactive playback controls (play, pause, seek, next, previous)
* 💾 **Playlist management** — Save playlists with custom aliases for quick access
* 🎨 **Beautiful UI** — Rich terminal interface with real-time progress display

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- FEATURES -->
## Features

### Playlist Management
- ✅ Add playlists with custom aliases
- ✅ List all saved playlists
- ✅ Rename playlist aliases
- ✅ Delete unwanted playlists
- ✅ Direct URL or alias-based playback

### Playback Features
- ✅ Play YouTube playlists
- ✅ Shuffle mode
- ✅ Real-time progress display (MM:SS / MM:SS)
- ✅ Next track
- ✅ Previous track
- ✅ Pause / Resume
- ✅ Seek forward (+10 seconds)
- ✅ Seek backward (-10 seconds)
- ✅ Clean exit and return to menu

### Technical Highlights
- 🔌 **mpv IPC integration** — Non-blocking playback with full control
- 🎨 **Rich terminal UI** — Beautiful panels and tables powered by Rich
- 🎹 **Interactive prompts** — User-friendly menus with Questionary
- 📦 **Easy distribution** — Installable Python package with `tubetunes` command

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

TubeTunes requires the following to be installed on your system:

* **Python 3.10 or higher**
  ```sh
  python --version
  ```

* **mpv media player**
  - **Windows**: Download from [mpv.io](https://mpv.io/installation/) and add to PATH
  - **macOS**: `brew install mpv`
  - **Linux**: `sudo apt install mpv` (Debian/Ubuntu) or `sudo dnf install mpv` (Fedora)

  Verify installation:
  ```sh
  mpv --version
  ```

### Installation

#### Method 1: Windows Installer (.exe) — Easiest ⭐

> **No Python required!** Just download and run.

1. Go to the [Releases](https://github.com/RyannPy/TubeTunes/releases/latest) page
2. Download **`TubeTunes-v1.1.0-Setup.exe`** (Windows only)
3. Run the installer — TubeTunes will be ready to use from your terminal:
   ```sh
   tubetunes
   ```

> **Note:** mpv must still be installed and available in PATH. See [Prerequisites](#prerequisites).

#### Method 2: Install from GitHub Release (Python)

1. Download the latest `.whl` file from the [Releases](https://github.com/RyannPy/TubeTunes/releases) page

2. Install the package:
   ```sh
   pip install tubetunes-1.1.0-py3-none-any.whl
   ```

3. Verify installation:
   ```sh
   tubetunes
   ```

#### Method 3: Install from Source

1. Clone the repository:
   ```sh
   git clone https://github.com/RyannPy/TubeTunes.git
   cd TubeTunes
   ```

2. Install the package:
   ```sh
   pip install .
   ```

3. Run TubeTunes:
   ```sh
   tubetunes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
## Usage

### Interactive Menu

Launch TubeTunes without any arguments to enter the interactive menu:

```sh
tubetunes
```

You'll see:
```
? TubeTunes
❯ Play Playlist
  Add Playlist
  List Playlists
  Rename Playlist
  Delete Playlist
  Exit
```

**Adding a playlist:**
1. Select "Add Playlist"
2. Enter a custom alias (e.g., `chill`)
3. Paste the YouTube playlist URL
4. Press Enter to save

**Playing a playlist:**
1. Select "Play Playlist"
2. Choose your saved playlist
3. Select playback mode (Normal / Shuffle)
4. Enjoy your music!

### Command-Line Mode

TubeTunes also supports direct command-line usage:

**Save a playlist:**
```sh
tubetunes save <alias> <playlist_url>
```

Example:
```sh
tubetunes save lofi "https://youtube.com/playlist?list=PLOzDu-..."
```

**Play a saved playlist:**
```sh
tubetunes play <alias>
```

**Play with shuffle:**
```sh
tubetunes play <alias> --shuffle
```

**Play a URL directly:**
```sh
tubetunes play "https://youtube.com/playlist?list=PLOzDu-..."
```

### Playback Controls

While music is playing, use these keyboard controls:

| Key | Action |
|-----|--------|
| <kbd>SPACE</kbd> | Pause / Resume |
| <kbd>N</kbd> | Next track |
| <kbd>P</kbd> | Previous track |
| <kbd>F</kbd> | Seek forward +10 seconds |
| <kbd>B</kbd> | Seek backward -10 seconds |
| <kbd>Q</kbd> | Quit playback (return to menu) |

**During playback, you'll see:**

```
╭──────────────── TubeTunes ───────────────────╮
│                                              │
│            YOASOBI - Idol                    │
│                                              │
│       ▶  PLAYING       01:32  /  03:48       │
│                                              │
│    #  Up Next                                │
│    1  Next Song Title                        │
│    2  Another Song                           │
│    3  One More Track                         │
│                                              │
│   SPACE  Pause / Resume                      │
│       N  Next song                           │
│       P  Previous song                       │
│       F  +10s                                │
│       B  -10s                                │
│       Q  Quit playback                       │
│                                              │
╰──────────────────────────────────────────────╯
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- PROJECT STRUCTURE -->
## Project Structure

```
tubetunes/
├── src/
│   ├── cli/              # Command-line interface
│   │   ├── cli.py        # Argument parser
│   │   └── menu.py       # Interactive menu
│   ├── core/             # Core playback logic
│   │   ├── player.py     # mpv player wrapper
│   │   ├── queue_manager.py
│   │   ├── playlist_loader.py
│   │   └── mpv_ipc.py    # mpv IPC communication
│   ├── services/         # Business logic
│   │   ├── playback_service.py
│   │   └── playlist_service.py
│   ├── storage/          # Data persistence
│   │   └── playlist_storage.py
│   ├── utils/            # Utilities
│   │   └── console.py    # Rich console wrapper
│   └── app.py            # Main entry point
├── data/
│   └── playlists.json    # Saved playlists
├── pyproject.toml        # Package configuration
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

### Implemented (v1.0)
- [x] Interactive menu-driven interface
- [x] Playlist CRUD operations
- [x] Full playback control (play, pause, seek, next, previous)
- [x] Real-time progress display
- [x] Shuffle mode
- [x] mpv IPC integration
- [x] Rich terminal UI

### v1.1.0 — GitHub Presence Update 🚀
- [x] Windows standalone installer (`.exe`) — no Python needed
- [x] Project logo & badges on README
- [x] Official GitHub release page

### Future Enhancements (v2.0+)
- [ ] Volume control
- [ ] Repeat / repeat-one modes
- [ ] Search within playlists
- [ ] Playlist folders/categories
- [ ] Export/import playlists
- [ ] Track history
- [ ] Configurable keyboard shortcuts
- [ ] Multiple audio quality options

See the [open issues](https://github.com/RyannPy/TubeTunes/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube audio extraction
* [mpv](https://mpv.io/) - High-quality media playback
* [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
* [Questionary](https://github.com/tmbo/questionary) - Interactive prompts
* [psutil](https://github.com/giampaolo/psutil) - Process management

<p align="right">(<a href="#readme-top">back to top</a>)</p>
