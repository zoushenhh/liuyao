import type {
  CastRequest,
  CastResponse,
  InterpretRequest,
  InterpretResponse,
  ValidateKeyRequest,
  ValidateKeyResponse,
  TextItem,
  TextContent,
} from '../types';

const BASE = import.meta.env.VITE_API_BASE_URL || '';

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      msg = body.detail || msg;
    } catch {
      msg = (await res.text()) || msg;
    }
    throw new Error(msg);
  }
  return res.json();
}

export async function cast(req: CastRequest): Promise<CastResponse> {
  return fetchJSON<CastResponse>('/api/cast', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function interpret(req: InterpretRequest): Promise<InterpretResponse> {
  return fetchJSON<InterpretResponse>('/api/interpret', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function validateApiKey(req: ValidateKeyRequest): Promise<ValidateKeyResponse> {
  return fetchJSON<ValidateKeyResponse>('/api/validate-api-key', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function fetchTexts(): Promise<TextItem[]> {
  const data = await fetchJSON<{ texts: TextItem[] }>('/api/texts');
  return data.texts;
}

export async function fetchText(name: string): Promise<TextContent> {
  return fetchJSON<TextContent>(`/api/texts/${name}`);
}
