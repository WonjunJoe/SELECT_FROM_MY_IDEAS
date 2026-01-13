#!/usr/bin/env python3
"""
Server entry point for Select From My Ideas
Runs the FastAPI server with the web frontend
"""

import uvicorn
from core.logging import logger, setup_logging


if __name__ == "__main__":
    # Initialize logging
    setup_logging(level="INFO", log_to_file=True, log_to_console=True)

    logger.info("=" * 50)
    logger.info("Select From My Ideas - Web Server")
    logger.info("=" * 50)
    logger.info("Starting server at http://localhost:8000")

    try:
        uvicorn.run(
            "api.routes:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        raise
