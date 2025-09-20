
from datetime import datetime
import hashlib
import json
from typing import Any

def make_id(prefix: str, payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True).encode()
    digest = hashlib.sha256(raw).hexdigest()[:12]
    return f"{prefix}_{digest}_{int(datetime.utcnow().timestamp())}"
