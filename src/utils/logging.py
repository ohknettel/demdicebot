import logging;

logger = logging.getLogger("fastlog")
logger.setLevel(logging.INFO)

if not logger.handlers:
	handler = logging.FileHandler("./logs/dev_logfile.log", mode="a", encoding="utf-8");
	formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
	handler.setFormatter(formatter);
	logger.addHandler(handler);