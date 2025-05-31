from 智谱Flash import call_glm_4_flash
import requests
import datetime
import json
import time
import argparse
from dateutil import parser
import os

# ================= 全局配置 =================
MAX_PAGE = 30                  # 最大采集页数，不必太大，随便填
COMMENT_INTERVAL = 33          # 发帖间隔(秒)，必须大于30秒
DATE_FORMAT = "%Y%m%d"         # 日期匹配格式
AI_MAX_RETRY = 3               # AI接口重试次数
DEBUG_DATE = ""                # 调试日期(示例："20250302"即为指定2025年3月3号，建议留空使用系统时间)
url_you = "223.240.224.059"    #谁便挑几个数字改改就行
type_ph = "遥遥领先16 Pro Max"     #评论下面显示的手机型号，
DEBUG_DATE_FORMATS = [         # 支持的调试日期格式，后面就不要动了
    "%Y%m%d", 
    "%Y-%m-%d", 
    "%Y/%m/%d"
]

# API请求头配置
headers = {
    'Connection': 'Close',
    'Host': 'newapi.ali213.net',
    'User-Agent': 'okhttp/3.10.0',
}

# ================= 命令行参数解析 =================
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='游侠网自动评论脚本')
    parser.add_argument('--date', 
                        type=str,
                        help='调试日期（格式：YYYYMMDD/YYYY-MM-DD/YYYY/MM/DD）')
    return parser.parse_args()

# ================= 日期处理增强 =================
def get_target_date():
    """获取目标日期（优先使用调试日期）"""
    if DEBUG_DATE:
        for fmt in DEBUG_DATE_FORMATS:
            try:
                return datetime.datetime.strptime(DEBUG_DATE, fmt)
            except ValueError:
                continue
        raise ValueError(f"无效的调试日期格式：{DEBUG_DATE}，支持的格式：{DEBUG_DATE_FORMATS}")
    return datetime.datetime.now()

# ================= 日志系统 =================
# ================= 日志系统 =================
def log_message(message, level="INFO"):
    """多级日志记录系统"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    # 控制台显示所有级别日志
    print(log_entry)
# ================= AI评论生成 =================
def ai_generate_reply(title):
    """带重试机制的AI评论生成"""
    prompt = f"你需要以游侠网用户的身份根据帖子标题生成回复，要求字数大于8小于15，并且禁用表情，只能输出汉字，标题为：{title}"
    
    for _ in range(AI_MAX_RETRY):
        try:
            reply = call_glm_4_flash(prompt)
            if 8 <= len(reply) <= 35:
                return reply
            log_message(f"AI回复长度异常：{reply}", "WARNING")
        except Exception as e:
            log_message(f"AI接口调用失败：{str(e)}", "ERROR")
            time.sleep(2)
    
    # 降级方案
    replies = [
        "这个标题很有意思，期待后续！",
        "看起来是个大新闻！",
        "希望内容不要让人失望！",
        "这个组合太让人期待了！",
        "终于等到了！"
    ]
    return replies[hash(title) % len(replies)]

# ================= 智能采集系统 =================
class DataCollector:
    def __init__(self, target_date):
        self.target_date = target_date
        self.target_date_str = target_date.strftime(DATE_FORMAT)
        self.url_date_str = target_date.strftime("%Y/%m/%d").replace('/', '')
    
    def _check_pic_url(self, pic_url):
        """检查图片URL是否匹配目标日期"""
        clean_url = pic_url.replace('/', '')
        return self.target_date_str in clean_url or self.url_date_str in clean_url
    
    def parse_items(self, response_data):
        """解析API响应数据"""
        result = []
        for idx, item in enumerate(response_data.get('data', {}).get('list', [])):
            # 处理主条目
            if item.get('pic'):
                for pic_url in item['pic']:
                    if self._check_pic_url(pic_url):
                        result.append({
                            'id': item['resourceId'],
                            'title': item['label'],
                            'time': item.get('createTime', 0)
                        })
                        log_message(f"发现主条目[{idx}]：{item['label']}")
                        break
            
            # 处理子条目
            if item.get('subList'):
                for sub_idx, sub_item in enumerate(item['subList']):
                    if sub_item.get('pic'):
                        for pic_url in sub_item['pic']:
                            if self._check_pic_url(pic_url):
                                result.append({
                                    'id': sub_item['resourceId'],
                                    'title': sub_item['label'],
                                    'time': sub_item.get('createTime', 0)
                                })
                                log_message(f"发现子条目[{idx}-{sub_idx}]：{sub_item['label']}")
                                break
        return result

# ================= 分页采集引擎 =================
def fetch_paginated_data(base_params, target_date):
    """智能分页采集系统"""
    collector = DataCollector(target_date)
    all_items = []
    current_page = 1
    
    log_message(f"▶▶ 开始采集任务，目标日期：{target_date.strftime('%Y-%m-%d')}")
    
    while current_page <= MAX_PAGE:
        try:
            # 配置请求参数
            params = base_params.copy()
            params['navId'] = str(current_page)
            
            # 发送请求
            log_message(f"正在采集第{current_page}页...")
            start_time = time.time()
            response = requests.get(
                'https://newapi.ali213.net/app/v1/recommendList',
                params=params,
                headers=headers,
                timeout=15
            ).json()
            
            # 解析数据
            page_items = collector.parse_items(response)
            log_message(f"第{current_page}页获取到{len(page_items)}条数据（耗时{time.time()-start_time:.2f}s）")
            
            # 检查终止条件
            if not page_items:
                log_message(f"第{current_page}页无有效数据，停止采集", "WARNING")
                break
                
            # 日期边界检查
            last_item = max(page_items, key=lambda x:x['time'], default=None)
            if last_item:
                try:
                    item_time = datetime.datetime.fromtimestamp(int(last_item['time'])) \
                        if len(str(last_item['time'])) == 10 else parser.parse(str(last_item['time']))
                    if item_time.date() < target_date.date():
                        log_message(f"最后条目日期{item_time.date()}早于目标日期，停止采集", "WARNING")
                        break
                except Exception as e:
                    log_message(f"时间解析失败：{last_item['time']}，错误：{str(e)}", "ERROR")
            
            all_items.extend(page_items)
            current_page += 1
            time.sleep(1)  # 页间间隔
            
        except Exception as e:
            log_message(f"第{current_page}页采集失败: {str(e)}", "ERROR")
            break
    
    log_message(f"◀◀ 采集完成，共获取{len(all_items)}条有效数据")
    return all_items

# ================= 发帖系统 =================
class PostSystem:
    def __init__(self):
        self.headers = {
            "authorizationapp": os.getenv('YXRCCK').split('#')[0],
            "Content-Type": "application/json; charset=utf-8",
            "Host": "comment2.ali213.net",
            "User-Agent": "okhttp/3.10.0",
        }
    
    def send_post(self, item):
        """执行发帖操作"""
        payload = {
            "appId": 1,
            "conId": str(item['id']),
            "title": item['title'],
            "content": ai_generate_reply(item['title']),
            "url": url_you,
            "platform": "3",
            "phoneos": type_ph
        }
        
        try:
            with requests.Session() as s:
                s.headers.update(self.headers)
                response = s.post(
                    "https://comment2.ali213.net/api/SubmitV1",
                    data=json.dumps(payload, ensure_ascii=False).encode('utf-8')
                )
                resp_data = response.json()
                msg = resp_data.get('msg', '无返回信息')
                log_message(f"ID:{item['id']} 发帖成功 - {msg}")
                return True
        except Exception as e:
            log_message(f"ID:{item['id']} 发帖失败 - {str(e)}", "ERROR")
            return False

# ================= 主控制系统 =================
def main():
    try:
        # 获取目标日期
        target_date = get_target_date()
        log_message(f"运行模式：{'调试' if DEBUG_DATE else '正常'}，目标日期：{target_date.strftime('%Y-%m-%d')}")
        
        # 基础参数配置
        base_params = {
            'navId': '1',
            'pageNo': '1',
            'pageNum': '10',
            'lastId': '',
            'keyword': '',
            'confirmNo': '0',
        }
        
        # 执行采集
        all_items = fetch_paginated_data(base_params, target_date)
        
        # 执行发帖
        if all_items:
            post_system = PostSystem()
            log_message(f"开始发送{len(all_items)}条评论，间隔{COMMENT_INTERVAL}秒")
            
            for idx, item in enumerate(all_items, 1):
                start_time = time.time()
                success = post_system.send_post(item)
                log_message(f"进度：{idx}/{len(all_items)} ({idx/len(all_items):.0%})")
                
                if idx < len(all_items):
                    sleep_time = COMMENT_INTERVAL - (time.time() - start_time)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
        else:
            log_message("没有需要发送的条目", "WARNING")
            
    except ValueError as e:
        log_message(f"参数错误：{str(e)}", "ERROR")
    except Exception as e:
        log_message(f"系统异常：{str(e)}", "ERROR")

if __name__ == "__main__":
    main()