/**
 * Frontend authentication utilities for managing JWT tokens and automatic logout.
 * Handles token storage, expiry checking, and automatic logout after 24 hours.
 */

const TOKEN_KEY = "token";
const TOKEN_EXPIRY_KEY = "token_expiry";
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://vocabulary-app-python-service:8000";

/**
 * Save authentication token and its expiry time to localStorage
 */
export function saveAuthToken(token: string, expiresAt: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiresAt);
}

/**
 * Get the current authentication token
 */
export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Get the token expiry time
 */
export function getTokenExpiry(): Date | null {
  const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY);
  return expiry ? new Date(expiry) : null;
}

/**
 * Check if the current token is expired
 */
export function isTokenExpired(): boolean {
  const expiry = getTokenExpiry();
  if (!expiry) return true;
  
  return new Date() >= expiry;
}

/**
 * Check if token is valid (exists and not expired)
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  return !!token && !isTokenExpired();
}

/**
 * Remove authentication token and expiry from localStorage
 */
export function logout(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
}

/**
 * Verify token with backend and handle automatic logout if expired
 */
export async function verifyToken(): Promise<boolean> {
  const token = getAuthToken();
  
  if (!token || isTokenExpired()) {
    logout();
    return false;
  }

  try {
    const res = await fetch(`${API_BASE_URL}/auth/verify`, {
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      logout();
      return false;
    }

    return true;
  } catch (error) {
    console.error("Token verification failed:", error);
    logout();
    return false;
  }
}

/**
 * Setup automatic logout timer that checks token expiry
 * Call this after successful login or on app initialization
 */
export function setupAutoLogout(onLogout: () => void): NodeJS.Timeout | null {
  const expiry = getTokenExpiry();
  
  if (!expiry) return null;

  const timeUntilExpiry = expiry.getTime() - Date.now();
  
  if (timeUntilExpiry <= 0) {
    // Token already expired
    logout();
    onLogout();
    return null;
  }

  // Set timeout to logout when token expires
  return setTimeout(() => {
    logout();
    onLogout();
  }, timeUntilExpiry);
}
