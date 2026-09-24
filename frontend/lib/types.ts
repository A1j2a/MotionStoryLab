export type JobStatus =
  | "DRAFT"
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
  | "FAILED";

export interface TopicOpportunity {
  topic: string;
  title?: string;
  suggested_title: string;
  category: string;
  target_age: string;
  search_keywords: string[];
  content_angle: string;
  why_worth_considering: string;
  opportunity_signals: string;
  suggested_characters: string[];
  story_concept?: string;
  suggested_story_concept: string;
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
  details: string[];
  timestamp?: string;
}

export interface Project {
  id: string;
  title: string;
  topic: string;
  language: string;
  duration_min: number;
  duration_max: number;
  video_type: string;
  visual_style: string;
  target_age: string;
  character_style?: string | null;
  music_style?: string | null;
  voice_style?: string | null;
  status: string;
  lyrics_text?: string | null;
  metadata_json?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  characters?: Character[];
  scenes?: Scene[];
  jobs?: Job[];
  assets?: Asset[];
}

export interface Job {
  id: string;
  project_id: string;
  status: JobStatus;
  current_step: string;
  progress: number;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Character {
  id: string;
  project_id: string;
  name: string;
  type: string;
  appearance: string;
  colors?: string[] | null;
  clothing?: string | null;
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
  characters?: string[];
  actions?: string[];
  camera?: Record<string, any> | null;
  lighting?: Record<string, any> | null;
  dialogue?: string | null;
  lyrics?: string | null;
  music?: string | null;
  sound_effects?: string[];
  transition?: string | null;
  status: string;
  render_path?: string | null;
  error?: string | null;
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
