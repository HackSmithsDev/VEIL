function getConfiguredApiBaseUrl() {
  const value = import.meta.env.VITE_API_BASE_URL
  if (!value) {
    throw new Error('VITE_API_BASE_URL must be configured before starting VEIL Guard.')
  }

  let url
  try {
    url = new URL(value)
  } catch (error) {
    throw new Error('VITE_API_BASE_URL must be an absolute HTTP(S) URL.', { cause: error })
  }

  const loopbackHosts = new Set(['localhost', '127.0.0.1', '[::1]'])
  if (
    !['http:', 'https:'].includes(url.protocol)
    || (url.protocol === 'http:' && !loopbackHosts.has(url.hostname))
    || url.username
    || url.password
    || url.search
    || url.hash
  ) {
    throw new Error('VITE_API_BASE_URL must use HTTPS, or HTTP on a loopback host, without credentials or query parameters.')
  }

  return url.toString().replace(/\/+$/, '')
}

const API_BASE_URL = getConfiguredApiBaseUrl()

export async function cloudRequest(path, { token, method = 'GET', body, onUnauthorized } = {}) {
  const headers = new Headers()
  if (body !== undefined) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`Cannot reach VEIL Cloud at ${API_BASE_URL}. Check that the service is running.`, {
        cause: error,
      })
    }
    throw error
  }

  if (response.status === 401 && token) onUnauthorized?.()
  if (response.status === 204) return null

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = payload?.detail
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(' ')
      : detail || `The service returned an error (${response.status}).`
    throw new Error(message)
  }
  if (payload === null) throw new Error('The service returned an unreadable response.')
  return payload
}

export function getApiBaseUrl() {
  return API_BASE_URL
}
