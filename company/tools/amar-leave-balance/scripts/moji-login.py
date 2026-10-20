#!/usr/bin/env python3
"""Moji OA 平台登录脚本。

通过 Aegis SSO 登录 moji.wemomo.com，获取 session cookie，
供 leave-balance.py 等脚本使用。

用法：
    python3 moji-login.py

凭据从 ~/.aegis/credentials.json 读取，格式：
{
    "username": "your_ldap_username",
    "password": "your_password"
}

输出文件 ~/.aegis/moji-cookies.json 格式：
{
    "userName": "xxx",
    "cookies": {"aegis_v3_session": "...", "JSESSIONID": "...", ...}
}
"""

import os
import sys

# 加载公共认证模块（通过 realpath 解析软链接，确保找到 common/ 目录）
_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_TOOLS_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
sys.path.insert(0, os.path.join(_TOOLS_ROOT, "common"))

from aegis_auth import (  # noqa: E402
    AEGIS_DIR,
    check_requests, load_credentials, create_session,
    sso_login, export_cookies, save_cookie_file,
)

COOKIES_FILE = os.path.join(AEGIS_DIR, "moji-cookies.json")

MOJI_HOME = "https://moji.wemomo.com/"


def main():
    check_requests()
    creds = load_credentials()
    session = create_session()

    # Aegis SSO 登录
    aegis_user = sso_login(session, creds)
    user_name = aegis_user.get("name", "")

    # 访问 Moji 建立 session（SSO cookie 自动触发认证回调）
    resp = session.get(MOJI_HOME, allow_redirects=True)
    if "aegis.immomo.com" in resp.url:
        session.get(resp.url, allow_redirects=True)

    # 保存 cookies（格式与原脚本完全一致，不影响 leave-balance.py）
    save_cookie_file({
        "userName": user_name,
        "cookies": export_cookies(session),
    }, COOKIES_FILE)

    print(f"✅ Moji 登录成功！")
    print(f"  用户: {user_name}")
    print(f"  cookie 已保存到: {COOKIES_FILE}")


if __name__ == "__main__":
    main()
