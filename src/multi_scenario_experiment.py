import pandas as pd
from pathlib import Path
from heuristic_search import HeuristicSearch


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "route_data.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "multi_scenario_results.csv"
)


def run_scenario(
    planner,
    df,
    disrupted_mode
):

    print("\n" + "=" * 60)
    print(
        f"DISRUPTION: {disrupted_mode} UNAVAILABLE"
    )
    print("=" * 60)

    # ---------------------------------------------------------
    # Find affected orders
    # ---------------------------------------------------------

    affected_orders = (
        df[
            df["Shipping Mode"]
            == disrupted_mode
        ]["Order Id"]
        .unique()
    )

    print(
        f"\nAffected Orders: "
        f"{len(affected_orders):,}"
    )

    recovery_results = []

    # ---------------------------------------------------------
    # Run heuristic recovery
    # ---------------------------------------------------------

    for order_id in affected_orders:

        best = planner.find_best_recovery(
            order_id,
            disrupted_mode
        )

        if best is not None:

            recovery_results.append({

                "Disrupted Mode":
                    disrupted_mode,

                "Order Id":
                    order_id,

                "Recovered Shipping Mode":
                    best["Shipping Mode"],

                "Heuristic Score":
                    best["Heuristic Score"],

                "Estimated Logistics Cost":
                    best[
                        "Estimated Logistics Cost"
                    ],

                "Expected Delay":
                    best["Expected Delay"],

                "Delay Penalty":
                    best["Delay Penalty"],

                "Historical Delay Penalty":
                    best[
                        "Historical Delay Penalty"
                    ],

                "Recovery Penalty":
                    best["Recovery Penalty"]
            })

    results = pd.DataFrame(
        recovery_results
    )

    # ---------------------------------------------------------
    # Calculate metrics
    # ---------------------------------------------------------

    recovered_orders = len(results)

    if len(affected_orders) > 0:

        recovery_rate = (
            recovered_orders
            / len(affected_orders)
            * 100
        )

    else:

        recovery_rate = 0

    if not results.empty:

        average_score = (
            results[
                "Heuristic Score"
            ].mean()
        )

        average_cost = (
            results[
                "Estimated Logistics Cost"
            ].mean()
        )

        average_delay = (
            results[
                "Expected Delay"
            ].mean()
        )

    else:

        average_score = 0
        average_cost = 0
        average_delay = 0

    # ---------------------------------------------------------
    # Display scenario results
    # ---------------------------------------------------------

    print(
        f"Recovered Orders: "
        f"{recovered_orders:,}"
    )

    print(
        f"Recovery Rate: "
        f"{recovery_rate:.2f}%"
    )

    print(
        f"Average Heuristic Score: "
        f"{average_score:.2f}"
    )

    print(
        f"Average Estimated Cost: "
        f"{average_cost:.2f}"
    )

    print(
        f"Average Expected Delay: "
        f"{average_delay:.2f} days"
    )

    # ---------------------------------------------------------
    # Recovery distribution
    # ---------------------------------------------------------

    print(
        "\nRecovery Shipping Mode Distribution:"
    )

    if not results.empty:

        distribution = (
            results[
                "Recovered Shipping Mode"
            ]
            .value_counts()
        )

        print(
            distribution.to_string()
        )

    return results


def main():

    print("=" * 60)
    print("MULTI-SCENARIO SUPPLY CHAIN EXPERIMENT")
    print("=" * 60)

    # ---------------------------------------------------------
    # Load data
    # ---------------------------------------------------------

    print("\nLoading route data...")

    if not INPUT_FILE.exists():

        print(
            "ERROR: route_data.csv not found."
        )

        return

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Loaded {len(df):,} records."
    )

    # ---------------------------------------------------------
    # Create heuristic planner
    # ---------------------------------------------------------

    planner = HeuristicSearch(
        df
    )

    # ---------------------------------------------------------
    # Disruption scenarios
    # ---------------------------------------------------------

    disruption_modes = [

        "Standard Class",

        "Second Class",

        "First Class",

        "Same Day"
    ]

    all_results = []

    # ---------------------------------------------------------
    # Run all scenarios
    # ---------------------------------------------------------

    for mode in disruption_modes:

        scenario_results = run_scenario(

            planner,

            df,

            mode
        )

        if not scenario_results.empty:

            all_results.append(
                scenario_results
            )

    # ---------------------------------------------------------
    # Combine results
    # ---------------------------------------------------------

    if not all_results:

        print(
            "\nNo recovery results generated."
        )

        return

    final_results = pd.concat(
        all_results,
        ignore_index=True
    )

    # ---------------------------------------------------------
    # Save detailed results
    # ---------------------------------------------------------

    final_results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # Overall summary
    # ---------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "MULTI-SCENARIO SUMMARY"
    )

    print(
        "=" * 60
    )

    summary = (
        final_results
        .groupby("Disrupted Mode")
        .agg(
            Affected_Orders=(
                "Order Id",
                "count"
            ),

            Average_Score=(
                "Heuristic Score",
                "mean"
            ),

            Average_Cost=(
                "Estimated Logistics Cost",
                "mean"
            ),

            Average_Expected_Delay=(
                "Expected Delay",
                "mean"
            )
        )
        .reset_index()
    )

    print(
        summary.to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Overall recovery distribution
    # ---------------------------------------------------------

    print(
        "\nOverall Recovery Decisions:"
    )

    distribution = (
        final_results
        .groupby(
            [
                "Disrupted Mode",
                "Recovered Shipping Mode"
            ]
        )
        .size()
        .reset_index(
            name="Orders"
        )
    )

    print(
        distribution.to_string(
            index=False
        )
    )

    print(
        "\nDetailed results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "MULTI-SCENARIO EXPERIMENT COMPLETE"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":

    main()