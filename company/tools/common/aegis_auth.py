"""Aegis SSO 认证公共模块。

提供 LDAP 凭据读取、Aegis SSO 登录、cookie 持久化等公共功能，
被 amar-cube-task-creator、amar-leave-balance 等工具共享。

典型用法：
    from aegis_auth import check_requests, load_credentials, create_session, \
                           sso_login, export_cookies, save_cookie_file

    check_requests()
    creds = load_credentials()
    session = create_session()
    user_info = sso_login(session, creds)
    # ... 建立特定服务 session ...
    save_cookie_file({"cookies": export_cookies(session)}, output_path)
"""

import base64
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

AEGIS_DIR = os.path.expanduser("~/.aegis")
CREDENTIALS_FILE = os.path.join(AEGIS_DIR, "credentials.json")

AEGIS_SSO_LOGIN = "https://aegis.immomo.com/v3/sso/login"
AEGIS_USER_API = "https://aegis.immomo.com/v3/api/login-user?fields=name,momoid"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36")


# ---------------------------------------------------------------------------
# 依赖检查
# ---------------------------------------------------------------------------

def check_requests():
    """确保 requests 库可用，不可用时打印提示并退出。"""
    try:
        import requests  # noqa: F401
    except ImportError:
        print("错误：需要 requests 库", file=sys.stderr)
        print("安装：pip3 install requests", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# 凭据
# ---------------------------------------------------------------------------

def load_credentials():
    """从 ~/.aegis/credentials.json 读取 LDAP 凭据。

    文件不存在时自动创建空模板并退出。

    Returns:
        dict: {"username": "...", "password": "..."}
    """
    if not os.path.exists(CREDENTIALS_FILE):
        os.makedirs(AEGIS_DIR, exist_ok=True)
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump({"username": "", "password": ""}, f, indent=2)
        print(f"请先填写凭据文件: {CREDENTIALS_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(CREDENTIALS_FILE) as f:
        creds = json.load(f)

    if not creds.get("username") or not creds.get("password"):
        print(f"凭据文件中 username 或 password 为空: {CREDENTIALS_FILE}",
              file=sys.stderr)
        sys.exit(1)
    return creds


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def create_session():
    """创建带 User-Agent 的 requests.Session。"""
    import requests
    session = requests.Session()
    session.headers["User-Agent"] = UA
    return session


# ---------------------------------------------------------------------------
# SSO 登录
# ---------------------------------------------------------------------------

def sso_login(session, creds):
    """执行 Aegis SSO 登录。

    成功后 session 中会携带 Aegis SSO cookie，可用于后续访问任意
    *.wemomo.com / *.immomo.com 服务并建立对应 session。

    Args:
        session: requests.Session，登录后 cookie 写入此 session。
        creds: load_credentials() 返回的凭据 dict。

    Returns:
        dict: Aegis 用户信息，如 {"name": "胡晓冬", "momoid": "xxx"}
    """
    # Step 1: 获取 SSO 登录页，提取 key
    resp = session.get(AEGIS_SSO_LOGIN, allow_redirects=True)
    match = re.search(r"/sso/login/([0-9a-f\-]{36})", resp.url)
    if not match:
        print(f"错误：无法从 Aegis SSO 提取 key, URL={resp.url}", file=sys.stderr)
        sys.exit(1)
    key = match.group(1)

    # Step 2: POST 登录（密码 Base64 编码）
    password_b64 = base64.b64encode(creds["password"].encode()).decode()
    login_url = f"{AEGIS_SSO_LOGIN}/{key}?callback_request_uri=/sso/login"
    session.post(login_url, data={
        "email": creds["username"],
        "email_password": password_b64,
        "key": key,
        "callback": "",
    }, allow_redirects=True)

    # Step 3: 验证
    resp = session.get(AEGIS_USER_API)
    user_data = resp.json()
    aegis_user = user_data.get("data", {}).get("user")
    if not aegis_user:
        print("错误：Aegis 登录失败，用户名或密码错误", file=sys.stderr)
        sys.exit(1)

    return aegis_user


# ---------------------------------------------------------------------------
# Cookie 持久化
# ---------------------------------------------------------------------------

def export_cookies(session):
    """将 session 中所有 cookie 导出为 {name: value} dict。"""
    return {c.name: c.value for c in session.cookies}


def save_cookie_file(data, output_path):
    """将 cookie 数据（dict）写入 JSON 文件。

    Args:
        data: 要写入的完整 dict（应包含 "cookies" 键）。
        output_path: 目标文件绝对路径。
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
