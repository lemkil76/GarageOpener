import logging
import pymysql
import config

logger = logging.getLogger(__name__)

_CREATE_DB = f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    event_type  VARCHAR(50)  NOT NULL,
    timestamp   DATETIME     NOT NULL,
    ip_address  VARCHAR(45),
    success     TINYINT(1)   DEFAULT 1,
    message     VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


def _connect(with_db=True):
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME if with_db else None,
        connect_timeout=5,
    )


def init_db():
    try:
        conn = _connect(with_db=False)
        with conn.cursor() as cur:
            cur.execute(_CREATE_DB)
        conn.select_db(config.DB_NAME)
        with conn.cursor() as cur:
            cur.execute(_CREATE_TABLE)
        conn.commit()
        conn.close()
        logger.info("DB initialiserad")
    except Exception as e:
        logger.error(f"DB init misslyckades: {e}")


def log_event(event_type, ip=None, success=True, message=None):
    try:
        conn = _connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (event_type, timestamp, ip_address, success, message) VALUES (%s, NOW(), %s, %s, %s)",
                (event_type, ip, int(success), message),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB log misslyckades: {e}")
