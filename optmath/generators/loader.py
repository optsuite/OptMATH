"""Dynamic generator loader"""

import importlib.util
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any


def load_generators_from_dir(base_dir: str) -> List[Tuple[Any, Dict[str, Any], Path]]:
    """
    Scan directory and load all generators.
    Each generator directory should contain:
      - *.py: Contains Generator class
      - metadata.json: subclass, math_formula, etc.

    Returns:
        List of (Generator_class, metadata_dict, folder_path)
    """
    base = Path(base_dir)
    if not base.exists() or not base.is_dir():
        return []

    results = []
    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue
        py_file = None
        metadata_file = item / "metadata.json"
        for f in item.iterdir():
            if f.suffix == ".py" and not f.name.startswith("__"):
                py_file = f
                break
        if not py_file or not metadata_file.exists():
            continue

        try:
            Generator = _load_generator_class(py_file)
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            results.append((Generator, metadata, item))
        except Exception:
            continue
    return results


def _load_generator_class(py_path: Path) -> type:
    """Dynamically load Generator class from Python module"""
    spec = importlib.util.spec_from_file_location("generator_module", py_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "Generator"):
        raise ValueError(f"Module {py_path} has no Generator class")
    return module.Generator
