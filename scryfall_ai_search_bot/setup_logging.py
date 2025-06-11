import base64
import logging
from unittest.mock import patch
import logfire
from logfire.sampling import SpanLevel
from logfire._internal.exporters.console import SimpleConsoleSpanExporter
from opentelemetry.context.context import Context
from opentelemetry.sdk.trace import Span, SpanProcessor
from opentelemetry.sdk._logs import LogRecord
from opentelemetry._logs import SeverityNumber
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from .settings import settings

import os


class DualPublishSpanToLogProcessor(SpanProcessor):
    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        attributes = span.attributes
        if attributes is None:
            return

        if attributes.get("logfire.span_type") != "log":
            return

        timestamp = span.start_time
        span_id = span.context.span_id if span.context else None
        trace_id = span.context.trace_id if span.context else None
        trace_flags = span.context.trace_flags if span.context else None

        logfire_level_num = attributes.get("logfire.level_num")
        if not isinstance(logfire_level_num, int):
            logfire_level_num = 0
        level = SpanLevel(logfire_level_num)
        severity_text = level.name
        severity_number = SeverityNumber(level.number)

        body = attributes.get("logfire.msg") or ""
        record = LogRecord(
            timestamp=timestamp,
            span_id=span_id,
            trace_id=trace_id,
            trace_flags=trace_flags,
            severity_text=severity_text,
            severity_number=severity_number,
            body=body,
            resource=span.resource,
            attributes=span.attributes,
        )

        name = span.instrumentation_scope.name if span.instrumentation_scope else ""

        with patch("logfire._internal.exporters.logs.is_instrumentation_suppressed", return_value=False):
            logfire.DEFAULT_LOGFIRE_INSTANCE.config.get_logger_provider().get_logger(name).emit(record)


def setup_logging(service_name: str):
    if settings.OTLP_ENDPOINT:
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = settings.OTLP_ENDPOINT
        if settings.OTLP_USERNAME and settings.OTLP_PASSWORD:
            credentials = f"{settings.OTLP_USERNAME}:{settings.OTLP_PASSWORD}".encode("utf-8")
            encoded_credentials = base64.b64encode(credentials).decode("utf-8")
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"authorization=Basic {encoded_credentials}"

    logfire.configure(
        service_name=service_name,
        send_to_logfire="if-token-present",
        code_source=logfire.CodeSource(
            repository="https://github.com/btarr101/scryfall-ai-search-bot",
            revision="main>",
        ),
        additional_span_processors=[
            SimpleSpanProcessor(
                SimpleConsoleSpanExporter(
                    colors="auto",
                    include_timestamp=True,
                    include_tags=False,
                    verbose=False,
                    min_log_level="info",
                )
            ),
            DualPublishSpanToLogProcessor(),
        ],
        console=False,  # We give our own console logger
    )

    logfire.instrument_httpx()
    logfire.instrument_pydantic_ai()

    logging.basicConfig(
        level=logging.DEBUG,
        format="[{asctime}] [{levelname}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        handlers=[logfire.LogfireLoggingHandler(level=logging.INFO)],
    )

    logging.info(
        {
            "otel_exporter": os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
            "otel_credentials": True if os.environ.get("OTEL_EXPORTER_OTLP_HEADERS") is not None else False,
        }
    )
