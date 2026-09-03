#!/usr/bin/env python3
"""
Kibana 日志关键词统计工具
自动扫描 Java 项目提取日志关键词并统计条数，或手动指定关键词
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
from typing import Dict, List, Tuple, Optional, Set


def detect_appkey_from_project(base_path: Path = None) -> Optional[str]:
    """
    从项目的 app.yaml 文件中自动检测 appKey
    支持多模块项目（如 Maven multi-module）
    """
    if base_path is None:
        base_path = Path.cwd()
    
    # 需要排除的目录（避免遍历大型目录）
    EXCLUDE_DIRS = {'.git', 'node_modules', 'target', 'build', 'dist', '.idea', 
                    '__pycache__', '.venv', 'venv', '.svn', '.hg'}
    
    # 策略1: 优先查找 src 目录中的 app.yaml（最常见的位置）
    try:
        for path in base_path.glob('**/src/**/app.yaml'):
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
                            try:
                                rel_path = path.relative_to(base_path)
                            except ValueError:
                                rel_path = path
                            print(f"   (从 {rel_path} 读取)", file=sys.stderr)
                            return appkey
                except Exception:
                    pass
    except Exception:
        pass
    
    # 策略2: 查找其他位置的 app.yaml（但排除大型目录）
    try:
        count = 0
        max_files = 50  # 限制最多检查50个文件，避免遍历过多
        for path in base_path.glob('**/app.yaml'):
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
                            try:
                                rel_path = path.relative_to(base_path)
                            except ValueError:
                                rel_path = path
                            print(f"   (从 {rel_path} 读取)", file=sys.stderr)
                            return appkey
                except Exception:
                    pass
    except Exception:
        pass
    
    # 策略2: 查找固定位置的 app.yaml（兼容旧逻辑）
    possible_paths = [
        base_path / 'app.yaml',
        base_path / 'config' / 'app.yaml',
        base_path / 'conf' / 'app.yaml',
    ]
    
    # 向上查找父目录
    parent = base_path.parent
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
                        try:
                            rel_path = path.relative_to(base_path)
                        except ValueError:
                            rel_path = path
                        print(f"   (从 {rel_path} 读取)", file=sys.stderr)
                        return appkey
            except Exception:
                pass
    
    return None


def extract_log_keywords_from_java(project_path: Path, max_keywords_per_level: int = 50, max_files: int = 500) -> Dict[str, Set[str]]:
    """
    扫描 Java 项目，提取所有日志关键词
    
    Args:
        project_path: 项目路径
        max_keywords_per_level: 每个日志级别最多提取的关键词数量（默认 50）
        max_files: 最多扫描的文件数量（默认 500）
    
    Returns:
        按日志级别分组的关键词集合
        格式: {'ERROR': {'关键词1', '关键词2'}, 'INFO': {...}, ...}
    """
    print("🔍 正在扫描 Java 项目...", file=sys.stderr)
    
    # 使用字典记录关键词出现频率
    keywords_frequency = {
        'ERROR': {},  # {keyword: count}
        'WARN': {},
        'INFO': {},
        'DEBUG': {}
    }
    
    # 日志方法的正则模式
    # 匹配: log.error("xxx"), logger.info("xxx"), log.warn("xxx {}", var)
    patterns = {
        'ERROR': [
            r'log(?:ger)?\.error\s*\(\s*"([^"]+)"',
            r'log(?:ger)?\.error\s*\(\s*\'([^\']+)\'',
        ],
        'WARN': [
            r'log(?:ger)?\.warn\s*\(\s*"([^"]+)"',
            r'log(?:ger)?\.warn\s*\(\s*\'([^\']+)\'',
        ],
        'INFO': [
            r'log(?:ger)?\.info\s*\(\s*"([^"]+)"',
            r'log(?:ger)?\.info\s*\(\s*\'([^\']+)\'',
        ],
        'DEBUG': [
            r'log(?:ger)?\.debug\s*\(\s*"([^"]+)"',
            r'log(?:ger)?\.debug\s*\(\s*\'([^\']+)\'',
        ]
    }
    
    # 优先扫描 src/main/java 目录
    priority_paths = [
        project_path / 'src' / 'main' / 'java',
        project_path / 'src',
        project_path
    ]
    
    java_files = []
    for path in priority_paths:
        if path.exists() and path.is_dir():
            files = list(path.rglob('*.java'))
            java_files.extend(files)
            if len(java_files) >= max_files:
                java_files = java_files[:max_files]
                break
    
    if not java_files:
        print("  ⚠️  未找到 Java 文件", file=sys.stderr)
        return {}
    
    print(f"  找到 {len(java_files)} 个 Java 文件", end='', file=sys.stderr)
    if len(java_files) >= max_files:
        print(f"（已限制为 {max_files} 个）", file=sys.stderr)
    else:
        print("", file=sys.stderr)
    
    file_count = 0
    for java_file in java_files:
        try:
            content = java_file.read_text(encoding='utf-8', errors='ignore')
            
            for level, level_patterns in patterns.items():
                for pattern in level_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        keyword = match.group(1)
                        # 清理关键词（移除占位符、参数等）
                        keyword = clean_keyword(keyword)
                        if keyword:
                            # 统计频率
                            keywords_frequency[level][keyword] = keywords_frequency[level].get(keyword, 0) + 1
            
            file_count += 1
            if file_count % 50 == 0:
                print(f"  已扫描 {file_count}/{len(java_files)} 个文件...", file=sys.stderr)
                
        except Exception as e:
            # 跳过无法读取的文件
            pass
    
    # 按频率排序，只保留 Top N
    keywords_by_level = {}
    total_before_limit = 0
    total_after_limit = 0
    
    for level, freq_dict in keywords_frequency.items():
        total_before_limit += len(freq_dict)
        
        # 按频率降序排序
        sorted_keywords = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)
        
        # 限制数量
        top_keywords = sorted_keywords[:max_keywords_per_level]
        keywords_by_level[level] = set(kw for kw, _ in top_keywords)
        
        total_after_limit += len(keywords_by_level[level])
    
    # 统计结果
    print(f"  ✅ 扫描完成，找到 {total_before_limit} 个关键词", end='', file=sys.stderr)
    if total_before_limit > total_after_limit:
        print(f"（已按频率选择 Top {total_after_limit} 个）：", file=sys.stderr)
    else:
        print("：", file=sys.stderr)
    
    for level, keywords in keywords_by_level.items():
        if keywords:
            # 显示频率信息
            level_freq = keywords_frequency[level]
            total_freq = sum(level_freq.get(kw, 0) for kw in keywords)
            print(f"     {level}: {len(keywords)} 个关键词（出现 {total_freq} 次）", file=sys.stderr)
    
    return keywords_by_level


def clean_keyword(keyword: str) -> str:
    """
    清理日志关键词
    - 移除占位符：{}, {0}, {}等
    - 移除多余空格
    - 限制长度（避免太长的日志消息）
    """
    # 移除占位符
    keyword = re.sub(r'\{[^}]*\}', '', keyword)
    
    # 移除多余空格
    keyword = re.sub(r'\s+', ' ', keyword).strip()
    
    # 如果太短或太长，跳过
    if len(keyword) < 3 or len(keyword) > 100:
        return ''
    
    # 移除一些常见的无意义词
    skip_keywords = ['error', 'warn', 'info', 'debug', 'exception', 'null']
    if keyword.lower() in skip_keywords:
        return ''
    
    return keyword


class KibanaKeywordStats:
    """Kibana 关键词统计类"""
    
    KIBANA_URLS = {
        'offline': 'https://alpha-kibana.wemomo.com/alpha-public/api/console/proxy',
        'online': 'https://aws-kibana-mdp-logs.wemomo.com/api/console/proxy'
    }
    
    def __init__(self, appkey: str, env: str = 'offline', hours: int = 24):
        self.appkey = appkey
        self.env = env
        self.hours = hours
        self.base_url = self.KIBANA_URLS.get(env, self.KIBANA_URLS['offline'])
    
    def build_query(self, keyword: str, log_level: str = None) -> str:
        """构建查询 JSON"""
        must_conditions = [
            {"match_phrase": {"appKey": self.appkey}},
            {"query_string": {"query": f'"{keyword}"'}}  # 精确短语搜索
        ]
        
        if log_level:
            must_conditions.append({"match": {"logLevel": log_level}})
        
        query = {
            "query": {
                "bool": {
                    "must": must_conditions
                }
            }
        }
        
        return json.dumps(query)
    
    def query_keyword_count(self, keyword: str, log_level: str = None) -> Tuple[int, Dict]:
        """查询指定关键词的日志条数"""
        # 通过 Kibana API Proxy 查询 ES（查询所有索引，通过 appKey 过滤）
        # 注意：某些服务（如 user/composite/discover）在 Kibana 页面中有独立的索引模式 ID
        # 但 API 查询通过 appKey 过滤即可，无需指定索引 ID
        url = f"{self.base_url}?path=_count&method=POST"
        query_data = self.build_query(keyword, log_level)
        
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
                    raise Exception(f"查询失败: {result['error'].get('reason', '未知错误')}")
                
                count = result.get('count', 0)
                shards = result.get('_shards', {})
                
                return count, shards
                
        except error.URLError as e:
            raise Exception(f"网络错误: {e.reason}")
        except Exception as e:
            raise Exception(f"查询出错: {str(e)}")
    
    def batch_query_keywords(self, keywords_by_level: Dict[str, Set[str]]) -> List[Dict]:
        """批量查询关键词统计"""
        results = []
        total_keywords = sum(len(kws) for kws in keywords_by_level.values())
        
        print(f"\n🔍 正在查询 {total_keywords} 个关键词的日志条数...", file=sys.stderr)
        print(f"   环境: {'线上' if self.env == 'online' else '线下'}", file=sys.stderr)
        print(f"   时间范围: 最近 {self.hours} 小时\n", file=sys.stderr)
        
        processed = 0
        for level, keywords in keywords_by_level.items():
            for keyword in sorted(keywords):  # 按字母排序
                try:
                    processed += 1
                    print(f"   [{processed}/{total_keywords}] 查询: {level:5s} - {keyword[:50]:50s}", end='', flush=True, file=sys.stderr)
                    
                    count, shards = self.query_keyword_count(keyword, level)
                    
                    results.append({
                        'keyword': keyword,
                        'level': level,
                        'count': count,
                        'shards': shards
                    })
                    
                    print(f" ✅ {count:,} 条", file=sys.stderr)
                    time.sleep(0.3)  # 避免请求过快
                    
                except Exception as e:
                    print(f" ❌ 失败: {e}", file=sys.stderr)
                    results.append({
                        'keyword': keyword,
                        'level': level,
                        'count': 0,
                        'error': str(e)
                    })
        
        return results
    
    @staticmethod
    def format_count(count: int) -> str:
        """格式化数字显示"""
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        elif count >= 10_000:
            return f"{count / 1000:.1f}K"
        else:
            return f"{count:,}"
    
    def generate_report(self, results: List[Dict], output_file: str = None, save_to_file: bool = True):
        """生成报告
        
        Args:
            results: 查询结果列表
            output_file: 输出文件名（当 save_to_file=True 时使用）
            save_to_file: 是否保存到文件。False 时只输出到控制台
        """
        env_name = "线上（生产环境）" if self.env == 'online' else "线下（测试环境）"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 按条数降序排序
        sorted_results = sorted(results, key=lambda x: x.get('count', 0), reverse=True)
        
        # 按日志级别分组
        by_level = {}
        for result in sorted_results:
            level = result['level']
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(result)
        
        lines = [
            f"# 📊 Kibana 日志关键词统计报告\n",
            f"**生成时间**: {now}  ",
            f"**服务**: `{self.appkey}`  ",
            f"**环境**: {env_name}  ",
            f"**时间范围**: 最近 {self.hours} 小时  ",
            f"**统计关键词数**: {len(results)} 个\n",
        ]
        
        # 总览：Top 10
        lines.append("## 🔥 热门关键词 Top 10\n")
        lines.append("| 排名 | 关键词 | 日志级别 | 日志条数 | 格式化 |")
        lines.append("|------|--------|---------|---------|--------|")
        
        for idx, result in enumerate(sorted_results[:10], 1):
            keyword = result['keyword'][:50]
            level = result['level']
            count = result.get('count', 0)
            formatted = self.format_count(count)
            
            if 'error' in result:
                lines.append(f"| {idx} | {keyword} | {level} | ❌ 查询失败 | - |")
            else:
                lines.append(f"| {idx} | {keyword} | {level} | {count:,} | {formatted} |")
        
        # 按日志级别统计
        lines.append("\n## 📈 按日志级别统计\n")
        
        for level in ['ERROR', 'WARN', 'INFO', 'DEBUG']:
            if level not in by_level or not by_level[level]:
                continue
            
            level_results = by_level[level]
            level_total = sum(r.get('count', 0) for r in level_results)
            
            lines.append(f"### {level} 级别 ({len(level_results)} 个关键词，共 {level_total:,} 条日志)\n")
            lines.append("| 排名 | 关键词 | 日志条数 | 格式化 |")
            lines.append("|------|--------|---------|--------|")
            
            for idx, result in enumerate(level_results[:20], 1):  # 每个级别最多显示 20 个
                keyword = result['keyword'][:60]
                count = result.get('count', 0)
                formatted = self.format_count(count)
                
                if 'error' in result:
                    lines.append(f"| {idx} | {keyword} | ❌ 失败 | - |")
                else:
                    lines.append(f"| {idx} | {keyword} | {count:,} | {formatted} |")
            
            if len(level_results) > 20:
                lines.append(f"\n*还有 {len(level_results) - 20} 个关键词未显示*\n")
        
        # 统计汇总
        lines.extend([
            "\n## 📋 统计汇总\n",
            f"- **总关键词数**: {len(results)} 个",
            f"- **有日志的关键词**: {len([r for r in results if r.get('count', 0) > 0])} 个",
            f"- **无日志的关键词**: {len([r for r in results if r.get('count', 0) == 0])} 个",
            f"- **查询失败**: {len([r for r in results if 'error' in r])} 个\n",
            "---",
            f"*由 Kibana Log Keyword Statistics 生成 @ {now}*"
        ])
        
        report_content = '\n'.join(lines)
        
        # 根据参数决定是否保存到文件
        if save_to_file and output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\n✅ 报告已生成: {output_file}", file=sys.stderr)
        
        # 总是输出到控制台
        print(report_content)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='统计 Kibana 日志关键词条数（自动扫描或手动指定）'
    )
    
    parser.add_argument(
        '--appkey',
        help='服务的完整 appKey。不提供时从 app.yaml 自动检测'
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
        '--keywords',
        nargs='+',
        help='手动指定关键词列表（空格分隔）。不提供时自动扫描项目'
    )
    
    parser.add_argument(
        '--levels',
        nargs='+',
        choices=['ERROR', 'WARN', 'INFO', 'DEBUG'],
        help='指定日志级别（配合 --keywords 使用）。不提供时使用 ALL'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        help='Java 项目路径。不提供时使用当前目录'
    )
    
    parser.add_argument(
        '--output',
        default='log_keyword_statistics',
        help='输出文件名前缀，默认 log_keyword_statistics'
    )
    
    parser.add_argument(
        '--max-keywords',
        type=int,
        default=50,
        help='每个日志级别最多查询的关键词数量，默认 50'
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        default=500,
        help='最多扫描的 Java 文件数量，默认 500'
    )
    
    parser.add_argument(
        '--auto-save',
        action='store_true',
        help='自动保存报告文件，不询问用户（默认会询问）'
    )
    
    args = parser.parse_args()
    
    try:
        # 获取项目路径
        project_path = Path(args.project) if args.project else Path.cwd()
        
        # 获取 appKey
        appkey = args.appkey
        if not appkey:
            print("📍 未指定 appKey，尝试自动检测...\n", file=sys.stderr)
            appkey = detect_appkey_from_project(project_path)
            
            if not appkey:
                print("❌ 无法自动检测 appKey，请通过 --appkey 参数指定\n", file=sys.stderr)
                sys.exit(1)
            
            print(f"🔍 自动检测到 appKey: {appkey}\n", file=sys.stderr)
        
        # 获取关键词
        if args.keywords:
            # 手动模式
            print(f"📝 使用手动指定的 {len(args.keywords)} 个关键词", file=sys.stderr)
            keywords_by_level = {}
            
            if args.levels:
                # 指定了级别
                for level in args.levels:
                    keywords_by_level[level] = set(args.keywords)
            else:
                # 未指定级别，使用所有级别
                for level in ['ERROR', 'WARN', 'INFO', 'DEBUG']:
                    keywords_by_level[level] = set(args.keywords)
        else:
            # 自动模式：扫描项目
            keywords_by_level = extract_log_keywords_from_java(
                project_path,
                max_keywords_per_level=args.max_keywords,
                max_files=args.max_files
            )
            
            if not any(keywords_by_level.values()):
                print("❌ 未找到任何日志关键词", file=sys.stderr)
                sys.exit(1)
        
        # 创建统计对象
        stats = KibanaKeywordStats(
            appkey=appkey,
            env=args.env,
            hours=args.hours
        )
        
        # 批量查询
        results = stats.batch_query_keywords(keywords_by_level)
        
        # 计算实际的关键词数量（去重）
        unique_keywords = set(r['keyword'] for r in results)
        keyword_count = len(unique_keywords)
        
        # 决定是否生成文件
        should_save_file = False
        output_file = f"{args.output}.md"
        
        if keyword_count <= 3:
            # 关键词数量少，默认只输出到控制台
            print(f"\n💡 关键词数量较少（{keyword_count} 个），直接输出到控制台\n", file=sys.stderr)
        else:
            # 关键词数量多，询问是否生成文件
            if args.auto_save:
                # 自动保存模式
                should_save_file = True
            else:
                # 询问用户
                print(f"\n📄 统计完成！共 {keyword_count} 个关键词", file=sys.stderr)
                print(f"   是否保存为报告文件 {output_file}? (y/n): ", end='', file=sys.stderr)
                response = input().strip().lower()
                should_save_file = response in ['y', 'yes', '是']
        
        # 生成报告
        stats.generate_report(results, output_file=output_file, save_to_file=should_save_file)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
