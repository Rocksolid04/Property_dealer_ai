import type {
  Property,
  PropertyResponse,
  AISearchResponse,
} from "./types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function request<T>(
  path: string,
  options: RequestInit = {}
) {
  const r = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    cache: "no-store",
  });

  if (!r.ok) {
    throw new Error(`API ${r.status}`);
  }

  return r.json() as Promise<T>;
}

export async function getProperties(params = "") {
  const data = await request<PropertyResponse>(
    `/properties/${params}`
  );

  return Array.isArray(data) ? data : data.items;
}

export async function getProperty(id: string) {
  return request<Property>(`/properties/${id}`);
}

export async function registerUser(body: {
  name: string;
  email: string;
  password: string;
}) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function loginUser(
  email: string,
  password: string
) {
  const body = new URLSearchParams({
    username: email,
    password,
  });

  const r = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  if (!r.ok) {
    throw new Error(`Login failed: ${r.status}`);
  }

  return r.json();
}

export async function ragSearch(
  query: string
): Promise<AISearchResponse> {
  return request<AISearchResponse>(
    `/properties/ai-search?query=${encodeURIComponent(query)}`
  );
}
