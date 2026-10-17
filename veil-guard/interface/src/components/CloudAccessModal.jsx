import { useEffect, useRef } from 'react'

export default function CloudAccessModal({ onClose, children }) {
  const closeButtonRef = useRef(null)
  const dialogRef = useRef(null)

  useEffect(() => {
    const previouslyFocused = document.activeElement
    closeButtonRef.current?.focus()

    function manageKeyboard(event) {
      if (event.key === 'Escape') {
        onClose()
        return
      }
      if (event.key !== 'Tab') return

      const focusableElements = dialogRef.current?.querySelectorAll(
        'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])',
      )
      if (!focusableElements?.length) return

      const first = focusableElements[0]
      const last = focusableElements[focusableElements.length - 1]
      if (event.shiftKey && (document.activeElement === first || !dialogRef.current.contains(document.activeElement))) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && (document.activeElement === last || !dialogRef.current.contains(document.activeElement))) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', manageKeyboard)
    return () => {
      document.removeEventListener('keydown', manageKeyboard)
      if (previouslyFocused instanceof HTMLElement && previouslyFocused.isConnected) {
        previouslyFocused.focus()
      }
    }
  }, [onClose])

  return (
    <div
      className="cloud-access-backdrop"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <section
        aria-labelledby="cloud-access-title"
        aria-modal="true"
        className="cloud-access-modal"
        ref={dialogRef}
        role="dialog"
      >
        <button
          aria-label="Close VEIL Cloud access"
          className="cloud-access-close"
          onClick={onClose}
          ref={closeButtonRef}
          type="button"
        >
          ×
        </button>
        {children}
      </section>
    </div>
  )
}
