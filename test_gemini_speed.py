import time
from services.llm_service import client, MODEL_NAME

print("Sending a minimal request to Gemini...", flush=True)
start = time.perf_counter()

try:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents="Reply with exactly: OK",
    )

    elapsed = time.perf_counter() - start
    print(f"Response time: {elapsed:.2f} seconds")
    print("Response:", response.text)

except Exception as exc:
    elapsed = time.perf_counter() - start
    print(f"Failed after {elapsed:.2f} seconds")
    print(type(exc).__name__, str(exc))
