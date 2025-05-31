import requests



authorization_token='need token'  #改成你自己的,22行可以选择换AI模型，不过目前的模型够用且免费




def call_glm_4_flash(prompt):
    """
    调用 GLM-4-Flash 模型的 API，根据输入的 prompt 获取响应内容
    :param prompt: 用户输入的提示信息
    :param authorization_token: 用于身份验证的令牌
    :return: 模型返回的消息内容，如果请求失败则返回 None
    """
    headers = {
        'Authorization': f'Bearer {authorization_token}',
    }

    json_data = {
        'model': 'GLM-4-Flash',
        'messages': [
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    }

    # 发送 POST 请求
    response = requests.post('https://open.bigmodel.cn/api/paas/v4/chat/completions', headers=headers, json=json_data)

    # 检查响应状态码
    if response.status_code == 200:
        response_data = response.json()
        # 提取 message 中的 content 内容
        message_content = response_data["choices"][0]["message"]["content"]
        return message_content
    else:
        print(f"请求失败，状态码: {response.status_code}，错误信息: {response.text}")
        return None
