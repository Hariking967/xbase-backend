"""Smart Fill: predict missing values in a target column using other columns as features."""

import pandas as pd
import numpy as np
from typing import Any


def smart_fill_column(
    rows: list[dict],
    target_column: str,
    strategy: str = "auto",
) -> dict[str, Any]:
    """
    Predict missing values in target_column using all other columns as features.
    Returns dict with predictions, filled_rows, fields, metrics, model_type.
    """
    if not rows:
        return {"error": "No data provided"}

    df = pd.DataFrame(rows)

    if target_column not in df.columns:
        return {"error": f"Column '{target_column}' not found. Available: {list(df.columns)}"}

    # Identify rows with missing target
    missing_mask = df[target_column].isna() | (df[target_column].astype(str) == "") | (df[target_column].astype(str) == "None")
    n_missing = int(missing_mask.sum())

    if n_missing == 0:
        return {
            "predictions": [],
            "filled_rows": rows,
            "fields": list(df.columns),
            "metrics": {"n_missing": 0, "n_filled": 0, "message": "No missing values found"},
            "model_type": "none",
        }

    n_known = int((~missing_mask).sum())
    if n_known < 5:
        return {"error": f"Not enough labeled rows to train ({n_known} found, need >= 5)"}

    # Determine if target is numeric or categorical
    known_target = df.loc[~missing_mask, target_column]
    is_numeric = pd.to_numeric(known_target, errors="coerce").notna().all()
    model_type = "regressor" if is_numeric else "classifier"

    # Prepare features
    feature_cols = [c for c in df.columns if c != target_column]
    X = df[feature_cols].copy()

    # Encode each feature column
    for col in feature_cols:
        numeric_test = pd.to_numeric(X[col], errors="coerce")
        if numeric_test.notna().mean() < 0.8:
            categories = X[col].dropna().unique().tolist()
            cat_map = {v: i for i, v in enumerate(categories)}
            X[col] = X[col].map(cat_map).fillna(-1).astype(int)
        else:
            median_val = numeric_test.median() if numeric_test.notna().any() else 0
            X[col] = numeric_test.fillna(median_val)

    X_known = X[~missing_mask]
    X_unknown = X[missing_mask]

    if is_numeric:
        y_known = pd.to_numeric(df.loc[~missing_mask, target_column], errors="coerce").fillna(0)
    else:
        y_known = df.loc[~missing_mask, target_column].astype(str)

    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

    if model_type == "regressor":
        model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    else:
        model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)

    model.fit(X_known, y_known)
    predictions_raw = model.predict(X_unknown)

    missing_indices = df.index[missing_mask].tolist()
    predictions = []
    for idx, pred in zip(missing_indices, predictions_raw):
        val = float(pred) if is_numeric else str(pred)
        predictions.append({"row_index": int(idx), "predicted_value": val})

    filled_df = df.copy()
    for p in predictions:
        filled_df.at[p["row_index"], target_column] = p["predicted_value"]

    filled_rows = filled_df.to_dict(orient="records")

    importance = []
    for col, imp in zip(feature_cols, model.feature_importances_):
        importance.append({"feature": col, "importance": round(float(imp), 4)})
    importance.sort(key=lambda x: x["importance"], reverse=True)

    return {
        "predictions": predictions,
        "filled_rows": filled_rows,
        "fields": list(df.columns),
        "metrics": {
            "n_missing": n_missing,
            "n_filled": n_missing,
            "n_training_rows": n_known,
            "model_type": model_type,
            "top_features": importance[:5],
        },
        "model_type": model_type,
    }
