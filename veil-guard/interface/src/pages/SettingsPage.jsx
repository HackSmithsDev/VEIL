import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'

const PREFERENCES_KEY = 'veil-guard.preferences.v1'
const defaultPreferences = {
  ollamaEndpoint: 'http://127.0.0.1:11434',
  preferredModel: '',
}

function readPreferences() {
  try {
    const stored = localStorage.getItem(PREFERENCES_KEY)
    if (!stored) return { values: defaultPreferences, error: '' }

    const parsed = JSON.parse(stored)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error('Saved settings have an invalid format.')
    }

    return {
      values: {
        ollamaEndpoint: typeof parsed.ollamaEndpoint === 'string'
          ? parsed.ollamaEndpoint
          : defaultPreferences.ollamaEndpoint,
        preferredModel: typeof parsed.preferredModel === 'string'
          ? parsed.preferredModel
          : defaultPreferences.preferredModel,
      },
      error: '',
    }
  } catch (error) {
    return {
      values: defaultPreferences,
      error: `Could not read saved settings: ${error.message}`,
    }
  }
}

function validateEndpoint(value) {
  let endpoint
  try {
    endpoint = new URL(value)
  } catch {
    return 'Enter a valid local Ollama URL.'
  }

  const hostname = endpoint.hostname.toLowerCase()
  const isLoopback = hostname === 'localhost'
    || hostname === '[::1]'
    || /^127(?:\.\d{1,3}){3}$/.test(hostname)
  if (!['http:', 'https:'].includes(endpoint.protocol) || !isLoopback) {
    return 'For local-first use, the Ollama URL must point to localhost or a loopback address.'
  }
  if (endpoint.username || endpoint.password || endpoint.search || endpoint.hash) {
    return 'The Ollama URL cannot contain credentials, a query, or a fragment.'
  }
  return ''
}

export default function SettingsPage() {
  const [initial] = useState(readPreferences)
  const [endpoint, setEndpoint] = useState(initial.values.ollamaEndpoint)
  const [preferredModel, setPreferredModel] = useState(initial.values.preferredModel)
  const [error, setError] = useState(initial.error)
  const [notice, setNotice] = useState('')
  const [isConfirmingRemoval, setIsConfirmingRemoval] = useState(false)
  const [isRemoving, setIsRemoving] = useState(false)

  function savePreferences(event) {
    event.preventDefault()
    setNotice('')
    const endpointError = validateEndpoint(endpoint.trim())
    if (endpointError) {
      setError(endpointError)
      return
    }
    if (preferredModel.trim().length > 128) {
      setError('The preferred model name must be 128 characters or fewer.')
      return
    }

    const preferences = {
      ollamaEndpoint: endpoint.trim().replace(/\/+$/, ''),
      preferredModel: preferredModel.trim(),
    }
    try {
      localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences))
      setEndpoint(preferences.ollamaEndpoint)
      setPreferredModel(preferences.preferredModel)
      setError('')
      setNotice('Preferences saved on this device.')
    } catch (storageError) {
      setError(`Could not save settings: ${storageError.message}`)
    }
  }

  function resetPreferences() {
    setEndpoint(defaultPreferences.ollamaEndpoint)
    setPreferredModel(defaultPreferences.preferredModel)
    setError('')
    setNotice('')
  }

  async function uninstall() {
    setIsRemoving(true)
    setError('')
    try {
      await invoke('uninstall_application')
    } catch (uninstallError) {
      setError(`Could not uninstall VEIL Guard: ${uninstallError.message || uninstallError}`)
      setIsRemoving(false)
      setIsConfirmingRemoval(false)
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">ON THIS DEVICE</div>
          <h1>Settings</h1>
          <p>Choose local model preferences. These settings stay on this device.</p>
        </div>
      </div>

      <section className="surface-card settings-card">
        <div className="card-title">
          <span className="feedback-title-icon">AI</span>
          <div><h2>Ollama and local model</h2><p>Preferences for a future VEIL Engine integration.</p></div>
        </div>
        <div className="settings-availability" role="status">
          <strong>Not connected in this build.</strong> Saving these preferences does not start Ollama, download or select a model for use, or enable protection.
        </div>
        <form className="form-stack settings-form" onSubmit={savePreferences}>
          <label className="field">
            <span>Ollama server URL</span>
            <input
              autoComplete="url"
              maxLength={256}
              required
              value={endpoint}
              onChange={(event) => setEndpoint(event.target.value)}
              placeholder="http://127.0.0.1:11434"
            />
            <small>Local loopback addresses only; this setting never sends prompts to VEIL Cloud.</small>
          </label>
          <label className="field">
            <span>Preferred model <small>Optional</small></span>
            <input
              maxLength={128}
              value={preferredModel}
              onChange={(event) => setPreferredModel(event.target.value)}
              placeholder="e.g. llama3.2:3b"
            />
            <small>Enter a model tag you plan to use, such as a model name and size.</small>
          </label>
          {notice && <div className="alert alert-success" role="status">{notice}</div>}
          {error && <div className="alert alert-error" role="alert">{error}</div>}
          <div className="settings-actions">
            <button className="button button-quiet" type="button" onClick={resetPreferences}>Reset fields</button>
            <button className="button button-primary" type="submit">Save preferences</button>
          </div>
        </form>
      </section>

      <section className="surface-card uninstall-card">
        <div>
          <div className="eyebrow">VEIL GUARD APPLICATION</div>
          <h2>Uninstall VEIL Guard</h2>
          <p>Move the installed app to the macOS Trash. This does not erase your VEIL Cloud account or saved local preferences.</p>
        </div>
        {!isConfirmingRemoval ? (
          <button className="button button-danger" type="button" onClick={() => setIsConfirmingRemoval(true)}>
            Uninstall…
          </button>
        ) : (
          <div className="uninstall-confirm" role="alert">
            <strong>Remove only the VEIL Guard app?</strong>
            <span>The app will quit after Finder moves it to the Trash. You can restore it from the Trash before emptying it.</span>
            <div className="settings-actions">
              <button className="button button-quiet" type="button" disabled={isRemoving} onClick={() => setIsConfirmingRemoval(false)}>Keep VEIL Guard</button>
              <button className="button button-danger" type="button" disabled={isRemoving} onClick={uninstall}>
                {isRemoving ? 'Removing…' : 'Move app to Trash'}
              </button>
            </div>
          </div>
        )}
      </section>
    </>
  )
}
