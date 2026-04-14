"""Configuration loader with environment variable expansion."""

import os
import re
from pathlib import Path

import yaml


def _expand_env_vars(value):
    """Recursively expand ${VAR} patterns in config values."""
    if isinstance(value, str):
        return re.sub(
            r"\$\{(\w+)\}",
            lambda m: os.environ.get(m.group(1), m.group(0)),
            value,
        )
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_expand_env_vars(v) for v in value]
    return value


def load_config(path: str = "config/config.yaml") -> dict:
    """Load and validate configuration."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}. Copy config/config.example.yaml to config/config.yaml"
        )
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return _expand_env_vars(config)
