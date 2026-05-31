"""
XBase Python Execution Backend
FastAPI server that executes Python code securely with timeout and isolation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, List

from smart_fill import smart_fill_column
from apriori_mining import run_apriori

app = FastAPI(title="XBase Python Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PythonExecutionRequest(BaseModel):
    code: str
    csv: Optional[str] = None
    files: Optional[Dict[str, str]] = None
    timeoutMs: Optional[int] = 20000


class PythonExecutionResult(BaseModel):
    prints: str
    result: Optional[dict] = None
    error: Optional[Dict[str, str]] = None


class SmartFillRequest(BaseModel):
    rows: List[dict]
    target_column: str
    strategy: Optional[str] = "auto"


class AprioriRequest(BaseModel):
    rows: List[dict]
    columns: List[str]
    min_support: Optional[float] = 0.1
    min_confidence: Optional[float] = 0.5
    min_lift: Optional[float] = 1.0
    max_itemset_len: Optional[int] = 4


@app.get("/")
async def root():
    return {
        "service": "XBase Python Backend",
        "status": "running",
        "endpoints": {
            "/execute": "POST - Execute Python code",
            "/health": "GET - Health check",
            "/smart-fill": "POST - Predict missing column values",
            "/apriori": "POST - Association rule mining (Apriori)",
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "xbase-python-backend"}


@app.post("/execute", response_model=PythonExecutionResult)
async def execute_python(request: PythonExecutionRequest):
    """Execute Python code in a sandboxed environment."""

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        request_file = tmpdir_path / "request.json"
        request_data = {
            "code": request.code,
            "csv": request.csv or "",
            "files": request.files or {}
        }

        with open(request_file, "w") as f:
            json.dump(request_data, f)

        helpers_src = Path(__file__).parent / "helpers.py"
        helpers_dst = tmpdir_path / "helpers.py"

        if helpers_src.exists():
            import shutil
            shutil.copy(helpers_src, helpers_dst)

        runner_src = Path(__file__).parent / "runner.py"
        runner_dst = tmpdir_path / "runner.py"

        if runner_src.exists():
            import shutil
            shutil.copy(runner_src, runner_dst)

        try:
            timeout_seconds = (request.timeoutMs or 20000) / 1000

            result = subprocess.run(
                ["python", str(runner_dst)],
                cwd=tmpdir_path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env={**os.environ, "REQUEST_PATH": str(request_file)}
            )

            if result.returncode != 0:
                return PythonExecutionResult(
                    prints="",
                    result=None,
                    error={
                        "message": f"Execution failed with code {result.returncode}",
                        "traceback": result.stderr
                    }
                )

            try:
                output = json.loads(result.stdout)
                return PythonExecutionResult(**output)
            except json.JSONDecodeError as e:
                return PythonExecutionResult(
                    prints=result.stdout,
                    result=None,
                    error={
                        "message": "Failed to parse execution output",
                        "traceback": str(e)
                    }
                )

        except subprocess.TimeoutExpired:
            return PythonExecutionResult(
                prints="",
                result=None,
                error={
                    "message": f"Execution timed out after {timeout_seconds} seconds",
                    "traceback": ""
                }
            )
        except Exception as e:
            return PythonExecutionResult(
                prints="",
                result=None,
                error={
                    "message": f"Execution error: {str(e)}",
                    "traceback": ""
                }
            )


@app.post("/smart-fill")
async def smart_fill(request: SmartFillRequest):
    """Predict missing values in target_column using other columns as features."""
    try:
        result = smart_fill_column(
            rows=request.rows,
            target_column=request.target_column,
            strategy=request.strategy or "auto",
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/apriori")
async def run_apriori_endpoint(request: AprioriRequest):
    """Run Apriori association rule mining on selected columns."""
    try:
        result = run_apriori(
            rows=request.rows,
            columns=request.columns,
            min_support=request.min_support or 0.1,
            min_confidence=request.min_confidence or 0.5,
            min_lift=request.min_lift or 1.0,
            max_itemset_len=request.max_itemset_len or 4,
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
