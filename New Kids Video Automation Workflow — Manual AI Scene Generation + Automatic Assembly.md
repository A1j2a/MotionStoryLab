We are changing the video-generation workflow of the EXISTING project.

IMPORTANT:

You already know the existing project structure and architecture.

DO NOT assume a new project structure.

DO NOT rebuild the application.

DO NOT rewrite the existing project.

First inspect the existing implementation and then integrate this new workflow into the existing architecture, components, services, database patterns, routes, APIs, UI components, styling system, and storage system.

The goal is to create a new end-to-end workflow for producing kids rhyme YouTube videos where AI video scenes are generated MANUALLY outside this application, while this application manages:

- topic
- SEO metadata
- song
- SRT
- scene planning
- scene prompts
- scene copy tracking
- generated scene tracking
- generated scene upload
- automatic scene ordering
- audio/song
- subtitle/SRT
- final video assembly

There will be NO AI video-generation API integration in this workflow.

==================================================
1. CORE CONCEPT
==================================================

The application should NOT generate AI videos itself.

Instead:

Application generates the scene prompts.

User copies each scene prompt.

User generates the video manually using Google Flow or another external AI video generator.

User uploads the generated scene videos back into this application.

Application automatically organizes the uploaded scenes according to the planned scene sequence.

Then application creates the final video using:

- uploaded scene videos
- original song/audio
- original SRT lyrics
- scene timing
- FFmpeg or the existing video-processing system

==================================================
2. COMPLETE WORKFLOW
==================================================

The new workflow must be:

STEP 1:
User selects a topic.

STEP 2:
Generate SEO content.

STEP 3:
Generate/select song.

STEP 4:
Generate SRT.

STEP 5:
Generate scene plan based on the song/SRT.

STEP 6:
Show all scene prompts.

STEP 7:
User copies scenes one by one.

STEP 8:
After copying a scene, visually mark that scene as copied.

STEP 9:
Display total copied/generated count.

STEP 10:
After the user has generated the scenes externally, show scene-video upload interface.

STEP 11:
User uploads generated scene videos.

STEP 12:
System identifies/organizes uploaded videos into the correct scene sequence.

STEP 13:
Show ordered scene list with uploaded video status.

STEP 14:
User confirms the sequence.

STEP 15:
System combines:

Scene videos
+
song/audio
+
SRT lyrics

STEP 16:
Generate final complete video.

==================================================
3. DO NOT BREAK EXISTING PROJECT
==================================================

This is mandatory.

Do not remove or break existing:

- authentication
- existing dashboard
- existing projects
- existing topic functionality
- existing AI integrations
- existing song generation
- existing SRT generation
- existing storage
- existing FFmpeg/video processing
- existing settings
- existing APIs
- existing database structure

Reuse existing functionality wherever possible.

If a current feature already performs part of this workflow, extend it instead of creating duplicate functionality.

==================================================
4. TOPIC STEP
==================================================

When user selects/enters a topic, the first stage should generate SEO metadata.

Required outputs:

1. YouTube Title
2. YouTube Description
3. YouTube Tags
4. YouTube Caption

Each output must have its own copy button.

Example:

TITLE
[ generated title ]

[ COPY ]

DESCRIPTION
[ generated description ]

[ COPY ]

TAGS
[ tag1, tag2, tag3... ]

[ COPY ]

CAPTION
[ generated caption ]

[ COPY ]

==================================================
5. COPY BUTTON BEHAVIOR
==================================================

Every copyable content item must have a single-click copy button.

After clicking:

COPY

change temporarily to:

COPIED ✓

Do not require opening a modal.

Do not copy additional formatting unless appropriate.

The copied content must be clean/plain text.

==================================================
6. SONG STEP
==================================================

After SEO content, show the song-generation stage.

The song must remain associated with the selected topic/project.

The song stage should support the existing song-generation functionality.

If the project already has song/audio generation:

reuse it.

Do not create duplicate audio-generation systems.

The song becomes the source for scene planning.

==================================================
7. SRT / LYRICS
==================================================

The SRT must remain the authoritative timing source.

The application should use:

SRT start time
SRT end time
SRT lyric

to plan the scenes.

Do NOT modify the original SRT timing automatically.

Do NOT change lyric text unless the user explicitly requests it.

==================================================
8. SCENE GENERATION
==================================================

Generate scenes according to the existing scene-duration setting.

Example:

8-second scene duration.

If the project already has a scene-duration setting:

reuse it.

Do not hardcode 8 seconds if the existing application already supports configurable duration.

Each scene must contain:

Scene Number
Start Time
End Time
Duration
Lyrics
Scene Description
Video Generation Prompt
Continuity Instructions
Character Instructions
Environment Instructions
Camera Instructions
Style Instructions
Negative Prompt

==================================================
9. SCENE PROMPTS MUST BE READY TO COPY
==================================================

Every scene must have a dedicated prompt block.

Example:

SCENE 01

Time:
00:00 - 00:08

Lyrics:
"Brush, brush, brush your teeth..."

Prompt:
[complete generation prompt]

[ COPY SCENE ]

The user should be able to copy the COMPLETE prompt with one click.

==================================================
10. SCENE COPY TRACKING
==================================================

Every scene starts as:

Not Generated

When the user clicks:

COPY SCENE

the system should mark that scene as:

Generated / Copied

Use a GREEN DOT or GREEN CHECK indicator.

Example:

● Scene 01 — Copied
● Scene 02 — Copied
○ Scene 03 — Not Copied

The green indicator must be visually obvious.

IMPORTANT:

This does NOT mean the actual AI video has been generated.

It means:

"User has copied the scene prompt and can now generate it externally."

Use wording that avoids falsely claiming the video exists.

Recommended status:

Prompt Copied

not:

Video Generated

==================================================
11. SCENE COUNTER
==================================================

At the top of the scene section show:

Scenes: 12
Prompt Copied: 7 / 12

When another scene is copied:

7 / 12

becomes:

8 / 12

When all are copied:

12 / 12

Optionally show:

All scene prompts copied ✓

Do not mark video generation complete at this stage.

==================================================
12. SCENE STATUS MODEL
==================================================

Use clear states:

NOT_COPIED

PROMPT_COPIED

VIDEO_UPLOADED

ORDER_CONFIRMED

FAILED

Do not confuse these states.

Example:

Scene 01
✓ Prompt Copied
✓ Video Uploaded
✓ Ordered

Scene 02
✓ Prompt Copied
○ Video Pending

==================================================
13. CONTINUITY PROMPTS
==================================================

The scene generator must follow the existing continuity requirements.

Each scene should explicitly describe continuity from the previous scene.

For example:

Scene 01 ending:
Teddy standing beside the bed.

Scene 02 starting:
Start with the SAME teddy in the SAME bedroom, in the SAME position and visual state as the final moment of Scene 01.

The prompt must preserve:

- character identity
- clothing
- colors
- environment
- props
- lighting
- visual style
- camera relationship
- action continuity

Do not introduce random characters.

Do not change the teddy into a human.

==================================================
14. EXTERNAL VIDEO GENERATION
==================================================

The user will generate videos externally.

Example:

Google Flow.

The application must NOT call Google Flow.

The application must NOT require a video-generation API key.

The application only creates the prompt.

==================================================
15. SCENE VIDEO UPLOAD
==================================================

After the scene prompt workflow is complete, show:

UPLOAD GENERATED SCENES

Allow multiple video files to be uploaded.

Supported formats should follow the existing project capabilities.

Prefer:

MP4
MOV
WEBM

if the existing processing pipeline supports them.

Do not add unsupported formats without verifying FFmpeg compatibility.

==================================================
16. UPLOAD UI
==================================================

Show:

Upload Generated Scenes

Drag & Drop
or
Browse Files

After selecting files:

Show upload progress.

Example:

scene_01.mp4     ✓ Uploaded
scene_02.mp4     ✓ Uploaded
scene_03.mp4     Uploading 65%
scene_04.mp4     Waiting

Do not reload the entire page unnecessarily.

==================================================
17. SCENE IDENTIFICATION
==================================================

The system must determine which uploaded video belongs to which planned scene.

Use this priority order:

PRIORITY 1:
Explicit scene number in filename.

Examples:

scene_01.mp4
scene_1.mp4
Scene-01.mp4
scene01.mp4

Map automatically to Scene 01.

PRIORITY 2:
Existing upload metadata if available.

PRIORITY 3:
If filename does not contain a scene number, allow the user to manually assign the scene.

PRIORITY 4:
Only if an existing AI/video-analysis capability is already available in the project, optionally use visual/semantic matching as an assistive method.

DO NOT rely exclusively on AI to determine scene order.

Deterministic filename mapping should always take priority.

==================================================
18. RANDOM FILE NAMES
==================================================

Users may upload files with random names.

Example:

video_839472.mp4

In this case:

Do NOT guess silently.

Show:

"Which scene does this video belong to?"

Provide:

[ Scene 01 ]
[ Scene 02 ]
[ Scene 03 ]
...

Allow manual assignment.

Once assigned, store the mapping.

==================================================
19. DUPLICATE SCENE PROTECTION
==================================================

If two files are assigned to the same scene:

Show:

Scene 03 already has a video.

Options:

Replace
Keep Existing
Cancel

Do not silently overwrite.

==================================================
20. UPLOAD VALIDATION
==================================================

After upload, validate:

- file type
- file readability
- video duration
- resolution
- codec compatibility
- file corruption

If the file cannot be processed:

mark:

UPLOAD_FAILED

and show the reason.

==================================================
21. SCENE DURATION VALIDATION
==================================================

Compare uploaded video duration against planned scene duration.

Example:

Expected:
8 seconds

Uploaded:
7.8 seconds

This may be acceptable depending on the existing tolerance.

If the difference is significant:

show warning.

Example:

"Scene 04 expected approximately 8 seconds but uploaded video is 12.4 seconds."

Do NOT automatically destroy/crop the source without user confirmation unless the existing pipeline already defines that behavior.

==================================================
22. ORDERED SCENE VIEW
==================================================

After upload, show:

FINAL SCENE SEQUENCE

01 ✓ Uploaded
02 ✓ Uploaded
03 ✓ Uploaded
04 ✓ Uploaded
05 ○ Missing
06 ✓ Uploaded

Each scene should show:

- scene number
- lyric
- planned duration
- uploaded filename
- uploaded duration
- status

This allows the user to identify missing scenes before final generation.

==================================================
23. MISSING SCENE PROTECTION
==================================================

Do NOT allow final video generation if required scenes are missing.

Show:

"3 scenes are still missing."

List:

Scene 04
Scene 09
Scene 12

Provide upload option.

==================================================
24. MANUAL REORDER
==================================================

The system should automatically order scenes by:

scene number.

Also provide manual drag-and-drop reorder as a safety mechanism.

However:

Default order MUST be:

Scene 01
Scene 02
Scene 03
...

Do not use upload order as the default sequence.

==================================================
25. SEQUENCE CONFIRMATION
==================================================

Before final rendering show:

SCENE SEQUENCE

01 → 02 → 03 → 04 → 05 → ...

Button:

[ CONFIRM SEQUENCE ]

After confirmation:

ORDER_CONFIRMED

Then enable:

[ GENERATE FINAL VIDEO ]

==================================================
26. FINAL VIDEO GENERATION
==================================================

Final video should combine:

Ordered scene videos
+
Song/audio
+
SRT subtitles/lyrics

Use the existing FFmpeg/video-processing system.

Do NOT replace existing FFmpeg functionality.

Do NOT introduce another video-processing library if FFmpeg is already integrated.

==================================================
27. AUDIO
==================================================

Use the song/audio associated with the project.

Do not regenerate audio unnecessarily.

Audio should be synchronized with the SRT timing.

If the existing project already has audio normalization, keep it.

==================================================
28. SRT
==================================================

Use the original SRT as the subtitle source.

Final video must contain the complete lyrics according to the existing subtitle implementation.

Do not change subtitle timing unless explicitly required by the existing video-rendering system.

==================================================
29. SCENE + LYRIC SYNCHRONIZATION
==================================================

The final output should follow:

SRT timing
↓
Scene timing
↓
Audio timing

Example:

00:00–00:08
Scene 01
Lyrics 01

00:08–00:16
Scene 02
Lyrics 02

00:16–00:24
Scene 03
Lyrics 03

and so on.

The final video must preserve synchronization.

==================================================
30. FINAL VIDEO OUTPUT
==================================================

After successful rendering:

Show:

Final Video Ready ✓

Display:

- video preview
- duration
- resolution
- file size
- download/open action according to existing application behavior

Do not remove existing export functionality.

==================================================
31. FINAL VIDEO SHOULD NOT CONTAIN GAPS
==================================================

Before rendering:

Validate that all scene videos can be assembled continuously.

Check:

Scene 01 end
→ Scene 02 start
→ Scene 03 start
→ ...

Avoid unintended:

- black frames
- silence
- gaps
- overlaps
- duplicated frames

Use the existing FFmpeg pipeline.

==================================================
32. PROJECT DATA MODEL
==================================================

Reuse existing project/song/scene tables and models wherever possible.

If additional fields are required, add only minimal fields.

Possible scene status:

NOT_COPIED
PROMPT_COPIED
VIDEO_UPLOADED
ORDER_CONFIRMED
FAILED

Possible fields:

prompt_copied_at
uploaded_at
uploaded_file
uploaded_duration
scene_order
status

Do NOT create duplicate project/song/scene entities if equivalent entities already exist.

==================================================
33. AUTO-SAVE
==================================================

When user clicks:

COPY SCENE

save the copied state.

If the page is refreshed:

the green copied indicator must remain.

If the user leaves and comes back:

the state must remain.

Do not depend only on browser localStorage if the project already has a backend/database.

Use the existing persistence architecture.

==================================================
34. COPY ALL OPTION
==================================================

Optionally provide:

[ COPY ALL SCENE PROMPTS ]

But individual copy buttons are mandatory.

If COPY ALL is implemented:

copy scenes in clean sequential format.

Do not remove individual copy buttons.

==================================================
35. UI DESIGN
==================================================

Do not redesign the whole application.

Use the existing:

- typography
- colors
- cards
- buttons
- spacing
- responsive behavior
- components

The new workflow should visually feel like a natural part of the existing application.

==================================================
36. USER FLOW UI
==================================================

Prefer a step-based workflow if the existing application supports it:

1. Topic
2. SEO
3. Song
4. SRT
5. Scenes
6. Generate Externally
7. Upload Scenes
8. Verify Sequence
9. Final Video

The exact implementation should follow the existing application's UI architecture.

Do not introduce a new frontend framework.

==================================================
37. IMPORTANT: DO NOT AUTO-GENERATE VIDEOS
==================================================

There must be NO video-generation API call.

The application does NOT generate the scene videos.

The application generates:

- prompts
- scene metadata
- continuity instructions

Then user generates videos externally.

==================================================
38. EXTERNAL GENERATION INSTRUCTIONS
==================================================

Each scene should make it obvious to the user:

"Copy this prompt and generate this scene in your external AI video generator."

After copying:

✓ Prompt Copied

Do not say:

✓ Video Generated

because the actual video is generated outside this application.

==================================================
39. FINAL GENERATION REQUIREMENTS
==================================================

Before final video generation verify:

[✓] Topic exists
[✓] SEO metadata exists
[✓] Song exists
[✓] SRT exists
[✓] All required scenes exist
[✓] All scene prompts exist
[✓] All required scene videos uploaded
[✓] Scene sequence confirmed
[✓] Audio available
[✓] SRT available

Only then enable:

GENERATE FINAL VIDEO

==================================================
40. FAILURE HANDLING
==================================================

If final rendering fails:

Do NOT lose:

- uploaded videos
- scene mapping
- copied states
- SRT
- song
- project data

Show the actual error.

Allow:

[ RETRY FINAL VIDEO ]

Do not require the user to upload everything again.

==================================================
41. RESUME WORKFLOW
==================================================

The user may close the browser after generating some scenes.

When returning to the project:

restore:

SEO status
Song status
SRT status
Scene list
Copied scene count
Uploaded scene count
Scene mappings
Missing scenes
Sequence confirmation status

The workflow must be resumable.

==================================================
42. IMPORTANT CONTINUITY REQUIREMENT
==================================================

The scene prompt generator must continue following the existing continuity rules from previous work.

For every scene:

- same character
- same clothes
- same colors
- same environment
- same visual style
- same props when applicable
- logical action continuation
- logical camera continuation
- logical lighting continuation

The prompt should explicitly reference the previous scene's ending state where applicable.

==================================================
43. NO UNNECESSARY AI DEPENDENCY
==================================================

The scene ordering system must NOT require an AI API.

Use deterministic scene numbers and metadata first.

AI-based visual matching is optional only if an existing capability is already available.

Do not add an expensive AI API just for ordering files.

==================================================
44. IMPLEMENTATION PROCESS
==================================================

Before changing code:

1. Inspect the existing project.
2. Identify existing project workflow.
3. Identify existing topic functionality.
4. Identify existing SEO generation.
5. Identify existing song generation.
6. Identify existing SRT generation.
7. Identify existing scene generation.
8. Identify existing video processing.
9. Identify existing upload/storage.
10. Identify existing database models.
11. Identify existing settings.
12. Identify reusable components.

Then provide a short implementation plan.

After that:

Implement the new workflow using existing architecture.

==================================================
45. DO NOT MODIFY UNRELATED CODE
==================================================

Only modify files necessary for this workflow.

Do not refactor unrelated code.

Do not change production configuration unnecessarily.

Do not remove old functionality.

==================================================
46. TESTING
==================================================

Test with a small example first.

Example:

3 scenes.

Scene 01
Scene 02
Scene 03

Test:

1. Generate prompts.
2. Copy Scene 01.
3. Verify green indicator.
4. Copy Scene 02.
5. Verify counter.
6. Copy Scene 03.
7. Verify 3/3.
8. Upload scene_03.mp4 first.
9. Upload scene_01.mp4 second.
10. Upload scene_02.mp4 third.
11. Verify application orders them:

01
02
03

12. Confirm sequence.
13. Generate final video.
14. Verify audio.
15. Verify SRT.
16. Verify scene sequence.
17. Verify final MP4.

==================================================
47. SECOND TEST
==================================================

Upload:

scene_01.mp4
scene_03.mp4

Do NOT upload Scene 02.

The system must show:

Scene 02 — Missing

Final Video button must remain disabled.

==================================================
48. THIRD TEST
==================================================

Upload random filenames:

abc.mp4
xyz.mp4
test.mp4

System must ask for scene assignment instead of guessing.

==================================================
49. FOURTH TEST
==================================================

Refresh the page after copying 5 of 10 scenes.

Expected:

Prompt Copied: 5 / 10

The green indicators must remain.

==================================================
50. FINAL ACCEPTANCE CRITERIA
==================================================

The implementation is complete only when:

✓ Topic can be selected.

✓ SEO title can be generated.

✓ SEO description can be generated.

✓ SEO tags can be generated.

✓ SEO caption can be generated.

✓ Each can be copied individually.

✓ Song workflow works.

✓ SRT workflow works.

✓ Scenes are generated from song/SRT.

✓ Each scene has a complete external AI-video prompt.

✓ Each scene has an individual COPY button.

✓ Clicking COPY changes the scene status to Prompt Copied.

✓ Green indicator appears.

✓ Counter updates correctly.

✓ Copied status persists.

✓ User can generate videos externally.

✓ User can upload generated scene videos.

✓ Scene-number filenames are automatically mapped.

✓ Random filenames can be manually mapped.

✓ Duplicate scene uploads are protected.

✓ Missing scenes are detected.

✓ Uploaded scenes are displayed.

✓ Scene order is automatically determined.

✓ Manual reorder is available.

✓ Sequence can be confirmed.

✓ Final video generation uses ordered scenes.

✓ Existing audio/song is used.

✓ Existing SRT is used.

✓ Lyrics remain synchronized.

✓ Existing FFmpeg/video processing is reused.

✓ Final MP4 is generated.

✓ Existing project functionality remains intact.

✓ No AI video-generation API is required.

✓ No existing workflow is broken.

==================================================
FINAL PRINCIPLE
==================================================

This application is NOT an AI video generator anymore.

It is an:

AI VIDEO PRODUCTION AUTOMATION WORKFLOW

The AI generates the planning and prompts.

The user generates videos externally.

The application manages:

PLAN
→ PROMPT
→ COPY
→ TRACK
→ UPLOAD
→ IDENTIFY
→ ORDER
→ SYNC
→ ASSEMBLE
→ FINAL VIDEO

DO NOT BREAK THE EXISTING PROJECT.

DO NOT REBUILD THE PROJECT.

DO NOT ASSUME A NEW PROJECT STRUCTURE.

USE THE EXISTING PROJECT ARCHITECTURE AND IMPLEMENT THIS WORKFLOW INSIDE IT.