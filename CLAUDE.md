# XBase Backend — CLAUDE.md

## What This Is
FastAPI Python service that executes arbitrary Python code in a subprocess sandbox. Called by xbase-app when the AI agent needs to run Python analysis or visualization.

## Development
```bash
cd c:\HARI\ETAIH\xbase-backend
pip install -r requirements.txt
python main.py        # Start server on port 8000 (or $PORT)
```

## Endpoints
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/execute` | POST | Execute arbitrary Python code |
| `/smart-fill` | POST | Predict missing column values (RandomForest) |
| `/apriori` | POST | Run Apriori association rule mining |

## Execution Model (`/execute`)

**Request:**
```json
{
  "code": "result = {'answer': 42}",
  "csv": "col1,col2\n1,2",
  "files": {"data.json": "{...}"},
  "timeoutMs": 20000
}
```

**What happens:**
1. `main.py` creates a temp directory
2. Writes `request.json` with the request payload
3. Copies `runner.py` + `helpers.py` into temp dir
4. Runs `python runner.py` in subprocess with `REQUEST_PATH` env var
5. `runner.py` reads request, writes CSV to `/work/input.csv`, calls `exec(code)` 
6. User code MUST set a `result` variable; matplotlib figures auto-convert to base64
7. Output is JSON: `{prints, result, error}`

**Available in user code:**
- `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`
- `scikit-learn` (RandomForest, KNNImputer, etc.)
- `mlxtend` (apriori, association_rules)
- `fig_to_base64`, `create_visualization_result`, `format_table_result` from helpers

## Smart Fill (`/smart-fill`)

Uses `smart_fill.py`. Takes `rows`, `target_column`. Trains RandomForestClassifier (categorical) or RandomForestRegressor (numeric) on rows where target is known. Returns predictions for rows where target is missing.

**Request:** `{rows: [...], target_column: "age", strategy: "auto"}`
**Response:** `{predictions: [{row_index, predicted_value}], filled_rows, metrics, model_type}`

## Apriori Mining (`/apriori`)

Uses `apriori_mining.py`. Takes rows and selected column names. Binarizes values (numeric: ≥median; categorical: one-hot) then runs mlxtend Apriori.

**Request:** `{rows: [...], columns: ["dept", "grade"], min_support: 0.1, min_confidence: 0.5, min_lift: 1.0}`
**Response:** `{frequent_itemsets: [...], rules: [{antecedents, consequents, support, confidence, lift}], metrics}`

## File Layout
```
main.py           # FastAPI app — all endpoints
runner.py         # Subprocess code execution harness
helpers.py        # Utilities: fig_to_base64, fill_missing_with_sklearn, etc.
smart_fill.py     # ML-based column prediction
apriori_mining.py # Apriori association mining
requirements.txt  # Python dependencies
render.yaml       # Render.com deployment config
runtime.txt       # Python version (3.12.8)
```

## Deployment
- Render.com: `render.yaml` defines the service
- Start command: `python main.py`
- Port: `$PORT` env var (default 8000)
- Python: 3.12.8 (see `runtime.txt`)
