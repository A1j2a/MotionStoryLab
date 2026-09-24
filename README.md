# AI Kids Video Studio

> **Production-Ready Local-First Web Application for 3D Kids Animated Nursery Rhymes & Songs**
> Designed and optimized for **Apple Silicon Mac (M4 / 16 GB Unified Memory)**.

---

## 1. Overview & Architecture

**AI Kids Video Studio** automatically generates original 5–7 minute English 3D animated nursery rhyme and kids-song videos from a single user idea. 

To honor the hardware specifications (Apple Silicon Mac mini M4 with 16 GB unified memory), the architecture strictly enforces **sequential, non-overlapping processing** across memory-heavy modules:
- LLM / Planning (OmniRoute / OpenAI-compatible endpoint)
- Procedural & 3D Rendering (Headless Blender Python scripts)
- Generative Visuals (Optional local ComfyUI)
- Local Speech & Narration (Kokoro TTS / AudioProvider)
- Multi-track Compositing & Subtitles (FFmpeg engine)

```
                     +---------------------------------------+
                     |         Next.js Dashboard             |
                     |       (Port 3000, 127.0.0.1)          |
                     +-------------------+-------------------+
                                         | REST / SSE
                                         v
                     +---------------------------------------+
                     |       FastAPI Python Backend          |
                     |       (Port 8000, 127.0.0.1)          |
                     +-------------------+-------------------+
                                         |
     +-------------------+---------------+-------------------+--------------------+
     |                   |                                   |                    |
     v                   v                                   v                    v
+---------+     +-------------------+               +------------------+    +-------------+
| SQLite  |     |  Sequential Job   |               |  Audio Provider  |    |   Blender   |
| Engine  |     |  Orchestrator     |               | (Kokoro TTS/SFX) |    |  Headless   |
+---------+     +---------+---------+               +------------------+    +------+------+
                          |                                                        |
                          +-------------> [ FFmpeg Compositor ] <------------------+
                                                 |
                                                 v
                                        [ Final 1080p MP4 ]
```

---

## 2. Requirements

- **Operating System:** macOS (Apple Silicon M1/M2/M3/M4 recommended)
- **Python:** 3.11+ (Python 3.13 tested)
- **Node.js:** v18.0+ (v20+ recommended)
- **FFmpeg:** Installed via `brew install ffmpeg`
- **Blender:** Blender 4.x installed (in `/Applications/Blender.app` or added to `$PATH`)
- **Optional Local Adapters:**
  - OmniRoute Gateway (port 20128)
  - n8n Workflow Engine (port 5678)
  - ComfyUI Local Instance (port 8188)
  - Kokoro TTS Service (port 8880)

---

## 3. Installation & Setup

### Clone & Enter Directory
```bash
cd youtube-ai-studio
```

### Environment Configuration
```bash
cp .env.example .env
```
Key configuration values in `.env`:
- `BACKEND_HOST=127.0.0.1` (Strict local binding)
- `BACKEND_PORT=8000`
- `FRONTEND_PORT=3000`
- `DATABASE_URL=sqlite+aiosqlite:///./projects/studio.db`
- `PROJECT_DIR=./projects`

### Python Virtual Environment Setup
```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
```

---

## 4. Subsystem Setup Guides

### OmniRoute Setup
Start OmniRoute locally on port `20128`. Configure local models or OpenAI-compatible gateways. The backend connects via `OMNIROUTE_URL=http://127.0.0.1:20128`.

### n8n Setup
Install n8n via npm or Docker:
```bash
npx n8n
```
Exported workflows are organized in `n8n/`.

### Blender Headless Automation
Ensure Blender is in `/Applications/Blender.app/Contents/MacOS/blender` or in your `$PATH`. The automation runner executes scripts headlessly (`blender -b -P blender/scripts/render_scene.py`).

### ComfyUI Setup (Optional)
Clone and launch ComfyUI on port `8188`. JSON workflows reside in `comfyui/workflows/`. When unavailable, the core procedural pipeline runs without generative AI stalls.

### Kokoro TTS Setup
Launch the Kokoro local TTS server on port `8880` or use the direct Python audio provider interface located in `audio/`.

### FFmpeg Setup
```bash
brew install ffmpeg
```

### YouTube OAuth Setup
1. Create a project in Google Cloud Console.
2. Enable YouTube Data API v3.
3. Configure OAuth consent screen and download client secrets JSON.
4. Place JSON in `config/youtube_client_secrets.json` (keep outside source control).
5. Initial uploads are strictly set to **PRIVATE**.

---

## 5. Starting and Stopping the Studio

### Start Studio
```bash
./start.sh
```
`start.sh` automatically:
1. Validates dependencies (Python, Node, npm, FFmpeg, Blender).
2. Sets up folders (`logs/`, `projects/`).
3. Verifies adapter health (OmniRoute, n8n, ComfyUI, TTS).
4. Sequentially launches the backend and frontend on `127.0.0.1`.
5. Prints active endpoints and runs initial health checks.

### Stop Studio
```bash
./stop.sh
```
Gracefully terminates backend, frontend, and associated subprocesses.

---

## 6. Development Order (Phases)

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Project Scaffold & Base Structure | **Completed & Tested** |
| **Phase 2** | Database Layer (SQLite + Async Repository) | **Completed & Tested** |
| **Phase 3** | FastAPI Backend & REST APIs | **Completed & Tested** |
| **Phase 4** | Frontend Dashboard (Next.js) | **Completed & Tested** |
| **Phase 5** | AI Content Planner | Next |
| **Phase 6** | Strict JSON Schema Validation & Repair | Pending |
| **Phase 7** | Character Bible System | Pending |
| **Phase 8** | Scene & Shot Engine | Pending |
| **Phase 9** | Blender 3D Renderer | Pending |
| **Phase 10** | Kokoro TTS & Vocal Pipeline | Pending |
| **Phase 11** | Subtitle & SRT Generator | Pending |
| **Phase 12** | FFmpeg Multi-track Compositor | Pending |
| **Phase 13** | Thumbnail Generator | Pending |
| **Phase 14** | ComfyUI Adapter | Pending |
| **Phase 15** | n8n Orchestrator | Pending |
| **Phase 16** | Review & Approval System | Pending |
| **Phase 17** | YouTube Data API Upload (Private Mode) | Pending |
| **Phase 18** | End-to-End Pipeline & Integration | Pending |

---

## 7. Testing

### Run Scaffold & Environment Test (Phase 1)
```bash
python3 scripts/test_phase1.py
```

### Run Database & Repository Tests (Phase 2)
```bash
pytest backend/tests/test_db.py -v
```

---

## 8. License
Proprietary / Internal - Built for MotionStoryLabs.
