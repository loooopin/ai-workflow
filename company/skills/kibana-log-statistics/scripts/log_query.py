#!/usr/bin/env python3
"""
Kibana 日志查询工具
查询指定服务的具体日志内容，支持查看日志消息、异常堆栈等详细信息
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
from typing import Dict, List, Optional


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
                            print(f"   (从 {path.relative_to(cwd)} 读取)\n", file=sys.stderr)
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
                            print(f"   (从 {path.relative_to(cwd)} 读取)\n", file=sys.stderr)
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
                        print(f"   (从 {path} 读取)\n", file=sys.stderr)
                        return appkey
            except Exception:
                pass
    
    return None


class KibanaLogQuery:
    """Kibana 日志查询类"""
    
    # API 地址配置
    KIBANA_URLS = {
        'offline': 'https://alpha-kibana.wemomo.com/alpha-public/api/console/proxy',
        'online': 'https://aws-kibana-mdp-logs.wemomo.com/api/console/proxy'
    }
    
    # Kibana 页面地址
    KIBANA_WEB_URLS = {
        'offline': 'https://alpha-kibana.wemomo.com/alpha-public/app/discover',
        'online': 'https://aws-kibana-mdp-logs.wemomo.com/app/discover'
    }
    
    # 服务专用索引模式配置（用于生成 Kibana 页面链接）
    # 说明：
    # - 线上环境：user/composite/discover 三个核心服务各有独立索引，其他服务共享通用索引
    # - 线下环境：所有服务共享统一索引
    SERVICE_INDEX_PATTERN = {
        # user-moa 服务
        'momo.bpm.biz.overseas-matchmaker.ultron-user': {
            'online': 'c107cb00-6f8d-11ef-aa03-d3bc0b7f0e23',  # 线上独立索引
            'offline': '0310dce0-d400-11ef-af13-7bb4d61b8a53',  # 线下统一索引
            'note': 'ultron-user 服务索引模式'
        },
        # composite 服务
        'momo.bpm.biz.overseas-matchmaker.ultron-composite': {
            'online': '5ded4280-6f7d-11ef-afb0-fd6a31e42ab8',  # 线上独立索引
            'offline': '0310dce0-d400-11ef-af13-7bb4d61b8a53',  # 线下统一索引
            'note': 'ultron-composite 服务索引模式'
        },
        # discover 服务
        'momo.bpm.biz.overseas-matchmaker.ultron-discover': {
            'online': '1945ec30-6f7e-11ef-afb0-fd6a31e42ab8',  # 线上独立索引
            'offline': '0310dce0-d400-11ef-af13-7bb4d61b8a53',  # 线下统一索引
            'note': 'ultron-discover 服务索引模式'
        }
    }
    
    # 其他服务的通用索引（线上环境）
    # 对于未在 SERVICE_INDEX_PATTERN 中配置的服务，使用此通用索引
    DEFAULT_INDEX_PATTERN = {
        'online': '850705e0-7243-11ef-aa03-d3bc0b7f0e23',  # 线上其他服务通用索引
        'offline': '0310dce0-d400-11ef-af13-7bb4d61b8a53'  # 线下统一索引
    }
    
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
        
    def build_query(self, log_level: str = 'ERROR', size: int = 10, keyword: Optional[str] = None) -> str:
        """
        构建 Elasticsearch 查询 JSON
        
        Args:
            log_level: 日志级别
            size: 返回的日志条数
            keyword: 可选的关键词过滤
        
        Returns:
            查询 JSON 字符串
        """
        must_conditions = [
            {
                "match_phrase": {
                    "appKey": self.appkey
                }
            },
            {
                "match": {
                    "logLevel": log_level
                }
            }
        ]
        
        # 如果指定了关键词，添加关键词过滤
        if keyword:
            must_conditions.append({
                "match_phrase": {
                    "line": keyword
                }
            })
        
        query = {
            "size": size,
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ],
            "query": {
                "bool": {
                    "must": must_conditions,
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": f"now-{self.hours}h",
                                    "lte": "now"
                                }
                            }
                        }
                    ]
                }
            },
            "_source": ["@timestamp", "line", "logLevel", "host", "appKey"]
        }
        
        return json.dumps(query)
    
    def generate_kibana_link(self, log_level: Optional[str] = None, keyword: Optional[str] = None) -> str:
        """
        生成 Kibana 页面链接（参考 Kotlin 实现）
        
        Args:
            log_level: 可选的日志级别过滤
            keyword: 可选的关键词过滤
            
        Returns:
            Kibana 页面链接
        """
        # 获取索引模式 ID
        # 1. 优先使用服务专用索引
        index_config = self.SERVICE_INDEX_PATTERN.get(self.appkey)
        index_id = None
        if index_config:
            index_id = index_config.get(self.env)
        
        # 2. 如果没有专用索引，使用默认索引（通用索引）
        if not index_id:
            index_id = self.DEFAULT_INDEX_PATTERN.get(self.env)
        
        # 3. 如果还是没有，返回提示信息
        if not index_id:
            env_name = '线上' if self.env == 'online' else '线下'
            return f"⚠️ 服务 {self.appkey} 在 {env_name} 环境没有配置索引模式 ID，无法生成 Kibana 链接"
        
        # 构建查询条件（Kuery 语法）
        query_parts = []
        if log_level and log_level != "ALL":
            query_parts.append(f"logLevel:{log_level}")
        if keyword:
            # 使用双引号进行精确短语搜索
            query_parts.append(f'"{keyword}"')
        
        # 用 "and" 连接（Kuery 语法）
        full_query = " and ".join(query_parts) if query_parts else "*"
        
        # 对查询条件进行 Kibana/rison 兼容的编码
        encoded_query = self._encode_for_kibana(full_query)
        
        # 判断是否为 ultron-user 服务（线上环境）
        is_ultron_user_online = (
            self.env == 'online' and 
            self.appkey == 'momo.bpm.biz.overseas-matchmaker.ultron-user'
        )
        
        # 根据环境和服务选择模板
        if self.env == 'offline':
            # 线下环境（所有服务）
            template = (
                "https://alpha-kibana.wemomo.com/alpha-public/app/discover#/"
                "?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))"
                "&_a=(columns:!(),filters:!(('$state':(store:appState),"
                "meta:(alias:!n,disabled:!f,index:'{index}',"
                "key:appKey,negate:!f,params:(query:{appkey}),type:phrase),"
                "query:(match_phrase:(appKey:{appkey})))),"
                "index:'{index}',interval:auto,"
                "query:(language:kuery,query:'{query}'),sort:!(!('@timestamp',desc)))"
            )
            url = template.format(index=index_id, appkey=self.appkey, query=encoded_query)
        elif is_ultron_user_online:
            # 线上环境 - ultron-user 服务（无 appKey 过滤器，使用专用索引）
            template = (
                "https://aws-kibana-mdp-logs.wemomo.com/app/discover#/"
                "?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))"
                "&_a=(columns:!(),filters:!(),"
                "index:{index},interval:auto,"
                "query:(language:kuery,query:'{query}'),sort:!(!('@timestamp',desc)))"
            )
            url = template.format(index=index_id, query=encoded_query)
        else:
            # 线上环境 - 其他服务
            template = (
                "https://aws-kibana-mdp-logs.wemomo.com/app/discover#/"
                "?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))"
                "&_a=(columns:!(),filters:!(('$state':(store:appState),"
                "meta:(alias:!n,disabled:!f,index:'{index}',"
                "key:appKey,negate:!f,params:(query:{appkey}),type:phrase),"
                "query:(match_phrase:(appKey:{appkey})))),"
                "index:'{index}',interval:auto,"
                "query:(language:kuery,query:'{query}'),sort:!(!('@timestamp',desc)))"
            )
            url = template.format(index=index_id, appkey=self.appkey, query=encoded_query)
        
        return url
    
    def _encode_for_kibana(self, query: str) -> str:
        """
        对查询条件进行 Kibana/rison 兼容的编码
        参考 Kotlin 实现：只编码必要的字符，保留冒号、括号等
        
        Args:
            query: 原始查询字符串
            
        Returns:
            编码后的字符串
        """
        # 1. 清理和标准化查询字符串
        cleaned = query.strip()
        cleaned = cleaned.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        cleaned = cleaned.replace('\t', ' ')
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)  # 多个空格合并为一个
        
        # 2. 逐字符编码（只编码必要的字符）
        result = []
        for char in cleaned:
            if char == ' ':
                result.append('%20')
            elif char == '"':
                result.append('%22')
            elif char == "'":
                result.append('%27')
            elif char == '%':
                result.append('%25')
            elif char == '#':
                result.append('%23')
            elif char == '&':
                result.append('%26')
            elif char == '=':
                result.append('%3D')
            elif char == '+':
                result.append('%2B')
            elif char == '<':
                result.append('%3C')
            elif char == '>':
                result.append('%3E')
            elif char == '[':
                result.append('%5B')
            elif char == ']':
                result.append('%5D')
            elif char == '{':
                result.append('%7B')
            elif char == '}':
                result.append('%7D')
            elif char == '|':
                result.append('%7C')
            elif char == '\\':
                result.append('%5C')
            else:
                # 保留所有其他字符（字母、数字、冒号、括号、星号、连字符等）
                result.append(char)
        
        return ''.join(result)
    
    def query_logs(self, log_level: str = 'ERROR', size: int = 10, keyword: Optional[str] = None) -> List[Dict]:
        """
        查询日志
        
        Args:
            log_level: 日志级别
            size: 返回的日志条数
            keyword: 可选的关键词过滤
        
        Returns:
            日志列表
        """
        query_body = self.build_query(log_level, size, keyword)
        
        # 通过 Kibana API Proxy 查询 ES（查询所有索引，通过 appKey 过滤）
        # 注意：某些服务（如 user/composite/discover）在 Kibana 页面中有独立的索引模式 ID
        # 但 API 查询通过 appKey 过滤即可，无需指定索引 ID
        url = f'{self.base_url}?path=_search&method=POST'
        
        req = request.Request(
            url,
            data=query_body.encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'kbn-xsrf': 'kibana'
            }
        )
        
        try:
            with request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                hits = result.get('hits', {}).get('hits', [])
                return [hit.get('_source', {}) for hit in hits]
                
        except error.HTTPError as e:
            print(f'❌ HTTP 错误: {e.code} {e.reason}', file=sys.stderr)
            print(e.read().decode('utf-8'), file=sys.stderr)
            return []
        except Exception as e:
            print(f'❌ 查询出错: {e}', file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return []
    
    def parse_log_line(self, line: str) -> Dict[str, str]:
        """
        解析日志行，提取各个组成部分
        
        日志格式示例：
        2026-01-29 17:36:14,715 ERROR [trace-id] [Class.method] [UID9522] (Location:Line) thread-name - message
        
        Args:
            line: 完整的日志行
        
        Returns:
            解析后的字典，包含 timestamp, level, trace_id, class_method, uid, location, thread, message, stack_trace
        """
        result = {
            'timestamp': '',
            'level': '',
            'trace_id': '',
            'class_method': '',
            'uid': '',
            'location': '',
            'thread': '',
            'message': '',
            'stack_trace': ''
        }
        
        if not line:
            return result
        
        # 分割日志内容和堆栈
        parts = line.split('\n', 1)
        log_header = parts[0]
        stack_trace = parts[1] if len(parts) > 1 else ''
        
        # 使用正则表达式解析日志头
        import re
        
        # 解析模式：时间戳 级别 [trace-id] [Class.method] [UID] (Location) thread - message
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+(\w+)\s+\[(.*?)\]\s+\[(.*?)\]\s+\[(.*?)\]\s+\((.*?)\)\s+(.*?)\s+-\s+(.*)'
        match = re.match(pattern, log_header)
        
        if match:
            result['timestamp'] = match.group(1)
            result['level'] = match.group(2)
            result['trace_id'] = match.group(3)
            result['class_method'] = match.group(4)
            result['uid'] = match.group(5)
            result['location'] = match.group(6)
            result['thread'] = match.group(7)
            result['message'] = match.group(8)
        else:
            # 如果正则匹配失败，尝试简单分割
            result['message'] = log_header
        
        result['stack_trace'] = stack_trace
        
        return result
    
    def format_log_entry(self, log: Dict, index: int) -> str:
        """
        格式化单条日志
        
        Args:
            log: 日志数据
            index: 日志序号
        
        Returns:
            格式化后的字符串
        """
        timestamp = log.get('@timestamp', '')
        line = log.get('line', '')
        level = log.get('logLevel', '')
        host = log.get('host', '')
        
        # 解析日志行
        parsed = self.parse_log_line(line)
        
        # 提取异常类名（如果有）
        exception_class = ''
        if parsed['stack_trace']:
            lines = parsed['stack_trace'].split('\n')
            if lines:
                exception_class = lines[0].strip()
        
        # 提取代码位置（文件名和行号）
        code_location = ''
        if parsed['stack_trace']:
            # 从堆栈的第一行找到实际的代码位置
            import re
            match = re.search(r'at ([\w.$]+\.[a-zA-Z]+)\(([^:]+):(\d+)\)', parsed['stack_trace'])
            if match:
                class_name = match.group(1)
                file_name = match.group(2)
                line_number = match.group(3)
                code_location = f'{class_name} ({file_name}:{line_number})'
        
        output = []
        output.append(f'\n📋 日志 #{index}')
        output.append(f'━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        output.append(f'⏰ 时间: {parsed["timestamp"] or timestamp}')
        output.append(f'🔖 级别: {level}')
        output.append(f'🧵 线程: {parsed["thread"]}')
        output.append(f'📦 Class: {parsed["class_method"]}')
        output.append(f'🖥️  主机: {host}')
        
        if parsed['uid']:
            output.append(f'👤 UID: {parsed["uid"]}')
        
        if parsed['trace_id']:
            output.append(f'🔗 TraceID: {parsed["trace_id"]}')
        
        if exception_class:
            output.append(f'⚠️  异常: {exception_class}')
        
        if code_location:
            output.append(f'📍 位置: {code_location}')
        
        output.append(f'\n💬 日志消息:')
        output.append(f'{parsed["message"]}')
        
        if parsed['stack_trace']:
            output.append(f'\n📚 异常堆栈:')
            # 只显示前20行堆栈，避免过长
            stack_lines = parsed['stack_trace'].split('\n')
            if len(stack_lines) > 20:
                output.append('\n'.join(stack_lines[:20]))
                output.append(f'\n... (还有 {len(stack_lines) - 20} 行，已省略)')
            else:
                output.append(parsed['stack_trace'])
        
        output.append('\n' + '='*100)
        
        return '\n'.join(output)
    
    def display_logs(self, logs: List[Dict], log_level: str, keyword: Optional[str] = None):
        """
        显示日志列表
        
        Args:
            logs: 日志列表
            log_level: 日志级别
            keyword: 搜索关键词（如果有）
        """
        env_name = '线上环境' if self.env == 'online' else '线下环境'
        
        print(f'\n🔍 查询结果')
        print(f'   服务: {self.appkey}')
        print(f'   环境: {env_name}')
        print(f'   级别: {log_level}')
        print(f'   时间范围: 最近 {self.hours} 小时')
        if keyword:
            print(f'   关键词: {keyword}')
        print(f'   找到: {len(logs)} 条日志')
        print('='*100)
        
        if not logs:
            print('\n❌ 未找到符合条件的日志')
            return
        
        for i, log in enumerate(logs, 1):
            print(self.format_log_entry(log, i))


def main():
    parser = argparse.ArgumentParser(
        description='Kibana 日志查询工具 - 查询具体的日志内容',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 查询最近10条ERROR日志
  python3 log_query.py --size 10 --level ERROR
  
  # 查询最近20条WARN日志（最近6小时）
  python3 log_query.py --size 20 --level WARN --hours 6
  
  # 查询包含特定关键词的ERROR日志
  python3 log_query.py --size 10 --keyword "timeout" --level ERROR
  
  # 查询线上环境的错误日志
  python3 log_query.py --size 10 --env online --level ERROR

说明:
  - appKey 会自动从项目的 app.yaml 文件中检测
  - 默认查询线下环境（alpha）最近24小时的ERROR日志
  - 日志按时间倒序排列（最新的在前）
        """
    )
    
    parser.add_argument(
        '--appkey',
        help='服务的 appKey（可选，默认自动检测）'
    )
    
    parser.add_argument(
        '--env',
        choices=['offline', 'online'],
        default='offline',
        help='环境：offline=线下, online=线上（默认: offline）'
    )
    
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='时间范围（小时，默认: 24）'
    )
    
    parser.add_argument(
        '--level',
        choices=['ERROR', 'WARN', 'INFO', 'DEBUG'],
        default='ERROR',
        help='日志级别（默认: ERROR）'
    )
    
    parser.add_argument(
        '--size',
        type=int,
        default=10,
        help='查询的日志条数（默认: 10）'
    )
    
    parser.add_argument(
        '--keyword',
        help='日志消息中的关键词（可选）'
    )
    
    parser.add_argument(
        '--link',
        action='store_true',
        help='生成 Kibana 页面链接（而不是查询日志）'
    )
    
    args = parser.parse_args()
    
    # 获取 appKey
    appkey = args.appkey
    if not appkey:
        print('📍 未指定 appKey，尝试自动检测...', file=sys.stderr)
        appkey = detect_appkey_from_project()
        
        if not appkey:
            print('❌ 无法自动检测 appKey，请使用 --appkey 参数指定', file=sys.stderr)
            sys.exit(1)
    
    # 创建查询器
    querier = KibanaLogQuery(appkey, args.env, args.hours)
    
    # 根据参数决定是生成链接还是查询日志
    if args.link:
        # 生成 Kibana 页面链接
        print(f'\n🔗 生成 Kibana 页面链接...', file=sys.stderr)
        link = querier.generate_kibana_link(args.level, args.keyword)
        
        env_name = '线上环境' if args.env == 'online' else '线下环境'
        print(f'\n📊 Kibana 日志查看链接', file=sys.stderr)
        print(f'   服务: {appkey}', file=sys.stderr)
        print(f'   环境: {env_name}', file=sys.stderr)
        print(f'   级别: {args.level}', file=sys.stderr)
        print(f'   时间范围: 最近 {args.hours} 小时', file=sys.stderr)
        if args.keyword:
            print(f'   关键词: {args.keyword}', file=sys.stderr)
        print(f'\n{link}')
    else:
        # 查询日志
        print(f'\n🔄 正在查询 {args.level} 级别日志...', file=sys.stderr)
        logs = querier.query_logs(args.level, args.size, args.keyword)
        
        # 显示结果
        querier.display_logs(logs, args.level, args.keyword)


if __name__ == '__main__':
    main()
