import {
  Project,
  Job,
  Character,
  Scene,
  Asset,
  DashboardStats,
  HealthData,
  TopicOpportunity,
  ContentPackage,
  AudioTimeline,
  QCResult,
  AISettings,
  TestConnectionResult,
  SeoData,
  ServiceToolItem,
  SunoPromptPackage,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, options: RequestInit = {}, timeoutMs = 30000): Promise<T> {
  const url = `${API_BASE}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      cache: "no-store",
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errMessage = `HTTP error ${response.status}`;
      try {
        const errData = await response.json();
        errMessage = errData.detail || errMessage;
      } catch {
        // fallback
      }
      throw new Error(errMessage);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") {
      throw new Error("Request timed out. The local engine is busy, please try again.");
    }
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request<HealthData>("/health", {}, 5000),

  // Dashboard Stats
  getDashboardStats: () => request<DashboardStats>("/api/v1/dashboard/stats", {}, 10000),

  // Tool & Daemon Server Management
  getServicesStatus: () => request<{ services: ServiceToolItem[] }>("/api/v1/services/status", {}, 5000),
  startService: (serviceKey: string) =>
    request<{ message: string; running: boolean; pid?: number }>(`/api/v1/services/${serviceKey}/start`, {
      method: "POST",
    }),
  stopService: (serviceKey: string) =>
    request<{ message: string; running: boolean }>(`/api/v1/services/${serviceKey}/stop`, {
      method: "POST",
    }),
  stopUnusedServices: () =>
    request<{ message: string; stopped_count: number; stopped: string[] }>("/api/v1/services/stop-unused", {
      method: "POST",
    }),

  // AI & OpenRouter Settings
  getAISettings: () => request<AISettings>("/api/v1/settings/ai", {}, 5000),
  updateAISettings: (payload: {
    openrouter_enabled: boolean;
    openrouter_api_key?: string;
    openrouter_model?: string;
    video_provider?: string;
    use_wan_video?: boolean;
    fal_key?: string;
    wan_model?: string;
    wan_resolution?: string;
    wan_test_mode?: boolean;
    video_aspect_ratio?: string;
    use_ai_thumbnail?: boolean;
    use_ai_reference_images?: boolean;
    ai_provider_test_mode?: boolean;
    thumbnail_generator_enabled?: boolean;
    thumbnail_engine?: string;
    thumbnail_model?: string;
    thumbnail_aspect_ratio?: string;
    auto_song_generation_enabled?: boolean;
  }) =>
    request<AISettings>("/api/v1/settings/ai", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  testOpenRouterConnection: (payload: { api_key?: string; model?: string }) =>
    request<TestConnectionResult>("/api/v1/settings/ai/test", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Step 1: Topics Discovery & Selection with Filters
  discoverTopics: (options?: number | { limit?: number; target_age?: string; duration?: string; language?: string; seed?: number }) => {
    if (typeof options === "number") {
      return request<TopicOpportunity[]>(`/api/v1/topics/discover?limit=${options}&seed=${Date.now()}`, {}, 90000);
    }
    const params = new URLSearchParams();
    params.set("limit", String(options?.limit || 8));
    if (options?.target_age && options.target_age !== "all") params.set("target_age", options.target_age);
    if (options?.duration) params.set("duration", options.duration);
    if (options?.language) params.set("language", options.language);
    params.set("seed", String(options?.seed || Date.now()));
    return request<TopicOpportunity[]>(`/api/v1/topics/discover?${params.toString()}`, {}, 90000);
  },
  selectTopic: (payload: Partial<TopicOpportunity>) =>
    request<Project>("/api/v1/topics/select", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Step 2 & 4: Content Package & Approved Lyrics
  getContentPackage: (projectId: string) =>
    request<ContentPackage>(`/api/v1/projects/${projectId}/content-package`),
  generateContentPackage: (projectId: string) =>
    request<ContentPackage>(`/api/v1/projects/${projectId}/content-package/generate`, {
      method: "POST",
    }, 90000),
  saveContentPackage: (projectId: string, payload: Partial<ContentPackage>) =>
    request<ContentPackage>(`/api/v1/projects/${projectId}/content-package`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  regenerateLyrics: (projectId: string) =>
    request<ContentPackage>(`/api/v1/projects/${projectId}/lyrics/regenerate`, {
      method: "POST",
    }, 90000),

  // Suno AI & Audio Upload
  getSunoPrompt: (projectId: string) =>
    request<SunoPromptPackage>(`/api/v1/projects/${projectId}/suno-prompt`),
  uploadSongAudio: async (projectId: string, file: File, lyrics?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (lyrics) {
      formData.append("lyrics", lyrics);
    }
    const res = await fetch(`${API_BASE}/api/v1/projects/${projectId}/audio/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Audio upload failed");
    }
    return res.json();
  },
  getSubtitlesDownloadUrl: (projectId: string) =>
    `${API_BASE}/api/v1/projects/${projectId}/subtitles`,

  // Step 6 & 7: Song Generation & Audio Timeline
  generateSong: (projectId: string) =>
    request<{ status: string; message: string }>(`/api/v1/projects/${projectId}/song/generate`, {
      method: "POST",
    }, 90000),
  getAudioTimeline: (projectId: string) =>
    request<AudioTimeline>(`/api/v1/projects/${projectId}/audio-timeline`),
  getSongAudioUrl: (projectId: string) =>
    `${API_BASE}/api/v1/projects/${projectId}/song`,

  // Step 8, 9, 10, 13: Storyboard, Scene Rendering, and Re-rendering
  generateStoryboard: (projectId: string, targetSceneDuration?: number) =>
    request<any[]>(
      `/api/v1/projects/${projectId}/storyboard/generate${targetSceneDuration ? `?target_scene_duration=${targetSceneDuration}` : ""}`,
      {
        method: "POST",
      },
      90000
    ),
  validateStoryboard: (projectId: string) =>
    request<{ is_valid: boolean; errors: string[]; total_scenes: number; total_duration: number }>(
      `/api/v1/projects/${projectId}/storyboard/validate`
    ),
  renderScenes: (projectId: string) =>
    request<any>(`/api/v1/projects/${projectId}/render/scenes`, {
      method: "POST",
    }),
  rerenderSingleScene: (sceneId: string) =>
    request<{ status: string; scene_id: string; render_path: string }>(
      `/api/v1/scenes/${sceneId}/rerender`,
      { method: "POST" }
    ),
  rerenderScene: (sceneId: string, prompt?: string) =>
    request<{ status: string; scene_id: string; render_path: string }>(
      `/api/v1/scenes/${sceneId}/rerender`,
      {
        method: "POST",
        body: prompt ? JSON.stringify({ prompt }) : undefined,
      }
    ),

  // Step 8 Quality Control (QC) Check
  runQCCheck: (projectId: string) =>
    request<QCResult>(`/api/v1/projects/${projectId}/qc/run`, {
      method: "POST",
    }),
  runQC: (projectId: string) =>
    request<QCResult>(`/api/v1/projects/${projectId}/qc/run`, {
      method: "POST",
    }),
  getQCReport: (projectId: string) =>
    request<QCResult>(`/api/v1/projects/${projectId}/qc`),

  // Step 10 Manual YouTube Upload & SEO
  uploadToYoutube: (
    projectId: string,
    payload: string | { privacy_status?: string; category_id?: string; made_for_kids?: boolean }
  ) => {
    const body = typeof payload === "string" ? { privacy_status: payload } : payload;
    return request<{ status: string; video_id?: string; youtube_url?: string; privacy_status: string; message?: string }>(
      `/api/v1/projects/${projectId}/youtube/upload`,
      {
        method: "POST",
        body: JSON.stringify(body),
      }
    );
  },
  uploadYouTube: (
    projectId: string,
    payload: string | { privacy_status?: string; category_id?: string; made_for_kids?: boolean }
  ) => {
    const body = typeof payload === "string" ? { privacy_status: payload } : payload;
    return request<{ status: string; video_id?: string; youtube_url?: string; privacy_status: string; message?: string }>(
      `/api/v1/projects/${projectId}/youtube/upload`,
      {
        method: "POST",
        body: JSON.stringify(body),
      }
    );
  },
  getProjectSeo: (projectId: string) =>
    request<SeoData>(`/api/v1/projects/${projectId}/seo`),
  regenerateProjectSeo: (projectId: string) =>
    request<SeoData>(`/api/v1/projects/${projectId}/seo/regenerate`, {
      method: "POST",
    }),
  generateManualSeo: (projectId: string, topic?: string) =>
    request<{ title: string; description: string; tags: string; caption: string }>(
      `/api/v1/projects/${projectId}/seo/generate`,
      { method: "POST", body: JSON.stringify({ topic }) }
    ),
  getManualSeo: (projectId: string) =>
    request<{ title: string; description: string; tags: string; caption: string }>(
      `/api/v1/projects/${projectId}/seo`
    ),

  // Projects
  getProjects: (params?: any) => {
    const query = params?.status ? `?status=${params.status}` : "";
    return request<Project[]>(`/api/v1/projects/${query}`, {}, 10000);
  },
  getProject: (id: string) => request<Project>(`/api/v1/projects/${id}`, {}, 10000),
  createProject: (data: Partial<Project>) =>
    request<Project>("/api/v1/projects/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  generateProject: (id: string) =>
    request<Job>(`/api/v1/projects/${id}/start`, {
      method: "POST",
    }),
  deleteProject: (id: string) =>
    request<{ message: string }>(`/api/v1/projects/${id}`, {
      method: "DELETE",
    }),
  updateProject: (id: string, data: Partial<Project>) =>
    request<Project>(`/api/v1/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Jobs
  getJobs: (projectId?: string) => {
    const query = projectId ? `?project_id=${projectId}` : "";
    return request<Job[]>(`/api/v1/jobs/${query}`, {}, 5000);
  },
  getJob: (id: string) => request<Job>(`/api/v1/jobs/${id}`, {}, 5000),
  cancelJob: (id: string) =>
    request<Job>(`/api/v1/jobs/${id}/cancel`, {
      method: "POST",
    }),
  retryJob: (id: string) =>
    request<Job>(`/api/v1/jobs/${id}/retry`, {
      method: "POST",
    }),

  // Pipeline Execution
  startPipeline: (projectId: string) =>
    request<Job>(`/api/v1/projects/${projectId}/start`, {
      method: "POST",
    }),

  // Scenes
  getScenes: (projectId: string) =>
    request<Scene[]>(`/api/v1/scenes/project/${projectId}`, {}, 10000),
  getScene: (sceneId: string) => request<Scene>(`/api/v1/scenes/${sceneId}`),
  updateScene: (sceneId: string, data: Partial<Scene>) =>
    request<Scene>(`/api/v1/scenes/${sceneId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  regenerateScene: (sceneId: string) =>
    request<Scene>(`/api/v1/scenes/${sceneId}/regenerate`, {
      method: "POST",
    }),

  // Characters
  getCharacters: (projectId: string) =>
    request<Character[]>(`/api/v1/characters/project/${projectId}`),
  saveCharacters: (projectId: string, chars: Partial<Character>[]) =>
    request<Character[]>(`/api/v1/characters/project/${projectId}`, {
      method: "POST",
      body: JSON.stringify(chars),
    }),

  // Assets
  getAssets: (projectId: string, assetType?: string) => {
    const query = assetType ? `?asset_type=${encodeURIComponent(assetType)}` : "";
    return request<Asset[]>(`/api/v1/assets/project/${projectId}${query}`);
  },
  createAsset: (projectId: string, data: Partial<Asset>) =>
    request<Asset>(`/api/v1/assets/project/${projectId}`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Logs
  getLogs: () => request<{ logs: Array<{ filename: string; exists: boolean; size_bytes: number }> }>("/api/v1/logs/", {}, 5000),
  getLogFile: (filename: string, lines = 150) =>
    request<{ filename: string; total_lines: number; lines: string[]; message?: string }>(
      `/api/v1/logs/${filename}?lines=${lines}`,
      {},
      5000
    ),

  // Storage Management
  getStorageStatus: () =>
    request<{
      status: string;
      total_bytes: number;
      total_formatted: string;
      projects_bytes: number;
      projects_formatted: string;
      logs_bytes: number;
      logs_formatted: string;
      project_count: number;
      project_dir: string;
    }>("/api/v1/storage/status", {}, 5000),
  clearStorage: (purgeAll = false) =>
    request<{ cleared: boolean; cleaned_bytes: number; cleaned_formatted: string; message: string }>(
      `/api/v1/storage/clear?purge_all=${purgeAll}`,
      { method: "POST" }
    ),
  // Thumbnail Generation
  generateThumbnail: (projectId: string, payload?: { aspect_ratio?: string; prompt_override?: string }) =>
    request<{ status: string; thumbnail_url: string; aspect_ratio: string; message: string }>(
      `/api/v1/projects/${projectId}/thumbnail/generate`,
      {
        method: "POST",
        body: JSON.stringify(payload || { aspect_ratio: "16:9" }),
      },
      60000
    ),

  // Thumbnail AI Test
  testThumbnailConnection: (payload: { title?: string; topic?: string; model?: string; aspect_ratio?: string }) =>
    request<any>("/api/v1/settings/thumbnail/test", {
      method: "POST",
      body: JSON.stringify(payload),
    }, 30000),

  // ── Manual External Generation Workflow ──────────────────────────────────

  markSceneCopied: (projectId: string, sceneId: string) =>
    request<{ scene_id: string; scene_number: number; prompt_status: string; prompt_copied_at: string }>(
      `/api/v1/projects/${projectId}/scenes/${sceneId}/mark-copied`,
      { method: "POST" }
    ),

  getCopyStatus: (projectId: string) =>
    request<{
      total_scenes: number;
      copied_count: number;
      uploaded_count: number;
      scenes: Array<{
        scene_id: string;
        scene_number: number;
        prompt_status: string;
        prompt_copied_at: string | null;
        uploaded_file: string | null;
        uploaded_duration: number | null;
        scene_order: number;
        lyrics: string | null;
        duration: number;
      }>;
    }>(`/api/v1/projects/${projectId}/scenes/copy-status`),

  uploadSceneVideo: async (
    projectId: string,
    sceneId: string,
    file: File,
    forceReplace = false
  ) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("force_replace", String(forceReplace));
    const res = await fetch(
      `${API_BASE}/api/v1/projects/${projectId}/scenes/${sceneId}/upload-video`,
      { method: "POST", body: formData }
    );
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  batchUploadScenes: async (projectId: string, files: File[]) => {
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    const res = await fetch(
      `${API_BASE}/api/v1/projects/${projectId}/scenes/batch-upload`,
      { method: "POST", body: formData }
    );
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Batch upload failed" }));
      throw new Error(err.detail || "Batch upload failed");
    }
    return res.json();
  },

  assignUnresolvedVideo: async (
    projectId: string,
    sceneNumber: number,
    tmpPath: string,
    forceReplace = false
  ) => {
    const formData = new FormData();
    formData.append("scene_number", String(sceneNumber));
    formData.append("tmp_path", tmpPath);
    formData.append("force_replace", String(forceReplace));
    const res = await fetch(
      `${API_BASE}/api/v1/projects/${projectId}/scenes/assign-video`,
      { method: "POST", body: formData }
    );
    if (!res.ok) throw new Error("Assignment failed");
    return res.json();
  },

  confirmSceneSequence: (projectId: string, sceneOrder: number[]) =>
    request<{ confirmed: boolean; sequence: number[]; message: string }>(
      `/api/v1/projects/${projectId}/scenes/confirm-sequence`,
      { method: "POST", body: JSON.stringify({ scene_order: sceneOrder }) }
    ),

  checkAssemblyReadiness: (projectId: string) =>
    request<{
      ready: boolean;
      total_scenes: number;
      uploaded_scenes: number;
      missing_scenes: number[];
      audio_available: boolean;
      srt_available: boolean;
      sequence_confirmed: boolean;
    }>(`/api/v1/projects/${projectId}/assembly/readiness`),

  generateFinalVideoFromUploads: (projectId: string) =>
    request<{ status: string; final_video: string; duration: number; message: string }>(
      `/api/v1/projects/${projectId}/assembly/generate-final-video`,
      { method: "POST" },
      600000  // 10 min timeout for large videos
    ),

  getFinalVideoUrl: (projectId: string) =>
    `${API_BASE}/api/v1/projects/${projectId}/assembly/final-video`,
};

