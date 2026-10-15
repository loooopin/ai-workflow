#!/usr/bin/env python3
"""Aegis SSO 登录脚本。

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

import base64
import json
import os
import re
import sys

AEGIS_DIR = os.path.expanduser("~/.aegis")
CREDENTIALS_FILE = os.path.join(AEGIS_DIR, "credentials.json")
COOKIES_FILE = os.path.join(AEGIS_DIR, "cookies.json")

AEGIS_SSO_LOGIN = "https://aegis.immomo.com/v3/sso/login"
CUBE_HOME = "https://cube.wemomo.com/"
CUBE_SESSION_USER = "https://cube.wemomo.com/apirest/session/user"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36")


def check_requests():
    try:
        import requests  # noqa: F401
    except ImportError:
        print("错误：需要 requests 库", file=sys.stderr)
        print("安装：pip3 install requests", file=sys.stderr)
        sys.exit(1)


def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        os.makedirs(AEGIS_DIR, exist_ok=True)
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({"username": "", "password": ""}, f, indent=2)
        print(f"请先填写凭据文件: {CREDENTIALS_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(CREDENTIALS_FILE) as f:
        creds = json.load(f)

    if not creds.get("username") or not creds.get("password"):
        print(f"凭据文件中 username 或 password 为空: {CREDENTIALS_FILE}", file=sys.stderr)
        sys.exit(1)
    return creds


def login(creds):
    import requests

    session = requests.Session()
    session.headers["User-Agent"] = UA

    # Step 1: 获取 Aegis SSO 登录页，提取 key
    resp = session.get(AEGIS_SSO_LOGIN, allow_redirects=True)
    match = re.search(r"/sso/login/([0-9a-f\-]{36})", resp.url)
    if not match:
        print(f"错误：无法从 Aegis SSO 提取 key, URL={resp.url}", file=sys.stderr)
        sys.exit(1)
    key = match.group(1)

    # Step 2: POST 登录（密码 Base64 编码）
    password_b64 = base64.b64encode(creds["password"].encode()).decode()
    login_url = f"{AEGIS_SSO_LOGIN}/{key}?callback_request_uri=/sso/login"
    resp = session.post(login_url, data={
        "email": creds["username"],
        "email_password": password_b64,
        "key": key,
        "callback": "",
    }, allow_redirects=True)

    # 验证 Aegis 登录
    resp = session.get("https://aegis.immomo.com/v3/api/login-user?fields=name,momoid")
    user_data = resp.json()
    aegis_user = user_data.get("data", {}).get("user")
    if not aegis_user:
        print("错误：Aegis 登录失败，用户名或密码错误", file=sys.stderr)
        sys.exit(1)

    # Step 3: 建立 Cube session
    # 先触发 JSESSIONID
    session.get(CUBE_HOME, allow_redirects=True)
    # session/user 建立 Cube 认证 session（设置 auth_cookie）
    resp = session.post(CUBE_SESSION_USER, data={"corp": "alpha", "env": "stage"})
    cube_user = resp.json().get("result", {})
    momo_id = cube_user.get("userId", "")
    momo_name = cube_user.get("userName", "")

    if not momo_id:
        print("错误：无法建立 Cube session", file=sys.stderr)
        sys.exit(1)

    # Step 4: 导出 cookies
    cookies_dict = {c.name: c.value for c in session.cookies}
    result = {
        "momoId": momo_id,
        "momoName": momo_name,
        "cookies": cookies_dict,
    }

    os.makedirs(AEGIS_DIR, exist_ok=True)
    with open(COOKIES_FILE, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ 登录成功！")
    print(f"  用户: {cube_user.get('userCnName', '')} ({momo_id})")
    print(f"  cookie 已保存到: {COOKIES_FILE}")


def main():
    check_requests()
    creds = load_credentials()
    login(creds)


if __name__ == "__main__":
    main()
