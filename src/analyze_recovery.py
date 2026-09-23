import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

ROUTE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "route_data.csv"
)


def main():

    print("=" * 60)
    print("RECOVERY MODE ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(ROUTE_FILE)

    # Only affected Standard Class orders
    affected = df[
        df["Shipping Mode"] == "Standard Class"
    ].copy()

    print(
        f"\nAffected orders: {len(affected):,}"
    )

    print("\nOriginal Order Characteristics")
    print("-" * 60)

    print(
        affected[
            [
                "Days for shipment (scheduled)",
                "Days for shipping (real)",
                "Shipping Delay",
                "Order Item Quantity"
            ]
        ].describe().to_string()
    )

    # ---------------------------------------------------------
    # Shipping mode profiles
    # ---------------------------------------------------------

    profiles = (
        df.groupby("Shipping Mode")
        .agg(
            Orders=("Order Id", "count"),
            Avg_Shipping_Days=(
                "Days for shipping (real)",
                "mean"
            ),
            Avg_Scheduled_Days=(
                "Days for shipment (scheduled)",
                "mean"
            ),
            Avg_Delay=(
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

    profiles["Delay_Rate_%"] = (
        profiles["Delay_Rate"] * 100
    )

    print(
        "\nShipping Mode Performance"
    )

    print(
        profiles[
            [
                "Shipping Mode",
                "Orders",
                "Avg_Shipping_Days",
                "Avg_Scheduled_Days",
                "Avg_Delay",
                "Delay_Rate_%"
            ]
        ].to_string(index=False)
    )

    # ---------------------------------------------------------
    # Scheduled-day distribution
    # ---------------------------------------------------------

    print(
        "\nScheduled Delivery Requirement"
    )

    print(
        affected[
            "Days for shipment (scheduled)"
        ]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # ---------------------------------------------------------
    # Actual shipping mode distribution
    # ---------------------------------------------------------

    print(
        "\nOriginal Shipping Mode Distribution"
    )

    print(
        df["Shipping Mode"]
        .value_counts()
        .to_string()
    )

    print(
        "\n" + "=" * 60
    )
    print(
        "ANALYSIS COMPLETE"
    )
    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()