/**
 * ChristianMind AI - API Client
 * ============================
 * All API calls go to http://localhost:8000
 * Session ID is stored in localStorage
 */

const API_BASE = 'http://localhost:8000';


/**
 * Get or create session ID
 */
export function getSessionId() {
  let sessionId = localStorage.getItem('christianmind_session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('christianmind_session_id', sessionId);
  }
  return sessionId;
}


/**
 * Send a chat message
 */
export async function sendChat(message, denomination = null) {
  const sessionId = getSessionId();

  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      denomination,
    }),
  });

  if (!response.ok) {
    throw new Error(`Chat API error: ${response.status}`);
  }

  return response.json();
}


/**
 * Generate an image
 */
export async function generateImage(prompt) {
  const sessionId = getSessionId();

  const response = await fetch(`${API_BASE}/image`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Image API error: ${response.status}`);
  }

  return response.json();
}


/**
 * Clear session history
 */
export async function clearSession() {
  const sessionId = getSessionId();

  const response = await fetch(`${API_BASE}/chat/session/${sessionId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Clear session error: ${response.status}`);
  }

  return response.json();
}


/**
 * Health check
 */
export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error(`Health check error: ${response.status}`);
  }
  return response.json();
}
