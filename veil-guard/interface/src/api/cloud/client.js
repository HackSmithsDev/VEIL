const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'https://veil-api.hacksmiths.dev/api/v1'
).replace(/\/+$/, '')

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
