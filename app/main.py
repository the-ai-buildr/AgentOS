import logging

from settings import get_settings
from src.runtime import build_agent_os

_SUPPRESSED_PATTERNS = [
    "Failed to add validate decorator to entrypoint",
    "is not a module, class, method, or function",
]


class _AgnoWarningFilter(logging.Filter):
    """Suppress known benign Agno introspection warnings until upstream fix lands."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(p in msg for p in _SUPPRESSED_PATTERNS)


_filter = _AgnoWarningFilter()
for _handler in logging.root.handlers:
    _handler.addFilter(_filter)
logging.root.addFilter(_filter)

settings = get_settings()
agent_os = build_agent_os(settings=settings)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="app.main:app",
        reload=settings.runtime_env == "dev",
    )
