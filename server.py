#!/usr/bin/env python3
"""
Server entry point for Select From My Ideas
Runs the FastAPI server with the web frontend
"""

import uvicorn


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Select From My Ideas - Web Server")
    print("=" * 50)
    print("\n  Starting server at http://localhost:8000")
    print("  Press Ctrl+C to stop\n")

    uvicorn.run(
        "api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
