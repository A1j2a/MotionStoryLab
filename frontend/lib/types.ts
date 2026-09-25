export type JobStatus =
  | "DRAFT"
  | "PROCESSING"
  | "TOPIC_DISCOVERY"
  | "TOPIC_SELECTED"
  | "PLANNING"
  | "CONTENT_GENERATING"
  | "CONTENT_APPROVED"
  | "ASSET_GENERATION"
  | "SONG_GENERATING"
  | "SONG_READY"
  | "AUDIO_ANALYZING"
  | "AUDIO_GENERATION"
  | "STORYBOARD_GENERATING"
  | "STORYBOARD_READY"
  | "SCENE_GENERATING"
  | "SCENE_RENDERING"
  | "ANIMATION"
  | "RENDERING"
  | "ASSEMBLING"
  | "COMPOSITING"
  | "QC"
  | "QUALITY_CHECK"
  | "READY_FOR_REVIEW"
  | "READY"
  | "APPROVED"
  | "UPLOADING"
  | "COMPLETED"
  | "FAILED"
  | (string & {});

export interface TopicOpportunity {
  topic: string;
  title?: string;
  suggested_title: string;
  category: string;
  target_age: string;
  duration?: string;
  search_keywords: string[];
  content_angle: string;
  why_worth_considering: string;
  opportunity_signals: string;
  suggested_characters: string[];
  story_concept?: string;
  suggested_story_concept: string;
  seo_tags?: string[];
}

export interface CharacterProfile {
  character_id?: string;
  id?: string;
  name: string;
  species?: string;
  type?: string;
  age?: string;
  gender?: string;
  appearance: string;
  colors?: string[];
  clothing?: string;
  face?: string;
  personality?: string;
  voice?: string;
  animation_set?: string[];
}

export interface EnvironmentProfile {
  id: string;
  name: string;
  description: string;
}

export interface VisualBible {
  visual_style: string;
  render_style: string;
  lighting_style: string;
  camera_style: string;
  environment_style: string;
}

export interface ContentPackage {
  title: string;
  description: string;
  chapters: Array<{ time: string; title: string }>;
  hashtags: string[];
  tags: string[];
  story_concept: string;
  lyrics_full: string;
  approved_lyrics: string;
  verses?: Array<{ section: string; lines: string[]; character?: string; action?: string }>;
  characters: CharacterProfile[];
  environments: EnvironmentProfile[];
  music_style: string;
  voice_style: string;
  thumbnail_prompt: string;
  target_audience: string;
  educational_angle?: string;
  visual_bible?: VisualBible;
}

export interface AudioSection {
  type: string;
  name: string;
  start: number;
  end: number;
  bpm?: number;
  lines?: string[];
}

export interface LyricTimestamp {
  line: string;
  section: string;
  start: number;
  end: number;
}

export interface AudioTimeline {
  audio_file?: string;
  duration: number;
  bpm: number;
  total_beats: number;
  sections: AudioSection[];
  lyrics_timestamps: LyricTimestamp[];
  cues?: Array<{ time: number; type: string; action: string }>;
}

export interface StrictScene {
  id?: string;
  scene_id: string;
  scene_number: number;
  start_time: number;
  duration: number;
  end_time: number;
  lyrics?: string;
  video_prompt?: string;
  characters: any[];
  environment: any;
  actions: string[];
  camera?: any;
  emotion?: string;
  lighting?: any;
  animation?: string[];
  transition?: string;
  status: string;
  render_path?: string | null;
  error?: string | null;
}

export interface QCResult {
  status: "passed" | "warning" | "failed";
  checks: {
    video: boolean;
    audio: boolean;
    scenes: boolean;
    lyrics: boolean;
    characters: boolean;
    subtitles: boolean;
  };
  metrics: {
    video_duration: number;
    audio_duration: number;
    duration_delta: number;
    video_resolution: string;
    video_fps: number;
    audio_sample_rate: number;
    total_scenes: number;
    rendered_scenes: number;
    failed_scenes: number;
    lyrics_word_count: number;
    character_count: number;
    subtitles_generated: boolean;
  };
  details?: any[];
  errors: string[];
  warnings: string[];
}

export interface Project {
  id: string;
  title: string;
  topic: string;
  status: JobStatus;
  target_duration?: number;
  duration_min?: number;
  duration_max?: number;
  music_style?: string | null;
  voice_style?: string | null;
  video_type: string;
  visual_style: string;
  target_age: string;
  duration?: string;
  language: string;
  metadata_json?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  jobs?: Job[];
  scenes?: Scene[];
  characters?: Character[];
  assets?: Asset[];
}

export interface Job {
  id: string;
  project_id: string;
  type: string;
  status: JobStatus;
  progress: number;
  stage: string;
  current_step: string;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Character {
  id: string;
  project_id: string;
  name: string;
  type?: string | null;
  species?: string | null;
  appearance?: string | null;
  clothing?: string | null;
  colors?: string[] | null;
  description?: string | null;
  personality?: string | null;
  age?: string | null;
  voice?: string | null;
  animation_set?: string[] | null;
  reference_images?: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface Scene {
  id: string;
  project_id: string;
  scene_number: number;
  duration: number;
  environment: string;
  characters?: any;
  actions?: string[];
  camera?: Record<string, any> | null;
  lighting?: Record<string, any> | null;
  dialogue?: string | null;
  lyrics?: string | null;
  video_prompt?: string | null;
  music?: string | null;
  sound_effects?: string[];
  transition?: string | null;
  status: string;
  render_path?: string | null;
  error?: string | null;
  provider?: string | null;
  start_frame?: string | null;
  end_frame?: string | null;
  video_url?: string | null;
  // Manual external generation workflow
  prompt_status?: string | null;  // NOT_COPIED | PROMPT_COPIED | VIDEO_UPLOADED | ORDER_CONFIRMED | FAILED
  prompt_copied_at?: string | null;
  uploaded_file?: string | null;
  uploaded_duration?: number | null;
  scene_order?: number | null;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  project_id: string;
  asset_type: string;
  file_path: string;
  status: string;
  metadata_json?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_projects: number;
  projects_by_status: Record<string, number>;
  active_jobs: number;
  total_scenes: number;
  completed_scenes: number;
  storage_used_bytes: number;
  storage_used_mb: number;
}

export interface ServiceStatus {
  status: "connected" | "offline";
  url?: string;
  port?: number;
  path?: string | null;
}

export interface HealthData {
  status: string;
  backend: ServiceStatus;
  ollama: ServiceStatus;
  n8n: ServiceStatus;
  comfyui: ServiceStatus;
  tts: ServiceStatus;
  ffmpeg: ServiceStatus;
}

export interface SeoData {
  title: string;
  titles: string[];
  description: string;
  hashtags: string[];
  tags: string;
  tags_list: string[];
  chapters: Array<{ time: string; title: string }>;
  chapters_formatted: string;
}

export interface AIModelOption {
  id: string;
  name: string;
  is_free: boolean;
}

export interface AISettings {
  openrouter_enabled: boolean;
  openrouter_api_key: string;
  openrouter_api_key_masked: string;
  openrouter_model: string;
  active_provider: string;
  available_models: AIModelOption[];

  // Video Settings
  video_provider?: string;
  use_wan_video?: boolean;
  available_video_providers?: { id: string; name: string; recommended?: boolean }[];
  fal_key_configured?: boolean;
  fal_key_masked?: string;
  wan_model?: string;
  wan_resolution?: string;
  wan_test_mode?: boolean;
  video_aspect_ratio: string;

  // AI Thumbnail & Reference Image Settings
  use_ai_thumbnail?: boolean;
  use_ai_reference_images?: boolean;
  ai_provider_test_mode?: boolean;

  // Thumbnail Settings
  thumbnail_generator_enabled: boolean;
  thumbnail_engine: string;
  thumbnail_model: string;
  thumbnail_aspect_ratio: string;
  available_thumbnail_models: AIModelOption[];

  // Audio & Suno Mode Settings
  auto_song_generation_enabled: boolean;
}

export interface TestVideoResult {
  success: boolean;
  job_id?: string;
  polling_url?: string;
  model: string;
  aspect_ratio: string;
  latency_ms: number;
  message: string;
}

export interface TestThumbnailResult {
  success: boolean;
  model: string;
  aspect_ratio: string;
  message: string;
  file_size: number;
}

export interface TestConnectionResult {
  success: boolean;
  latency_ms: number;
  model: string;
  response: string;
  detail?: string;
}

export interface ServiceToolItem {
  key: string;
  name: string;
  port: number | null;
  running: boolean;
  pid: number | string | null;
  log_file: string;
  description: string;
  can_toggle: boolean;
}

export interface SunoPromptPackage {
  project_id: string;
  title: string;
  topic: string;
  style_prompt: string;
  suno_title: string;
  suno_lyrics: string;
  suno_url: string;
  instructions: string;
}
