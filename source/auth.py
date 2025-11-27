# auth.py
"""
Модуль аутентификации и авторизации.

Функционал:
- хэширование паролей (Argon2id)
- регистрация пользователей
- аутентификация с экспоненциальной задержкой при частых ошибках
- авторизация по ролям и правам
- управление сессиями (refresh, logout)
- смена пароля с проверкой старого
"""

from datetime import datetime, timedelta
import uuid
import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from db import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    log_failed_login,
    count_failed_logins,
    create_session,
    get_session_by_token,
    update_session_expiry,
    delete_session,
    update_password_hash,
)


# ----------------- Константы и настройки -----------------

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
)

SESSION_LIFETIME_DAYS = 30
MAX_BACKOFF_SECONDS = 300  # максимум 5 минут задержки


def now_utc():
    """
    Возвращает naive-UTC datetime.
    Совместимо с колонками TIMESTAMP WITHOUT TIME ZONE в PostgreSQL.
    """
    return datetime.utcnow()


def calculate_backoff(attempts: int) -> int:
    """
    Экспоненциальная задержка:
    backoff = min(2^attempts, 300)
    """
    if attempts <= 0:
        return 0
    delay = 2 ** attempts
    return min(delay, MAX_BACKOFF_SECONDS)


# ----------------- Исключения -----------------

class AuthError(Exception):
    """Базовое исключение для ошибок аутентификации."""


class RateLimitError(AuthError):
    """Оставлено про запас, если захочется жёсткий лимит."""


# ----------------- Хэширование -----------------

def hash_password(plain: str) -> str:
    """Возвращает Argon2-хэш пароля."""
    return ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Проверяет соответствие пароля и хэша."""
    try:
        return ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


# ----------------- Роли и права -----------------

ROLE_LEVELS = {
    "student": 1,
    "teacher": 2,
    "admin": 3,
}

ROLE_PERMISSIONS = {
    "student": {"view_self", "view_courses"},
    "teacher": {"view_self", "view_courses", "edit_grades"},
    "admin": {"view_self", "view_courses", "edit_grades", "manage_users", "view_audit"},
}


def has_min_role(role: str, required: str) -> bool:
    """Иерархическая проверка роли (admin >= teacher >= student)."""
    return ROLE_LEVELS.get(role, 0) >= ROLE_LEVELS.get(required, 0)


def has_permission(role: str, perm: str) -> bool:
    """Проверка по таблице прав."""
    return perm in ROLE_PERMISSIONS.get(role, set())


# ----------------- Регистрация -----------------

async def register_user(email: str, password: str, role: str = "student"):
    """
    Регистрирует нового пользователя:
    - проверка, что email свободен
    - хэширование пароля
    - создание записи в БД
    """
    existing = await get_user_by_email(email)
    if existing:
        raise AuthError("Пользователь уже существует")

    hashed = hash_password(password)
    user = await create_user(email=email, password_hash=hashed, role=role)
    return dict(user)


# ----------------- Аутентификация -----------------

async def authenticate_user(email: str, password: str):
    """
    Аутентификация пользователя с экспоненциальной задержкой
    при большом числе неудачных попыток.
    """
    # 1) считаем ошибки за последние 15 минут
    attempts = await count_failed_logins(email, minutes=15)

    # 2) экспоненциальный бэкофф
    delay = calculate_backoff(attempts)
    if delay > 0:
        print(f"Слишком много ошибок входа: задержка {delay} секунд...")
        await asyncio.sleep(delay)

    # 3) проверяем наличие пользователя
    user = await get_user_by_email(email)
    if not user:
        await log_failed_login(email)
        raise AuthError("Неверный email или пароль")

    # 4) проверяем пароль
    if not verify_password(password, user["password_hash"]):
        await log_failed_login(email)
        raise AuthError("Неверный email или пароль")

    # 5) успешная аутентификация — создаём сессию
    token = str(uuid.uuid4())
    expires_at = now_utc() + timedelta(days=SESSION_LIFETIME_DAYS)

    session = await create_session(user["id"], token, expires_at)

    return {
        "token": str(session["token"]),
        "user_id": str(user["id"]),
        "role": user["role"],
        "email": user["email"],
        "expires_at": session["expires_at"],
    }


# ----------------- Авторизация -----------------

async def _get_user_by_token(token: str):
    """
    Вспомогательная функция:
    по токену находит сессию и пользователя, проверяя срок действия.
    """
    session = await get_session_by_token(token)
    if not session:
        return None, None

    expires = session["expires_at"]  # TIMESTAMP WITHOUT TIME ZONE → naive datetime
    now = now_utc()

    if expires < now:
        # сессия истекла
        return None, None

    user = await get_user_by_id(session["user_id"])
    return session, user


async def authorize_by_role(token: str, required_role: str) -> bool:
    """
    Проверка доступа по иерархии ролей.
    """
    _, user = await _get_user_by_token(token)
    if not user:
        return False
    return has_min_role(user["role"], required_role)


async def authorize_by_permission(token: str, perm: str) -> bool:
    """
    Проверка доступа по таблице прав.
    """
    _, user = await _get_user_by_token(token)
    if not user:
        return False
    return has_permission(user["role"], perm)


# ----------------- Управление сессиями -----------------

async def refresh_session(token: str):
    """
    Продление сессии ещё на SESSION_LIFETIME_DAYS.
    Возвращает обновлённую сессию или None, если токен недействителен.
    """
    session, user = await _get_user_by_token(token)
    if not session or not user:
        return None

    new_expires = now_utc() + timedelta(days=SESSION_LIFETIME_DAYS)
    updated = await update_session_expiry(token, new_expires)
    return dict(updated) if updated else None


async def logout(token: str):
    """
    Завершение сессии (выход пользователя).
    """
    await delete_session(token)


# ----------------- Смена пароля -----------------

async def change_password(user_id: str, old_password: str, new_password: str):
    """
    Смена пароля:
    1) Проверка старого пароля
    2) Генерация нового Argon2-хэша
    3) Сохранение в БД
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise AuthError("Пользователь не найден")

    if not verify_password(old_password, user["password_hash"]):
        raise AuthError("Старый пароль неверный")

    new_hash = hash_password(new_password)
    updated = await update_password_hash(user_id, new_hash)
    return dict(updated)
