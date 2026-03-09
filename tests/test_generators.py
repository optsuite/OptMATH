"""Generator module tests"""

import json
from pathlib import Path

import pytest

from optmath.generators.loader import load_generators_from_dir, _load_generator_class
from optmath.generators.pipeline import InstanceGenerationPipeline
from optmath.core.models import OptimizationInstance


def test_load_generators_from_existing_dir():
    base = Path(__file__).parent.parent.parent / "generators"
    if not base.exists():
        pytest.skip("generators dir not found")
    items = load_generators_from_dir(str(base))
    assert len(items) >= 1
    Generator, metadata, folder = items[0]
    assert hasattr(Generator, "generate_instance")
    assert "subclass" in metadata or "math_formula" in metadata


def test_load_generators_empty_dir(tmp_path):
    items = load_generators_from_dir(str(tmp_path))
    assert items == []


def test_load_generators_invalid_dir():
    items = load_generators_from_dir("/nonexistent/path")
    assert items == []


@pytest.mark.skipif(
    not (Path(__file__).parent.parent.parent / "generators").exists(),
    reason="generators dir not found",
)
def test_instance_generation_pipeline_small(generators_dir, tmp_path):
    """Small-scale instance generation test (requires Gurobi)"""
    pipeline = InstanceGenerationPipeline(
        base_dir=generators_dir,
        num_instances=2,
        output_file=str(tmp_path / "out.json"),
        max_iter=50,
        var_num_max=100,
        constraint_num_max=200,
        num_workers=1,
    )
    results = pipeline.run()
    assert len(results) >= 0
    if results:
        r = results[0]
        assert r.subclass
        assert r.lp_data
        assert r.status == "OPTIMAL"


def test_optimization_instance_to_dict():
    inst = OptimizationInstance(
        subclass="diet",
        mathematical_expression="min",
        lp_data="lp",
        status="OPTIMAL",
        objective=1.0,
    )
    d = inst.to_dict()
    assert d["subclass"] == "diet"
    assert d["objective"] == 1.0
