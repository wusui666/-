import requests
import time
import random
import os
import datetime


'''
使用说明见游侠签到
'''

# 定义常量，提高代码的可维护性
BASE_URL_API3 = "https://api3.ali213.net"
BASE_URL_NEWAPI = "https://newapi.ali213.net"
HEADER_HOST = "api3.ali213.net"
USER_AGENT = "okhttp/3.10.0"

# 通用的请求函数，减少代码重复
def make_request(url, headers, params):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.RequestException as e:
        print(f"请求出错: {e}")
        return None
    except ValueError as e:
        print(f"解析JSON出错: {e}")
        return None

# 发送获得阅读金币请求
def read(ID, token, headers):
    marklog_params = {
        "token": token,
        "channelID": "1",
        "entityID": ID,
        "id": ""
    }
    # 发送 marklog 请求
    make_request(f"{BASE_URL_API3}/feedearn/marklog", headers, marklog_params)
    # 随机休眠
    time.sleep(random.randint(9, 12))

    readresource_params = {
        "token": token,
        "channelID": "1",
        "entityID": ID
    }
    # 发送 readresource 请求
    res = make_request(f"{BASE_URL_API3}/feedearn/readresource", headers, readresource_params)
    if res and 'status' in res and res['status'] == 1:
        msg = res['msg']
        print(f'[阅读成功]：获币{msg}')
    elif res:
        msg = res['msg']
        print(f'{msg}😒')

# 获取文章id
def getid(pageno, token, headers):
    recommend_params = {
        "navId": "2",
        "pageNo": pageno,
        "pageNum": "10",
        "lastId": "",
        "keyword": "",
        "confirmNo": "0"
    }
    # 获取推荐列表
    res = make_request(f"{BASE_URL_NEWAPI}/app/v1/recommendList", headers, recommend_params)
    if res:
        try:
            sub_list = res["data"]["list"][0]["subList"]
            for item in sub_list[:3]:
                ID = item['resourceId']
                read(ID, token, headers)

            main_list = res["data"]["list"]
            for item in main_list[:10]:
                ID = item['resourceId']
                read(ID, token, headers)
        except (KeyError, IndexError) as e:
            print(f"解析推荐列表出错: {e}")

if __name__ == "__main__":
    CKS = os.getenv('YXRCCK')
    if not CKS:
        print("未找到环境变量 YXRCCK，请设置该变量。")
    else:
        CKL = CKS.split("@")
        print(f"【游侠阅读】共检测到{len(CKL)}个账号")
        print(f"==========================================")
        print(f"===============鼠鼠自用版🥱===============")
        for index, CK in enumerate(CKL, start=1):
            print(f"========【账号{index}】开始运行脚本========")
            token = CK.split("#")[0]
            headers = {
                "Host": HEADER_HOST,
                "accept-encoding": "gzip",
                "user-agent": USER_AGENT
            }
            # 阅读文章
            for i in range(20):
                pageno = i + random.randint(5, 33)
                getid(pageno, token, headers)
                print(f'第{i + 1}页读')
            if index < len(CKL):
                print("延迟一小会,准备跑下一个账号🥳")