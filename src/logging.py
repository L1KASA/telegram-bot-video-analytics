import logging
import sys

# Create a shared logger instance for the application
logger = logging.getLogger("app")

def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the entire application.
    
    :param level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Log format: Time - Logger Name - Level - Message
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure specific levels for third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)

    logger.info(f"Logging configured with level {level}")
