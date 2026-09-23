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
    / "disruption_results.csv"
)


def main():

    print("=" * 60)
    print("SUPPLY CHAIN DISRUPTION RECOVERY ENGINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load data
    # ---------------------------------------------------------

    print("\nLoading route data...")

    if not INPUT_FILE.exists():
        print("ERROR: route_data.csv not found.")
        return

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df):,} records.")

    # ---------------------------------------------------------
    # 2. Create heuristic search engine
    # ---------------------------------------------------------

    planner = HeuristicSearch(df)

    # ---------------------------------------------------------
    # 3. Define disruption
    # ---------------------------------------------------------

    disrupted_mode = "Standard Class"

    print("\n" + "=" * 60)
    print("DISRUPTION SCENARIO")
    print("=" * 60)

    print(f"\nDisrupted Shipping Mode: {disrupted_mode}")

    affected_orders = df[
        df["Shipping Mode"] == disrupted_mode
    ]["Order Id"].unique()

    print(f"Affected Orders: {len(affected_orders):,}")

    # ---------------------------------------------------------
    # 4. Recover affected orders
    # ---------------------------------------------------------

    recovery_results = []

    print("\nRunning heuristic recovery...")

    for i, order_id in enumerate(affected_orders):

        best = planner.find_best_recovery(
            order_id,
            disrupted_mode
        )

        if best is not None:

            recovery_results.append({
                "Order Id": order_id,
                "Original Shipping Mode": disrupted_mode,
                "Recovered Shipping Mode": best["Shipping Mode"],
                "Heuristic Score": best["Heuristic Score"],
                "Estimated Logistics Cost": best["Estimated Logistics Cost"],
                "Expected Delay": best["Expected Delay"],
                "Delay Penalty": best["Delay Penalty"],
                "Historical Delay Penalty": best["Historical Delay Penalty"]
            })

        # Progress indicator
        if (i + 1) % 500 == 0:
            print(
                f"Processed {i + 1:,} / "
                f"{len(affected_orders):,} orders"
            )

    results = pd.DataFrame(recovery_results)

    # ---------------------------------------------------------
    # 5. Calculate recovery metrics
    # ---------------------------------------------------------

    if results.empty:

        print("\nNo recovery solutions found.")
        return

    recovered_orders = len(results)

    recovery_rate = (
        recovered_orders
        / len(affected_orders)
        * 100
    )

    average_score = results[
        "Heuristic Score"
    ].mean()

    average_cost = results[
        "Estimated Logistics Cost"
    ].mean()

    average_expected_delay = results[
        "Expected Delay"
    ].mean()

    # ---------------------------------------------------------
    # 6. Display results
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("RECOVERY RESULTS")
    print("=" * 60)

    print(
        f"\nAffected Orders: "
        f"{len(affected_orders):,}"
    )

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
        f"Average Estimated Logistics Cost: "
        f"{average_cost:.2f}"
    )

    print(
        f"Average Expected Delay: "
        f"{average_expected_delay:.2f} days"
    )

    # ---------------------------------------------------------
    # 7. Recovery mode distribution
    # ---------------------------------------------------------

    print("\nRecovery Shipping Mode Distribution:")

    distribution = (
        results["Recovered Shipping Mode"]
        .value_counts()
    )

    print(distribution.to_string())

    # ---------------------------------------------------------
    # 8. Save results
    # ---------------------------------------------------------

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nResults saved to:")
    print(OUTPUT_FILE)

    print("\n" + "=" * 60)
    print("DISRUPTION RECOVERY COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()