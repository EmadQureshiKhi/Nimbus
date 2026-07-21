<h1 align="center">Nimbus</h1>

<p align="center">
  A voice-driven, screen-aware AI buddy for Windows, powered by OpenAI. Hold a hotkey, ask anything about whatever app you are looking at, and Nimbus talks back and points at the answer with a blue cursor.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-f4d35e" alt="MIT" />
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078d4" alt="Windows 10/11" />
  <img src="https://img.shields.io/badge/powered%20by-OpenAI-10a37f" alt="OpenAI" />
  <a href="https://github.com/EmadQureshiKhi/Nimbus/actions/workflows/tests.yml"><img src="https://github.com/EmadQureshiKhi/Nimbus/actions/workflows/tests.yml/badge.svg" alt="Tests" /></a>
</p>

## What it does

You are working in some app. You hit a wall. You hold `Ctrl+Alt+Space`, ask a question out loud, release. A moment later you hear the answer, and a blue cursor lands on the exact button or menu item you needed to click.

A few ways to use it:

- **Live analysis of whatever is on screen.** *"What is this chart telling me?"* Nimbus reads the screen and walks you through it, pointing at the relevant spots.
- **Niche or company-internal software the model does not know.** Drop a markdown file with the docs into `~/Documents/Nimbus Wiki/<app>.exe.md` and Nimbus becomes an expert, pointing at things like a TA who already read the manual.
- **Learning a new tool or codebase.** Don't know what something does? Hit the hotkey, ask, Nimbus reads your editor and explains what is happening and where to click.

There is also a **teaching mode** (toggle *Draw on screen* in Settings). Instead of a single cursor, Nimbus marks up your screen the way a tutor would: it circles the thing you asked about, draws an arrow to it, underlines a term, and writes a short label, then clears them once you've read them.

Everything runs through your own API key. Nothing routes through a proxy server. See [Privacy](#privacy) for the specifics.

## Install Nimbus

Nimbus supports Windows 10/11 on 64-bit PCs. You can either install a ready-to-run release or run it from this repository.

### Option A: install without the repository

1. Open the [Nimbus Releases page](https://github.com/EmadQureshiKhi/Nimbus/releases) and download the latest `Nimbus-Windows-Setup-v*.exe` file.
2. Run the installer. It installs only for your Windows account, so it does not need administrator access.
3. Leave **Run Nimbus** selected at the end of setup, or open Nimbus later from the Start menu or desktop shortcut.
4. On first launch, choose your providers in Settings. The simplest setup is **OpenAI** for LLM, **faster-whisper (local)** for speech-to-text, and **Kokoro (local)** for speech output; enter only your OpenAI API key.
5. Nimbus appears as a blue cursor icon in the Windows system tray. Right-click it for Settings, your knowledge/memory folders, session export, or Quit.

Nimbus checks GitHub Releases when it starts. When a newer version is published, it shows an **Update available** message; select **Open** to download the new installer and run it to update Nimbus.

### Option B: run from this repository

Requires Windows 10/11 and Python 3.13.

```powershell
# 1. Clone the repository and enter it
git clone https://github.com/EmadQureshiKhi/Nimbus.git
cd Nimbus

# 2. Create and activate a virtual environment
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your key (copy .env.example to .env and fill it in)
#    Minimal setup: OpenAI for the LLM, local models for speech in/out.
#      OPENAI_API_KEY=sk-...
#      LLM_PROVIDER=openai
#      STT_PROVIDER=faster-whisper   # local, no key
#      TTS_PROVIDER=kokoro           # local, no key

# 5. Run it
py -3.13 -m app
```

## Use Nimbus

1. Start Nimbus. It runs from the **system tray** rather than opening a normal app window.
2. Open the app or webpage you want help with and place your cursor near the relevant area.
3. Hold `Ctrl+Alt+Space`, speak your question, then release the keys.
4. Nimbus captures the screen, answers out loud, and moves its blue cursor to a relevant control when useful.
5. Right-click the tray icon to change providers/keys, export the current session, open your knowledge folder, or quit.

If another application already uses `Ctrl+Alt+Space`, change that application’s shortcut so Nimbus can receive the hotkey. Nimbus observes the combination and does not block normal typing.

On first run the local speech models download once (~150 MB for speech-to-text, ~330 MB for the voice), so the first interaction is slower. After that it is fast.

## Build from source

Build the Windows onedir distributable from an activated Python 3.13 environment:

```powershell
py -3.13 -m PyInstaller nimbus.spec --noconfirm
```

The executable is written to `dist\Nimbus\Nimbus.exe`. Before launching it normally, verify the frozen bundle has every runtime import and native DLL without opening a tray window, microphone, or network connection:

```powershell
dist\Nimbus\Nimbus.exe --selftest
# SELFTEST OK
```

To make the optional installer after a successful PyInstaller build, install Inno Setup 6+ and run:

```powershell
iscc installer\nimbus.iss
```

This produces `installer\Output\Nimbus-Windows-Setup-v1.0.0.exe`. Inno Setup is not a Python dependency; if `iscc` is unavailable, install it separately or skip this optional installer step.

Every push to `main` also runs the release workflow. After tests pass, GitHub Actions builds the installer, publishes a new GitHub Release, and marks it as the latest download. The release version is automatically `1.0.<GitHub run number>`.

### Providers

Nimbus is OpenAI-first but supports swapping any stage from the Settings dialog:

- **LLM (vision + reasoning):** OpenAI (default). Ollama is available for a fully local option.
- **Speech-to-text:** local faster-whisper (default in the sample config, no key) or AssemblyAI (cloud, faster).
- **Text-to-speech:** local Kokoro (default in the sample config, no key), or Cartesia / ElevenLabs (cloud).

Pick the local options for STT and TTS and the only key you need is your OpenAI key. Go fully local (Ollama + faster-whisper + Kokoro) and you need no keys at all.

## How it works

The hotkey listener observes `Ctrl+Alt+Space` without consuming the keys, so your typing keeps working. On release, four things kick off in parallel: speech-to-text finalizes, the screen gets captured, per-app memory gets recalled, and a knowledge-base file gets looked up if one exists. The vision model receives the screenshot plus the transcript plus the memory plus the knowledge base, and streams a response. Sentences flush to the text-to-speech provider as soon as a `.!?` boundary is hit, so you start hearing audio while the model is still generating. A `[POINT:x,y:label]` tag in the response drives a per-monitor overlay to point at the exact pixel.

```
User holds Ctrl+Alt+Space
        │
        ├── speech-to-text finalizes         ┐
        ├── screen capture (overlay hidden)   │  all four run in parallel
        ├── per-app memory recall             │
        └── knowledge-base lookup             ┘
                    │
                    ▼
        OpenAI vision model (streaming)
        ┌───────────┴───────────┐
        ▼                       ▼
  sentence-level TTS      [POINT:x,y] → blue cursor overlay
        │
        ▼
   audio playback + memory record
```

## Engineering highlights

- **Sub-2s first-audible-word despite sequential APIs.** Parallel kick-off, sentence-level streaming to TTS, and a double-buffered playback path so the user starts hearing sentence one while the model is still generating sentence two.
- **Win32 layered click-through overlay, per-monitor DPI-aware.** One overlay widget per physical screen sidesteps mixed-DPI rendering bugs. The blue cursor is always-on-top, click-through, never steals focus, and lands on the correct pixel across monitors at different scaling.
- **A hotkey that does not break your typing.** An observe-only keyboard listener sees the combo without suppressing it system-wide.
- **Single-instance mutex.** A named Win32 mutex acquired before the app starts prevents duplicate processes and overlapping voice responses.
- **Multi-provider via progressive-disclosure UX.** A three-category dropdown (LLM / STT / TTS) with a single key field per selected provider.
- **Markdown memory and a drop-in knowledge folder.** Two plain-text stores, one `.md` file per app, no vector DB.

## Where things live

- Per-app memory: `~/.nimbus/memory/<app>.exe.md`
- Debug logs (attach these when reporting a bug): `~/.nimbus/debug/`
- Knowledge base: `~/Documents/Nimbus Wiki/<app>.exe.md`
- API keys: `.env` in the repo, mirrored to Windows Credential Manager

## Privacy

Nothing leaves your machine, except the things you explicitly send to your own APIs.

- API keys live in Windows Credential Manager via DPAPI per-user encryption.
- Screenshots, voice, transcripts, and model responses go directly from your machine to whichever providers you pick, using YOUR keys, with no proxy in between. Pick the local providers (Ollama, faster-whisper, Kokoro) and that data never leaves your machine at all.
- Per-app memory and the knowledge-base folder live on your local disk in plain markdown. You can read them, edit them, delete them.

## License

[MIT](LICENSE).
