'''
Author: gh0stNinja
Blog: https://gh0stninja.github.io/
Date: 2024-12-12 15:57:06
Description: 
'''
import random
import string
from flask import Flask, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# 生成不同类型的验证码
def generate_captcha_expression(captcha_type):
    if captcha_type == "digits":
        # 纯数字验证码
        chars = string.digits
        expression = ''.join(random.choice(chars) for _ in range(4))  # 生成4位数字
    elif captcha_type == "lowercase":
        # 纯小写字母验证码
        chars = string.ascii_lowercase
        expression = ''.join(random.choice(chars) for _ in range(4))  # 生成4个小写字母
    elif captcha_type == "uppercase":
        # 纯大写字母验证码
        chars = string.ascii_uppercase
        expression = ''.join(random.choice(chars) for _ in range(4))  # 生成4个大写字母
    elif captcha_type == "lowercase_uppercase":
        # 小写字母 + 大写字母
        chars = string.ascii_lowercase + string.ascii_uppercase
        expression = ''.join(random.choice(chars) for _ in range(4))  # 生成4个字母（大小写混合）
    elif captcha_type == "lowercase_digits":
        # 小写字母 + 数字
        chars = string.ascii_lowercase + string.digits
        expression = ''.join(random.choice(chars) for _ in range(4))  # 生成4个字符（小写字母 + 数字）
    elif captcha_type == "uppercase_digits":
        # 大写字母 + 数字
        chars = string.ascii_uppercase + string.digits
        expression = ''.join(random.choice(chars) for _ in range(4))  # 生成4个字符（大写字母 + 数字）
    elif captcha_type == "all":
        # 小写字母 + 大写字母 + 数字
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        expression = ''.join(random.choice(chars) for _ in range(4))  # 生成4个字符（小写 + 大写 + 数字）
    elif captcha_type == "arithmetic":
        # 加减乘除运算式
        num1 = random.randint(1, 9)
        num2 = random.randint(1, 9)
        operator = random.choice(['+', '-', '*', 'x', 'x'])
        
        # if operator == '/':
        #     num1 = num1 * num2  # 为避免除数为0，确保可以整除

        expression = f"{num1} {operator} {num2} = ?"
        # expression = f"{num1}{operator}{num2}=?"
    
    return expression

# 生成验证码图像
def generate_captcha_image(captcha_type):
    expression = generate_captcha_expression(captcha_type)

    # 创建图像
    width, height = 200, 60
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 使用默认字体，如果没有指定字体，可能会导致某些环境下无法运行
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # 画出运算式
    draw.text((20, 10), expression, font=font, fill=(0, 0, 0))

    # 返回图像数据
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io, expression

@app.route('/captcha')
def captcha():
    # 随机选择验证码类型
    # captcha_types = ["digits", "lowercase", "uppercase", "lowercase_uppercase", "lowercase_digits", "uppercase_digits", "all", "arithmetic"]
    captcha_types = ["arithmetic"]
    captcha_type = random.choice(captcha_types)

    # 生成验证码
    img_io, expression = generate_captcha_image(captcha_type)

    # 返回图像
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    # 启动时打印出接口地址
    print("应用已启动，访问以下地址获取验证码：")
    print("http://127.0.0.1:5000/captcha")
    
    app.run(debug=True)
