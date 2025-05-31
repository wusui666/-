import requests
import logging
import time
from datetime import datetime, timezone, timedelta
import os

'''
不需要配置环境变量，定时三小时一次
需要后于yx签到本使用
'''





# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(message)s')

# 从环境变量中获取 YXRCCK 的值
yxrcck = os.getenv('YXRCCK')
if yxrcck:
    # 分割 YXRCCK 的值，取出 token
    auth_token = yxrcck.split('#')[0]
else:
    logging.error("未找到环境变量 YXRCCK，请设置该环境变量。")
    auth_token = None

yxwckArr = []
msg = ''


def get_utc8_time():
    """
    获取当前北京时间（UTC+8）
    :return: 北京时间的字符串表示
    """
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_time = utc_now.astimezone(timezone(timedelta(hours=8)))
    return beijing_time.strftime('%Y-%m-%d %H:%M:%S')


def get_cookie_from_request():
    """
    模拟 curl 请求并获取 Set-Cookie 字段的值
    :return: 提取的 api3AliSSO 部分的 cookie 值
    """
    if not auth_token:
        return None
    h1 = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; iPlay50mini Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.61 Safari/537.36 ali213app",
    }
    p1 = {
        'token': auth_token,
        'redirectUrl': 'https://api3.ali213.net/feedearn/luckybox',
    }
    try:
        response = requests.get('https://api3.ali213.net/feedearn/tokenexchanger', params=p1, headers=h1)
        # logging.info(f"请求状态码: {response.status_code}")
        # logging.info(f"响应头: {response.headers}")
        set_cookie = response.headers.get('Set-Cookie')
        if set_cookie:
            # 假设需要提取 api3AliSSO 部分的 cookie
            for part in set_cookie.split(';'):
                if 'api3AliSSO' in part:
                    return part.split('=')[1].strip()
        else:
            logging.info("响应头中未找到 Set-Cookie 字段")
    except Exception as e:
        logging.error(f"获取 cookie 时出错: {e}")
    return None


async def envs():
    """
    检查并处理变量 yxwck
    :return: 如果变量存在并处理成功返回 True，否则返回 False
    """
    global yxwckArr
    # 从请求获取 cookie
    api3AliSSO = get_cookie_from_request()
    if api3AliSSO:
        yxwckArr = [api3AliSSO]
    else:
        logging.info(f"\n 【游侠网宝箱】：未获取到有效的 cookie，请检查请求")
        return False
    return True


async def do_sign(timeout=3):
    """
    领宝箱
    :param timeout: 请求超时时间，默认为 3 秒
    :return: None
    """
    global msg
    for index, data in enumerate(yxwckArr):
        num = index + 1
        logging.info(f"\n========= 开始【第 {num} 个账号】=========\n")
        msg += f"\n第{num}个账号运行结果："
        logging.info('开始领金币')

        url = 'https://api3.ali213.net/feedearn/luckybox?action=get'
        headers = {
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ali213app",
            "Cookie": f"api3AliSSO={data}"
        }
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            result = response.json()
            if result.get('logined'):
                logging.info('登录成功，CK 有效')
                if result['data']['msg'] == '领取成功':
                    logging.info(f"领取成功，获得{result['data']['coins']}金币")
                    msg += f"领取成功，获得{result['data']['coins']}金币"
                else:
                    logging.info('领取失败，这个时间段已经领取过了')
                    msg += '领取失败，这个时间段已经领取过了'
            else:
                logging.info('登录失败:CK 无效，请重新获取')
        except Exception as e:
            logging.error(f"领宝箱请求出错: {e}")


async def main():
    """
    主函数，脚本的入口
    :return: None
    """
    if not auth_token:
        return
    if not await envs():
        return
    logging.info(f"\n\n=============================================    \n脚本执行 - 北京时间(UTC+8)：{get_utc8_time()} \n=============================================\n")
    logging.info(f"\n=================== 共找到 {len(yxwckArr)} 个账号 ===================")
    await do_sign()


if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except Exception as e:
        logging.error(f"脚本执行出错: {e}")
    finally:
        logging.info("脚本执行完毕")