#!/usr/bin/env python3
"""Aegis SSO 登录脚本（Cube 平台）。

通过 Aegis SSO 登录，建立 Cube session，获取身份信息，
供 cube-create-task.py 等脚本使用。

用法：
    python3 aegis-login.py

凭据从 ~/.aegis/credentials.json 读取，格式：
{
    "username": "your_ldap_username",
    "password": "your_password"
}

输出文件 ~/.aegis/cookies.json 格式：
{
    "momoId": "xxx",
    "momoName": "xxx",
    "cookies": {"aegis_v3_session": "...", "JSESSIONID": "...", "auth_cookie": "..."}
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

COOKIES_FILE = os.path.join(AEGIS_DIR, "cookies.json")

CUBE_HOME = "https://cube.wemomo.com/"
CUBE_SESSION_USER = "https://cube.wemomo.com/apirest/session/user"


def main():
    check_requests()
    creds = load_credentials()
    session = create_session()

    # Aegis SSO 登录
    sso_login(session, creds)

    # 建立 Cube session
    session.get(CUBE_HOME, allow_redirects=True)
    resp = session.post(CUBE_SESSION_USER, data={"corp": "alpha", "env": "stage"})
    cube_user = resp.json().get("result", {})
    momo_id = cube_user.get("userId", "")
    momo_name = cube_user.get("userName", "")

    if not momo_id:
        print("错误：无法建立 Cube session", file=sys.stderr)
        sys.exit(1)

    # 保存 cookies（格式与原脚本完全一致，不影响 cube-create-task.py）
    save_cookie_file({
        "momoId": momo_id,
        "momoName": momo_name,
        "cookies": export_cookies(session),
    }, COOKIES_FILE)

    print(f"✅ 登录成功！")
    print(f"  用户: {cube_user.get('userCnName', '')} ({momo_id})")
    print(f"  cookie 已保存到: {COOKIES_FILE}")


if __name__ == "__main__":
    main()
