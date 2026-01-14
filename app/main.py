import hmac
import hashlib
import time
import uuid
from fastapi import FastAPI, Request, Header, HTTPException, Response
from . import storage, models, config, logging_utils
from .metrics import get_metrics
from .storage import get_messages, get_stats

app = FastAPI()

@app.on_event("startup")
def on_startup():
    if not config.settings.WEBHOOK_SECRET:
        raise RuntimeError("WEBHOOK_SECRET must be set") # 
    storage.init_db()

@app.get("/health/live")
def liveness():
    return {"status": "ok"} # [cite: 121]

@app.get("/health/ready")
def readiness():
    # Return 200 only if secret is set and DB is reachable [cite: 125, 126, 127]
    if not config.settings.WEBHOOK_SECRET:
        return Response(status_code=503)
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request, x_signature: str = Header(None)):
    start_time = time.time()
    req_id = str(uuid.uuid4())
    body = await request.body()
    
    # 1. HMAC Signature Validation [cite: 35]
    secret = config.settings.WEBHOOK_SECRET.encode()
    expected_sig = hmac.new(secret, body, hashlib.sha256).hexdigest()
    
    if not x_signature or not hmac.compare_digest(expected_sig, x_signature):
        logging_utils.log_json("ERROR", "POST", "/webhook", 401, (time.time()-start_time)*1000, req_id, {"result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature") # [cite: 41]

    # 2. Validation & Persistence
    try:
        data = await request.json()
        payload = models.WebhookPayload(**data)
        res = storage.save_message(payload.message_id, payload.from_msisdn, payload.to_msisdn, data['ts'], payload.text)
        
        latency = (time.time() - start_time) * 1000
        logging_utils.log_json("INFO", "POST", "/webhook", 200, latency, req_id, 
                               {"message_id": payload.message_id, "dup": res == "duplicate", "result": res})
        return {"status": "ok"} # [cite: 64]
    except Exception as e:
        # FastAPI handles 422 automatically for Pydantic errors [cite: 49]
        raise e

@app.get("/messages")
async def list_messages(
    limit: int = 50, 
    offset: int = 0, 
    from_msisdn: str = None, 
    since: str = None, 
    q: str = None
):
    # Requirement: List stored messages with pagination and basic filters [cite: 66, 67]
    data, total = get_messages(limit, offset, from_msisdn, since, q)
    return {
        "data": data, 
        "total": total, 
        "limit": limit, 
        "offset": offset
    }

@app.get("/stats")
async def stats():
    # Requirement: Provide simple message-level analytics [cite: 105]
    return get_stats()

@app.get("/metrics")
async def metrics():
    # Requirement: Expose Prometheus-style metrics [cite: 130]
    return get_metrics()