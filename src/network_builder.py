import pandas as pd
import networkx as nx
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "supply_chain_subset.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "route_data.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("\nLoading processed dataset...")

    if not INPUT_FILE.exists():

        print("ERROR: Processed dataset not found!")

        print(INPUT_FILE)

        return None

    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df):,} records.")

    return df


# ============================================================
# CREATE ROUTE DATA
# ============================================================

def create_route_data(df):

    print("\nCreating logistics route data...")

    route_data = df[
        [
            "Market",
            "Order Region",
            "Order Country",
            "Order City",
            "Customer Country",
            "Customer City",

            "Order Id",
            "Order Item Id",

            "Product Name",
            "Category Name",

            "Order Item Quantity",

            "Sales",
            "Order Item Total",
            "Order Profit Per Order",

            "Shipping Mode",

            "Days for shipping (real)",
            "Days for shipment (scheduled)",

            "Shipping Delay",
            "Is Delayed",

            "Delivery Status",
            "Late_delivery_risk"
        ]
    ].copy()


    # --------------------------------------------------------
    # Calculate route-level information
    # --------------------------------------------------------

    route_data["Route"] = (
        route_data["Order Region"].astype(str)
        + " → "
        + route_data["Order Country"].astype(str)
        + " → "
        + route_data["Order City"].astype(str)
    )


    # --------------------------------------------------------
    # Save route data
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    route_data.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Route data saved to: {OUTPUT_FILE}"
    )

    return route_data


# ============================================================
# BUILD NETWORK GRAPH
# ============================================================

def build_network(df):

    print("\nBuilding supply-chain graph...")

    graph = nx.DiGraph()


    # ========================================================
    # MARKET LEVEL
    # ========================================================

    markets = df["Market"].dropna().unique()

    for market in markets:

        graph.add_node(
            f"MARKET_{market}",
            node_type="market",
            name=market
        )


    # ========================================================
    # REGION LEVEL
    # ========================================================

    regions = df[
        ["Market", "Order Region"]
    ].drop_duplicates()

    for _, row in regions.iterrows():

        market = row["Market"]
        region = row["Order Region"]

        market_node = f"MARKET_{market}"
        region_node = f"REGION_{region}"

        graph.add_node(
            region_node,
            node_type="region",
            name=region
        )

        graph.add_edge(
            market_node,
            region_node,
            weight=1
        )


    # ========================================================
    # COUNTRY LEVEL
    # ========================================================

    countries = df[
        ["Order Region", "Order Country"]
    ].drop_duplicates()

    for _, row in countries.iterrows():

        region = row["Order Region"]
        country = row["Order Country"]

        region_node = f"REGION_{region}"
        country_node = f"COUNTRY_{country}"

        graph.add_node(
            country_node,
            node_type="country",
            name=country
        )

        graph.add_edge(
            region_node,
            country_node,
            weight=1
        )


    # ========================================================
    # CITY LEVEL
    # ========================================================

    cities = df[
        [
            "Order Country",
            "Order City"
        ]
    ].drop_duplicates()

    for _, row in cities.iterrows():

        country = row["Order Country"]
        city = row["Order City"]

        country_node = f"COUNTRY_{country}"
        city_node = f"CITY_{city}"

        graph.add_node(
            city_node,
            node_type="city",
            name=city
        )

        graph.add_edge(
            country_node,
            city_node,
            weight=1
        )


    # ========================================================
    # ORDER LEVEL
    # ========================================================

    orders = df[
        [
            "Order City",
            "Order Id",
            "Order Item Quantity",
            "Sales",
            "Shipping Mode",
            "Days for shipping (real)",
            "Shipping Delay"
        ]
    ].drop_duplicates()


    for _, row in orders.iterrows():

        city = row["Order City"]
        order_id = row["Order Id"]

        city_node = f"CITY_{city}"
        order_node = f"ORDER_{order_id}"

        graph.add_node(
            order_node,
            node_type="order",
            name=str(order_id)
        )

        graph.add_edge(
            city_node,
            order_node,

            quantity=float(
                row["Order Item Quantity"]
            ),

            sales=float(
                row["Sales"]
            ),

            shipping_mode=str(
                row["Shipping Mode"]
            ),

            shipping_days=float(
                row["Days for shipping (real)"]
            ),

            delay=float(
                row["Shipping Delay"]
            )
        )


    return graph


# ============================================================
# NETWORK STATISTICS
# ============================================================

def display_statistics(graph, df):

    print("\n")
    print("=" * 60)
    print("NETWORK STATISTICS")
    print("=" * 60)

    print(
        "\nTotal graph nodes:",
        graph.number_of_nodes()
    )

    print(
        "Total graph edges:",
        graph.number_of_edges()
    )


    # Count node types

    node_types = {}

    for _, data in graph.nodes(data=True):

        node_type = data.get(
            "node_type",
            "unknown"
        )

        node_types[node_type] = (
            node_types.get(node_type, 0) + 1
        )


    print("\nNode types:")

    for node_type, count in node_types.items():

        print(
            f"{node_type.capitalize():15} : {count}"
        )


    # Geographic statistics

    print("\nGeographic statistics:")

    print(
        "Regions:",
        df["Order Region"].nunique()
    )

    print(
        "Countries:",
        df["Order Country"].nunique()
    )

    print(
        "Cities:",
        df["Order City"].nunique()
    )


    # Product statistics

    print("\nProduct statistics:")

    print(
        "Products:",
        df["Product Name"].nunique()
    )

    print(
        "Categories:",
        df["Category Name"].nunique()
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("DYNAMIC SUPPLY CHAIN RECOVERY")
    print("NETWORK BUILDER")
    print("=" * 60)


    # Load dataset

    df = load_data()

    if df is None:

        return


    # Create route data

    route_data = create_route_data(df)


    # Build graph

    graph = build_network(
        route_data
    )


    # Display statistics

    display_statistics(
        graph,
        route_data
    )


    print("\n")
    print("=" * 60)
    print("NETWORK BUILDING COMPLETE")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()