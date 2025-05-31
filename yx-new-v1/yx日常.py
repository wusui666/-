import requests
import time
import random
import os
import datetime

'''
25-3-1
使用说明见游侠签到
'''


def read(ID, token):
    try:
        # 发送获得阅读金币请求
        params = {
            "token": token,
            "channelID": "1",
            "entityID": ID,
            "id": ""
        }
        res = requests.get("https://api3.ali213.net/feedearn/marklog", headers=headers, params=params).json()
        time.sleep(random.randint(9, 12))
        params1 = {
            "token": token,
            "channelID": "1",
            "entityID": ID
        }
        res = requests.get("https://api3.ali213.net/feedearn/readresource", headers=headers, params=params1).json()
        if 'status' in res and res['status'] == 1:
            msg = res['msg']
            print(f'[阅读成功]：获币{msg}')
        else:
            msg = res['msg']
            print(f'{msg}😒')
    except Exception as e:
        print(f"阅读文章 {ID} 时出现错误: {e}")


def getid(pageno, token):
    try:
        params = {
            "navId": "2",
            "pageNo": pageno,
            "pageNum": "10",
            "lastId": "",
            "keyword": "",
            "confirmNo": "0"
        }
        res = requests.get("https://newapi.ali213.net/app/v1/recommendList", headers=headers, params=params).json()
        lis = res["data"]["list"][0]["subList"]
        for i in range(3):
            ID = lis[i]['resourceId']
            read(ID, token)
        lis1 = res["data"]["list"]
        for a in range(10):
            ID = lis1[a]['resourceId']
            read(ID, token)
    except Exception as e:
        print(f"获取第 {pageno} 页文章ID时出现错误: {e}")


def readclub(threadid, token):
    try:
        params = {
            "threadid": threadid,
            "commentid": "0",
            "token": token
        }
        response = requests.get("https://club.ali213.net/application/comment/threadlatestajax", headers=headers,
                                params=params)  # 社区帖子
        params = {
            "token": token,
            "threadid": threadid
        }
        response = requests.get("https://club.ali213.net/application/thread/readingreward", headers=headers,
                                params=params).json()  # 发送获取金币请求
        print(response)
    except Exception as e:
        print(f"阅读社区帖子 {threadid} 时出现错误: {e}")


def share(token):
    try:
        params = {
            "navId": "2",
            "pageNo": '1',
            "pageNum": "10",
            "lastId": "",
            "keyword": "",
            "confirmNo": "0"
        }
        res = requests.get("https://newapi.ali213.net/app/v1/recommendList", headers=headers, params=params).json()
        lis1 = res["data"]["list"]
        for a in range(10):
            ID = lis1[a]['resourceId']
            param = {
                "token": token,
                "channelID": "1",
                "entityID": ID
            }
            res = requests.get("https://api3.ali213.net/feedearn/sharearticle", headers=headers, params=param).json()
            print(res)
    except Exception as e:
        print(f"分享文章时出现错误: {e}")


def check(token):
    try:
        params = {
            "token": token
        }
        res = requests.get("https://api3.ali213.net/feedearn/userbaseinfo", headers=headers, params=params).json()
        name = res["username"]
        available = int(res["available"]) / 100
        total = int(res["total"]) / 100
        coin = res["coins"]
        garde = res["grade"]
        exp0 = res["experience"]
        exp1 = res["nextgrade"]["experience"]
        print(f'[昵称]：{name}\n[总CNY]:{total} [可提CNY]：{available}\n[币数]：{coin}\n[等级]：{garde} 进度：[{exp0}/{exp1}]')
        return coin
    except Exception as e:
        print(f"查询用户信息时出现错误: {e}")
        return 0


def change(coin, token):
    try:
        url = "https://api3.ali213.net/feedearn/coinschangemoney"
        params = {
            "token": token,
            "coin": coin
        }
        res = requests.get(url, headers=headers, params=params).json()
        print(res)
    except Exception as e:
        print(f"金币换CNY时出现错误: {e}")


def gxid_of_club(token):
    try:
        club_id = []
        params = {
            "token": token
        }
        res = requests.get("https://club.ali213.net/application/forum/square", headers=headers, params=params).json()
        RQ = datetime.datetime.now().strftime("%Y-%m-%d")
        lis = res['data']['threadList']
        for parm in lis:
            if 'addtime' in parm and parm['addtime'] == RQ:
                club_id.append(parm['id'])
        return club_id
    except Exception as e:
        print(f"获取社区帖子ID时出现错误: {e}")
        return []


def shareauth(token):
    url = f'https://api3.ali213.net/feedearn/sharebycode?token={token}&sharecode=DiTer1-0yXzPK-u5iX50-08SWX1'
    try:
        requests.get(url, headers=headers)
        return url
    except Exception as e:
        print(f"none")
        return None


if __name__ == "__main__":
    CKS = os.getenv('YXRCCK')
    CKL = CKS.split("@")
    print(f"【游侠日常】共检测到{len(CKL)}个账号")
    print(f"==========================================")
    print(f"===============鼠鼠自用版🥱===============")
    t = 1
    for CK in CKL:
        print(CK)
        print(f"========【账号{t}】开始运行脚本========")
        token = CK.split("#")[0]
        ua = CK.split('#')[1]
        headers = {"Host": "api3.ali213.net", "accept-encoding": "gzip", "user-agent": ua}
        share_url = shareauth(token)
        #for i in range(20):  # 阅读文章
            #getid(i + 1, token)
            #print(f'第{i + 1}/{20}次页读')
        club_id = gxid_of_club(token)
        for i in club_id:  # 阅读社区帖子
            readclub(i, token)
        share(token)  # 分享
        coin = check(token)  # 查询用户信息
        change(coin, token)  # 金币换CNY
        check(token)  # 再次查询
        print(f"====【账号{t}】已完成，打搅去喽🥵====")
        t += 1
        if t > len(CKL):
            break
        else:
            print("延迟一小会,准备跑下一个账号🥳")

    if share_url:
        try:
            requests.get(share_url, headers=headers)
        except Exception as e:
            print(f"none")