"""Application configuration using OmegaConf dataclasses."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from omegaconf import OmegaConf

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(ROOT_DIR / ".env")


@dataclass
class LLMConfig:
    model_name: str = os.getenv("LLM_MODEL", "qwen-plus")
    api_key: str = os.getenv("API_KEY", "")
    base_url: str = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")


@dataclass
class QdrantConfig:
    host: str = os.getenv("QDRANT_HOST", "192.168.10.150")
    port: int = int(os.getenv("QDRANT_PORT", "6333"))
    embedding_size: int = int(os.getenv("QDRANT_EMBEDDING_SIZE", "1024"))


@dataclass
class ESConfig:
    host: str = os.getenv("ES_HOST", "192.168.10.150")
    port: int = int(os.getenv("ES_PORT", "9200"))


@dataclass
class EmbeddingConfig:
    host: str = os.getenv("EMBEDDING_HOST", "192.168.10.150")
    port: int = int(os.getenv("EMBEDDING_PORT", "8080"))


@dataclass
class DBConfig:
    host: str = os.getenv("DB_HOST", "192.168.10.150")
    port: int = int(os.getenv("DB_PORT", "3306"))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "123321")
    database: str = os.getenv("DB_NAME", "finance")
    charset: str = "utf8mb4"


@dataclass
class MetaDBConfig:
    host: str = os.getenv("DB_HOST", "192.168.10.150")
    port: int = int(os.getenv("DB_PORT", "3306"))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "123321")
    database: str = "meta"
    charset: str = "utf8mb4"


@dataclass
class ConsoleLoggingConfig:
    enable: bool = True
    level: str = "DEBUG"


@dataclass
class FileLoggingConfig:
    enable: bool = True
    level: str = "DEBUG"
    path: str = "logs"
    rotation: str = "10 MB"
    retention: str = "7 days"


@dataclass
class LoggingConfig:
    console: ConsoleLoggingConfig = field(default_factory=ConsoleLoggingConfig)
    file: FileLoggingConfig = field(default_factory=FileLoggingConfig)


@dataclass
class AppConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    qdrant: QdrantConfig = field(default_factory=QdrantConfig)
    es: ESConfig = field(default_factory=ESConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    dw_db: DBConfig = field(default_factory=DBConfig)
    meta_db: MetaDBConfig = field(default_factory=MetaDBConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    app_port: int = int(os.getenv("APP_PORT", "8000"))


app_config: AppConfig = OmegaConf.structured(AppConfig)