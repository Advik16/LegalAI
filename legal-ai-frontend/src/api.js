// src/api.js
const BASE = "http://127.0.0.1:8080";

export function startQueryStream({ question, top_k = 1, onToken, onDone, onError }) {
  const url = `${BASE}/query/stream`;
  return _startSSE(url, { question, top_k }, onToken, onDone, onError);
}

export function startChatStream({ conversation_id, question, onToken, onDone, onError }) {
  const url = `${BASE}/chat/stream`;
  // Backend expects 'question' for chat endpoint
  return _startSSE(url, { conversation_id, question }, onToken, onDone, onError);
}

function _startSSE(url, payload, onToken, onDone, onError) {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream, */*" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let idx;
        while ((idx = buffer.indexOf("\n\n")) !== -1) {
          const raw = buffer.slice(0, idx).trim();
          buffer = buffer.slice(idx + 2);
          const lines = raw.split(/\r?\n/);
          
          for (const line of lines) {
            if (!line.startsWith("data:")) continue;
            const payloadText = line.replace(/^data:\s*/, "");
            
            if (payloadText === "[DONE]") {
              onDone?.();
              controller.abort();
              return;
            }
            
            try {
              const parsed = JSON.parse(payloadText);
              onToken?.(parsed);
            } catch {
              onToken?.(payloadText);
            }
          }
        }
      }

      // leftover
      if (buffer.trim()) {
        const lines = buffer.trim().split(/\r?\n/);
        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const payloadText = line.replace(/^data:\s*/, "");
          
          if (payloadText === "[DONE]") {
            onDone?.();
            break;
          }
          
          try {
            const parsed = JSON.parse(payloadText);
            onToken?.(parsed);
          } catch {
            onToken?.(payloadText);
          }
        }
      }

      onDone?.();
    } catch (err) {
      if (err.name !== "AbortError") onError?.(err);
      onDone?.();
    }
  })();

  return controller;
}