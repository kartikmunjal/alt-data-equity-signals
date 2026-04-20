from pathlib import Path

from altdata_equity_signals.pipeline import run_pipeline


def test_synthetic_pipeline_writes_outputs(tmp_path: Path):
    outputs = run_pipeline(use_synthetic=True, output_dir=tmp_path, horizons=[1, 5], min_stocks=10)

    assert not outputs["ic"].empty
    assert not outputs["fama_macbeth"].empty
    assert (tmp_path / "ic_summary.csv").exists()
    assert (tmp_path / "fama_macbeth.csv").exists()
    assert (tmp_path / "quintile_returns.csv").exists()
