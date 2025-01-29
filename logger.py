import logging

# Create a logger
logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

# Create a file handler and set the level to DEBUG
file_handler = logging.FileHandler("log_file.log")
file_handler.setLevel(logging.DEBUG)

# Create a stream handler and set the level to INFO (or any other level you prefer)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Create format for both handlers
file_handler_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_handler_formatter)

stream_handler_formatter = logging.Formatter("%(levelname)s: %(message)s")
stream_handler.setFormatter(stream_handler_formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


if __name__ == "__main__":
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")