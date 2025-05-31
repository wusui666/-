import requests
import hashlib
import time
from requests.exceptions import RequestException, ConnectionError
from 青龙面板ck更新 import QL

# 配置信息
address = "http://192.168.1.241:5700/"     #need青龙地址
client_id = "h--hKdDc1111"                      #need client_id
client_secret = "biAl8vXEFscEvC2-Oh7U8Nwi"      #need client_secret
ua= 'okhttp/3.10.0'                             #默认即可
need的账密 = '账号&密码'        #need的账号和密码

'''
账密登录自动更新token

你需要把 青龙面板ck更新.py 和这个脚本放到同一路径下
你需要新建一个名为YXRCCK的变量，内容谁便填
你需要在系统设置里面新建应用，并且允许操作环境变量，将你的client_id和client_secret填到上面
5个本的顺序：签到先于其他
签到本除签到和抽奖外还会更新你的游侠token，一天一次
日常本主要是看你账号的金币数和将金币兑换为cny，一天一次
阅读本就是读帖子的，由于阅读是概率得币，着实恶心，于是把阅读单独拿出来了，定时随意，鼠鼠我是一天六次。
作者的邀请码：DiTer1-0yXzPK-u5iX50-08SWX1   （我的->每日任务——>往下滑，有个分享，点进去填写，感谢支持）
签到会有概率get到steam的兑换码（虽然我换到的几个都是我感觉不好玩的doge）

3-3-2025
更新yx评论.py，调用免费的AI生成评论并且发送评论。以日期界定是否发评论，所以这个脚本里的调试日期参数建议不填，定时可以晚上10点之后吧，别人发帖也要时间
需要用到 智谱Flash.py 这个脚本。要保证它们在同一个目录下
同时你需要去搞一个智谱的api
方法：
    1.打开链接 ：https://www.bigmodel.cn/invite?icode=CzzIFut3cPGv8BgznuPNdVwpqjqOwPB5EXW6OL4DgqY%3D
    2.注册登录
    3.头像的左边有个钥匙的 图标点进去，然后点”添加新的API key“ 名字随意，把key复制下来
    4.打开智谱Flash.py  在第五行填入


此外你最好打开yx评论脚本，修改里面的全局配置，
除去全局配置修改外，建议还修改64行和77-82行的内容，以免大伙的评论都一个样🤣



'''





# 定义环境变量类
class Env:
    def __init__(self, name):
        self.name = name
        self.yxwlogin = None
        self.Notify = 1  # 0为关闭通知，1为打开通知,默认为1
        self.loginBack = 0
        self.token = ''
        self.user_name = ''
        self.allcoin = ''
        self.cash = ''
        self.message_content = ''

    def isNode(self):
        return True  # 这里简单假设在Node环境下，实际可根据情况调整

    def log(self, message):
        print(message)

    def msg(self, message):
        if self.Notify > 0:
            if self.isNode():
                # 这里未实现sendNotify功能，可根据实际情况添加
                pass
            else:
                print(message)
        else:
            self.log(message)

    def done(self):
        pass

# 定义重试函数
def retry_request(url, headers=None, data=None, method='post', max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            if method == 'post':
                response = requests.post(url, headers=headers, data=data)
            else:
                response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except (RequestException, ConnectionError) as e:
            retries += 1
            if retries < max_retries:
                env.log(f"请求失败，正在进行第 {retries} 次重试: {e}")
                time.sleep(2)  # 等待2秒后重试
            else:
                env.log(f"请求失败，已达到最大重试次数: {e}")
    return None

# 定义主函数
async def main():

    global env
    env = Env('游侠网')
    # 获取环境变量 YX_zhangmi 的值
    env.YX_zhangmi = need的账密
    # 添加调试信息，验证是否成功获取到环境变量的值
    if env.YX_zhangmi is None:
        print("未获取到 YX_zhangmin 环境变量的值")
    else:
        print(f"成功获取到 YX_zhangmi 环境变量的值: {env.YX_zhangmi}")

    yxw = env.YX_zhangmi
    yxwArr = []
    if yxw:
        if "@" in yxw:
            yxwArr = yxw.split("@")
        elif "\n" in yxw:
            yxwArr = yxw.split("\n")
        else:
            yxwArr = [yxw]
    else:
        env.log(f"\n 【{env.name}】：未填写变量 yxw")
        return

    env.log(f"\n\n=============================================    \n脚本执行 - 北京时间(UTC+8)：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} \n=============================================\n")
    env.log(f"\n=================== 共找到 {len(yxwArr)} 个账号 ===================")

    for index, item in enumerate(yxwArr, 1):
        env.log(f"\n========= 开始【第 {index} 个账号】=========\n")
        yxw = item.split('&')
        env.message_content += f"\n第{index}个账号运行结果："
        env.log('【开始登录】')
        await login(env, yxw)
        time.sleep(2)
        if env.loginBack != 1:
            env.log('\n【开始查询签到状态】')
            await getSign(env)
            time.sleep(2)
            env.log('\n【开始查询新旧用户签到】')
            await checknew(env)
            time.sleep(2)
        await checkcoin(env)

    await SendMsg(env, env.message_content)

# 登录函数
async def login(env, yxw):
    time10 = int(time.time())
    signature_str = "username-" + yxw[0] + "-time-" + str(time10) + "-passwd-" + yxw[1] + "-from-feedearn-action-loginBGg)K6ng4?&x9sCIuO%C2%{@TJ?fnFJ,bZKy/[/EWnw9UsC$@1"
    signature = hashlib.md5(signature_str.encode()).hexdigest()
    url = "https://i.ali213.net/api.html"
    headers = {
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = f"action=login&username={yxw[0]}&passwd={yxw[1]}&time={time10}&from=feedearn&signature={signature}"
    response = retry_request(url, headers=headers, data=body)
    if response:
        try:
            result = response.json()
            if result["status"] == 1:
                env.token = result["data"]["token"]
                env.user_name = result["data"]["userinfo"]["username"]
                env.log(f"{result['msg']},{env.user_name}")


                 # 拼接 token 和自定义ua
                custom_string = ua
                combined_value = f"{env.token}#{custom_string}"

                # 更新到青龙面板环境变量
                QL(address, client_id, client_secret).updateEnvByName("YXRCCK", combined_value, '游侠auth&ua')
            else:
                env.loginBack = 1
                env.log(f"【登录失败】{result['message']}")
                env.message_content += f"\n【登陆失败】{result['message']}"
        except Exception as e:
            env.log(e)
    else:
        env.loginBack = 1
        env.message_content += f"\n【登陆失败】无法连接到服务器"

# 查询签到状态并签到函数
async def getSign(env):
    url = f"https://api3.ali213.net/feedearn/signing?action=set&token={env.token}"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "ali213app",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": 'api3.ali213.net',
        "Accept-Language": 'zh-Hans-CN;q=1'
    }
    body = 'count=5&paged=1'
    response = retry_request(url, headers=headers, data=body)
    if response:
        try:
            result = response.json()
            if result["data"]["status"] == 1 and result["data"]["msg"] == '签到成功':
                env.log(f"签到成功，获得金币:{result['data']['coins']}")
                env.message_content += f"\n签到成功，获得金币:{result['data']['coins']}"
            elif result["data"]["status"] == 0 and result["data"]["msg"] == '签到失败，重复签到':
                env.log(f"账号[{env.user_name}]今天已签到，签到日期：{result['signinfo']['qiandaotime']}")
                env.message_content += f"\n账号[{env.user_name}]今天已经签到了"
            elif result["data"]["status"] == 0 and result["data"]["msg"] == '用户未登录或登录已超时':
                env.log(f"\n用户未登录或登录已超时")
                env.message_content += f"\n用户未登录或登录已超时"
            elif result is None:
                env.log(f"\n账号[{env.user_name}]签到失败：原因未知")
                env.message_content += f"\n账号[{env.user_name}]签到失败：签到失效"
        except Exception as e:
            env.log(e)
    else:
        env.message_content += f"\n【签到失败】无法连接到服务器"

# 看看是不是新用户函数
async def checknew(env):
    url = f"https://api3.ali213.net/feedearn/newusercheck?token={env.token}"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "ali213app",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": 'api3.ali213.net',
        "Accept-Language": 'zh-Hans-CN;q=1'
    }
    response = retry_request(url, headers=headers, method='get')
    if response:
        try:
            result = response.json()
            if result["status"] == 3 and result["msg"] == '您是最新用户，可以跳最新活动页面了':
                env.log(f"账号[{env.user_name}]您是最新用户，可以跳最新活动页面了")
                await newusersign(env)
            else:
                env.log(f"账号[{env.user_name}]老用户了，去周签")
                env.message_content += f"\n账号[{env.user_name}]老用户了，去周签"
                env.log('\n【开始一周签到】')
                await weeksign(env)
                await weeksigncheck(env)
        except Exception as e:
            env.log(e)
    else:
        env.message_content += f"\n【查询新用户状态失败】无法连接到服务器"

# 查一周签到时间，到时间自动抽奖函数
async def weeksigncheck(env):
    url = f"https://api3.ali213.net/feedearn/oldusermonthactivity?token={env.token}"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Host": 'api3.ali213.net',
        "User-Agent": "ali213app",
        "Accept-Language": 'zh-Hans-CN;q=1',
        "Content-Length": "0"
    }
    response = retry_request(url, headers=headers, method='get')
    if response:
        try:
            result = response.json()
            weeksingday = result["data"]["signday"]
            if result["status"] == 1:
                env.log(f"第{weeksingday}天完成签到，第七天可以抽奖领取奖励\n")
                env.message_content += f"\n账号[{env.user_name}]第{weeksingday}天完成签到，第七天可以抽奖领取奖励"
                if weeksingday == 7:
                    env.log(f"今天是第七天了，可以抽奖领取奖励")
                    await kjl(env)
            else:
                env.log('查询失败')
        except Exception as e:
            env.log(e)
    else:
        env.message_content += f"\n【查询周签到状态失败】无法连接到服务器"

# 查询金币信息函数
async def checkcoin(env):
    url = f"https://api3.ali213.net/feedearn/userbaseinfo?token={env.token}"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Host": 'api3.ali213.net',
        "User-Agent": "ali213app",
        "Accept-Language": 'zh-Hans-CN;q=1',
        "Content-Length": "0"
    }
    response = retry_request(url, headers=headers, method='get')
    if response:
        try:
            result = response.json()
            if result["username"] == env.user_name:
                env.allcoin = result["coins"]
                env.cash = result["available"]
                env.log('\n【开始查询金币信息】')
                env.log(f"账号[{env.user_name}]总金币：{env.allcoin}个，可用现金：{env.cash}（忽略小数点）")
                env.message_content += f"\n账号[{env.user_name}]总金币：{env.allcoin}个，可用现金：{env.cash}（忽略小数点）"
            else:
                env.log(f"查询失败")
                env.message_content += f"\n查询失败"
        except Exception as e:
            env.log(e)
    else:
        env.message_content += f"\n【查询金币信息失败】无法连接到服务器"

# 一周签到函数
async def weeksign(env):
    url = f"https://api3.ali213.net/feedearn/olduseractivitysign?token={env.token}"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "ali213app",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": 'api3.ali213.net',
        "Accept-Language": 'zh-Hans-CN;q=1'
    }
    response = retry_request(url, headers=headers, method='get')
    if response:
        try:
            result = response.json()
            if result["status"] == 1 and result["msg"] == '签到成功':
                env.log('周签成功')
            elif result["msg"] == '您今天已签到':
                env.log(f"账号[{env.user_name}]礼包周签今天已签到")
            else:
                env.log('查询签到状态失败')
        except Exception as e:
            env.log(e)
    else:
        env.message_content += f"\n【周签到失败】无法连接到服务器"

# 新用户签到函数
async def newusersign(env):
    url = f"https://api3.ali213.net/feedearn/newuseractivitysign?token={env.token}"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "ali213app",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": 'api3.ali213.net',
        "Accept-Language": 'zh-Hans-CN;q=1'
    }
    response = retry_request(url, headers=headers, method='get')
    if response:
        try:
            result = response.json()
            if result["status"] == 1 and result["msg"] == '签到成功':
                env.log('新用户福利签到成功')
            elif result["msg"] == '您今天已签到':
                env.log(f"账号[{env.user_name}]新用户福利今天已签到")
            else:
                env.log('查询签到状态失败')
        except Exception as e:
            env.log(e)
    else:
        env.message_content += f"\n【新用户签到失败】无法连接到服务器"

# 第七天抽奖函数
async def kjl(env):
    url = f"https://api3.ali213.net/feedearn/olduseractivityprizing?token={env.token}"
    headers = {
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "ali213app",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": 'api3.ali213.net',
        "Accept-Language": 'zh-Hans-CN;q=1'
    }
    response = retry_request(url, headers=headers, method='get')
    if response:
        try:
            result = response.json()
            if result["status"] == 0 and result["msg"] == '未到抽奖日期':
                env.log('未到抽奖日期')
                env.message_content += f"\n账号[{env.user_name}]今天不是抽奖日"
            elif result["status"] == 1 and result["msg"] == '恭喜中奖':
                env.log(f"开奖并获得了{result['data']['name']}")
                env.message_content += f"\n账号[{env.user_name}]开奖并获得了{result['data']['name']},游戏需要手动到APP查看cd-key"
            elif result["status"] == 0 and result["msg"] == '您已抽过奖了':
                env.log(f"今天已经抽过奖了")
                env.message_content += f"\n账号[{env.user_name}]今天已经抽过奖了"
        except Exception as e:
            env.log(e)
    else:
        env.message_content += f"\n【抽奖失败】无法连接到服务器"

# 发送消息函数
async def SendMsg(env, message):
    if not message:
        return
    env.msg(message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())