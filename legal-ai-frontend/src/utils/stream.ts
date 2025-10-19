export async function streamChatResponse(question: string, top_k = 1, onToken: (token: string) => void, p0: () => void) {
    const response = await fetch("http://127.0.0.1:8080/query/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question, top_k }),
    });
  
    if (!response.ok || !response.body) {
      throw new Error(`Network response was not ok: ${response.statusText}`);
    }
  
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
  
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
  
      // Split the SSE stream by "data: "
      const parts = buffer.split("\n\n");
  
      for (let i = 0; i < parts.length - 1; i++) {
        const line = parts[i].trim();
        if (line.startsWith("data:")) {
          try {
            const json = JSON.parse(line.replace("data:", "").trim());
            if (json.token) {
              onToken(json.token);
            }
          } catch (e) {
            console.error("Error parsing JSON chunk:", e, line);
          }
        }
      }
  
      // Keep the incomplete part for next read
      buffer = parts[parts.length - 1];
    }
  }
  