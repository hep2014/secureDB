
import argparse
import asyncio
import sys
import os
from typing import Optional
from tabulate import tabulate

from auth import (
    register_user,
    authenticate_user,
    authorize_by_role,
    authorize_by_permission,
    change_password,
    logout as auth_logout,
)
from db import init_db_pool
from auth import _get_user_by_token


SESSION_FILE = "session.txt"


# --------------------- helpers -------------------------

def save_token(token: str) -> None:
    with open(SESSION_FILE, "w") as f:
        f.write(token)


def load_token() -> Optional[str]:
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r") as f:
        return f.read().strip()


def delete_token() -> None:
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


# --------------------- commands -------------------------

async def cmd_signup(args):
    try:
        user = await register_user(args.email, args.password, args.role)
        print(f"Создан пользователь: {user['email']} (id={user['id']}, роль={user['role']})")
    except Exception as e:
        print("Ошибка:", e)


async def cmd_login(args):
    try:
        result = await authenticate_user(args.email, args.password)
        save_token(result["token"])
        print(f"Вход выполнен. Токен сохранён.")
    except Exception as e:
        print("Ошибка:", e)


async def cmd_whoami(args):
    token = load_token()
    if not token:
        print("Вы не авторизованы.")
        return

    session, user = await _get_user_by_token(token)
    if not user:
        print("Токен недействителен или сессия истекла.")
        return

    print(f"{user['email']} (id={user['id']}, роль={user['role']})")


async def cmd_logout(args):
    token = load_token()
    if not token:
        print("Вы не авторизованы.")
        return

    try:
        await auth_logout(token)
        delete_token()
        print("Вы вышли из системы.")
    except Exception as e:
        print("Ошибка:", e)


async def cmd_change_password(args):
    token = load_token()
    if not token:
        print("Сначала войдите.")
        return

    session, user = await _get_user_by_token(token)
    if not user:
        print("Сессия недействительна.")
        return

    try:
        await change_password(
            user_id=user["id"],
            old_password=args.old,
            new_password=args.new
        )
        print("Пароль успешно изменён!")
    except Exception as e:
        print("Ошибка:", e)


async def cmd_check_role(args):
    token = load_token()
    if not token:
        print("Вы не авторизованы.")
        return

    ok = await authorize_by_role(token, args.role)
    print(f"Доступ: {'РАЗРЕШЁН' if ok else 'ЗАПРЕЩЁН'}")


async def cmd_check_perm(args):
    token = load_token()
    if not token:
        print("Вы не авторизованы.")
        return

    ok = await authorize_by_permission(token, args.permission)
    print(f"Разрешение: {'ЕСТЬ' if ok else 'НЕТ'}")


# --------------------- main async -------------------------

async def main_async():
    await init_db_pool()

    parser = argparse.ArgumentParser(
        description="Матвеев - лабораторная 6."
    )
    sub = parser.add_subparsers(dest="cmd")

    # signup
    p = sub.add_parser("signup", help="Регистрация пользователя")
    p.add_argument("email")
    p.add_argument("password")
    p.add_argument("--role", default="student")
    p.set_defaults(func=cmd_signup)

    # login
    p = sub.add_parser("login", help="Вход в систему")
    p.add_argument("email")
    p.add_argument("password")
    p.set_defaults(func=cmd_login)

    # whoami
    p = sub.add_parser("whoami", help="Показать текущую сессию")
    p.set_defaults(func=cmd_whoami)

    # logout
    p = sub.add_parser("logout", help="Выйти из аккаунта")
    p.set_defaults(func=cmd_logout)

    # change-password
    p = sub.add_parser("change-password", help="Сменить пароль")
    p.add_argument("old")
    p.add_argument("new")
    p.set_defaults(func=cmd_change_password)

    # role-check
    p = sub.add_parser("check-role", help="Проверить доступ по роли")
    p.add_argument("role")
    p.set_defaults(func=cmd_check_role)

    # permission-check
    p = sub.add_parser("check-perm", help="Проверить доступ по разрешению")
    p.add_argument("permission")
    p.set_defaults(func=cmd_check_perm)

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    await args.func(args)


# --------------------- entrypoint -------------------------

def main():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
