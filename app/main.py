from settings import get_settings
from src.runtime import build_agent_os
from app.api.routes import router as slack_router

settings = get_settings()
agent_os = build_agent_os(settings=settings)
app = agent_os.get_app()
app.include_router(slack_router)

if __name__ == "__main__":
    agent_os.serve(
        app="app.main:app",
        reload=settings.runtime_env == "dev",
    )
