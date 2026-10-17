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
  const [isLaunching, setIsLaunching] = useState(false)

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

  async function launchUninstaller() {
    setIsLaunching(true)
    setError('')
    try {
      await invoke('launch_maintenance_tool')
    } catch (launchError) {
      setError(`Could not launch uninstaller: ${launchError.message || launchError}`)
      setIsLaunching(false)
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
          <p>Launch the VEIL Guard Maintenance Tool to completely remove the application and its installed files from this Mac.</p>
        </div>
        <button
          className="button button-danger"
          type="button"
          disabled={isLaunching}
          onClick={launchUninstaller}
        >
          {isLaunching ? 'Launching Uninstaller…' : 'Uninstall VEIL Guard'}
        </button>
      </section>
    </>
  )
}