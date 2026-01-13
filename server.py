#!/usr/bin/env python3
"""
Server entry point for Select From My Ideas
Runs the FastAPI server with the web frontend
"""

import uvicorn

from config import settings
from core.logging import logger, setup_logging


if __name__ == "__main__":
    # Initialize logging from config
    setup_logging(
        level=settings.log_level,
        log_to_file=settings.log_to_file,
        log_to_console=settings.log_to_console,
    )

    logger.info("=" * 50)
    logger.info("Select From My Ideas - Web Server")
    logger.info("=" * 50)
    logger.info(f"Starting server at http://localhost:{settings.server_port}")

    try:
        uvicorn.run(
            "api.routes:app",
            host=settings.server_host,
            port=settings.server_port,
            reload=settings.server_reload,
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        raise
