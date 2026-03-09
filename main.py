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
from typing import Optional, Dict

app = FastAPI(title="XBase Python Backend", version="1.0.0")

# CORS middleware to allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
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


@app.get("/")
async def root():
    return {
        "service": "XBase Python Backend",
        "status": "running",
        "endpoints": {
            "/execute": "POST - Execute Python code",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "xbase-python-backend"}


@app.post("/execute", response_model=PythonExecutionResult)
async def execute_python(request: PythonExecutionRequest):
    """
    Execute Python code in a sandboxed environment.
    
    The code should set a variable named 'result' with the output.
    Matplotlib figures are automatically converted to base64.
    """
    
    # Create temporary directory for execution
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Write request to JSON file
        request_file = tmpdir_path / "request.json"
        request_data = {
            "code": request.code,
            "csv": request.csv or "",
            "files": request.files or {}
        }
        
        with open(request_file, "w") as f:
            json.dump(request_data, f)
        
        # Copy helpers.py to temp directory
        helpers_src = Path(__file__).parent / "helpers.py"
        helpers_dst = tmpdir_path / "helpers.py"
        
        if helpers_src.exists():
            import shutil
            shutil.copy(helpers_src, helpers_dst)
        
        # Copy runner.py to temp directory
        runner_src = Path(__file__).parent / "runner.py"
        runner_dst = tmpdir_path / "runner.py"
        
        if runner_src.exists():
            import shutil
            shutil.copy(runner_src, runner_dst)
        
        try:
            # Execute Python code using subprocess
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
            
            # Parse output
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
