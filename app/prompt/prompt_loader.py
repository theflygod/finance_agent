"""Prompt loader: load prompt templates from YAML files."""

from __future__ import annotations

from pathlib import Path

from omegaconf import OmegaConf

from app.conf.app_config import ROOT_DIR

PROMPT_DIR = ROOT_DIR / "app" / "prompt" / "templates"


def load_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    cfg = OmegaConf.load(path)
    return cfg.prompt