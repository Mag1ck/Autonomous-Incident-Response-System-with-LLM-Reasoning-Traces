from fastapi import FastAPI
from datetime import datetime, timedelta, timezone
import hashlib



app = FastAPI()

observations = []

def analyze_observations(observations, window_seconds):
    failures = []
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds = window_seconds)
    for event in observations:
        if datetime.fromisoformat(event["timestamp"]) > window_start:
            status_code = event.get('status_code')
            if (status_code is not None and status_code >= 500) or event.get('error_type') is not None:
                failures.append(event)
            
    return failures

def group_observations(failures):
    grouped = {}
    for failure in failures:
        key = (
            failure["route"],
            failure["downstream_service"],
            failure.get("status_code"),
            failure.get("error_type")
        )
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(failure)
    return grouped

def get_incidents(groups):
    incidents = []
    #hardcoded for now
    service = "gateway"
    confidence = 0.6
    recommended_action = "pass"
    stat = "open"
    
    for key, events in groups.items():
        route, downstream_service, status_code, error_type = key
        incident_id = hashlib.sha256(f"{route}|{downstream_service}|{status_code}|{error_type}".encode("utf-8")).hexdigest()
        symptom = route + " returned " + str(status_code)
        suspected_dependency = downstream_service
        evidence = events
        first_seen = sorted(events, key = lambda x: x['timestamp'])
        incident = {
        "incident_id": "inc_" + incident_id[0:12],
        "status": stat,
        "affected_service": service,
        "symptom": symptom,
        "suspected_dependency": suspected_dependency,
        "error_type": error_type,
        "evidence": evidence,
        "first_seen": first_seen[0]['timestamp'],
        "last_seen": first_seen[-1]['timestamp'],
        "confidence": confidence,
        "recommended_action": recommended_action
        }
        incidents.append(incident)
    return incidents

@app.get("/health")
def get_health():
    return {"status": "healthy"}

@app.post("/observations")
def post_observation(observation: dict):
    observations.append(observation)
    return {"accepted": True, "stored_count": len(observations)}
        
@app.get("/observations/recent")
def get_observations(limit: int = 50):
    return {"observations": observations[-limit:]}

@app.get("/incidents/recent")
def return_incidents(window_seconds: int = 300):
    failures = analyze_observations(observations, window_seconds)
    grouped = group_observations(failures)
    inc = get_incidents(grouped)
    return {"incidents": inc}
    
