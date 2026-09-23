import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "final_evaluation_results.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "figures"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def save_figure(
    filename
):

    path = OUTPUT_DIR / filename

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {path}"
    )


def main():

    print("=" * 60)
    print("SUPPLY CHAIN RESULT VISUALIZATION")
    print("=" * 60)

    df = pd.read_csv(
        INPUT_FILE
    )

    # =========================================================
    # Figure 1 — Affected Records
    # =========================================================

    plt.figure(
        figsize=(9, 5)
    )

    plt.bar(
        df["Disrupted Mode"],
        df["Affected Records"]
    )

    plt.title(
        "Affected Transactions by Disruption Scenario"
    )

    plt.xlabel(
        "Disrupted Shipping Mode"
    )

    plt.ylabel(
        "Number of Affected Transactions"
    )

    plt.xticks(
        rotation=20
    )

    save_figure(
        "affected_transactions.png"
    )

    # =========================================================
    # Figure 2 — Baseline vs Recovery Delay
    # =========================================================

    plt.figure(
        figsize=(9, 5)
    )

    x = range(
        len(df)
    )

    width = 0.35

    plt.bar(
        [i - width / 2 for i in x],
        df["Baseline Avg Delay"],
        width=width,
        label="Baseline Delay"
    )

    plt.bar(
        [i + width / 2 for i in x],
        df["Recovery Expected Delay"],
        width=width,
        label="Recovery Expected Delay"
    )

    plt.xticks(
        list(x),
        df["Disrupted Mode"],
        rotation=20
    )

    plt.title(
        "Baseline vs Expected Recovery Delay"
    )

    plt.xlabel(
        "Disruption Scenario"
    )

    plt.ylabel(
        "Delay (days)"
    )

    plt.legend()

    save_figure(
        "baseline_vs_recovery_delay.png"
    )

    # =========================================================
    # Figure 3 — Baseline Delay Rate
    # =========================================================

    plt.figure(
        figsize=(9, 5)
    )

    plt.bar(
        df["Disrupted Mode"],
        df["Baseline Delay Rate (%)"]
    )

    plt.title(
        "Historical Delay Rate of Disrupted Modes"
    )

    plt.xlabel(
        "Shipping Mode"
    )

    plt.ylabel(
        "Delayed Transactions (%)"
    )

    plt.xticks(
        rotation=20
    )

    save_figure(
        "delay_rate_by_mode.png"
    )

    # =========================================================
    # Figure 4 — Estimated Recovery Cost
    # =========================================================

    plt.figure(
        figsize=(9, 5)
    )

    plt.bar(
        df["Disrupted Mode"],
        df["Recovery Avg Estimated Cost"]
    )

    plt.title(
        "Average Estimated Recovery Logistics Cost"
    )

    plt.xlabel(
        "Disruption Scenario"
    )

    plt.ylabel(
        "Estimated Cost"
    )

    plt.xticks(
        rotation=20
    )

    save_figure(
        "recovery_cost.png"
    )

    # =========================================================
    # Figure 5 — Delay Improvement
    # =========================================================

    plt.figure(
        figsize=(9, 5)
    )

    plt.bar(
        df["Disrupted Mode"],
        df["Delay Improvement"]
    )

    plt.axhline(
        y=0,
        linewidth=1
    )

    plt.title(
        "Delay Improvement After Heuristic Recovery"
    )

    plt.xlabel(
        "Disruption Scenario"
    )

    plt.ylabel(
        "Delay Improvement (days)"
    )

    plt.xticks(
        rotation=20
    )

    save_figure(
        "delay_improvement.png"
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "VISUALIZATION COMPLETE"
    )

    print("=" * 60)

    print(
        f"\nFigures saved in:\n{OUTPUT_DIR}"
    )


if __name__ == "__main__":

    main()