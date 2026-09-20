import "@testing-library/jest-dom";

// Mock matchMedia for jsdom
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Polyfill ResizeObserver for Radix UI primitives
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserverMock;
globalThis.ResizeObserver = ResizeObserverMock;

// Polyfill EventSource for jsdom
class EventSourceMock {
  close() {}
  onmessage: any = null;
  onerror: any = null;
  readyState = 1;
}

(globalThis as any).EventSource = EventSourceMock;
(window as any).EventSource = EventSourceMock;

// Polyfill WebSocket for jsdom
class WebSocketMock {
  close() {}
  send() {}
  onopen: any = null;
  onclose: any = null;
  onerror: any = null;
  onmessage: any = null;
  readyState = 1;
  static OPEN = 1;
}

(globalThis as any).WebSocket = WebSocketMock;
(window as any).WebSocket = WebSocketMock;
