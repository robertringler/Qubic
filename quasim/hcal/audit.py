"""HCAL audit logging."""

from typing import Dict, Any, Optional
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime


class AuditLogger:
    """Audit logger with hash chaining."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize audit logger.
        
        Args:
            log_dir: Directory for audit logs
        """
        self.log_dir = log_dir
        self._prev_hash = "0" * 64
        self._log_file = None
        
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._log_file = log_dir / f"audit_{timestamp}.jsonl"
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an audit event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if not self._log_file:
            return
        
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data,
            "prev_hash": self._prev_hash,
        }
        
        # Calculate hash of this entry
        event_json = json.dumps(event, sort_keys=True)
        event_hash = hashlib.sha256(event_json.encode()).hexdigest()
        event["hash"] = event_hash
        
        # Write to log file
        with open(self._log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        # Update previous hash for chaining
        self._prev_hash = event_hash


__all__ = ["AuditLogger"]
