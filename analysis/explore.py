import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import pandas as pd


import pandas as pd

from app.records import load_records


def main():
    records = load_records()
    df = pd.DataFrame(records)

    # Fact 1: Total records
    print(f"Fact 1: Total records: {len(df)}")

    # Fact 2: Most common main symbol
    top = df["main_symbol"].value_counts()
    if not top.empty:
        print(
            f"Fact 2: Most common symbol: "
            f"{top.index[0]} ({top.iloc[0]} records)"
        )

    # Fact 3: Records with empty example responses
    missing = (
        df["example_response"]
        .fillna("")
        .str.strip()
        .eq("")
        .sum()
    )

    print(f"Fact 3: Records with no example: {missing}")


if __name__ == "__main__":
    main()
