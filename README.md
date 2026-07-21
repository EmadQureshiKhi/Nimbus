<p align="center">
  <img src="assets/nimbus%20logo%201.png" alt="Nimbus logo" width="420" />
</p>

# Nimbus

> A voice-driven, screen-aware AI assistant for Windows that teaches you.

Nimbus is your on-screen AI study buddy and tutor for Windows. Hold a hotkey and ask about anything you see — a math problem, a paragraph in a PDF, a diagram, or how to use an app — and Nimbus reads your screen, answers out loud, and teaches you visually, circling and pointing to explain right where you're looking.

[![Tests](https://github.com/EmadQureshiKhi/Nimbus/actions/workflows/tests.yml/badge.svg)](https://github.com/EmadQureshiKhi/Nimbus/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-f4d35e.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078d4.svg)](#setup--running-from-source)

## Education: software tutoring that sees the screen

Nimbus is designed as a practical learning companion for software, not just a voice interface. A learner can keep working in the real application, ask a question aloud, and receive guidance in the context where it matters. In **Tutor mode**, Nimbus can draw circles, arrows, underlines, and short labels directly on the screen to show an action step by step.

That is useful for:

- **Students:** learn unfamiliar tools — coding environments, spreadsheets, design software, research tools, or learning platforms — without constantly switching to a tutorial video or searching for a menu by name.
- **Teachers:** demonstrate a workflow and give contextual help while a student is actually using the tool, including hands-free situations where typing is inconvenient.
- **Educational organizations:** add local, per-application knowledge in a Markdown knowledge-base folder and preserve per-app interaction memory, so guidance can become more useful for recurring software and workflows over time.
- **Accessible learning:** voice input, spoken answers, visible pointers, and on-screen tutor annotations offer multiple ways to receive guidance.

Nimbus is screen-aware: it captures the active screen context, understands the question alongside that context, and can guide the learner to the relevant interface control rather than merely describing it in abstract terms.

## Category

**Education.** Nimbus fits the Education track because it teaches people how to use software in context: it observes the learning environment, explains the task aloud, and visually guides the next action on the learner's own screen.

## How it works

### Push-to-talk pipeline

1. Hold the configured hotkey (default: `Ctrl+Alt+Space`) and speak.
2. On release, Nimbus finalizes speech-to-text while capturing the screen. It also recalls relevant per-app memory and, if present, the matching local knowledge-base Markdown file.
3. The configured vision model receives the screenshot and context, then streams a response.
4. Nimbus begins spoken output through the configured text-to-speech provider and, when appropriate, receives a `[POINT:x,y]` target for the UI.
5. A per-monitor, click-through Qt overlay renders the pointer without stealing focus or blocking clicks.

The overlay is DPI-aware and uses one window per physical monitor, which keeps physical screenshot coordinates and Qt logical coordinates aligned on mixed-DPI multi-monitor setups. It also provides the listening waveform, thinking spinner, tutor annotations, and non-blocking status/error toasts.

### Grounding and tutor guidance

Nimbus has two pointing routes:

- **Direct model grounding:** the normal OpenAI vision route returns a precise `[POINT:x,y]` target directly.
- **Two-stage grid-locator fallback:** when a model does not return direct coordinates, Nimbus asks it to identify a coarse numbered grid cell and then a finer sub-grid cell.

For directional questions and targets near the cursor, Nimbus can run a high-detail crop verification/refinement pass around the candidate coordinate before drawing the pointer. This preserves the direct result when refinement is uncertain rather than replacing it with a guess.

With **Tutor mode** enabled in Settings, the runtime model can return `[CIRCLE]`, `[ARROW]`, `[UNDERLINE]`, and `[LABEL]` geometry in addition to a point. Nimbus maps those annotations to the correct monitor and draws them temporarily on screen.

### Local context and provider choices

- **Persistent per-app memory:** `memory.py` stores human-readable Markdown per Windows executable and maintains a local SQLite index. Nimbus recalls recent context for the app currently in use.
- **Knowledge base:** put a Markdown file named for an app in the Nimbus Knowledge Folder (for example, `EXCEL.EXE.md`) to supply local instructions or organizational documentation for that app.
- **Pluggable providers:** OpenAI is the default LLM path. Settings can select OpenAI, Anthropic, Gemini/OpenRouter routing, Ollama, or OpenAI Realtime where configured; speech can use AssemblyAI or local faster-whisper; speech output can use Cartesia, ElevenLabs, or local Kokoro.
- **Offline/privacy-oriented speech:** faster-whisper STT and Kokoro TTS are local options. With a local Ollama vision model as well, the main interaction path can run without cloud model providers.

## Features

- Push-to-talk voice interaction with a configurable hotkey.
- Screen-aware spoken answers.
- On-screen pointing with a click-through, per-monitor overlay.
- Tutor mode with circles, arrows, underlines, and labels.
- Direct coordinate grounding, grid fallback, and targeted verification/refinement for small UI targets.
- Persistent per-app memory and a drop-in Markdown knowledge-base folder.
- Session-history export to a timestamped Markdown file, including recent memory for the current app.
- BYOK Settings stored through Windows Credential Manager, with optional `.env` setup for development.
- Opt-in diagnostic capture with retention controls, plus a confirmed **Clear all Nimbus local data** control.
- First-run welcome/permissions guidance and a one-time tray onboarding reminder.
- Distinct listening, completion, and error audio cues; waveform/spinner state feedback; non-blocking in-overlay error toasts.
- Tray controls for Settings, folder access, session export, push-to-talk pause/resume, and quit.
- GitHub Actions tests, automated Windows installer releases, and an in-app update check.

## Setup & running from source

Nimbus is **Windows-only**. Use Windows and Python 3.13.

```powershell
# Clone and enter the repository
git clone https://github.com/EmadQureshiKhi/Nimbus.git
cd Nimbus

# Create and activate a Python 3.13 virtual environment
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run Nimbus
py -3.13 -m app
```

On first launch, Nimbus opens its Settings dialog. Choose providers and enter the required **bring-your-own keys**; settings and keys are stored in Windows Credential Manager.

Alternatively, configure a development `.env` file:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` with your provider choices and keys. The example uses OpenAI for vision and local faster-whisper/Kokoro speech providers. Never commit `.env`.

After Nimbus starts, it lives in the system tray. Right-click its icon for Settings and controls, then hold `Ctrl+Alt+Space` (or your configured hotkey), speak, and release to ask a question.

## Install without the repo

1. Go to [GitHub Releases](https://github.com/EmadQureshiKhi/Nimbus/releases).
2. Download the latest `Nimbus-Windows-Setup-v*.exe` installer.
3. Run it and launch Nimbus from the final installer screen, Start menu, or desktop shortcut.
4. Complete the first-run Settings and welcome screens, then use the tray icon.

Releases are built and published automatically by GitHub Actions after pushes to `main` pass the release workflow.

The installer is currently unsigned. If Microsoft SmartScreen appears, choose **More info** and then **Run anyway** after confirming you downloaded the installer from the official Nimbus Releases page.

## Build & release

Build the PyInstaller onedir distribution from a Python 3.13 environment:

```powershell
py -3.13 -m PyInstaller nimbus.spec --noconfirm
```

The executable is produced at `dist\Nimbus\Nimbus.exe`. Verify its imports without opening a GUI, microphone, or network connection:

```powershell
dist\Nimbus\Nimbus.exe --selftest
```

Build the installer with Inno Setup 6+:

```powershell
iscc installer\nimbus.iss
```

The release workflow runs tests in a clean environment, assigns an automated `1.0.<GitHub run number>` version, builds the frozen app, runs its `--selftest`, builds the Inno Setup installer, and creates or updates the corresponding GitHub Release. Nimbus also checks the latest release asynchronously at startup and offers to open it when a newer version is available.

## Testing

Run the complete suite with `.env` loading disabled so local credentials cannot affect the result:

```powershell
python -c "import dotenv,pytest,sys; dotenv.load_dotenv=lambda *a,**k:False; sys.exit(pytest.main(['-q']))"
```

The suite currently has **470+ tests** (477 passing in the latest local verification). GitHub Actions runs it on Windows with Python 3.13 for every push and pull request, with `NIMBUS_DISABLE_DOTENV=1`.

For a deterministic import-only runtime check:

```powershell
python -m app --selftest
# SELFTEST OK
```

## Built with OpenAI Codex (powered by GPT-5.6)

Nimbus was built with **OpenAI Codex, powered by GPT-5.6**. GPT-5.6 powered the development process through Codex; it is not the runtime model used by the app.

Codex running on GPT-5.6 accelerated concrete engineering work across the repository:

- Implemented multi-file features from natural-language requests: session-history export, configurable hotkeys, diagnostics/privacy controls, automated releases and the in-app update system, push-to-talk pause, error toasts, audio cues, onboarding, and overlay visual polish.
- Diagnosed and fixed bugs directly from stack traces: the Qt/Win32 DPI startup conflict, the Knowledge Folder creation crash, the hotkey-validator conflict, and the debug-logging crash path.
- Authored unit tests and iterated the full suite to a green **470+** tests.
- Set up GitHub Actions CI and the Windows release pipeline.
- Refactored the hotkey parser from a fixed combination toward arbitrary supported key chords.
- Supported codebase Q&A and architecture decisions, including keeping direct model grounding as the preferred route with verification for small targets, offering OpenAI by default with local STT/TTS privacy options, and using a per-monitor overlay for mixed-DPI correctness.

Those are development-time contributions made with Codex/GPT-5.6. They are separate from Nimbus's runtime model calls described below.

## The app's runtime AI (separate from Codex)

At runtime, Nimbus uses an OpenAI vision model configured by `OPENAI_MODEL_VISION` for screen understanding, pixel-accurate `[POINT:x,y]` UI grounding, the verification/refinement pass for small targets, Tutor mode annotation geometry (`[CIRCLE]`, `[ARROW]`, `[UNDERLINE]`, `[LABEL]`), and natural spoken-answer generation through the selected LLM path.

This runtime AI is independent of the **GPT-5.6 model that powered development through Codex**. Nimbus can also use local faster-whisper for STT and Kokoro for TTS, and supports an Ollama LLM option for a local model path.

## Submission info

- Demo video: https://youtu.be/GZW97NDSOkk
- Codex /feedback session ID: 019f83a1-36a4-75a2-870b-d29421d4d1d5
- Code repository: https://github.com/EmadQureshiKhi/Nimbus

## License

[MIT (The Nimbus Authors)](LICENSE).
