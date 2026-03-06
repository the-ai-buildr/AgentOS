import json
import os
import shlex
from pathlib import Path
from typing import Any, Iterable

from agno.tools.mcp import MCPTools, StreamableHTTPClientParams


TOOLS_DIR = Path(__file__).resolve().parent
SERVER_FILES_DIR = TOOLS_DIR / "mcp_servers"


def _parse_urls(raw_urls: str) -> list[str]:
    urls: list[str] = []
    for part in raw_urls.replace("\n", ",").split(","):
        url = part.strip().strip('"').strip("'")
        if url and url.startswith(("http://", "https://")) and url not in urls:
            urls.append(url)
    return urls


def _replace_env_value(value: str) -> str:
    value = value.strip()
    expanded = os.path.expandvars(value)
    # If unresolved variable remains as "$VAR", coerce to empty.
    if expanded.startswith("$") and expanded == value:
        return ""
    return expanded


def _resolve_env_refs(value: Any) -> Any:
    if isinstance(value, str):
        return _replace_env_value(value)
    if isinstance(value, list):
        return [_resolve_env_refs(item) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_env_refs(item) for key, item in value.items()}
    return value


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
        return data if isinstance(data, dict) else {}


def _build_tool_from_config(config: dict[str, Any]) -> MCPTools | None:
    resolved_config = _resolve_env_refs(config)
    command = resolved_config.get("command")
    args = resolved_config.get("args", [])
    env = resolved_config.get("env", {})
    url = resolved_config.get("url")
    url_env = resolved_config.get("url_env")
    headers = resolved_config.get("headers")
    transport = resolved_config.get("transport")

    if isinstance(url_env, str) and url_env.strip():
        env_url = os.getenv(url_env.strip(), "").strip()
        if env_url:
            url = env_url

    if isinstance(url, str) and url.strip():
        url = url.strip()
        if isinstance(headers, dict) and headers:
            return MCPTools(
                server_params=StreamableHTTPClientParams(url=url, headers=headers),
                transport=transport or "streamable-http",
            )
        return MCPTools(url=url, transport=transport or "streamable-http")

    if isinstance(command, str) and command.strip():
        cmd = command.strip()
        if isinstance(args, list) and args:
            cmd = " ".join([cmd, *[shlex.quote(str(arg)) for arg in args]])
        if isinstance(env, dict) and env:
            env = {str(k): str(v) for k, v in env.items() if str(v)}
            return MCPTools(command=cmd, env=env)
        return MCPTools(command=cmd)

    return None


def get_mcp_urls(*, env_var: str = "MCP_SERVER_URLS", default_urls: Iterable[str] | None = None) -> list[str]:
    configured_urls = _parse_urls(os.getenv(env_var, ""))
    return configured_urls if configured_urls else list(default_urls or [])


def build_mcp_tools(
    *,
    env_var: str = "MCP_SERVER_URLS",
    default_urls: Iterable[str] | None = None,
 ) -> list[MCPTools]:
    tools = [MCPTools(url=url) for url in get_mcp_urls(env_var=env_var, default_urls=default_urls)]

    if not SERVER_FILES_DIR.exists():
        return tools

    for config_path in sorted(SERVER_FILES_DIR.glob("*.json")):
        config = _load_json(config_path)
        if config.get("enabled", True) is False:
            continue
        tool = _build_tool_from_config(config)
        if tool is not None:
            tools.append(tool)

    return tools
