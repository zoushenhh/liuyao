import type { AISettings, CastResponse } from '../types';
import { DEFAULT_SETTINGS } from '../types';

const SETTINGS_KEY = 'liuyao_ai_settings';
const CAST_KEY = 'liuyao_last_cast';

export function loadSettings(): AISettings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch { /* ignore */ }
  return { ...DEFAULT_SETTINGS };
}

export function saveSettings(settings: AISettings): void {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch { /* ignore */ }
}

export function saveLastCast(cast: CastResponse): void {
  try {
    sessionStorage.setItem(CAST_KEY, JSON.stringify(cast));
  } catch { /* ignore */ }
}

export function loadLastCast(): CastResponse | null {
  try {
    const raw = sessionStorage.getItem(CAST_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return null;
}
