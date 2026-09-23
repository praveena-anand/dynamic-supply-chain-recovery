import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "DataCoSupplyChainDataset.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "supply_chain_subset.csv"
)


# ============================================================
# SETTINGS
# ============================================================

TARGET_ROWS = 10000
RANDOM_STATE = 42


# ============================================================
# COLUMNS WE NEED
# ============================================================

REQUIRED_COLUMNS = [
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Benefit per order",
    "Sales per customer",

    "Delivery Status",
    "Late_delivery_risk",

    "Category Id",
    "Category Name",

    "Customer City",
    "Customer Country",
    "Customer Id",
    "Customer Segment",

    "Market",

    "Order City",
    "Order Country",
    "Order Customer Id",
    "Order Region",
    "Order State",

    "Order Id",
    "Order Item Id",
    "Order Item Quantity",
    "Order Item Total",

    "Sales",
    "Order Profit Per Order",

    "Shipping Mode",

    "order date (DateOrders)",
    "shipping date (DateOrders)",

    "Product Name",
    "Product Price"
]


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():

    print("=" * 60)
    print("DYNAMIC SUPPLY CHAIN RECOVERY")
    print("DATA PREPROCESSING")
    print("=" * 60)


    # --------------------------------------------------------
    # STEP 1: CHECK DATASET
    # --------------------------------------------------------

    print("\nSTEP 1: Checking dataset...")

    if not INPUT_FILE.exists():

        print("ERROR: Dataset not found!")

        print("\nExpected location:")
        print(INPUT_FILE)

        return

    print("Dataset found!")


    # --------------------------------------------------------
    # STEP 2: LOAD DATASET
    # --------------------------------------------------------

    print("\nSTEP 2: Loading DataCo dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        encoding="latin1"
    )

    print("Original rows:", len(df))
    print("Original columns:", len(df.columns))


    # --------------------------------------------------------
    # STEP 3: CHECK REQUIRED COLUMNS
    # --------------------------------------------------------

    print("\nSTEP 3: Checking required columns...")

    missing_columns = []

    for column in REQUIRED_COLUMNS:

        if column not in df.columns:

            missing_columns.append(column)


    if missing_columns:

        print("\nERROR: These columns are missing:")

        for column in missing_columns:

            print("-", column)

        return


    print("All required columns found!")


    # --------------------------------------------------------
    # STEP 4: SELECT ONLY REQUIRED COLUMNS
    # --------------------------------------------------------

    print("\nSTEP 4: Selecting useful columns...")

    df = df[REQUIRED_COLUMNS].copy()

    print("Columns retained:", len(df.columns))


    # --------------------------------------------------------
    # STEP 5: CONVERT DATE COLUMNS
    # --------------------------------------------------------

    print("\nSTEP 5: Converting date columns...")

    df["order date (DateOrders)"] = pd.to_datetime(
        df["order date (DateOrders)"],
        errors="coerce"
    )

    df["shipping date (DateOrders)"] = pd.to_datetime(
        df["shipping date (DateOrders)"],
        errors="coerce"
    )

    print("Dates converted!")


    # --------------------------------------------------------
    # STEP 6: FILTER EUROPE
    # --------------------------------------------------------

    print("\nSTEP 6: Filtering Europe...")

    europe_df = df[
        df["Market"]
        .astype(str)
        .str.strip()
        .str.lower()
        == "europe"
    ].copy()

    print("European records:", len(europe_df))


    # --------------------------------------------------------
    # STEP 7: SELECT 10,000 RECORDS
    # --------------------------------------------------------

    print("\nSTEP 7: Selecting records...")

    if len(europe_df) >= TARGET_ROWS:

        subset = europe_df.sample(
            n=TARGET_ROWS,
            random_state=RANDOM_STATE
        ).copy()

    else:

        print(
            "Europe has fewer than 10,000 records."
        )

        subset = europe_df.copy()


    print("Selected records:", len(subset))


    # --------------------------------------------------------
    # STEP 8: REMOVE MISSING VALUES
    # --------------------------------------------------------

    print("\nSTEP 8: Removing invalid records...")

    important_columns = [
        "Order Id",
        "Order Item Id",
        "Order Region",
        "Order City",
        "Order Item Quantity",
        "Shipping Mode",
        "Delivery Status",
        "Days for shipping (real)",
        "Days for shipment (scheduled)"
    ]

    before = len(subset)

    subset = subset.dropna(
        subset=important_columns
    )

    after = len(subset)

    print(
        "Removed records:",
        before - after
    )


    # --------------------------------------------------------
    # STEP 9: REMOVE INVALID QUANTITIES
    # --------------------------------------------------------

    subset = subset[
        subset["Order Item Quantity"] > 0
    ]


    # --------------------------------------------------------
    # STEP 10: REMOVE INVALID SHIPPING DAYS
    # --------------------------------------------------------

    subset = subset[
        subset["Days for shipping (real)"] >= 0
    ]

    subset = subset[
        subset["Days for shipment (scheduled)"] >= 0
    ]


    # --------------------------------------------------------
    # STEP 11: CREATE SHIPPING DELAY
    # --------------------------------------------------------

    print("\nSTEP 9: Creating derived features...")

    subset["Shipping Delay"] = (
        subset["Days for shipping (real)"]
        -
        subset["Days for shipment (scheduled)"]
    )


    # --------------------------------------------------------
    # STEP 12: CREATE DELAY FLAG
    # --------------------------------------------------------

    subset["Is Delayed"] = (
        subset["Shipping Delay"] > 0
    ).astype(int)


    # --------------------------------------------------------
    # STEP 13: CREATE REVENUE PER UNIT
    # --------------------------------------------------------

    subset["Revenue Per Unit"] = (
        subset["Sales"]
        /
        subset["Order Item Quantity"].replace(0, 1)
    )


    # --------------------------------------------------------
    # STEP 14: SORT BY DATE
    # --------------------------------------------------------

    subset = subset.sort_values(
        "order date (DateOrders)"
    )

    subset = subset.reset_index(drop=True)


    # --------------------------------------------------------
    # STEP 15: CREATE OUTPUT FOLDER
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # STEP 16: SAVE DATASET
    # --------------------------------------------------------

    print("\nSTEP 10: Saving processed dataset...")

    subset.to_csv(
        OUTPUT_FILE,
        index=False
    )


    # ========================================================
    # FINAL REPORT
    # ========================================================

    print("\n")
    print("=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)

    print("\nOriginal dataset:")
    print(f"{len(df):,} records")

    print("\nEurope dataset:")
    print(f"{len(europe_df):,} records")

    print("\nFinal dataset:")
    print(f"{len(subset):,} records")

    print("\nFinal columns:")
    print(f"{len(subset.columns)} columns")

    print("\nShipping modes:")

    print(
        subset["Shipping Mode"]
        .value_counts()
    )

    print("\nDelivery status:")

    print(
        subset["Delivery Status"]
        .value_counts()
    )

    print("\nOrder regions:")

    print(
        subset["Order Region"]
        .value_counts()
        .head(10)
    )

    print("\nSaved file:")

    print(OUTPUT_FILE)

    print("\n" + "=" * 60)


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()