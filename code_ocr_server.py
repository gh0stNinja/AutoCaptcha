#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: gh0stNinja
Blog: https://gh0stninja.github.io/
Date: 2024-12-12
Description: 验证码 OCR API 服务
"""

import argparse
import base64
import io
import json
import threading
import time

import ddddocr
import numpy as np
from aiohttp import web
from PIL import Image
import cv2
from sklearn.cluster import KMeans

# -------------------- 参数 --------------------

parser = argparse.ArgumentParser()
parser.add_argument("-p", help="HTTP port", default="58888")
args = parser.parse_args()
port = int(args.p)

# -------------------- OCR --------------------

ocr = ddddocr.DdddOcr()

# -------------------- 认证 --------------------

auth_key_list = []

def load_auth_key():
    """定时读取 auth_keys.json"""
    global auth_key_list
    while True:
        with open('auth_keys.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        auth_key_list = json_data.get("keys", [])
        time.sleep(60)

def auth_request(auth_header):
    """统一认证入口"""
    if not auth_header:
        return False
    token = auth_header.replace('Basic ', '')
    return token in auth_key_list

# -------------------- 图片预处理 --------------------

def get_dominant_color(image, k=4):
    """提取图像主色"""
    data = np.float32(image.reshape((-1, 3)))
    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(data)
    colors = kmeans.cluster_centers_.astype(int)
    return colors[np.argmin(np.sum(colors, axis=1))]

def is_black_on_white(image, threshold=0.9):
    """判断黑字白底"""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    total = gray.size
    white = np.sum(gray > 200)
    black = np.sum(gray < 50)
    return white / total > threshold and black / total < 0.1

def preprocess_captcha_image(base64_data):
    """验证码图像预处理"""
    image = Image.open(io.BytesIO(base64.b64decode(base64_data))).convert('RGB')
    rgb = np.array(image)

    if is_black_on_white(rgb):
        return base64_data

    dominant_rgb = get_dominant_color(rgb)
    hsv_val = cv2.cvtColor(np.uint8([[dominant_rgb[::-1]]]), cv2.COLOR_BGR2HSV)[0][0]
    lower = np.array([max(hsv_val[0]-10, 0), 30, 30])
    upper = np.array([min(hsv_val[0]+10, 179), 255, 255])

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.dilate(mask, np.ones((2, 2), np.uint8), iterations=1)
    result = cv2.bitwise_and(rgb, rgb, mask=mask)
    gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    enhanced = cv2.equalizeHist(gray)
    final = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # 调试可保存 tmp.png
    # cv2.imwrite('tmp.png', final)

    success, buffer = cv2.imencode('.png', final)
    return base64.b64encode(buffer).decode('utf-8') if success else None

# -------------------- 路由处理 --------------------

async def get_captcha_calc(request):
    """识别算术验证码"""
    if not auth_request(request.headers.get('Authorization')):
        return web.Response(text='Forbidden', status=403)

    img_base64 = await request.text()
    img_base64 = preprocess_captcha_image(img_base64)
    img_bytes = base64.b64decode(img_base64)
    code_text = ocr.classification(img_bytes)
    message = f"[+] 验证码结果：{code_text}"

    try:
        if '=' in code_text:
            code_text = code_text.split('=')[0]
            replacements = {
                "×": "*", "x": "*", "X": "*",
                "＋": "+", "－": "-", "÷": "/",
                "o": "0", "l": "1", "i": "1",
                "z": "2", "Z": "2", "g": "9"
            }
            for old, new in replacements.items():
                code_text = code_text.replace(old, new)

            result = None
            if '+' in code_text:
                a, b = map(int, code_text.split('+'))
                result = a + b
            elif '-' in code_text:
                a, b = map(int, code_text.split('-'))
                result = a - b
            elif '*' in code_text:
                a, b = map(int, code_text.split('*'))
                result = a * b
            elif '/' in code_text:
                a, b = map(int, code_text.split('/'))
                result = a / b if b != 0 else None

            if result is not None:
                message = f"[+] 验证码结果：{code_text} = {result}"
                code_text = result

    except Exception as e:
        print(f"[!] Parse error: {e}")

    print(message)
    return web.Response(text=str(code_text))

async def generic_ocr(request, range_id):
    """通用 OCR 路由"""
    if not auth_request(request.headers.get('Authorization')):
        return web.Response(text='Forbidden', status=403)
    ocr.set_ranges(range_id)
    img_base64 = await request.text()
    img_bytes = base64.b64decode(img_base64)
    res = ocr.classification(img_bytes, probability=True)
    code_text = ''.join(res['charsets'][i.index(max(i))] for i in res['probability'])
    print(f"[+] OCR Range {range_id}: {code_text}")
    return web.Response(text=code_text)

# 其他 OCR 路由
get_captcha_number = lambda request: generic_ocr(request, 0)
get_captcha_letter = lambda request: generic_ocr(request, 1)
get_captcha_LETTER = lambda request: generic_ocr(request, 2)
get_captcha_LETter = lambda request: generic_ocr(request, 3)
get_captcha_letter_number = lambda request: generic_ocr(request, 4)
get_captcha_LETTER_number = lambda request: generic_ocr(request, 5)
get_captcha_LETter_number = lambda request: generic_ocr(request, 6)

# -------------------- 路由注册 --------------------

app = web.Application()
app.add_routes([
    web.post('/get_captcha', get_captcha_calc),
    web.post('/get_captcha_number', get_captcha_number),
    web.post('/get_captcha_letter', get_captcha_letter),
    web.post('/get_captcha_LETTER', get_captcha_LETTER),
    web.post('/get_captcha_LETter', get_captcha_LETter),
    web.post('/get_captcha_letter_number', get_captcha_letter_number),
    web.post('/get_captcha_LETTER_number', get_captcha_LETTER_number),
    web.post('/get_captcha_LETter_number', get_captcha_LETter_number),
])

# -------------------- 主程序 --------------------

if __name__ == '__main__':
    threading.Thread(target=load_auth_key, daemon=True).start()
    web.run_app(app, port=port)
