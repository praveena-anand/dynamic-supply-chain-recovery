import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ROUTE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "route_data.csv"
)

RESULT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "multi_scenario_results.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "evaluation_results.csv"
)


def calculate_baseline(
    affected_orders,
    disrupted_mode
):

    # Actual performance of the affected orders
    baseline_delay = (
        affected_orders[
            "Shipping Delay"
        ].mean()
    )

    baseline_shipping_days = (
        affected_orders[
            "Days for shipping (real)"
        ].mean()
    )

    baseline_quantity = (
        affected_orders[
            "Order Item Quantity"
        ].mean()
    )

    return {

        "Baseline Average Delay":
            baseline_delay,

        "Baseline Average Shipping Days":
            baseline_shipping_days,

        "Baseline Average Quantity":
            baseline_quantity
    }


def main():

    print("=" * 60)
    print("SUPPLY CHAIN RECOVERY EVALUATION")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load data
    # ---------------------------------------------------------

    print("\nLoading datasets...")

    df = pd.read_csv(
        ROUTE_FILE
    )

    recovery = pd.read_csv(
        RESULT_FILE
    )

    print(
        f"Route records: {len(df):,}"
    )

    print(
        f"Recovery records: {len(recovery):,}"
    )

    evaluation_results = []

    # ---------------------------------------------------------
    # Evaluate each disruption
    # ---------------------------------------------------------

    disruption_modes = recovery[
        "Disrupted Mode"
    ].unique()

    for disrupted_mode in disruption_modes:

        print(
            "\n" + "-" * 60
        )

        print(
            f"Evaluating: {disrupted_mode}"
        )

        # -----------------------------------------------------
        # Affected orders
        # -----------------------------------------------------

        affected = df[
            df["Shipping Mode"]
            == disrupted_mode
        ].copy()

        # -----------------------------------------------------
        # Recovery results
        # -----------------------------------------------------

        scenario_recovery = recovery[
            recovery["Disrupted Mode"]
            == disrupted_mode
        ].copy()

        # -----------------------------------------------------
        # Baseline
        # -----------------------------------------------------

        baseline = calculate_baseline(
            affected,
            disrupted_mode
        )

        # -----------------------------------------------------
        # Recovery metrics
        # -----------------------------------------------------

        recovery_delay = (
            scenario_recovery[
                "Expected Delay"
            ].mean()
        )

        recovery_cost = (
            scenario_recovery[
                "Estimated Logistics Cost"
            ].mean()
        )

        recovery_score = (
            scenario_recovery[
                "Heuristic Score"
            ].mean()
        )

        affected_count = len(
            affected
        )

        recovered_count = len(
            scenario_recovery
        )

        recovery_rate = (
            recovered_count
            / affected_count
            * 100
        )

        # -----------------------------------------------------
        # Delay improvement
        # -----------------------------------------------------

        delay_improvement = (
            baseline[
                "Baseline Average Delay"
            ]
            - recovery_delay
        )

        # -----------------------------------------------------
        # Store results
        # -----------------------------------------------------

        evaluation_results.append({

            "Disrupted Mode":
                disrupted_mode,

            "Affected Orders":
                affected_count,

            "Recovered Orders":
                recovered_count,

            "Recovery Rate (%)":
                recovery_rate,

            "Baseline Avg Delay":
                baseline[
                    "Baseline Average Delay"
                ],

            "Recovery Expected Delay":
                recovery_delay,

            "Delay Improvement":
                delay_improvement,

            "Baseline Avg Shipping Days":
                baseline[
                    "Baseline Average Shipping Days"
                ],

            "Recovery Avg Estimated Cost":
                recovery_cost,

            "Recovery Avg Heuristic Score":
                recovery_score
        })

        # -----------------------------------------------------
        # Print scenario
        # -----------------------------------------------------

        print(
            f"Affected Orders: "
            f"{affected_count:,}"
        )

        print(
            f"Recovered Orders: "
            f"{recovered_count:,}"
        )

        print(
            f"Recovery Rate: "
            f"{recovery_rate:.2f}%"
        )

        print(
            f"Baseline Avg Delay: "
            f"{baseline['Baseline Average Delay']:.2f} days"
        )

        print(
            f"Recovery Expected Delay: "
            f"{recovery_delay:.2f} days"
        )

        print(
            f"Delay Improvement: "
            f"{delay_improvement:.2f} days"
        )

        print(
            f"Estimated Recovery Cost: "
            f"{recovery_cost:.2f}"
        )

    # ---------------------------------------------------------
    # Save evaluation
    # ---------------------------------------------------------

    evaluation_df = pd.DataFrame(
        evaluation_results
    )

    evaluation_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "FINAL EVALUATION SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        evaluation_df.to_string(
            index=False
        )
    )

    print(
        "\nEvaluation results saved to:"
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

    print(
        "=" * 60
    )


if __name__ == "__main__":

    main()