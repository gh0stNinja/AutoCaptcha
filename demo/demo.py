'''
Author: gh0stNinja
Blog: https://gh0stninja.github.io/
Date: 2024-12-12 17:54:52
Description: 
'''
import json
import base64
import requests


def load_auth_key(path='auth_key.json'):
    """
    加载授权 key，只加载一次。
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return json_data.get("key")
    except Exception as e:
        raise RuntimeError(f"读取授权文件失败: {e}")


# 全局只加载一次
AUTH_KEY = load_auth_key()


def ocr_png_code(data: bytes) -> str:
    hosts = [
        "http://127.0.0.1:58888",
    ]

    base64_data = base64.b64encode(data).decode("utf-8")

    for host in hosts:
        api_url = f"{host}/get_captcha"
        try:
            req = requests.post(api_url, data=base64_data, headers={"Authorization": f"Basic {AUTH_KEY}"}, timeout=2)
            if req.status_code == 200:
                return req.text
        except Exception:
            continue

    raise RuntimeError("所有 OCR 服务请求失败！")




# 示例调用
# 读取图片并转换为二进制数据


def main(png):
    with open(png, "rb") as f:
        image_data = f.read()

    result = ocr_png_code(image_data)
    if result:
        print(f"验证码：{png} 结果: {result}")
    else:
        print(f"{png} 请求失败")

for png in ["1.png", "2.png"]:
    main(png)