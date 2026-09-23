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
    / "row_level_recovery_results.csv"
)


def main():

    print("=" * 60)
    print("ROW-LEVEL SUPPLY CHAIN RECOVERY")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load dataset
    # ---------------------------------------------------------

    print("\nLoading route data...")

    if not INPUT_FILE.exists():

        print("ERROR: route_data.csv not found.")
        return

    df = pd.read_csv(INPUT_FILE)

    print(
        f"Loaded {len(df):,} records."
    )

    # ---------------------------------------------------------
    # 2. Create unique row identifier
    # ---------------------------------------------------------

    df = df.reset_index(drop=True)

    df["Record Id"] = df.index + 1

    # ---------------------------------------------------------
    # 3. Create heuristic planner
    # ---------------------------------------------------------

    planner = HeuristicSearch(df)

    shipping_modes = [

        "Standard Class",
        "Second Class",
        "First Class",
        "Same Day"
    ]

    all_results = []

    # ---------------------------------------------------------
    # 4. Process each disruption
    # ---------------------------------------------------------

    for disrupted_mode in shipping_modes:

        print("\n" + "=" * 60)

        print(
            f"DISRUPTION: {disrupted_mode}"
        )

        print("=" * 60)

        # -----------------------------------------------------
        # Select affected ROWS
        # -----------------------------------------------------

        affected = df[
            df["Shipping Mode"]
            == disrupted_mode
        ].copy()

        print(
            f"\nAffected records: "
            f"{len(affected):,}"
        )

        # -----------------------------------------------------
        # Evaluate every row independently
        # -----------------------------------------------------

        for counter, (_, row) in enumerate(
            affected.iterrows(),
            start=1
        ):

            quantity = (
                row["Order Item Quantity"]
            )

            scheduled_days = (
                row[
                    "Days for shipment (scheduled)"
                ]
            )

            original_delay = (
                row["Shipping Delay"]
            )

            candidates = []

            # -------------------------------------------------
            # Evaluate alternative modes
            # -------------------------------------------------

            for candidate_mode in shipping_modes:

                # Skip disrupted mode
                if candidate_mode == disrupted_mode:
                    continue

                result = planner.calculate_score(

                    quantity,

                    scheduled_days,

                    candidate_mode,

                    original_delay,

                    disrupted_mode
                )

                candidates.append({

                    "Shipping Mode":
                        candidate_mode,

                    "Heuristic Score":
                        result["score"],

                    "Estimated Logistics Cost":
                        result[
                            "logistics_cost"
                        ],

                    "Expected Delay":
                        result[
                            "expected_delay"
                        ],

                    "Delay Penalty":
                        result[
                            "delay_penalty"
                        ],

                    "Historical Delay Penalty":
                        result[
                            "historical_delay_penalty"
                        ],

                    "Recovery Penalty":
                        result[
                            "recovery_penalty"
                        ]
                })

            # -------------------------------------------------
            # Select minimum-score candidate
            # -------------------------------------------------

            candidate_df = pd.DataFrame(
                candidates
            )

            best = candidate_df.loc[
                candidate_df[
                    "Heuristic Score"
                ].idxmin()
            ]

            # -------------------------------------------------
            # Store result
            # -------------------------------------------------

            all_results.append({

                "Record Id":
                    row["Record Id"],

                "Order Id":
                    row["Order Id"],

                "Disrupted Mode":
                    disrupted_mode,

                "Original Shipping Mode":
                    row["Shipping Mode"],

                "Recovered Shipping Mode":
                    best["Shipping Mode"],

                "Original Shipping Days":
                    row[
                        "Days for shipping (real)"
                    ],

                "Original Scheduled Days":
                    scheduled_days,

                "Original Delay":
                    original_delay,

                "Quantity":
                    quantity,

                "Heuristic Score":
                    best[
                        "Heuristic Score"
                    ],

                "Estimated Logistics Cost":
                    best[
                        "Estimated Logistics Cost"
                    ],

                "Expected Delay":
                    best[
                        "Expected Delay"
                    ],

                "Delay Penalty":
                    best[
                        "Delay Penalty"
                    ],

                "Historical Delay Penalty":
                    best[
                        "Historical Delay Penalty"
                    ],

                "Recovery Penalty":
                    best[
                        "Recovery Penalty"
                    ]
            })

            # -------------------------------------------------
            # Progress
            # -------------------------------------------------

            if counter % 500 == 0:

                print(
                    f"Processed "
                    f"{counter:,} / "
                    f"{len(affected):,}"
                )

    # ---------------------------------------------------------
    # 5. Create results dataframe
    # ---------------------------------------------------------

    results = pd.DataFrame(
        all_results
    )

    # ---------------------------------------------------------
    # 6. Save results
    # ---------------------------------------------------------

    results.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ---------------------------------------------------------
    # 7. Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "ROW-LEVEL RECOVERY SUMMARY"
    )

    print("=" * 60)

    print(
        f"\nTotal recovery records: "
        f"{len(results):,}"
    )

    print(
        "\nRecords by disruption:"
    )

    print(
        results[
            "Disrupted Mode"
        ]
        .value_counts()
        .to_string()
    )

    print(
        "\nRecovery decisions:"
    )

    distribution = (
        results
        .groupby(
            [
                "Disrupted Mode",
                "Recovered Shipping Mode"
            ]
        )
        .size()
        .reset_index(
            name="Records"
        )
    )

    print(
        distribution.to_string(
            index=False
        )
    )

    print(
        "\nResults saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "ROW-LEVEL RECOVERY COMPLETE"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":

    main()