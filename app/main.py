from src.config import get_settings
from src.runtime import build_agent_os

settings = get_settings()
agent_os = build_agent_os(settings=settings)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(
        app="app.main:app",
        reload=settings.runtime_env == "dev",
    )
