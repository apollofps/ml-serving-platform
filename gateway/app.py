import os, time, json
import httpx
from fastapi import FastAPI , Request
from prometheus_client import Counter, Histogram , generate_latest , CONTENT_TYPE_LATEST
from starlette.responses import Response

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:9000")

app = FastAPI()
REQS = Counter("inference_requests_total", "Total number of inference requests", ["status"])
LAT = Histogram(
    "inference_latency_ms",
    "Inference latency in milliseconds",
    buckets=(25, 50, 100, 200, 400, 800, 1600, 3200, 6400)  # extended buckets
)


@app.post("/v1/infer")
async def infer(req: Request):
    payload = await req.json()
    start = time.time()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(f"{BACKEND_URL}/completion", json=payload)

        status = "ok" if r.status_code == 200 else "bad"
        REQS.labels(status).inc()
        LAT.observe((time.time() - start) *1000)
        return Response(r.content, status_code=r.status_code , media_type="application/json")
    except Exception as e:
        REQS.labels("error").inc()
        LAT.observe((time.time() - start) *1000)
        return {"error": str(e)}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"ok" : True}
    
