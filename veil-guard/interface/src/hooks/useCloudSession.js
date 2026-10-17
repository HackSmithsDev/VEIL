import { useCallback, useState } from 'react'
import { cloudRequest } from '../api/cloud/client'

export function useCloudSession() {
  const [session, setSession] = useState(null)

  const authenticate = useCallback(async (path, credentials) => {
    const result = await cloudRequest(path, { method: 'POST', body: credentials })
    setSession({ token: result.access_token, user: result.user })
    return result.user
  }, [])

  const login = useCallback(
    (credentials) => authenticate('/auth/login', credentials),
    [authenticate],
  )
  const register = useCallback(
    (details) => authenticate('/auth/register', details),
    [authenticate],
  )
  const logout = useCallback(() => setSession(null), [])

  const request = useCallback(
    (path, options = {}) =>
      cloudRequest(path, {
        ...options,
        token: session?.token,
        onUnauthorized: () => setSession(null),
      }),
    [session?.token],
  )

  const updateUser = useCallback((user) => {
    setSession((current) => (current ? { ...current, user } : current))
  }, [])

  return {
    user: session?.user ?? null,
    isAuthenticated: Boolean(session?.token),
    login,
    register,
    logout,
    request,
    updateUser,
  }
}
