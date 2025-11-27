import asyncpg
from config import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
from typing import Optional
_pool: Optional[asyncpg.pool.Pool] = None


async def init_db_pool():
    """Создаёт пул подключений к БД."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
            min_size=1,
            max_size=10,
        )


async def get_pool() -> asyncpg.pool.Pool:
    """Возвращает пул (или создаёт если ещё не создан)."""
    if _pool is None:
        await init_db_pool()
    return _pool


# -------- USERS --------

async def get_user_by_email(email: str):
    pool = await get_pool()
    query = "SELECT * FROM users WHERE email = $1"
    return await pool.fetchrow(query, email)


async def get_user_by_id(user_id: str):
    pool = await get_pool()
    query = "SELECT * FROM users WHERE id = $1"
    return await pool.fetchrow(query, user_id)


async def create_user(email: str, password_hash: str, role: str = "student"):
    pool = await get_pool()
    query = """
        INSERT INTO users (email, password_hash, role)
        VALUES ($1, $2, $3)
        RETURNING *;
    """
    return await pool.fetchrow(query, email, password_hash, role)


# -------- FAILED LOGINS --------

async def log_failed_login(email: str):
    pool = await get_pool()
    query = "INSERT INTO failed_logins (email) VALUES ($1)"
    await pool.execute(query, email)


async def count_failed_logins(email: str, minutes: int = 15) -> int:
    pool = await get_pool()
    query = """
        SELECT COUNT(*) AS cnt
        FROM failed_logins
        WHERE email = $1
          AND attempted_at >= (now() - make_interval(mins => $2))
    """
    row = await pool.fetchrow(query, email, minutes)
    return row["cnt"]


# -------- SESSIONS --------

async def create_session(user_id: str, token: str, expires_at):
    pool = await get_pool()
    query = """
        INSERT INTO sessions (token, user_id, expires_at)
        VALUES ($1, $2, $3)
        RETURNING *;
    """
    return await pool.fetchrow(query, token, user_id, expires_at)


async def get_session_by_token(token: str):
    pool = await get_pool()
    query = "SELECT * FROM sessions WHERE token = $1"
    return await pool.fetchrow(query, token)


async def update_session_expiry(token: str, new_expires_at):
    pool = await get_pool()
    query = """
        UPDATE sessions
        SET expires_at = $1
        WHERE token = $2
        RETURNING *;
    """
    return await pool.fetchrow(query, new_expires_at, token)


async def delete_session(token: str):
    pool = await get_pool()
    query = "DELETE FROM sessions WHERE token = $1"
    await pool.execute(query, token)

async def update_password_hash(user_id: str, new_hash: str):
    pool = await get_pool()
    query = """
        UPDATE users
        SET password_hash = $1
        WHERE id = $2
        RETURNING *;
    """
    return await pool.fetchrow(query, new_hash, user_id)