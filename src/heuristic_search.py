import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "route_data.csv"
)


class HeuristicSearch:

    def __init__(self, data):

        self.data = data.copy()

        self.mode_profiles = (
            self.data
            .groupby("Shipping Mode")
            .agg(
                Average_Shipping_Days=(
                    "Days for shipping (real)",
                    "mean"
                ),

                Average_Scheduled_Days=(
                    "Days for shipment (scheduled)",
                    "mean"
                ),

                Average_Delay=(
                    "Shipping Delay",
                    "mean"
                ),

                Delay_Rate=(
                    "Is Delayed",
                    "mean"
                )
            )
            .reset_index()
        )

    # ---------------------------------------------------------
    # Estimated logistics cost
    # ---------------------------------------------------------

    def estimate_logistics_cost(
        self,
        quantity,
        shipping_mode
    ):

        mode_cost = {

            "Standard Class": 8,

            "Second Class": 12,

            "First Class": 18,

            "Same Day": 25
        }

        base_cost = mode_cost.get(
            shipping_mode,
            10
        )

        quantity_cost = quantity * 2

        return base_cost + quantity_cost

    # ---------------------------------------------------------
    # Get historical profile
    # ---------------------------------------------------------

    def get_mode_profile(
        self,
        shipping_mode
    ):

        profile = self.mode_profiles[
            self.mode_profiles["Shipping Mode"]
            == shipping_mode
        ]

        if profile.empty:

            return None

        return profile.iloc[0]

    # ---------------------------------------------------------
    # Calculate expected shipping performance
    # ---------------------------------------------------------

    def calculate_expected_delay(
        self,
        scheduled_days,
        shipping_mode
    ):

        profile = self.get_mode_profile(
            shipping_mode
        )

        if profile is None:

            return 0

        average_shipping_days = (
            profile["Average_Shipping_Days"]
        )

        expected_delay = (
            average_shipping_days
            - scheduled_days
        )

        return max(
            expected_delay,
            0
        )

    # ---------------------------------------------------------
    # Calculate heuristic score
    # ---------------------------------------------------------

    def calculate_score(
        self,
        quantity,
        scheduled_days,
        shipping_mode,
        original_delay,
        disrupted_mode=None
    ):

        # ---------------------------------------------
        # 1. Logistics cost
        # ---------------------------------------------

        logistics_cost = (
            self.estimate_logistics_cost(
                quantity,
                shipping_mode
            )
        )

        # ---------------------------------------------
        # 2. Expected delay
        # ---------------------------------------------

        expected_delay = (
            self.calculate_expected_delay(
                scheduled_days,
                shipping_mode
            )
        )

        delay_penalty = (
            expected_delay * 20
        )

        # ---------------------------------------------
        # 3. Historical reliability
        # ---------------------------------------------

        profile = self.get_mode_profile(
            shipping_mode
        )

        if profile is not None:

            delay_rate = (
                profile["Delay_Rate"]
            )

        else:

            delay_rate = 0.5

        historical_delay_penalty = (
            delay_rate * 15
        )

        # ---------------------------------------------
        # 4. Recovery stability penalty
        # ---------------------------------------------

        # If the original order was already delayed,
        # prefer alternatives with lower historical
        # delay rates.

        recovery_penalty = 0

        if original_delay > 0:

            recovery_penalty = (
                delay_rate * 10
            )

        # ---------------------------------------------
        # 5. Disruption penalty
        # ---------------------------------------------

        disruption_penalty = 0

        if (
            disrupted_mode is not None
            and shipping_mode == disrupted_mode
        ):

            disruption_penalty = 1000

        # ---------------------------------------------
        # Final heuristic score
        # ---------------------------------------------

        score = (

            logistics_cost

            + delay_penalty

            + historical_delay_penalty

            + recovery_penalty

            + disruption_penalty
        )

        return {

            "score": score,

            "logistics_cost":
                logistics_cost,

            "expected_delay":
                expected_delay,

            "delay_penalty":
                delay_penalty,

            "historical_delay_penalty":
                historical_delay_penalty,

            "recovery_penalty":
                recovery_penalty,

            "disruption_penalty":
                disruption_penalty
        }

    # ---------------------------------------------------------
    # Evaluate all alternative shipping modes
    # ---------------------------------------------------------

    def evaluate_shipping_modes(
        self,
        order_id,
        disrupted_mode=None
    ):

        order_data = self.data[
            self.data["Order Id"]
            == order_id
        ]

        if order_data.empty:

            return pd.DataFrame()

        row = order_data.iloc[0]

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

        shipping_modes = [

            "Standard Class",

            "Second Class",

            "First Class",

            "Same Day"
        ]

        candidates = []

        for mode in shipping_modes:

            # Do not use disrupted mode

            if (
                disrupted_mode is not None
                and mode == disrupted_mode
            ):

                continue

            result = self.calculate_score(

                quantity,

                scheduled_days,

                mode,

                original_delay,

                disrupted_mode
            )

            candidates.append({

                "Order Id":
                    order_id,

                "Shipping Mode":
                    mode,

                "Heuristic Score":
                    round(
                        result["score"],
                        2
                    ),

                "Estimated Logistics Cost":
                    round(
                        result[
                            "logistics_cost"
                        ],
                        2
                    ),

                "Expected Delay":
                    round(
                        result[
                            "expected_delay"
                        ],
                        2
                    ),

                "Delay Penalty":
                    round(
                        result[
                            "delay_penalty"
                        ],
                        2
                    ),

                "Historical Delay Penalty":
                    round(
                        result[
                            "historical_delay_penalty"
                        ],
                        2
                    ),

                "Recovery Penalty":
                    round(
                        result[
                            "recovery_penalty"
                        ],
                        2
                    )
            })

        return (
            pd.DataFrame(candidates)
            .sort_values(
                "Heuristic Score"
            )
            .reset_index(drop=True)
        )

    # ---------------------------------------------------------
    # Find best recovery
    # ---------------------------------------------------------

    def find_best_recovery(
        self,
        order_id,
        disrupted_mode
    ):

        results = (
            self.evaluate_shipping_modes(
                order_id,
                disrupted_mode
            )
        )

        if results.empty:

            return None

        return results.iloc[0]


# =============================================================
# TEST
# =============================================================

def main():

    print("=" * 60)
    print("HEURISTIC SEARCH ENGINE")
    print("=" * 60)

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

    planner = HeuristicSearch(
        df
    )

    # ---------------------------------------------------------
    # Historical profiles
    # ---------------------------------------------------------

    print(
        "\nHistorical Shipping Profiles:"
    )

    print(
        planner.mode_profiles.to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Example order
    # ---------------------------------------------------------

    example_order = (
        df["Order Id"].iloc[0]
    )

    disrupted_mode = (
        "Standard Class"
    )

    print(
        "\nExample Order:",
        example_order
    )

    print(
        "\nDisruption:",
        disrupted_mode,
        "unavailable"
    )

    results = (
        planner.evaluate_shipping_modes(
            example_order,
            disrupted_mode
        )
    )

    print(
        "\nCandidate Recovery Options:"
    )

    print(
        results.to_string(
            index=False
        )
    )

    # ---------------------------------------------------------
    # Best recovery
    # ---------------------------------------------------------

    best = (
        planner.find_best_recovery(
            example_order,
            disrupted_mode
        )
    )

    print(
        "\n" + "=" * 60
    )

    print(
        "BEST RECOVERY OPTION"
    )

    print(
        "=" * 60
    )

    if best is not None:

        print(
            "\nSelected Mode:",
            best["Shipping Mode"]
        )

        print(
            "Heuristic Score:",
            best["Heuristic Score"]
        )

        print(
            "Estimated Cost:",
            best[
                "Estimated Logistics Cost"
            ]
        )

        print(
            "Expected Delay:",
            best["Expected Delay"]
        )

    print(
        "\n" + "=" * 60
    )


if __name__ == "__main__":

    main()