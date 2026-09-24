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
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
    cache: "no-store",
  });

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
}

export const api = {
  // Health
  getHealth: () => request<HealthData>("/health"),

  // Dashboard Stats
  getDashboardStats: () => request<DashboardStats>("/api/v1/dashboard/stats"),

  // Step 1: Topics Discovery & Selection
  discoverTopics: (limit = 12) =>
    request<TopicOpportunity[]>(`/api/v1/topics/discover?limit=${limit}`),
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
    }),
  saveContentPackage: (projectId: string, payload: Partial<ContentPackage>) =>
    request<ContentPackage>(`/api/v1/projects/${projectId}/content-package`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  regenerateLyrics: (projectId: string) =>
    request<ContentPackage>(`/api/v1/projects/${projectId}/lyrics/regenerate`, {
      method: "POST",
    }),

  // Step 6 & 7: Song Generation & Audio Timeline
  generateSong: (projectId: string) =>
    request<{ status: string; message: string }>(`/api/v1/projects/${projectId}/song/generate`, {
      method: "POST",
    }),
  getAudioTimeline: (projectId: string) =>
    request<AudioTimeline>(`/api/v1/projects/${projectId}/audio-timeline`),
  getSongAudioUrl: (projectId: string) =>
    `${API_BASE}/api/v1/projects/${projectId}/song`,

  // Step 8, 9, 10, 13: Storyboard, Scene Rendering, and Re-rendering
  generateStoryboard: (projectId: string) =>
    request<any[]>(`/api/v1/projects/${projectId}/storyboard/generate`, {
      method: "POST",
    }),
  validateStoryboard: (projectId: string) =>
    request<{ is_valid: boolean; errors: string[]; total_scenes: number; total_duration: number }>(
      `/api/v1/projects/${projectId}/storyboard/validate`
    ),
  renderScenes: (projectId: string) =>
    request<{ status: string; message: string }>(`/api/v1/projects/${projectId}/render/scenes`, {
      method: "POST",
    }),
  rerenderScene: (projectId: string, sceneId: string) =>
    request<{ status: string; scene_id: string; scene_number: number; message: string }>(
      `/api/v1/projects/${projectId}/scenes/${sceneId}/rerender`,
      { method: "POST" }
    ),

  // Step 8 QC
  runQC: (projectId: string) =>
    request<QCResult>(`/api/v1/projects/${projectId}/qc/run`, {
      method: "POST",
    }),
  getQC: (projectId: string) =>
    request<QCResult>(`/api/v1/projects/${projectId}/qc`),

  // Step 10 YouTube Private Upload
  uploadYouTube: (projectId: string, privacyStatus = "private") =>
    request<{ status: string; video_id?: string; video_url?: string; message: string }>(
      `/api/v1/projects/${projectId}/youtube/upload`,
      {
        method: "POST",
        body: JSON.stringify({ privacy_status: privacyStatus }),
      }
    ),

  // Projects CRUD
  getProjects: (status?: string) => {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    return request<Project[]>(`/api/v1/projects/${query}`);
  },
  getProject: (id: string) => request<Project>(`/api/v1/projects/${id}`),
  createProject: (data: Partial<Project>) =>
    request<Project>("/api/v1/projects/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateProject: (id: string, data: Partial<Project>) =>
    request<Project>(`/api/v1/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  deleteProject: (id: string) =>
    request<void>(`/api/v1/projects/${id}`, {
      method: "DELETE",
    }),
  generateProject: (id: string) =>
    request<{ status: string; message: string }>(`/api/v1/projects/${id}/generate`, {
      method: "POST",
    }),
  getProjectSeo: (id: string) =>
    request<import("./types").SeoData>(`/api/v1/projects/${id}/seo`),
  regenerateProjectSeo: (id: string) =>
    request<import("./types").SeoData>(`/api/v1/projects/${id}/seo`, {
      method: "POST",
    }),

  // Jobs
  getJobs: (projectId: string) =>
    request<Job[]>(`/api/v1/jobs/project/${projectId}`),
  getJob: (jobId: string) => request<Job>(`/api/v1/jobs/${jobId}`),
  updateJob: (jobId: string, data: Partial<Job>) =>
    request<Job>(`/api/v1/jobs/${jobId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  retryJob: (jobId: string) =>
    request<Job>(`/api/v1/jobs/${jobId}/retry`, {
      method: "POST",
    }),

  // Scenes
  getScenes: (projectId: string) =>
    request<Scene[]>(`/api/v1/scenes/project/${projectId}`),
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
  getLogs: () => request<{ logs: Array<{ filename: string; exists: boolean; size_bytes: number }> }>("/api/v1/logs/"),
  getLogFile: (filename: string, lines = 100) =>
    request<{ filename: string; total_lines: number; lines: string[]; message?: string }>(
      `/api/v1/logs/${filename}?lines=${lines}`
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
    }>("/api/v1/storage/status"),
  clearStorage: (purgeAll = false) =>
    request<{ cleared: boolean; cleaned_bytes: number; cleaned_formatted: string; message: string }>(
      `/api/v1/storage/clear?purge_all=${purgeAll}`,
      { method: "POST" }
    ),
};
