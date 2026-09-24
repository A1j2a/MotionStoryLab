Build a complete production-ready local-first web application called **AI Kids Video Studio**.

The application must automatically create original 5–7 minute English 3D animated nursery-rhyme / kids-song videos from a single user idea.

REFERENCE FORMAT:
The target format is colorful 3D preschool animation containing recurring characters, animals, vehicles, dancing, walking, jumping, camera movement, environments, songs, lyrics, sound effects, subtitles and transitions.

Do NOT copy any existing video's characters, lyrics, music, scenes, assets or copyrighted content. The system must generate original content.

IMPORTANT HARDWARE:
The primary machine is an Apple Silicon Mac mini M4 with 16 GB unified memory.

The architecture must therefore be memory-efficient and process heavy AI/video tasks sequentially instead of running all heavy models simultaneously.

CORE REQUIREMENT:
The complete application must work locally and must not require a paid AI API.

Paid providers may be supported as optional adapters, but they must NEVER be mandatory for the core pipeline.

==================================================

1. TECHNOLOGY STACK
   ==================================================

Frontend:

* Next.js
* TypeScript
* Tailwind CSS
* clean responsive dashboard

Backend:

* Python
* FastAPI
* Pydantic
* background job system

Database:

* SQLite for initial local deployment
* design repository layer so PostgreSQL can be added later

Automation:

* n8n

AI Gateway:

* OmniRoute
* configurable OpenAI-compatible API endpoint

3D:

* Blender
* Blender Python automation
* reusable character/environment/animation asset library

Generative Media:

* ComfyUI
* local API integration
* workflows stored in the project

TTS:

* Kokoro local TTS
* provider interface so another TTS engine can be added later

Video:

* FFmpeg

Subtitles:

* SRT/VTT generation

YouTube:

* YouTube Data API
* initial upload mode must be PRIVATE

==================================================
2. PROJECT STRUCTURE
====================

Create:

youtube-ai-studio/

frontend/
backend/
ai/
blender/
comfyui/
audio/
renderer/
projects/
n8n/
scripts/
config/
logs/

start.sh
stop.sh
.env.example
README.md

Each module must have clean separation of responsibilities.

==================================================
3. WEB DASHBOARD
================

Create the following pages:

Dashboard
Projects
Create Video
Project Details
Scene Editor
Character Library
Asset Library
Audio
Render
Approval
Settings
Logs

Create Video form:

* Topic / Idea
* Title
* Language
* Duration
* Video Type
* Visual Style
* Target Age
* Character Style
* Music Style
* Voice Style

Default:

Language = English
Duration = 5–7 minutes
Video Type = Nursery Rhyme
Style = 3D Cartoon
Target Age = Kids

==================================================
4. VIDEO CREATION PIPELINE
==========================

When user clicks CREATE VIDEO:

1. Create project
2. Generate AI content plan
3. Generate lyrics
4. Generate song structure
5. Generate character bible
6. Generate environments
7. Generate scene list
8. Generate shot list
9. Validate JSON
10. Generate assets
11. Generate audio
12. Generate animations
13. Render scenes
14. Generate subtitles
15. Add music
16. Add sound effects
17. Compose final video
18. Generate thumbnail
19. Generate SEO metadata
20. Run quality checks
21. Mark project READY FOR APPROVAL

==================================================
5. AI JSON SCHEMA
=================

AI must NEVER return uncontrolled free-form output to the backend.

Use strict Pydantic schemas.

Example:

{
"project": {},
"characters": [],
"environments": [],
"lyrics": {},
"scenes": [],
"audio": {},
"render": {},
"youtube": {}
}

If AI produces invalid JSON:

AI output
→ JSON parser
→ validation
→ automatic repair
→ validation again

Do not continue until valid.

==================================================
6. CHARACTER BIBLE
==================

Every project must have a character bible.

Each character must have:

id
name
type
appearance
colors
clothing
personality
age
voice
animation_set
reference_images

Characters must remain consistent throughout the project.

==================================================
7. SCENE SYSTEM
===============

Each scene must contain:

scene_id
duration
environment
characters
actions
camera
lighting
dialogue
lyrics
music
sound_effects
transition

Example:

{
"scene_id": 12,
"duration": 7,
"environment": "forest",
"characters": ["toto", "cow"],
"actions": [
"train moves forward",
"cow waves",
"children clap"
],
"camera": {
"type": "tracking",
"movement": "forward"
}
}

==================================================
8. BLENDER AUTOMATION
=====================

Create reusable Blender Python scripts.

Required functions:

load_project()
load_character()
load_environment()
apply_animation()
configure_camera()
configure_lighting()
render_scene()
render_animation()
export_scene()

Blender must run headless when possible.

Do not require manual Blender interaction for normal video generation.

==================================================
9. ANIMATION LIBRARY
====================

Create reusable animation types:

walk
run
jump
dance
wave
clap
sit
stand
look_left
look_right
nod
shake_head
point
drive
fly
bounce
spin

The AI scene planner must select from available animations.

Do not generate arbitrary animation names that do not exist.

==================================================
10. COMFYUI
===========

Integrate ComfyUI through its local API.

Create workflow templates for:

character reference
background
thumbnail
special hero shot
optional video shot

Store workflow JSON files in:

comfyui/workflows/

ComfyUI must remain optional.

The core pipeline must still work if ComfyUI is unavailable.

==================================================
11. AUDIO
=========

Create provider abstraction:

AudioProvider
├── TTSProvider
├── MusicProvider
├── SingingProvider
└── SFXProvider

Kokoro should be the default local TTS provider.

Normal narration and singing must be treated as separate capabilities.

Do not pretend normal TTS is singing.

If a local singing provider is unavailable, the system must gracefully fall back to the configured music/voice pipeline instead of crashing.

==================================================
12. MUSIC
=========

Generate original music.

Music must never use copyrighted commercial songs.

Store:

music.wav
vocals.wav
mixed.wav

Music must match:

intro
verse
chorus
verse
chorus
bridge
final chorus

==================================================
13. SUBTITLES
=============

Generate synchronized SRT.

Example:

00:00:04,000 --> 00:00:07,000
Choo choo, here we go!

Use lyric timing data whenever available.

==================================================
14. VIDEO RENDERING
===================

Do NOT attempt to generate one continuous 5–7 minute AI video.

Break the video into approximately 30–50 shots.

Each shot should normally be 3–10 seconds.

Render:

scene_001.mp4
scene_002.mp4
...

Then use FFmpeg to compose:

video
+
music
+
vocals
+
SFX
+
subtitles
+
transitions
+
intro
+
outro

into:

final.mp4

==================================================
15. QUALITY CONTROL
===================

Before project becomes READY:

Check:

* final file exists
* video duration
* resolution
* FPS
* video codec
* audio codec
* audio exists
* subtitles exist
* all scenes rendered
* no missing scene files
* thumbnail exists
* title exists
* description exists
* SEO metadata exists

If a scene fails, retry only that scene.

Never restart the entire project unnecessarily.

==================================================
16. JOB SYSTEM
==============

Implement persistent jobs.

Statuses:

DRAFT
PLANNING
ASSET_GENERATION
AUDIO_GENERATION
ANIMATION
RENDERING
COMPOSITING
QUALITY_CHECK
READY
APPROVED
UPLOADING
COMPLETED
FAILED

Store:

job_id
project_id
status
current_step
progress
error
created_at
updated_at

==================================================
17. RESUME SUPPORT
==================

If generation stops at scene 20:

Scenes 1–19 must remain valid.

Restart should continue from scene 20.

Do not regenerate completed work.

==================================================
18. REGENERATION
================

Allow:

Regenerate entire project
Regenerate lyrics
Regenerate character
Regenerate environment
Regenerate scene
Regenerate audio
Regenerate music
Regenerate thumbnail
Regenerate subtitles

==================================================
19. APPROVAL SYSTEM
===================

When project is ready:

Show:

Video Preview
Title
Description
Tags
Thumbnail
Duration
Scene count
Audio status
Subtitle status
Quality status

Buttons:

EDIT
REGENERATE
APPROVE
DELETE

Do not automatically publish.

==================================================
20. YOUTUBE
===========

After APPROVE:

Upload through YouTube Data API.

Default:

privacyStatus = private

Support later:

private
unlisted
public
scheduled

Keep YouTube credentials outside source code.

==================================================
21. SEO
=======

Generate:

title
description
tags
keywords
hashtags
thumbnail prompt

All metadata must be editable before upload.

==================================================
22. LOGGING
===========

Create:

logs/app.log
logs/ai.log
logs/blender.log
logs/comfyui.log
logs/ffmpeg.log

Show errors in the dashboard.

==================================================
23. HARDWARE MANAGEMENT
=======================

The machine has 16 GB unified memory.

Implement sequential processing.

Do not unnecessarily run:

LLM
ComfyUI
Blender
FFmpeg

at full load simultaneously.

After each heavy stage:

* release resources
* close subprocesses
* continue next stage

==================================================
24. SERVICE HEALTH CHECK
========================

The backend must expose:

GET /health

Check:

backend
OmniRoute
n8n
ComfyUI
TTS
FFmpeg
Blender

Dashboard should show:

✓ Connected
✗ Offline

==================================================
25. START SCRIPT
================

Create:

./start.sh

It must:

1. validate dependencies
2. create required directories
3. start OmniRoute if not running
4. start n8n
5. start backend
6. start frontend
7. start ComfyUI if enabled
8. start TTS service
9. print all URLs
10. perform health checks

Expected:

OmniRoute : 20128
n8n       : 5678
Backend   : 8000
Frontend  : 3000
ComfyUI   : 8188
TTS       : configurable

==================================================
26. STOP SCRIPT
===============

Create:

./stop.sh

It must gracefully stop project services.

==================================================
27. ENVIRONMENT
===============

Create .env.example:

APP_ENV=local

BACKEND_PORT=8000
FRONTEND_PORT=3000

OMNIROUTE_URL=http://localhost:20128
N8N_URL=http://localhost:5678
COMFYUI_URL=http://localhost:8188

PROJECT_DIR=./projects

DEFAULT_LANGUAGE=en
DEFAULT_DURATION_MIN=5
DEFAULT_DURATION_MAX=7

Never hardcode API keys.

==================================================
28. SECURITY
============

Never expose:

API keys
OAuth tokens
YouTube credentials
private configuration

to the frontend.

Use backend environment variables.

==================================================
29. N8N
=======

Create workflows for:

New Project
AI Planning
Asset Generation
Audio Generation
Rendering
Quality Check
Approval Notification
YouTube Upload

n8n should orchestrate jobs.

Heavy rendering must remain in backend workers.

==================================================
30. UI REQUIREMENTS
===================

The UI must be production-quality.

Use:

sidebar
dashboard cards
progress bars
job status
video preview
scene timeline
logs
error panels
approval controls

Avoid placeholder UI.

Every visible button must either work or be clearly marked as not configured.

==================================================
31. TESTING
===========

Create automated tests for:

AI JSON validation
project creation
scene creation
job creation
job retry
file generation
subtitle generation
FFmpeg composition
health checks
YouTube metadata
YouTube upload adapter

Also create an end-to-end test:

Idea
→ AI plan
→ 2 test scenes
→ audio
→ subtitles
→ FFmpeg
→ test MP4

The test must use a short 20–30 second project before attempting a full 5–7 minute render.

==================================================
32. DEVELOPMENT ORDER
=====================

Build in this exact order:

PHASE 1:
Project scaffold

PHASE 2:
Database

PHASE 3:
FastAPI backend

PHASE 4:
Frontend dashboard

PHASE 5:
AI planner

PHASE 6:
JSON validation

PHASE 7:
Character system

PHASE 8:
Scene system

PHASE 9:
Blender renderer

PHASE 10:
Kokoro TTS

PHASE 11:
Subtitle system

PHASE 12:
FFmpeg compositor

PHASE 13:
Thumbnail

PHASE 14:
ComfyUI

PHASE 15:
n8n

PHASE 16:
Approval system

PHASE 17:
YouTube API

PHASE 18:
Full end-to-end pipeline

==================================================
33. IMPORTANT DEVELOPMENT RULE
==============================

Do NOT create a fake demo.

Do NOT create buttons that only show alerts.

Do NOT use mock data for the actual pipeline once a module is implemented.

Each phase must produce a real working module.

Before moving to the next phase:

1. install dependencies
2. run tests
3. run health checks
4. run the module
5. verify output
6. document the result

==================================================
34. FIRST MVP
=============

The first fully working MVP must do this:

User enters:

"The Little Train Finds Five Animals"

Then:

AI generates original lyrics
→ generates characters
→ generates 5–10 scenes
→ generates scene JSON
→ creates simple 3D Blender scenes
→ applies reusable animations
→ generates local voice
→ creates subtitles
→ renders scenes
→ combines scenes with FFmpeg
→ produces MP4
→ shows video in dashboard.

Do NOT attempt YouTube upload until this local pipeline is completely working.

==================================================
35. FINAL ACCEPTANCE TEST
=========================

The project is considered complete only when:

1. User opens localhost dashboard.
2. User enters only a topic.
3. User clicks CREATE VIDEO.
4. AI creates a complete project plan.
5. Characters are created/reused.
6. Scenes are created.
7. Animation is generated.
8. Audio is generated.
9. Subtitles are generated.
10. Scenes are rendered.
11. FFmpeg creates final MP4.
12. Thumbnail is generated.
13. SEO is generated.
14. Quality checks pass.
15. User can preview the video.
16. User can edit metadata.
17. User can regenerate individual scenes.
18. User can approve.
19. Approved video can upload privately to YouTube.
20. Failed jobs can resume without rebuilding completed work.

Do not claim completion until these acceptance criteria have been tested.

==================================================
36. DOCUMENTATION
=================

Create README.md containing:

* requirements
* installation
* model installation
* environment setup
* OmniRoute setup
* n8n setup
* Blender setup
* ComfyUI setup
* Kokoro setup
* FFmpeg setup
* YouTube OAuth setup
* start command
* stop command
* troubleshooting
* architecture
* testing
* project generation example

==================================================
FINAL COMMANDS
==============

The final user experience should be:

cd ~/youtube-ai-studio

./start.sh

Then open:

http://localhost:3000

The project must be modular, local-first, restartable, testable, and designed for an Apple Silicon M4 Mac with 16 GB unified memory.

Do not replace real functionality with mock implementations.

When a component cannot be fully automated locally, create a clean provider interface and document the limitation rather than silently producing fake output.
