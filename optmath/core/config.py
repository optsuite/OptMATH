"""Configuration loading and validation"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class LLMProviderConfig:
    """Single LLM provider configuration"""
    model: str
    base_url: str
    api_key_env: str


@dataclass
class LLMConfig:
    """Unified LLM configuration"""
    default_model: str = "deepseek_official"
    providers: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "LLMConfig":
        providers = {}
        if "providers" in data:
            for name, cfg in data["providers"].items():
                providers[name] = LLMProviderConfig(**cfg)
        return cls(
            default_model=data.get("default_model", "deepseek_official"),
            providers=providers,
        )


@dataclass
class InstanceGenerationConfig:
    base_dir: str = "generators"
    num_instances: int = 2500
    max_iter: int = 3000
    var_num_max: int = 50
    constraint_num_max: int = 100
    num_workers: Optional[int] = None
    output_file: str = "output/instances.json"


@dataclass
class BacktranslationConfig:
    model_name: str = "deepseek_official"
    max_workers: int = 4
    batch_size: int = 10
    max_iter: int = 3
    sample_size: int = 100
    temperature: float = 0.8


@dataclass
class ModelingConfig:
    model_name: str = "deepseek_official"
    num_workers: int = 100
    temperature: float = 0.8


@dataclass
class EvaluationConfig:
    timeout: int = 100
    max_workers: int = 50
    numerical_tolerance: float = 0.05
    question_field: str = "en_question"
    answer_field: str = "en_answer"


@dataclass
class LoggingConfig:
    level: str = "INFO"
    dir: str = "logs"


@dataclass
class Config:
    """Unified configuration"""

    llm: LLMConfig = field(default_factory=LLMConfig)
    instance_generation: InstanceGenerationConfig = field(
        default_factory=InstanceGenerationConfig
    )
    backtranslation: BacktranslationConfig = field(
        default_factory=BacktranslationConfig
    )
    modeling: ModelingConfig = field(default_factory=ModelingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        config = cls()
        section_types = {
            "llm": (LLMConfig, True),
            "instance_generation": (InstanceGenerationConfig, False),
            "backtranslation": (BacktranslationConfig, False),
            "modeling": (ModelingConfig, False),
            "evaluation": (EvaluationConfig, False),
            "logging": (LoggingConfig, False),
        }
        for section, section_data in data.items():
            if section in section_types and section_data is not None:
                dc_type, use_custom_from_dict = section_types[section]
                if use_custom_from_dict:
                    setattr(config, section, dc_type.from_dict(section_data))
                else:
                    kwargs = {
                        k: v
                        for k, v in section_data.items()
                        if k in dc_type.__dataclass_fields__
                    }
                    setattr(config, section, dc_type(**kwargs))
        return config


def load_config(
    config_path: Optional[str] = None,
    overrides: Optional[dict] = None,
) -> Config:
    """
    Load configuration with hierarchical override: defaults → file → env vars → overrides
    """
    # 1. Default configuration
    default_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"
    with open(default_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # 2. Merge file configuration
    if config_path and os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            file_data = yaml.safe_load(f) or {}
        data = _deep_merge(data, file_data)

    # 3. Environment variables (e.g., OPTMATH_INSTANCE_GENERATION_NUM_INSTANCES)
    env_overrides = _get_env_overrides()
    data = _deep_merge(data, env_overrides)

    # 4. Explicit overrides
    if overrides:
        data = _deep_merge(data, overrides)

    return Config.from_dict(data)


def _deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _get_env_overrides() -> dict:
    prefix = "OPTMATH_"
    known_sections = sorted(Config.__dataclass_fields__.keys(), key=len, reverse=True)
    result = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            raw_key = key[len(prefix) :].lower()
            parts = None

            if "__" in raw_key:
                parts = raw_key.split("__")
            else:
                for section in known_sections:
                    section_prefix = f"{section}_"
                    if raw_key.startswith(section_prefix):
                        field_name = raw_key[len(section_prefix) :]
                        parts = [section, field_name]
                        break

            if parts is None:
                parts = [raw_key]

            d = result
            for p in parts[:-1]:
                d = d.setdefault(p, {})
            # Type conversion
            try:
                if value.isdigit():
                    value = int(value)
                elif value.replace(".", "").isdigit():
                    value = float(value)
            except (ValueError, AttributeError):
                pass
            d[parts[-1]] = value
    return result
