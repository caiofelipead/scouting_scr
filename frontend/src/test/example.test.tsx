import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'

// Simple component test example
function TestComponent() {
  return <div>Hello Test</div>
}

describe('Example Test', () => {
  it('renders hello message', () => {
    render(<TestComponent />)
    expect(screen.getByText('Hello Test')).toBeInTheDocument()
  })

  it('simple math test', () => {
    expect(1 + 1).toBe(2)
  })
})
