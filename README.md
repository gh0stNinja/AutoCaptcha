# AutoCaptcha

> 🚀 一个基于 Python、ddddocr 和 AIOHTTP 的轻量级验证码识别 API 服务，支持算术验证码和多种字符集的通用 OCR 识别。

---

## 📌 功能简介

- 🎯 **多种验证码类型**
  - 算术验证码自动计算（支持 `1+2=`、`4×5=` 等）
  - 数字、字母、大小写混合、多字符集自动识别

- 🧩 **高可用 OCR 引擎**
  - 使用 [ddddocr](https://github.com/sml2h3/ddddocr) 提供高效验证码识别
  - 内置图像预处理（去背景、提取主色、二值化增强）

- 🔐 **简易 Token 认证**
  - 支持 Basic Token，按需授权调用

- ⚡ **可自定义**
  - 基于 AIOHTTP，易于二次开发
  - 支持多路由切换不同 OCR 识别范围

---

## ⚙️ 快速开始

### 1️⃣ 安装依赖

```bash
pip install ddddocr aiohttp pillow numpy opencv-python scikit-learn
```

### 2️⃣ 配置授权密钥

在项目根目录创建 `auth_keys.json`：

```
{
  "keys": ["YOUR_TOKEN_1", "YOUR_TOKEN_2"]
}
```

### 3️⃣ 运行服务

```
python code_ocr_server.py -p 58888
```

------

### 4️⃣ 使用示例

**POST 请求**

```
curl -X POST http://localhost:58888/get_captcha \
     -H "Authorization: Basic YOUR_TOKEN_1" \
     -d "@base64.txt"
```

- `get_captcha`：算术验证码识别
- `get_captcha_number`：纯数字
- `get_captcha_letter`：小写字母
- `get_captcha_LETTER`：大写字母
- `get_captcha_LETter`：大小写字母
- `get_captcha_letter_number`：字母+数字
- `get_captcha_LETTER_number`：大写字母+数字
- `get_captcha_LETter_number`：大小写字母+数字

------

## ⚙️ 路由一览

| 路由                         | 描述                     |
| ---------------------------- | ------------------------ |
| `/get_captcha`               | 自动识别算术验证码并计算 |
| `/get_captcha_number`        | 纯数字验证码             |
| `/get_captcha_letter`        | 小写字母验证码           |
| `/get_captcha_LETTER`        | 大写字母验证码           |
| `/get_captcha_LETter`        | 大小写字母混合           |
| `/get_captcha_letter_number` | 字母+数字混合            |
| `/get_captcha_LETTER_number` | 大写字母+数字            |
| `/get_captcha_LETter_number` | 大小写字母+数字          |



------

## 🔒 授权机制

- 所有请求需携带：

  ```
  Authorization: Basic YOUR_TOKEN
  ```

- 后台每隔 60 秒自动重新加载 `auth_keys.json`。

------

## ⚙️ 图像预处理逻辑

- 自动判断背景色 / 字色
- 自动二值化 / 直方图均衡 / 高斯模糊
- 可自行调整阈值或替换预处理逻辑

------

## 📌 TODO

-  支持分布式部署
-  支持更多验证码类型（滑块、点选）
-  增加前端 Demo 页
