#!/usr/bin/env python3
"""Cube 创建定时任务脚本。

用法：
    python3 cube-create-task.py \\
        --env test \\
        --app-key "momo.bpm.biz.overseas-matchmaker.ultron-game" \\
        --name "任务名称" \\
        --nick-name "任务别名" \\
        --description "任务描述" \\
        --cron "0 0 2 * * ?" \\
        --url "/service/ultron/game/game-schedule-stage" \\
        --method "methodName"

可选参数：
    --param '[]'       方法入参（JSON数组字符串），默认 '[]'
    --timeout 3000     超时毫秒，默认 3000
    --cookie-file PATH cookie 文件路径，默认 ~/.aegis/cookies.json

依赖：pip3 install requests
"""

import argparse
import json
import os
import sys

CUBE_CREATE_TASK = "https://cube.wemomo.com/apirest/httpproxy/web/createTask"

ENV_MAP = {
    "test":  {"corp": "alpha",    "env": "stage", "ext_env": 1},
    "prod":  {"corp": "overseas", "env": "prod",  "ext_env": 0},
}


def check_requests():
    try:
        import requests  # noqa: F401
    except ImportError:
        print("错误：需要 requests 库", file=sys.stderr)
        print("安装：pip3 install requests", file=sys.stderr)
        sys.exit(1)


def load_cookies(cookie_file):
    path = os.path.expanduser(cookie_file)
    if not os.path.exists(path):
        print(f"错误：cookie 文件不存在: {path}", file=sys.stderr)
        print("请先运行 aegis-login.py 登录", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)
    for key in ["momoId", "momoName", "cookies"]:
        if key not in data:
            print(f"错误：cookie 文件缺少字段: {key}", file=sys.stderr)
            sys.exit(1)
    return data


def create_task(args, env_cfg, cookie_data):
    import requests

    ext = json.dumps({
        "taskSyncType": "sync",
        "env": env_cfg["ext_env"],
        "param": args.param,
        "contentType": "",
        "enablePreferredHost": False,
        "preferredHost": "",
        "preferredHostAddress": "",
        "url": args.url,
        "method": args.method,
        "scriptType": "",
        "scriptCommand": "",
        "timeout": str(args.timeout),
        "retryTime": "0",
        "retryDelay": "100",
        "failRetryTime": "0",
        "failRetryDelay": "100",
        "notifyPhase": "2,3",
        "notifyLevel": "1",
        "scriptUser": "",
        "execHosts": [],
    }, ensure_ascii=False)

    task = json.dumps({
        "momoId": cookie_data["momoId"],
        "momoName": cookie_data["momoName"],
        "appKey": args.app_key,
        "name": args.name,
        "nickName": args.nick_name,
        "description": args.description,
        "executeType": 1,
        "dispatchType": 1,
        "misfirePolicy": 2,
        "misfireThreshold": 60000,
        "delayDispatchPolicy": 1,
        "cronExpression": args.cron,
        "type": 1,
        "subType": 0,
        "creator": "",
        "coreType": 0,
        "ext": ext,
    }, ensure_ascii=False)

    session = requests.Session()
    session.headers["User-Agent"] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36"
    )
    for name, value in cookie_data["cookies"].items():
        session.cookies.set(name, value)

    resp = session.post(CUBE_CREATE_TASK, data={
        "json": task,
        "corp": env_cfg["corp"],
        "env": env_cfg["env"],
        "momoId": cookie_data["momoId"],
        "momoName": cookie_data["momoName"],
    }, headers={"X-Refer-ID": "scheduler"})

    return resp.json()


def main():
    check_requests()

    parser = argparse.ArgumentParser(description="Cube 创建定时任务")
    parser.add_argument("--env", required=True, choices=["test", "prod"])
    parser.add_argument("--app-key", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--nick-name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--cron", required=True, help="6位cron表达式")
    parser.add_argument("--url", required=True, help="MOA 服务 URI")
    parser.add_argument("--method", required=True, help="方法名")
    parser.add_argument("--param", default="[]", help="方法入参JSON数组")
    parser.add_argument("--timeout", type=int, default=3000, help="超时ms")
    parser.add_argument("--cookie-file", default="~/.aegis/cookies.json")
    args = parser.parse_args()

    env_cfg = ENV_MAP[args.env]
    cookie_data = load_cookies(args.cookie_file)

    print(f"正在创建 Cube 任务...")
    print(f"  环境: {args.env} (corp={env_cfg['corp']}, env={env_cfg['env']})")
    print(f"  应用: {args.app_key}")
    print(f"  任务: {args.name}")
    print(f"  方法: {args.url} -> {args.method}")
    print(f"  调度: {args.cron}")

    result = create_task(args, env_cfg, cookie_data)

    if result.get("ec") == 200 and result.get("result") == "success":
        print(f"\n✅ 任务创建成功！")
    else:
        print(f"\n❌ 任务创建失败", file=sys.stderr)
        print(f"  响应: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
