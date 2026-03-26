import os
from datetime import date, datetime
from typing import Optional

import mysql.connector


def connect_db():
    """
    Create a MySQL connection and ensure the required schema exists.

    Uses environment variables so you don't need to hardcode credentials.
    Defaults assume a local MySQL with root and empty password.
    """
    host = os.getenv("POWERCUT_DB_HOST", "localhost")
    port_raw = os.getenv("POWERCUT_DB_PORT", "").strip()
    port = int(port_raw) if port_raw else 3306
    user = os.getenv("POWERCUT_DB_USER", "root")
    password_env = os.getenv("POWERCUT_DB_PASSWORD")
    password = password_env if password_env is not None else ""
    database = os.getenv("POWERCUT_DB_NAME", "powercut_db")

    conn_kwargs: dict[str, object] = {
        "host": host,
        "port": port,
        "user": user,
    }
    # If password is empty/unset, omit it so MySQL can fall back to auth methods
    # like socket-based authentication (common on some local setups).
    if (password_env or "").strip():
        conn_kwargs["password"] = password
    conn = mysql.connector.connect(**conn_kwargs)

    _ensure_database_and_table(conn, database)
    conn.database = database
    return conn


def _ensure_database_and_table(conn, database: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS `{database}`.`powercuts` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `location` VARCHAR(255) NOT NULL,
            `start_time` DATETIME NOT NULL,
            `end_time` DATETIME NULL,
            `status` VARCHAR(20) NOT NULL,   -- Ongoing / Resolved
            `type` VARCHAR(20) NOT NULL,     -- Planned / Sudden
            `severity` VARCHAR(10) NOT NULL, -- Low / Medium / High
            `date_reported` DATE NOT NULL
        )
        """
    )
    cursor.close()
    conn.commit()


def insert_powercut(
    location: str,
    start_time: datetime,
    end_time: Optional[datetime],
    status: str,
    type_value: str,
    severity: str,
    date_reported: Optional[date] = None,
) -> int:
    if date_reported is None:
        date_reported = datetime.now().date()

    conn = connect_db()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO `powercuts`
                (`location`, `start_time`, `end_time`, `status`, `type`, `severity`, `date_reported`)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql,
            (
                location,
                start_time,
                end_time,
                status,
                type_value,
                severity,
                date_reported,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def fetch_all():
    conn = connect_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                `id`,
                `location`,
                `start_time`,
                `end_time`,
                `status`,
                `type`,
                `severity`,
                `date_reported`
            FROM `powercuts`
            ORDER BY `start_time` DESC, `id` DESC
            """
        )
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def delete_record(record_id: int) -> None:
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM `powercuts` WHERE `id` = %s", (record_id,))
        conn.commit()
    finally:
        conn.close()

