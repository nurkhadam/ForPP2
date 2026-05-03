# ─────────────────────────────────────────────────────────────────────────────
# db.py  — PostgreSQL integration via psycopg2
# Handles: connection, schema creation, saving results, leaderboard queries.
# All DB errors are caught and logged so the game keeps running without a DB.
# ─────────────────────────────────────────────────────────────────────────────

import psycopg2                        # PostgreSQL adapter for Python
import psycopg2.extras                 # provides RealDictCursor (rows as dicts)
from datetime import datetime
from config import DB_DEFAULTS         # default connection parameters


# ─────────────────────────────────────────────────────────────────────────────
# DDL: SQL that creates the tables if they don't exist yet
# Running this every startup is safe because of IF NOT EXISTS.
# ─────────────────────────────────────────────────────────────────────────────
CREATE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL    -- unique player identifier
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id) ON DELETE CASCADE,
    score         INTEGER   NOT NULL DEFAULT 0,
    level_reached INTEGER   NOT NULL DEFAULT 1,
    played_at     TIMESTAMP DEFAULT NOW()   -- automatic timestamp
);
"""


class Database:
    """Wraps a single psycopg2 connection with helper methods.

    All public methods are safe to call even when the connection failed:
    they return sensible defaults (None / empty list) instead of raising.
    """

    def __init__(self, settings: dict):
        """Open a connection using params from settings dict (merged with DB_DEFAULTS)."""
        self.conn = None           # will hold the psycopg2 connection object
        self._connect(settings)    # attempt to connect immediately

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _connect(self, settings: dict):
        """Build connection params from settings and open the DB connection."""
        # Merge user settings over defaults so missing keys fall back gracefully
        db_cfg = {**DB_DEFAULTS, **settings.get("db", {})}
        try:
            self.conn = psycopg2.connect(
                host=db_cfg["host"],
                port=db_cfg["port"],
                dbname=db_cfg["dbname"],
                user=db_cfg["user"],
                password=db_cfg["password"],
                connect_timeout=3,     # don't hang for more than 3 s
            )
            self.conn.autocommit = False   # we manage transactions manually
            self._create_schema()
            print("[DB] Connected to PostgreSQL successfully.")
        except psycopg2.OperationalError as e:
            # This is expected when PostgreSQL is not running locally
            print(f"[DB] Connection failed (game will run without DB): {e}")
            self.conn = None

    def _create_schema(self):
        """Execute the DDL to create tables if they don't exist yet."""
        with self.conn.cursor() as cur:
            cur.execute(CREATE_SCHEMA_SQL)   # create players + game_sessions
        self.conn.commit()                   # commit the DDL transaction

    @property
    def available(self) -> bool:
        """Return True when the DB connection is open and usable."""
        return self.conn is not None and not self.conn.closed

    # ── Public API ────────────────────────────────────────────────────────────

    def get_or_create_player(self, username: str) -> int | None:
        """Return the player's ID; insert a new row if the username is new.

        Returns None on any DB error.
        """
        if not self.available:
            return None
        try:
            with self.conn.cursor() as cur:
                # Try to find the existing player first
                cur.execute(
                    "SELECT id FROM players WHERE username = %s", (username,)
                )
                row = cur.fetchone()   # None if no matching row
                if row:
                    return row[0]      # return existing id

                # Player not found — create a new record
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) RETURNING id",
                    (username,),
                )
                new_id = cur.fetchone()[0]
                self.conn.commit()     # commit the INSERT
                return new_id
        except psycopg2.Error as e:
            print(f"[DB] get_or_create_player error: {e}")
            self.conn.rollback()       # roll back on any error to keep connection clean
            return None

    def save_session(self, player_id: int, score: int, level: int) -> bool:
        """Save the game result for this player.

        If the player already has a record, it is replaced only when the new
        score is strictly higher than the stored one.  This means each player
        appears in the leaderboard exactly once, always with their best result.
        """
        if not self.available or player_id is None:
            return False
        try:
            with self.conn.cursor() as cur:
                # Check whether a previous record exists for this player
                cur.execute(
                    "SELECT id, score FROM game_sessions WHERE player_id = %s",
                    (player_id,),
                )
                existing = cur.fetchone()   # (id, score) or None

                if existing is None:
                    # First game — just insert
                    cur.execute(
                        """
                        INSERT INTO game_sessions (player_id, score, level_reached)
                        VALUES (%s, %s, %s)
                        """,
                        (player_id, score, level),
                    )
                elif score > existing[1]:
                    # New personal best — overwrite the old record
                    cur.execute(
                        """
                        UPDATE game_sessions
                        SET score = %s, level_reached = %s, played_at = NOW()
                        WHERE id = %s
                        """,
                        (score, level, existing[0]),
                    )
                else:
                    # Score is not better — nothing to do
                    print(f"[DB] Score {score} is not better than existing {existing[1]}, skipping.")
                    return True

            self.conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"[DB] save_session error: {e}")
            self.conn.rollback()
            return False

    def get_leaderboard(self, limit: int = 10) -> list[dict]:
        """Return the top `limit` scores, each as a dict with keys:
        rank, username, score, level_reached, played_at.
        """
        if not self.available:
            return []    # no DB → empty leaderboard
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        RANK() OVER (ORDER BY gs.score DESC) AS rank,
                        p.username,
                        gs.score,
                        gs.level_reached,
                        gs.played_at
                    FROM game_sessions gs
                    JOIN players p ON p.id = gs.player_id
                    ORDER BY gs.score DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                # RealDictCursor returns rows that behave like dicts
                return [dict(row) for row in cur.fetchall()]
        except psycopg2.Error as e:
            print(f"[DB] get_leaderboard error: {e}")
            return []

    def get_personal_best(self, player_id: int) -> int:
        """Return the highest score ever recorded for this player (0 if none)."""
        if not self.available or player_id is None:
            return 0
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                    (player_id,),
                )
                return cur.fetchone()[0]   # COALESCE ensures we get 0 not NULL
        except psycopg2.Error as e:
            print(f"[DB] get_personal_best error: {e}")
            return 0

    def close(self):
        """Cleanly close the connection when the game exits."""
        if self.available:
            self.conn.close()
            print("[DB] Connection closed.")