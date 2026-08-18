import json
import logging
import logging.handlers
from pathlib import Path
from typing import ClassVar

from rich.logging import RichHandler


class StructuredJSONFormatter(logging.Formatter):
    _STANDARD_LOG_RECORD_KEYS: ClassVar[set[str]] = {
        "args", "asctime", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelname", "levelno", "lineno", "module", "msecs",
        "message", "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName",
    }

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        
        # OPTIMIZATION: Use pre-allocated set for O(1) lookup to check standard LogRecord keys
        # avoiding list allocation and O(N) linear search per attribute on every log entry.
        for key, value in record.__dict__.items():
            if key not in self._STANDARD_LOG_RECORD_KEYS:
                try:
                    json.dumps(value) 
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)
                    
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("forge_cli")
    logger.setLevel(logging.DEBUG) 
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    rich_handler = RichHandler(rich_tracebacks=True, markup=True)
    rich_handler.setLevel(logging.INFO)
    rich_handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
    logger.addHandler(rich_handler)
    
    log_dir = Path.home() / ".forge" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "forge.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(StructuredJSONFormatter())
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()
