import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ROUTE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "route_data.csv"
)

RECOVERY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "row_level_recovery_results.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "final_evaluation_results.csv"
)


def main():

    print("=" * 60)
    print("FINAL ROW-LEVEL EVALUATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load data
    # ---------------------------------------------------------

    print("\nLoading datasets...")

    df = pd.read_csv(ROUTE_FILE)

    recovery = pd.read_csv(RECOVERY_FILE)

    print(
        f"Original records: {len(df):,}"
    )

    print(
        f"Recovery records: {len(recovery):,}"
    )

    evaluation = []

    # ---------------------------------------------------------
    # Evaluate each disruption
    # ---------------------------------------------------------

    disruption_modes = [
        "Standard Class",
        "Second Class",
        "First Class",
        "Same Day"
    ]

    for mode in disruption_modes:

        print("\n" + "-" * 60)

        print(
            f"Evaluating disruption: {mode}"
        )

        # -----------------------------------------------------
        # Affected records
        # -----------------------------------------------------

        affected = df[
            df["Shipping Mode"] == mode
        ].copy()

        scenario = recovery[
            recovery["Disrupted Mode"] == mode
        ].copy()

        # -----------------------------------------------------
        # Baseline metrics
        # -----------------------------------------------------

        baseline_delay = (
            affected[
                "Shipping Delay"
            ].mean()
        )

        baseline_shipping_days = (
            affected[
                "Days for shipping (real)"
            ].mean()
        )

        baseline_delay_rate = (
            affected[
                "Is Delayed"
            ].mean()
            * 100
        )

        # -----------------------------------------------------
        # Recovery metrics
        # -----------------------------------------------------

        recovery_expected_delay = (
            scenario[
                "Expected Delay"
            ].mean()
        )

        recovery_cost = (
            scenario[
                "Estimated Logistics Cost"
            ].mean()
        )

        recovery_score = (
            scenario[
                "Heuristic Score"
            ].mean()
        )

        # -----------------------------------------------------
        # Recovery rate
        # -----------------------------------------------------

        affected_count = len(affected)

        recovered_count = len(scenario)

        recovery_rate = (
            recovered_count
            / affected_count
            * 100
        )

        # -----------------------------------------------------
        # Delay improvement
        # -----------------------------------------------------

        delay_improvement = (
            baseline_delay
            - recovery_expected_delay
        )

        # -----------------------------------------------------
        # Shipping-time difference
        # -----------------------------------------------------

        shipping_time_difference = (
            baseline_shipping_days
            - recovery_expected_delay
        )

        # -----------------------------------------------------
        # Recovery mode distribution
        # -----------------------------------------------------

        recovery_modes = (
            scenario[
                "Recovered Shipping Mode"
            ]
            .value_counts()
        )

        selected_mode = (
            recovery_modes
            .idxmax()
        )

        selected_mode_count = (
            recovery_modes
            .max()
        )

        # -----------------------------------------------------
        # Store metrics
        # -----------------------------------------------------

        evaluation.append({

            "Disrupted Mode":
                mode,

            "Affected Records":
                affected_count,

            "Recovered Records":
                recovered_count,

            "Recovery Rate (%)":
                recovery_rate,

            "Baseline Avg Shipping Days":
                baseline_shipping_days,

            "Baseline Avg Delay":
                baseline_delay,

            "Baseline Delay Rate (%)":
                baseline_delay_rate,

            "Recovery Expected Delay":
                recovery_expected_delay,

            "Delay Improvement":
                delay_improvement,

            "Recovery Avg Estimated Cost":
                recovery_cost,

            "Recovery Avg Heuristic Score":
                recovery_score,

            "Primary Recovery Mode":
                selected_mode,

            "Primary Recovery Count":
                selected_mode_count
        })

        # -----------------------------------------------------
        # Print results
        # -----------------------------------------------------

        print(
            f"Affected Records: "
            f"{affected_count:,}"
        )

        print(
            f"Recovered Records: "
            f"{recovered_count:,}"
        )

        print(
            f"Recovery Rate: "
            f"{recovery_rate:.2f}%"
        )

        print(
            f"Baseline Avg Shipping: "
            f"{baseline_shipping_days:.2f} days"
        )

        print(
            f"Baseline Avg Delay: "
            f"{baseline_delay:.2f} days"
        )

        print(
            f"Baseline Delay Rate: "
            f"{baseline_delay_rate:.2f}%"
        )

        print(
            f"Recovery Expected Delay: "
            f"{recovery_expected_delay:.2f} days"
        )

        print(
            f"Delay Improvement: "
            f"{delay_improvement:.2f} days"
        )

        print(
            f"Estimated Recovery Cost: "
            f"{recovery_cost:.2f}"
        )

        print(
            f"Primary Recovery Mode: "
            f"{selected_mode}"
        )

    # ---------------------------------------------------------
    # Create dataframe
    # ---------------------------------------------------------

    results = pd.DataFrame(
        evaluation
    )

    # ---------------------------------------------------------
    # Save results
    # ---------------------------------------------------------

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "FINAL EVALUATION SUMMARY"
    )

    print("=" * 60)

    print(
        results.to_string(
            index=False
        )
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "EVALUATION COMPLETE"
    )

    print("=" * 60)


if __name__ == "__main__":

    main()