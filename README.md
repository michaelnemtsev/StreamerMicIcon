# StreamerMicIcon

**A free, portable Windows microphone mute indicator overlay for streamers, gamers, and remote workers.**

Ever forget to unmute your mic on a Zoom call, Teams meeting, or Twitch stream? StreamerMicIcon is a tiny always-on-top desktop widget that floats a microphone icon on your screen showing whether your Windows default microphone is live or muted — in real time. When muted, the icon flashes red so you never accidentally talk while muted again.

No installation required. Just download the single `.exe` and run it.

![Windows](https://img.shields.io/badge/platform-Windows-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Latest Release](https://img.shields.io/github/v/release/michaelnemtsev/StreamerMicIcon)](https://github.com/michaelnemtsev/StreamerMicIcon/releases/latest)
[![Download](https://img.shields.io/github/downloads/michaelnemtsev/StreamerMicIcon/total)](https://github.com/michaelnemtsev/StreamerMicIcon/releases/latest)

## What It Does

StreamerMicIcon monitors your Windows default recording device (microphone) and displays a floating, transparent overlay icon on your desktop:

- **Green mic** — your microphone is active and picking up audio
- **Red flashing mic with slash** — your microphone is muted (pulses to grab your attention)
- **Gray mic** — no default microphone detected

The overlay has no window borders, no title bar, no background — just the mic icon floating on top of everything. It works over OBS, games, browsers, video calls, or any fullscreen application.

## Use Cases

- **Streamers** — see your mic mute status at a glance while streaming on Twitch, YouTube, or Kick
- **Gamers** — know if your mic is hot during Discord or in-game voice chat
- **Remote workers** — never say "sorry, I was on mute" again during Zoom, Teams, Google Meet, or Webex calls
- **Podcasters & content creators** — visual confirmation your mic is recording
- **Presenters** — confidence that your audience can hear you

## Features

- **Transparent floating icon** — only the mic shape is visible, no window chrome
- **Real-time monitoring** — polls the Windows default microphone every 250ms
- **Color-coded status** — green when live, red when muted, gray if no mic detected
- **Flashing mute alert** — the icon pulses when muted so you never miss it
- **Always on top** — stays visible over games, OBS, browsers, fullscreen apps
- **Draggable** — click and drag to reposition anywhere on screen
- **Portable** — single `.exe`, no install, no dependencies on the target PC
- **Lightweight** — minimal CPU and memory usage
- **Double-click to quit**

## Quick Start (portable exe)

Download the latest `StreamerMicIcon.exe` from the [latest release](https://github.com/michaelnemtsev/StreamerMicIcon/releases/latest) and run it. No installation or Python needed.

## Run from Source

```bash
pip install -r requirements.txt
python streamer_mic_icon.py
```

## Build Portable exe

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name StreamerMicIcon --version-file version_info.py streamer_mic_icon.py
```

The standalone exe will be in `dist/StreamerMicIcon.exe`.

## How It Works

StreamerMicIcon uses the [Windows Core Audio API](https://learn.microsoft.com/en-us/windows/win32/coreaudio/core-audio-apis-in-windows-vista) via [pycaw](https://pypi.org/project/pycaw/) to query the mute state of the default recording endpoint. The overlay is rendered with [PyQt5](https://pypi.org/project/PyQt5/) using a frameless, translucent widget with custom QPainter drawing. The icon is vector-drawn (not a bitmap), so it looks crisp at any DPI.

## Dependencies

- [PyQt5](https://pypi.org/project/PyQt5/) — transparent window and rendering
- [pycaw](https://pypi.org/project/pycaw/) — Windows Core Audio API bindings
- [comtypes](https://pypi.org/project/comtypes/) — COM interface support

## FAQ

**Q: Does it work with any microphone?**
A: It monitors whatever Windows has set as the default recording device. If you switch your default mic in Windows Sound settings, StreamerMicIcon follows automatically.

**Q: Does it work in fullscreen games?**
A: Yes — the overlay uses the "always on top" flag, so it stays visible over most fullscreen and borderless-windowed applications.

**Q: Does it use a lot of CPU?**
A: No. It polls the mic state via a lightweight COM call every 250ms and only repaints when the state changes.

**Q: Can I move the icon?**
A: Yes — click and drag it anywhere on screen. Double-click to close it.

**Q: Does it toggle my mic mute?**
A: No. It is a read-only indicator. It shows the current mute state but does not change it.

## Keywords

Microphone mute indicator, mic status overlay, mute notification, am I muted, Windows mic monitor, OBS mic indicator, streaming mic status, desktop mic widget, microphone on off indicator, mute alert, mic mute reminder, always on top mic indicator, floating mic icon, portable mic monitor, free mic mute indicator Windows.

## License

MIT
