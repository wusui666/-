import requests
from json import dumps as jsonDumps


class QL:
    def __init__(self, address: str, id: str, secret: str):
        self.address = address
        self.id = id
        self.secret = secret
        self.valid = True
        self.auth = self.login()

    def log(self, content: str):
        print(content)

    def login(self):
        url = f"{self.address}/open/auth/token?client_id={self.id}&client_secret={self.secret}"
        try:
            rjson = requests.get(url).json()
            if rjson['code'] == 200:
                return f"{rjson['data']['token_type']} {rjson['data']['token']}"
            self.log(f"登录失败：{rjson['message']}")
            self.valid = False
        except Exception as e:
            self.valid = False
            self.log(f"登录失败：{str(e)}")
        return None

    def getEnvs(self):
        if not self.auth:
            return []
        url = f"{self.address}/open/envs?searchValue="
        headers = {"Authorization": self.auth}
        try:
            rjson = requests.get(url, headers=headers).json()
            if rjson['code'] == 200:
                return rjson['data']
            self.log(f"获取环境变量失败：{rjson['message']}")
        except Exception as e:
            self.log(f"获取环境变量失败：{str(e)}")
        return []

    def updateEnvByName(self, name, value, remark=""):
        if not self.auth:
            self.log("未获取到有效的认证信息，无法更新环境变量。")
            return False
        envs = self.getEnvs()
        target_env = next((env for env in envs if env.get("name") == name), None)
        if not target_env:
            self.log(f"未找到名称为 {name} 的环境变量")
            return False
        env = {
            "id": target_env["id"],
            "name": name,
            "value": str(value),
            "remarks": str(remark)
        }
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, data=jsonDumps(env)).json()
            if rjson['code'] == 200:
                self.log(f"更新环境变量 {name} 成功")
                return True
            self.log(f"更新环境变量 {name} 失败：{rjson['message']}")
        except Exception as e:
            self.log(f"更新环境变量 {name} 失败：{str(e)}")
        return False



'''调用示例

from 青龙面板ck更新 import QL

# 配置青龙面板信息
address = "http://192.168.1.241:5700/"
client_id = "h--hKdDc1111"
client_secret = "biAl8vXEFscEvC2-Oh7U8Nwi"

# 调用 updateEnvByName 方法更新 ck
result =  QL(address, client_id, client_secret).updateEnvByName("名", 值, '备注')



if result:
    print("更新成功")
else:
    print("更新失败")

'''