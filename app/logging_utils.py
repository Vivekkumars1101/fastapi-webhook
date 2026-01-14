import json
import time
import sys
from datetime import datetime

def log_json(level, method, path, status, latency_ms, request_id, extra=None):
    log_entry = {
        "ts": datetime.utcnow().isoformat() + "Z", # ISO-8601 UTC [cite: 155]
        "level": level,
        "request_id": request_id,
        "method": method,
        "path": path,
        "status": status,
        "latency_ms": round(latency_ms, 2)
    }
    if extra:
        log_entry.update(extra)
    
    # Write to stdout as a single JSON line [cite: 170]
    print(json.dumps(log_entry), file=sys.stdout)