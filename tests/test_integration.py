import pandas as pd

from altdata_equity_signals.integration import (
    export_factor_panels,
    load_factor_panels,
    merge_with_factor_library,
)


def test_export_and_load_factor_panels(tmp_path):
    panel = pd.DataFrame(
        [[1.0, -1.0], [0.5, -0.5]],
        index=pd.bdate_range("2024-01-01", periods=2),
        columns=["aapl", "msft"],
    )

    paths = export_factor_panels({"mention_z": panel}, tmp_path)
    loaded = load_factor_panels(tmp_path)

    assert "WSB_MENTION_Z" in paths
    assert "WSB_MENTION_Z" in loaded
    assert list(loaded["WSB_MENTION_Z"].columns) == ["AAPL", "MSFT"]


def test_merge_with_factor_library_rejects_name_collisions():
    panel = pd.DataFrame()
    try:
        merge_with_factor_library({"MOM": panel}, {"MOM": panel})
    except ValueError as exc:
        assert "collision" in str(exc)
    else:
        raise AssertionError("expected ValueError")
