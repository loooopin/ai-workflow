#!/usr/bin/env python3
"""
Kibana 日志统计工具
统计指定服务的日志条数，按日志级别分组，生成报告
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib import request, error
from typing import Dict, List, Tuple, Optional


def detect_appkey_from_project() -> Optional[str]:
    """
    从当前项目的 app.yaml 文件中自动检测 appKey
    支持多模块项目（如 Maven multi-module）
    
    Returns:
        检测到的 appKey，如果未找到则返回 None
    """
    cwd = Path.cwd()
    
    # 需要排除的目录（避免遍历大型目录）
    EXCLUDE_DIRS = {'.git', 'node_modules', 'target', 'build', 'dist', '.idea', 
                    '__pycache__', '.venv', 'venv', '.svn', '.hg'}
    
    # 策略1: 优先查找 src 目录中的 app.yaml（最常见的位置）
    try:
        for path in cwd.glob('**/src/**/app.yaml'):
            # 检查路径中是否包含排除目录
            if any(excluded in path.parts for excluded in EXCLUDE_DIRS):
                continue
            
            if path.is_file():
                try:
                    content = path.read_text(encoding='utf-8')
                    pattern = r'appKey\s*:\s*([^\s#]+)'
                    match = re.search(pattern, content)
                    
                    if match:
                        appkey = match.group(1).strip()
                        if appkey.startswith('momo.'):
                            print(f"🔍 自动检测到 appKey: {appkey}", file=sys.stderr)
                            print(f"   (从 {path.relative_to(cwd)} 读取)", file=sys.stderr)
                            return appkey
                except Exception:
                    pass
    except Exception:
        pass
    
    # 策略2: 查找其他位置的 app.yaml（但排除大型目录）
    try:
        count = 0
        max_files = 50  # 限制最多检查50个文件，避免遍历过多
        for path in cwd.glob('**/app.yaml'):
            count += 1
            if count > max_files:
                break
            
            # 检查路径中是否包含排除目录
            if any(excluded in path.parts for excluded in EXCLUDE_DIRS):
                continue
            
            if path.is_file():
                try:
                    content = path.read_text(encoding='utf-8')
                    pattern = r'appKey\s*:\s*([^\s#]+)'
                    match = re.search(pattern, content)
                    
                    if match:
                        appkey = match.group(1).strip()
                        if appkey.startswith('momo.'):
                            print(f"🔍 自动检测到 appKey: {appkey}", file=sys.stderr)
                            print(f"   (从 {path.relative_to(cwd)} 读取)", file=sys.stderr)
                            return appkey
                except Exception:
                    pass
    except Exception:
        pass
    
    # 策略2: 查找固定位置的 app.yaml（兼容旧逻辑）
    possible_paths = [
        cwd / 'app.yaml',
        cwd / 'config' / 'app.yaml',
        cwd / 'conf' / 'app.yaml',
    ]
    
    # 向上查找父目录
    parent = cwd.parent
    for _ in range(3):
        possible_paths.append(parent / 'app.yaml')
        parent = parent.parent
    
    for path in possible_paths:
        if path.exists() and path.is_file():
            try:
                content = path.read_text(encoding='utf-8')
                pattern = r'appKey\s*:\s*([^\s#]+)'
                match = re.search(pattern, content)
                
                if match:
                    appkey = match.group(1).strip()
                    if appkey.startswith('momo.'):
                        print(f"🔍 自动检测到 appKey: {appkey}", file=sys.stderr)
                        print(f"   (从 {path} 读取)", file=sys.stderr)
                        return appkey
            except Exception:
                pass
    
    return None


class KibanaLogStats:
    """Kibana 日志统计类"""
    
    # API 地址配置
    KIBANA_URLS = {
        'offline': 'https://alpha-kibana.wemomo.com/alpha-public/api/console/proxy',
        'online': 'https://aws-kibana-mdp-logs.wemomo.com/api/console/proxy'
    }
    
    # 日志级别列表（按优先级排序）
    LOG_LEVELS = ['ALL', 'ERROR', 'WARN', 'INFO', 'DEBUG']
    
    def __init__(self, appkey: str, env: str = 'offline', hours: int = 24):
        """
        初始化
        
        Args:
            appkey: 服务的 appKey
            env: 环境（offline 或 online）
            hours: 时间范围（小时）
        """
        self.appkey = appkey
        self.env = env
        self.hours = hours
        self.base_url = self.KIBANA_URLS.get(env, self.KIBANA_URLS['offline'])
        
    def build_query(self, log_level: str) -> str:
        """
        构建 Elasticsearch 查询 JSON
        
        Args:
            log_level: 日志级别（ALL 表示不限）
        
        Returns:
            查询 JSON 字符串
        """
        must_conditions = [
            {
                "match_phrase": {
                    "appKey": self.appkey
                }
            }
        ]
        
        # 如果不是 ALL，添加日志级别过滤
        if log_level != 'ALL':
            must_conditions.append({
                "match": {
                    "logLevel": log_level
                }
            })
        
        query = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            }
        }
        
        return json.dumps(query)
    
    def query_count(self, log_level: str) -> Tuple[int, Dict]:
        """
        查询指定级别的日志条数
        
        Args:
            log_level: 日志级别
        
        Returns:
            (日志条数, 分片信息)
        """
        # 通过 Kibana API Proxy 查询 ES（查询所有索引，通过 appKey 过滤）
        # 注意：某些服务（如 user/composite/discover）在 Kibana 页面中有独立的索引模式 ID
        # 但 API 查询通过 appKey 过滤即可，无需指定索引 ID
        url = f"{self.base_url}?path=_count&method=POST"
        query_data = self.build_query(log_level)
        
        try:
            req = request.Request(
                url,
                data=query_data.encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'kbn-xsrf': 'true'
                },
                method='POST'
            )
            
            with request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'error' in result:
                    error_msg = result['error'].get('reason', '未知错误')
                    raise Exception(f"查询失败: {error_msg}")
                
                count = result.get('count', 0)
                shards = result.get('_shards', {})
                
                return count, shards
                
        except error.URLError as e:
            raise Exception(f"网络错误: {e.reason}")
        except Exception as e:
            raise Exception(f"查询出错: {str(e)}")
    
    def collect_statistics(self) -> Dict:
        """
        收集所有级别的统计信息
        
        Returns:
            统计结果字典
        """
        print(f"🔍 正在统计日志...", file=sys.stderr)
        print(f"   服务: {self.appkey}", file=sys.stderr)
        print(f"   环境: {'线上' if self.env == 'online' else '线下'}", file=sys.stderr)
        print(f"   时间范围: 最近 {self.hours} 小时\n", file=sys.stderr)
        
        results = {}
        total_shards = 0
        successful_shards = 0
        failed_shards = 0
        start_time = time.time()
        
        for level in self.LOG_LEVELS:
            try:
                print(f"   查询 {level:5s} 级别...", end='', flush=True, file=sys.stderr)
                count, shards = self.query_count(level)
                
                results[level] = {
                    'count': count,
                    'shards': shards
                }
                
                # 累加分片信息（使用第一次查询的分片数）
                if level == 'ALL':
                    total_shards = shards.get('total', 0)
                    successful_shards = shards.get('successful', 0)
                    failed_shards = shards.get('failed', 0)
                
                print(f" ✅ {count:,} 条", file=sys.stderr)
                time.sleep(0.5)  # 避免请求过快
                
            except Exception as e:
                print(f" ❌ 失败: {e}", file=sys.stderr)
                results[level] = {
                    'count': 0,
                    'error': str(e)
                }
        
        elapsed_time = time.time() - start_time
        
        return {
            'levels': results,
            'shards': {
                'total': total_shards,
                'successful': successful_shards,
                'failed': failed_shards
            },
            'elapsed_time': elapsed_time
        }
    
    @staticmethod
    def format_count(count: int) -> str:
        """格式化数字显示"""
        if count >= 1_000_000_000:
            return f"{count / 1_000_000_000:.1f}B"
        elif count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 10_000:
            return f"{count / 1000:.1f}K"
        else:
            return f"{count:,}"
    
    def _build_report_content(self, statistics: Dict) -> str:
        """
        构建报告内容
        
        Args:
            statistics: 统计结果
        
        Returns:
            报告内容字符串
        """
        env_name = "线上（生产环境）" if self.env == 'online' else "线下（测试环境）"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取 ALL 的总数用于计算占比
        total_count = statistics['levels'].get('ALL', {}).get('count', 0)
        
        # 按条数排序（ALL 始终排第一）
        sorted_levels = ['ALL'] + sorted(
            [l for l in self.LOG_LEVELS if l != 'ALL'],
            key=lambda x: statistics['levels'].get(x, {}).get('count', 0),
            reverse=True
        )
        
        # 生成 Markdown 内容
        lines = [
            f"# 📊 Kibana 日志统计报告\n",
            f"**生成时间**: {now}  ",
            f"**服务**: `{self.appkey}`  ",
            f"**环境**: {env_name}  ",
            f"**时间范围**: 最近 {self.hours} 小时  \n",
            "## 📈 统计结果\n",
            "| 日志级别 | 日志条数 | 格式化 | 占比 |",
            "|---------|---------|--------|------|"
        ]
        
        for level in sorted_levels:
            level_data = statistics['levels'].get(level, {})
            count = level_data.get('count', 0)
            
            if 'error' in level_data:
                lines.append(f"| {level} | ❌ 查询失败 | - | - |")
            else:
                formatted = self.format_count(count)
                percentage = (count / total_count * 100) if total_count > 0 and level != 'ALL' else 100.0
                lines.append(f"| {level} | {count:,} | {formatted} | {percentage:.1f}% |")
        
        # 添加查询详情
        shards = statistics['shards']
        success_rate = (shards['successful'] / shards['total'] * 100) if shards['total'] > 0 else 0
        
        lines.extend([
            "\n## 🔍 查询详情\n",
            f"- **查询成功率**: {success_rate:.1f}% ({shards['successful']}/{shards['total']} 分片)",
            f"- **失败分片**: {shards['failed']} 个",
            f"- **查询耗时**: {statistics['elapsed_time']:.1f} 秒\n",
            "---",
            f"*由 Kibana Log Statistics 生成 @ {now}*"
        ])
        
        return '\n'.join(lines)
    
    def print_report(self, statistics: Dict):
        """
        打印报告到控制台
        
        Args:
            statistics: 统计结果
        """
        report_content = self._build_report_content(statistics)
        print(report_content, file=sys.stderr)
    
    def save_report(self, statistics: Dict, output_file: str):
        """
        保存报告到文件
        
        Args:
            statistics: 统计结果
            output_file: 输出文件路径
        """
        report_content = self._build_report_content(statistics)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='统计 Kibana 日志条数，按日志级别分组生成报告'
    )
    
    parser.add_argument(
        '--appkey',
        required=False,
        help='服务的完整 appKey。如果不提供，会自动从项目的 app.yaml 中检测'
    )
    
    parser.add_argument(
        '--env',
        choices=['offline', 'online'],
        default='offline',
        help='环境：offline（线下）或 online（线上），默认 offline'
    )
    
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='时间范围（小时），默认 24'
    )
    
    parser.add_argument(
        '--output',
        default='log_statistics',
        help='输出文件名前缀（不含扩展名），默认 log_statistics'
    )
    
    parser.add_argument(
        '--auto-save',
        action='store_true',
        help='自动保存报告文件，不询问用户（默认会询问）'
    )
    
    args = parser.parse_args()
    
    try:
        # 获取 appKey（优先使用命令行参数，否则自动检测）
        appkey = args.appkey
        if not appkey:
            print("📍 未指定 appKey，尝试自动检测...\n", file=sys.stderr)
            appkey = detect_appkey_from_project()
            
            if not appkey:
                print("❌ 无法自动检测 appKey，请通过 --appkey 参数指定", file=sys.stderr)
                print("\n示例:", file=sys.stderr)
                print("  python3 log_stats.py --appkey momo.bpm.biz.overseas-matchmaker.ultron-user\n", file=sys.stderr)
                sys.exit(1)
        
        # 创建统计对象
        stats = KibanaLogStats(
            appkey=appkey,
            env=args.env,
            hours=args.hours
        )
        
        # 收集统计信息
        statistics = stats.collect_statistics()
        
        # 先输出统计结果到控制台
        print("\n" + "="*60, file=sys.stderr)
        stats.print_report(statistics)
        print("="*60 + "\n", file=sys.stderr)
        
        # 询问是否保存报告文件
        output_file = f"{args.output}.md"
        
        if args.auto_save:
            # 自动保存模式，直接生成文件
            stats.save_report(statistics, output_file)
            print(f"✅ 报告已保存: {output_file}", file=sys.stderr)
        else:
            # 询问用户是否保存
            try:
                answer = input(f"📄 是否保存为报告文件 {output_file}? (y/n): ").strip().lower()
                if answer in ['y', 'yes', '是']:
                    stats.save_report(statistics, output_file)
                    print(f"✅ 报告已保存: {output_file}", file=sys.stderr)
                else:
                    print("💡 已跳过保存", file=sys.stderr)
            except (EOFError, KeyboardInterrupt):
                # 处理非交互环境或用户中断的情况
                print("\n💡 非交互环境，已跳过保存", file=sys.stderr)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
