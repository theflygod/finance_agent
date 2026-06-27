"""Loguru-based logging configuration."""

from __future__ import annotations

import sys

from loguru import logger

from app.conf.app_config import app_config


def setup_logging() -> None:
    logger.remove()

    if app_config.logging.console.enable:
        logger.add(
            sys.stderr,
            level=app_config.logging.console.level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

    if app_config.logging.file.enable:
        logger.add(
            f"{app_config.logging.file.path}/app.log",
            level=app_config.logging.file.level,
            rotation=app_config.logging.file.rotation,
            retention=app_config.logging.file.retention,
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )

    logger.info("Logging configured")