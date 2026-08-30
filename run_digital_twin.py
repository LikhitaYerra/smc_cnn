#!/usr/bin/env python3
"""Launch the Robot Digital Twin — single server on port 8000."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import uvicorn

if __name__ == "__main__":
    print("Starting Robot Digital Twin at http://localhost:8000")
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
