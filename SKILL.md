---
name: jimeng-seedream
description: 即梦 AI 图片生成 - 调用火山引擎 Seedream 4.5 模型
metadata:
  openclaw:
    emoji: "🎨"
    requires:
      config: ["skills.entries.jimeng-seedream.apiKey"]
    primaryEnv: "ARK_API_KEY"
---

# 即梦 AI 生图技能 (Jimeng Seedream)

✅ **已验证可用** (2026-03-10) - 文生图、图生图、组图生成全部通过测试

调用火山引擎方舟 Seedream 4.5 模型生成图片。支持文生图、图生图、单图/组图生成。

## 目录

- [快速开始](#快速开始)
- [API 参数](#api-参数)
- [配置](#配置)
- [参考文件](#参考文件)

## 快速开始

### 安装依赖

```bash
pip install "volcengine-python-sdk[ark]"
```

### 文生图

```python
from skills.volcengine import text_to_image

result = text_to_image(prompt="4K超高清猫咪，橘色，可爱")
print(result["images"][0]["url"])
```

### 图生图

```python
from skills.volcengine import image_to_image

result = image_to_image(
    prompt="将背景换成星空",
    image="https://example.com/cat.jpg"
)
print(result["images"][0]["url"])
```

### 组图生成

```python
from skills.volcengine import text_to_image

result = text_to_image(
    prompt="四季庭院插画",
    sequential=True,
    max_images=4
)
for img in result["images"]:
    print(img["url"])
```

### 通用函数

```python
from skills.volcengine import generate

# 自动判断文生图/图生图
result = generate(prompt="科幻城市夜景")
result = generate(prompt="换装", image=["url1", "url2"])
```

## API 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | str | 必填 | 生成提示词 |
| image | str/list | None | 参考图 URL（图生图） |
| model | str | doubao-seedream-4-5-251128 | 模型 ID |
| size | str | "2K" | 图片尺寸 |
| watermark | bool | True | 是否添加水印 |
| sequential | bool | False | 是否生成组图 |
| max_images | int | 4 | 组图最大数量 |

## 返回值格式

```python
{
    "success": True,
    "images": [
        {"url": "https://...", "size": "2048x2048"}
    ],
    "usage": {
        "generated_images": 1,
        "output_tokens": 16384,
        "total_tokens": 16384
    }
}
```

## 配置

在 OpenClaw WebUI 的技能侧边栏配置 API Key：

| 字段 | 说明 |
|------|------|
| **API Key** | 火山引擎 ARK API Key |

**获取方式：** https://console.volcengine.com/ark/iam/keymanage

**环境变量（可选）：**

| 变量名 | 说明 |
|--------|------|
| `ARK_API_KEY` | 火山引擎 API Key |
| `VOLCENGINE_BASE_URL` | API 基础 URL |

## 参考文件

所有引用文件均为直接链接，一层深度：

- [README.md](README.md) - 详细文档和使用指南
- [__init__.py](__init__.py) - Python 模块实现
- [example.py](example.py) - 使用示例代码
- [requirements.txt](requirements.txt) - 依赖列表
- [skill.yaml](skill.yaml) - 技能元数据

## 相关链接

- [ARK 控制台](https://console.volcengine.com/ark)
- [API 文档](https://www.volcengine.com/docs/85621/1817045)

---

🦞 Created by 亏贼马的强壮大龙虾 · MIT License
