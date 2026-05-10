from fastapi import FastAPI


app = FastAPI()

observations = []

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