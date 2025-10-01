from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load data from the JSON file
with open('q-vercel-latency.json', 'r') as f:
    data = json.load(f)

@app.post("/")
def get_metrics(request_body: dict):
    # Ensure regions and threshold_ms are in the request body
    if "regions" not in request_body or "threshold_ms" not in request_body:
        raise HTTPException(status_code=400, detail="Invalid request body")

    regions = request_body["regions"]
    threshold_ms = request_body["threshold_ms"]
    
    metrics = {}
    
    for region in regions:
        region_data = [item for item in data if item["region"] == region]
        
        if not region_data:
            metrics[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = sorted([item["latency_ms"] for item in region_data])
        uptimes = [item["uptime_pct"] for item in region_data]
        
        # Calculate p95 latency
        p95_index = int(0.95 * len(latencies))
        p95_latency = latencies[p95_index] if len(latencies) > 0 else 0
        
        # Calculate other metrics
        avg_latency = sum(latencies) / len(latencies)
        avg_uptime = sum(uptimes) / len(uptimes)
        breaches = sum(1 for l in latencies if l > threshold_ms)
        
        metrics[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }
    
    return metrics
