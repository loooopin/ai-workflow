#!/usr/bin/env python3
"""调休余额计算脚本。

查询 Moji 平台的加班记录和调休记录，计算剩余可调休小时数。

用法：
    python3 leave-balance.py                    # 自动计算
    python3 leave-balance.py --debug            # 同时保存原始 HTML 到 /tmp/moji-debug/
    python3 leave-balance.py --discover         # 仅抓取页面并保存，不解析
    python3 leave-balance.py --json             # JSON 格式输出

依赖：pip3 install requests beautifulsoup4
"""

import argparse
import json
import os
import re
import sys

MOJI_BASE = "https://moji.wemomo.com"
OVERTIME_LIST_URL = f"{MOJI_BASE}/care/ef?ef_type=4"
LEAVE_LIST_URL = f"{MOJI_BASE}/care/ef?ef_type=1&type=9"
DETAIL_URL_TPL = MOJI_BASE + "/care/ef/{}"

DEFAULT_COOKIE_FILE = os.path.expanduser("~/.aegis/moji-cookies.json")
DEBUG_DIR = "/tmp/moji-debug"

HOURS_PER_DAY = 8.0

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36")


# ---------------------------------------------------------------------------
# Infra: cookies, session, fetch, debug
# ---------------------------------------------------------------------------

def load_cookies(path):
    if not os.path.exists(path):
        print(f"错误：cookie 文件不存在: {path}", file=sys.stderr)
        print("请先运行 moji-login.py 登录", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)
    if "cookies" not in data:
        print("错误：cookie 文件格式不正确", file=sys.stderr)
        sys.exit(1)
    return data


def create_session(cookie_data):
    import requests
    session = requests.Session()
    session.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    for name, value in cookie_data["cookies"].items():
        session.cookies.set(name, value)
    return session


def fetch(session, url):
    resp = session.get(url, allow_redirects=True)
    if "aegis.immomo.com" in resp.url and "sso/login" in resp.url:
        print("错误：登录态已过期，请重新运行 moji-login.py", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    return resp.text


def save_debug(filename, content):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    path = os.path.join(DEBUG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
# Parsing: Moji 列表页（加班 / 调休共用结构 <div class="apply-li">）
# ---------------------------------------------------------------------------

def parse_duration(text):
    """解析 '1天' → 8.0 或 '5小时' → 5.0"""
    m = re.search(r"(\d+\.?\d*)\s*天", text)
    if m:
        return float(m.group(1)) * HOURS_PER_DAY
    m = re.search(r"(\d+\.?\d*)\s*(?:小时|h|H)", text)
    if m:
        return float(m.group(1))
    return 0.0


def parse_list_page(html):
    """解析 Moji 列表页，返回 [{id, status, start_date, hours, raw}]。

    HTML 结构：<div class="apply-li"> 包含记录文本和 <a href="//moji.wemomo.com/care/ef/{id}"> 链接。
    文本格式示例：
      加班 已生效 2026-08-29 10:00 至 2026-08-29 16:00 5小时 撤销 详情
      请假 - 调休 已生效 2026-07-03 10:00 至 2026-07-03 19:00 1天 撤销 详情
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    records = []

    for div in soup.find_all("div", class_="apply-li"):
        text = div.get_text(" ", strip=True)

        eid = ""
        link = div.find("a", href=re.compile(r"/care/ef/\d+"))
        if link:
            m = re.search(r"/care/ef/(\d+)", link["href"])
            if m:
                eid = m.group(1)

        # 状态
        if "已生效" in text:
            status = "已生效"
        elif "已撤销" in text:
            status = "已撤销"
        elif "审批中" in text:
            status = "审批中"
        elif "已拒绝" in text:
            status = "已拒绝"
        else:
            status = "unknown"

        # 日期区间 "YYYY-MM-DD HH:MM 至 YYYY-MM-DD HH:MM"
        start_date = ""
        dm = re.search(
            r"(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}\s+至\s+(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}",
            text,
        )
        if dm:
            start_date = dm.group(1)

        hours = parse_duration(text)

        records.append({
            "id": eid,
            "status": status,
            "start_date": start_date,
            "hours": hours,
            "raw": text,
        })

    return records


# ---------------------------------------------------------------------------
# Parsing: Moji 详情页（调休详情 <p class="p-item">）
# ---------------------------------------------------------------------------

def parse_detail_page(html):
    """解析 Moji 详情页的 <p class="p-item"> 键值对。

    返回 dict，key 为字段名（如 '加班日期'、'申请天数'），value 为值字符串。
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    fields = {}
    for p in soup.find_all("p", class_="p-item"):
        text = p.get_text(" ", strip=True)
        parts = re.split(r"\s*[:：]\s*", text, maxsplit=1)
        if len(parts) == 2:
            fields[parts[0].strip()] = parts[1].strip()
    return fields


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

def fetch_all_pages(session, base_url, debug=False, prefix="page"):
    """抓取所有分页，返回各页 HTML 列表。"""
    pages = []
    page = 1
    while True:
        sep = "&" if "?" in base_url else "?"
        url = base_url if page == 1 else f"{base_url}{sep}page={page}"
        html = fetch(session, url)
        if debug:
            save_debug(f"{prefix}-p{page}.html", html)
        pages.append(html)

        if not _has_next_page(html, page):
            break
        page += 1
        if page > 100:
            break
    return pages


def _has_next_page(html, current):
    nxt = current + 1
    return bool(re.search(rf"[?&]page={nxt}[\"\s'&>]", html))


# ---------------------------------------------------------------------------
# Balance calculation
# ---------------------------------------------------------------------------

def calculate_balance(overtime_records, leave_deductions):
    """计算余额。

    overtime_records: [{start_date, hours}]
    leave_deductions: [{overtime_date, hours_used, leave_id}]

    返回 (balance_map, unmatched)
    """
    balance = {}
    for ot in overtime_records:
        d = ot["start_date"]
        if d in balance:
            balance[d]["total_hours"] += ot["hours"]
        else:
            balance[d] = {"total_hours": ot["hours"], "used_hours": 0.0, "leave_ids": []}

    unmatched = []
    for ld in leave_deductions:
        od = ld["overtime_date"]
        if od in balance:
            balance[od]["used_hours"] += ld["hours_used"]
            balance[od]["leave_ids"].append(ld["leave_id"])
        else:
            unmatched.append(ld)

    return balance, unmatched


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_result(balance, unmatched, json_output=False):
    if json_output:
        records = []
        total = 0.0
        for date in sorted(balance):
            info = balance[date]
            remaining = max(info["total_hours"] - info["used_hours"], 0.0)
            total += remaining
            records.append({
                "date": date,
                "overtime_hours": info["total_hours"],
                "used_hours": info["used_hours"],
                "remaining_hours": remaining,
            })
        out = {"records": records, "total_remaining_hours": total}
        if unmatched:
            out["warnings"] = [
                {"leave_id": u["leave_id"], "overtime_date": u["overtime_date"],
                 "hours": u["hours_used"]}
                for u in unmatched
            ]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print("\n📊 调休余额计算结果")
    print("=" * 60)

    total_ot = 0.0
    total_used = 0.0
    total_remaining = 0.0

    print("\n可调休明细：")
    for date in sorted(balance):
        info = balance[date]
        remaining = max(info["total_hours"] - info["used_hours"], 0.0)
        total_ot += info["total_hours"]
        total_used += info["used_hours"]
        total_remaining += remaining
        marker = " ✅" if remaining > 0 else ""
        print(f"  {date}  加班 {info['total_hours']:5.1f}h"
              f"  已调休 {info['used_hours']:5.1f}h"
              f"  剩余 {remaining:5.1f}h{marker}")

    print(f"\n{'─' * 60}")
    print(f"  加班总计:  {total_ot:6.1f} 小时")
    print(f"  已调休:    {total_used:6.1f} 小时")
    print(f"  剩余可调:  {total_remaining:6.1f} 小时")

    if total_remaining == 0:
        print("\n  所有加班已调休完毕 🎉")

    if unmatched:
        print(f"\n⚠️  以下调休关联的加班日不在当前加班列表中（可能是更早的记录）：")
        for u in unmatched:
            print(f"  调休#{u['leave_id']} → 加班 {u['overtime_date']} "
                  f"{u['hours_used']:.1f}h")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    check_requests()

    parser = argparse.ArgumentParser(description="调休余额计算")
    parser.add_argument("--debug", action="store_true",
                        help="保存原始 HTML 到 /tmp/moji-debug/")
    parser.add_argument("--discover", action="store_true",
                        help="仅抓取并保存页面，不解析")
    parser.add_argument("--json", action="store_true",
                        help="JSON 格式输出")
    parser.add_argument("--cookie-file", default=DEFAULT_COOKIE_FILE)
    args = parser.parse_args()

    cookie_data = load_cookies(args.cookie_file)
    session = create_session(cookie_data)

    # ── 1. 获取加班列表（全部分页） ──
    print("正在获取加班记录...")
    ot_pages = fetch_all_pages(session, OVERTIME_LIST_URL,
                               debug=args.debug or args.discover, prefix="overtime")
    all_ot_records = []
    for html in ot_pages:
        all_ot_records.extend(parse_list_page(html))

    # 过滤：仅保留「已生效」
    ot_effective = [r for r in all_ot_records if r["status"] == "已生效"]
    print(f"  共 {len(all_ot_records)} 条，已生效 {len(ot_effective)} 条"
          f"（跨 {len(ot_pages)} 页）")

    # ── 2. 获取调休列表（全部分页） ──
    print("正在获取调休记录...")
    leave_pages = fetch_all_pages(session, LEAVE_LIST_URL,
                                  debug=args.debug or args.discover, prefix="leave")
    all_leave_records = []
    for html in leave_pages:
        all_leave_records.extend(parse_list_page(html))

    leave_effective = [r for r in all_leave_records if r["status"] == "已生效"]
    print(f"  共 {len(all_leave_records)} 条，已生效 {len(leave_effective)} 条"
          f"（跨 {len(leave_pages)} 页）")

    if args.discover:
        # 仅保存样本详情
        for rec in leave_effective[:3]:
            if rec["id"]:
                html = fetch(session, DETAIL_URL_TPL.format(rec["id"]))
                save_debug(f"leave-detail-{rec['id']}.html", html)
                print(f"  已保存调休详情 #{rec['id']}")
        for rec in ot_effective[:3]:
            if rec["id"]:
                html = fetch(session, DETAIL_URL_TPL.format(rec["id"]))
                save_debug(f"overtime-detail-{rec['id']}.html", html)
                print(f"  已保存加班详情 #{rec['id']}")
        print(f"\n✅ 原始页面已保存到 {DEBUG_DIR}/")
        return

    # ── 3. 逐条获取调休详情，提取关联加班信息 ──
    if leave_effective:
        print("正在获取调休详情（关联加班信息）...")
    leave_deductions = []
    for i, rec in enumerate(leave_effective):
        if not rec["id"]:
            continue
        detail_html = fetch(session, DETAIL_URL_TPL.format(rec["id"]))
        if args.debug:
            save_debug(f"leave-detail-{rec['id']}.html", detail_html)

        fields = parse_detail_page(detail_html)
        overtime_date = fields.get("加班日期", "").strip()
        leave_hours = parse_duration(fields.get("申请天数", ""))

        if overtime_date:
            leave_deductions.append({
                "leave_id": rec["id"],
                "overtime_date": overtime_date,
                "hours_used": leave_hours,
            })

        if (i + 1) % 10 == 0:
            print(f"  已处理 {i + 1}/{len(leave_effective)} ...")

    print(f"  成功提取 {len(leave_deductions)}/{len(leave_effective)} 条关联加班信息")

    # ── 4. 计算余额 ──
    balance, unmatched = calculate_balance(ot_effective, leave_deductions)

    # ── 5. 输出 ──
    print_result(balance, unmatched, json_output=args.json)


def check_requests():
    try:
        import requests  # noqa: F401
    except ImportError:
        print("错误：需要 requests 库", file=sys.stderr)
        print("安装：pip3 install requests", file=sys.stderr)
        sys.exit(1)
    try:
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        print("错误：需要 beautifulsoup4 库", file=sys.stderr)
        print("安装：pip3 install beautifulsoup4", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
