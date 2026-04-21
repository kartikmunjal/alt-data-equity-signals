"""Plotting helpers for alt-data signal research outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_research_summary(
    ic_table: pd.DataFrame,
    fm_table: pd.DataFrame,
    quintiles: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """Create a compact summary figure for IC, FM, and quintile diagnostics."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("Alt-Data Equity Signal Research Summary", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ic_5d = ic_table[ic_table["horizon"] == 5].dropna(subset=["mean_ic"])
    if not ic_5d.empty:
        ic_5d = ic_5d.sort_values("mean_ic")
        colors = ["#b54a4a" if v < 0 else "#337a5b" for v in ic_5d["mean_ic"]]
        ax.barh(ic_5d["signal"], ic_5d["mean_ic"], color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_title("5D Mean Rank IC")
    else:
        ax.text(0.5, 0.5, "No 5D IC data", ha="center", va="center")
        ax.set_axis_off()

    ax = axes[0, 1]
    icir = ic_table[ic_table["horizon"] == 5].dropna(subset=["icir"])
    if not icir.empty:
        icir = icir.sort_values("icir")
        colors = ["#b54a4a" if v < 0 else "#3b6f9e" for v in icir["icir"]]
        ax.barh(icir["signal"], icir["icir"], color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.axvline(0.3, color="#337a5b", linestyle="--", linewidth=1.0)
        ax.set_title("5D ICIR")
    else:
        ax.text(0.5, 0.5, "No ICIR data", ha="center", va="center")
        ax.set_axis_off()

    ax = axes[1, 0]
    if not fm_table.empty and "t_stat_nw" in fm_table.columns:
        fm = fm_table.dropna(subset=["t_stat_nw"]).sort_values("t_stat_nw")
        colors = ["#337a5b" if abs(v) > 2 else "#64748b" for v in fm["t_stat_nw"]]
        ax.barh(fm.index.astype(str), fm["t_stat_nw"], color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.axvline(2, color="#337a5b", linestyle="--", linewidth=1.0)
        ax.axvline(-2, color="#337a5b", linestyle="--", linewidth=1.0)
        ax.set_title("Fama-MacBeth Newey-West t-stat")
    else:
        ax.text(0.5, 0.5, "No FM data", ha="center", va="center")
        ax.set_axis_off()

    ax = axes[1, 1]
    q_cols = [col for col in ["Q1", "Q2", "Q3", "Q4", "Q5"] if col in quintiles.columns]
    if q_cols:
        quintiles[q_cols].mean().plot(kind="bar", ax=ax, color="#4f7cac")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Mean Forward Return By Signal Quintile")
        ax.tick_params(axis="x", rotation=0)
    else:
        ax.text(0.5, 0.5, "No quintile data", ha="center", va="center")
        ax.set_axis_off()

    for ax in axes.flat:
        ax.grid(axis="x", alpha=0.2)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return output_path
