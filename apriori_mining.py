"""Apriori association rule mining using mlxtend."""

import pandas as pd
from typing import Any


def run_apriori(
    rows: list[dict],
    columns: list[str],
    min_support: float = 0.1,
    min_confidence: float = 0.5,
    min_lift: float = 1.0,
    max_itemset_len: int = 4,
) -> dict[str, Any]:
    """
    Run Apriori algorithm on selected columns of row data.
    Binarizes numeric (>=median) and categorical (one-hot top-10) columns.
    Returns frequent_itemsets, rules, and metrics.
    """
    if not rows:
        return {"error": "No data provided"}

    df = pd.DataFrame(rows)

    missing_cols = [c for c in columns if c not in df.columns]
    if missing_cols:
        return {"error": f"Columns not found: {missing_cols}. Available: {list(df.columns)}"}

    if len(columns) < 2:
        return {"error": "Select at least 2 columns for association mining"}

    df_sel = df[columns].copy()

    binary_frames = []
    for col in columns:
        col_data = df_sel[col]
        numeric_data = pd.to_numeric(col_data, errors="coerce")

        if numeric_data.notna().mean() > 0.8:
            median = numeric_data.median()
            binary_col = (numeric_data >= median).rename(f"{col}>=median")
            binary_frames.append(binary_col.astype(bool))
        else:
            top_vals = col_data.value_counts().head(10).index.tolist()
            for val in top_vals:
                binary_col = (col_data == val).rename(f"{col}={val}")
                binary_frames.append(binary_col.astype(bool))

    if not binary_frames:
        return {"error": "Could not build binary transaction matrix from selected columns"}

    binary_df = pd.concat(binary_frames, axis=1)

    from mlxtend.frequent_patterns import apriori, association_rules

    frequent_itemsets = apriori(
        binary_df,
        min_support=min_support,
        use_colnames=True,
        max_len=max_itemset_len,
    )

    if frequent_itemsets.empty:
        return {
            "frequent_itemsets": [],
            "rules": [],
            "metrics": {
                "n_transactions": len(df),
                "n_items": len(binary_df.columns),
                "n_frequent_itemsets": 0,
                "n_rules": 0,
                "message": f"No frequent itemsets found at min_support={min_support}. Try lowering it.",
            },
        }

    rules_df = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=min_confidence,
    )
    rules_df = rules_df[rules_df["lift"] >= min_lift]
    rules_df = rules_df.sort_values("lift", ascending=False).head(100)

    itemsets_out = []
    for _, row in frequent_itemsets.iterrows():
        itemsets_out.append({
            "itemset": sorted(list(row["itemsets"])),
            "support": round(float(row["support"]), 4),
        })
    itemsets_out.sort(key=lambda x: x["support"], reverse=True)

    rules_out = []
    for _, row in rules_df.iterrows():
        rules_out.append({
            "antecedents": sorted(list(row["antecedents"])),
            "consequents": sorted(list(row["consequents"])),
            "support": round(float(row["support"]), 4),
            "confidence": round(float(row["confidence"]), 4),
            "lift": round(float(row["lift"]), 4),
        })

    return {
        "frequent_itemsets": itemsets_out[:50],
        "rules": rules_out,
        "metrics": {
            "n_transactions": len(df),
            "n_items": len(binary_df.columns),
            "n_frequent_itemsets": len(frequent_itemsets),
            "n_rules": len(rules_df),
            "min_support": min_support,
            "min_confidence": min_confidence,
        },
    }
