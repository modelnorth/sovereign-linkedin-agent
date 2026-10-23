"""
ModelNorth Sovereign LinkedIn Agent - OpenTelemetry Observability Engine
https://modelnorth.com

Implements distributed tracing, latency accounting, and flight ledger auditability:
- Hierarchical OTEL spans (Session -> Governor -> Browser -> Action).
- Langfuse, Datadog, Honeycomb, and LangSmith compatible attributes.
- Local-first append-only flight ledger (otel_traces.jsonl) in sovereign vault.
"""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Generator, Optional
import uuid

logger = logging.getLogger("sovereign_linkedin.otel")

# Try importing official opentelemetry, provide robust fallbacks
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode, Span
    OTEL_INSTALLED = True
    tracer = trace.get_tracer("modelnorth.sovereign_linkedin", "1.0.0")
except ImportError:
    OTEL_INSTALLED = False
    tracer = None
    Status = None
    StatusCode = None
    Span = Any


class FlightLedgerExporter:
    """Local-first append-only JSONL span ledger for zero-trust compliance."""
    def __init__(self, log_dir: Optional[Path] = None):
        if log_dir is None:
            self.log_dir = Path(os.path.expanduser("~/.modelnorth/linkedin_vault"))
        else:
            self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.trace_file = self.log_dir / "otel_traces.jsonl"

    def emit_span(self, span_data: dict[str, Any]) -> None:
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(span_data) + "\n")
        except Exception as e:
            logger.debug(f"Failed to append to otel flight ledger: {e}")

    def read_recent_spans(self, limit: int = 15) -> list[dict[str, Any]]:
        if not self.trace_file.exists():
            return []
        try:
            with open(self.trace_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            records = [json.loads(line) for line in lines if line.strip()]
            return records[-limit:]
        except Exception as e:
            logger.warning(f"Error reading otel traces: {e}")
            return []


ledger_exporter = FlightLedgerExporter()


@contextmanager
def trace_agent_step(
    step_name: str,
    action: str = "general",
    model: str = "gemini-3.8-flash",
    **attributes: Any
) -> Generator[Any, None, None]:
    """
    Instruments an agent step with standard OpenTelemetry distributed spans
    and records to the local ModelNorth sovereign flight ledger.
    """
    span_id = uuid.uuid4().hex[:16]
    trace_id = attributes.get("trace_id") or uuid.uuid4().hex
    start_time = time.time()
    iso_start = datetime.now(timezone.utc).isoformat()

    span_record: dict[str, Any] = {
        "span_id": span_id,
        "trace_id": trace_id,
        "step_name": step_name,
        "action": action,
        "gen_ai.system": "modelnorth",
        "gen_ai.request.model": model,
        "start_time": iso_start,
        "attributes": {f"agent.{k}": v for k, v in attributes.items()},
        "status": "OK",
        "error": None,
    }

    if OTEL_INSTALLED and tracer:
        with tracer.start_as_current_span(step_name) as otel_span:
            otel_span.set_attribute("gen_ai.system", "modelnorth")
            otel_span.set_attribute("gen_ai.request.model", model)
            otel_span.set_attribute("agent.action", action)
            for k, v in attributes.items():
                otel_span.set_attribute(f"agent.{k}", str(v))
            try:
                yield otel_span
                otel_span.set_status(Status(StatusCode.OK))
            except Exception as exc:
                span_record["status"] = "ERROR"
                span_record["error"] = str(exc)
                if otel_span and Status and StatusCode:
                    otel_span.set_status(Status(StatusCode.ERROR, str(exc)))
                    otel_span.record_exception(exc)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000.0
                otel_span.set_attribute("agent.duration_ms", duration_ms)
                span_record["duration_ms"] = round(duration_ms, 2)
                span_record["end_time"] = datetime.now(timezone.utc).isoformat()
                ledger_exporter.emit_span(span_record)
    else:
        try:
            yield span_record
        except Exception as exc:
            span_record["status"] = "ERROR"
            span_record["error"] = str(exc)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000.0
            span_record["duration_ms"] = round(duration_ms, 2)
            span_record["end_time"] = datetime.now(timezone.utc).isoformat()
            ledger_exporter.emit_span(span_record)
