import base64
import logfire
import logging
from .settings import settings

import os


def setup_logging(service_name: str):
    if settings.OTLP_ENDPOINT:
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = settings.OTLP_ENDPOINT
        os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = (
            f"{os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]}/v1/logs"
        )
        if settings.OTLP_USERNAME and settings.OTLP_PASSWORD:
            credentials = f"{settings.OTLP_USERNAME}:{settings.OTLP_PASSWORD}".encode("utf-8")
            encoded_credentials = base64.b64encode(credentials).decode("utf-8")
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"authorization=Basic {encoded_credentials}"

    logfire.configure(service_name=service_name, send_to_logfire=False)
    logfire.instrument_httpx()
    logfire.instrument_pydantic_ai()

    logging.basicConfig(
        level=logging.INFO,
        format="[{asctime}] [{levelname}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        handlers=[logfire.LogfireLoggingHandler()],
    )

    logging.info(
        {
            "otel_exporter": os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
            "otel_credentials": True if os.environ.get("OTEL_EXPORTER_OTLP_HEADERS") is not None else False,
        }
    )
