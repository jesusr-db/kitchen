import type { LocationsResponse } from '@/types/location';
import type { TimeRangeResponse } from '@/types/order';

const API_BASE_URL = '/api/v1';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithRetry(
  url: string,
  options?: RequestInit,
  retries = 3
): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      return response;
    } catch (error) {
      if (i === retries - 1) throw error;
      // Exponential backoff
      await new Promise((resolve) => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
  throw new Error('Failed after retries');
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText || response.statusText);
  }
  return response.json();
}

export const api = {
  async fetchLocations(): Promise<LocationsResponse> {
    const response = await fetchWithRetry(`${API_BASE_URL}/locations`);
    return handleResponse<LocationsResponse>(response);
  },

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetchWithRetry('/health');
    return handleResponse(response);
  },

  async fetchTimeRange(
    location: string,
    startTime: Date,
    endTime: Date,
    limit: number = 100
  ): Promise<TimeRangeResponse> {
    const params = new URLSearchParams({
      start: startTime.toISOString(),
      end: endTime.toISOString(),
      limit: limit.toString(),
    });
    const response = await fetchWithRetry(
      `${API_BASE_URL}/locations/${location}/time-range?${params}`
    );
    return handleResponse<TimeRangeResponse>(response);
  },
};
