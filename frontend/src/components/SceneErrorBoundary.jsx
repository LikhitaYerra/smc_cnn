import { Component } from 'react'

export class SceneErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="scene-error">
          <p>3D view failed to load</p>
          <button onClick={() => this.setState({ hasError: false })}>Retry</button>
        </div>
      )
    }
    return this.props.children
  }
}
