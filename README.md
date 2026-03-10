# 即梦 AI 生图技能 (Jimeng Seedream)

![Status](https://img.shields.io/badge/status-active-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

调用火山引擎方舟 Seedream 4.5 模型生成图片的 OpenClaw 技能。支持文生图、图生图、单图/组图生成。

## 目录 (Table of Contents)

- [功能特性](#功能特性)
- [安装](#安装)
- [配置](#配置)
- [快速开始](#快速开始)
  - [文生图](#文生图)
  - [图生图](#图生图)
  - [组图生成](#组图生成)
- [API 参考](#api-参考)
  - [text_to_image](#text_to_image)
  - [image_to_image](#image_to_image)
  - [generate](#generate)
- [返回值格式](#返回值格式)
- [示例代码](#示例代码)
- [故障排除](#故障排除)
- [相关链接](#相关链接)

## 功能特性

- ✅ **文生图**：从文本提示生成图片
- ✅ **图生图**：基于参考图进行编辑/生成
- ✅ **组图生成**：一次生成多张相关图片
- ✅ **多参考图**：支持传入多张参考图
- ✅ **灵活配置**：支持尺寸、水印等参数
- ✅ **SDK 自动处理**：使用官方 Ark SDK，自动处理签名

## 安装

### 方式一：让龙虾帮你部署（推荐给 OpenClaw 用户）

如果你正在使用 OpenClaw，直接把下面这句话发给你的龙虾：

> **请按照这个 SKILL.md 帮我完成 jimeng-seedream-skill 的安装：**  
> https://github.com/crazyma99/jimeng-seedream-skill/blob/main/SKILL.md

龙虾会自动完成：
1. Clone 仓库
2. Skill 安装部署
3. 提示你把 API Key 发给它
4. 将使用方式发送给你

### 方式二：手动安装

#### 1. 安装依赖

```bash
pip install "volcengine-python-sdk[ark]"
```

#### 2. 复制技能文件

将整个 `jimeng-seedream-skill` 目录复制到 OpenClaw 技能目录：

```bash
cp -r jimeng-seedream-skill ~/.openclaw/workspace/skills/jimeng-seedream
```

## 配置

### 方式一：OpenClaw WebUI（推荐）

在 OpenClaw WebUI 的技能侧边栏中配置：

| 字段 | 说明 |
|------|------|
| **API Key** | 火山引擎 ARK API Key |

**获取 API Key：** https://console.volcengine.com/ark/iam/keymanage

### 方式二：环境变量

```bash
export ARK_API_KEY="your-api-key"
```

### 方式三：OpenClaw 配置文件

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "skills": {
    "entries": {
      "jimeng-seedream": {
        "apiKey": "your-api-key"
      }
    }
  }
}
```

## 快速开始

### 文生图

```python
from skills.volcengine import text_to_image

result = text_to_image(
    prompt="4K超高清猫咪，橘色，可爱，温暖阳光",
    size="2K",
    watermark=False
)

print(result["images"][0]["url"])
```

### 图生图

```python
from skills.volcengine import image_to_image

result = image_to_image(
    prompt="将背景换成星空，添加霓虹灯光效果",
    image="https://example.com/cat.jpg",
    size="2K"
)

print(result["images"][0]["url"])
```

### 组图生成

```python
from skills.volcengine import text_to_image

result = text_to_image(
    prompt="四季庭院插画，春夏秋冬",
    sequential=True,
    max_images=4,
    watermark=False
)

for i, img in enumerate(result["images"]):
    print(f"图片 {i+1}: {img['url']}")
```

## API 参考

### text_to_image

```python
def text_to_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: str = "2K",
    watermark: bool = True,
    sequential: bool = False,
    max_images: int = 4,
) -> Dict[str, Any]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | str | 必填 | 生成提示词 |
| model | str | doubao-seedream-4-5-251128 | 模型 ID |
| size | str | "2K" | 图片尺寸 |
| watermark | bool | True | 是否添加水印 |
| sequential | bool | False | 是否生成组图 |
| max_images | int | 4 | 组图最大数量 |

### image_to_image

```python
def image_to_image(
    prompt: str,
    image: Union[str, List[str]],
    model: str = DEFAULT_MODEL,
    size: str = "2K",
    watermark: bool = True,
    sequential: bool = False,
    max_images: int = 4,
) -> Dict[str, Any]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | str | 必填 | 编辑/生成提示词 |
| image | str/list | 必填 | 参考图 URL |
| model | str | doubao-seedream-4-5-251128 | 模型 ID |
| size | str | "2K" | 图片尺寸 |
| watermark | bool | True | 是否添加水印 |
| sequential | bool | False | 是否生成组图 |
| max_images | int | 4 | 组图最大数量 |

### generate

```python
def generate(
    prompt: str,
    image: Optional[Union[str, List[str]]] = None,
    model: str = DEFAULT_MODEL,
    size: str = "2K",
    watermark: bool = True,
    sequential: bool = False,
    max_images: int = 4,
) -> Dict[str, Any]
```

通用生成函数，自动判断文生图/图生图：
- 有 `image` 参数 → 图生图
- 无 `image` 参数 → 文生图

## 返回值格式

所有函数返回统一格式：

```python
{
    "success": True,
    "images": [
        {
            "url": "https://ark-content-generation-v2-.../image.jpg",
            "size": "2048x2048"
        }
    ],
    "usage": {
        "generated_images": 1,
        "output_tokens": 16384,
        "total_tokens": 16384
    }
}
```

## 示例代码

### 完整示例

```python
from skills.volcengine import text_to_image, image_to_image, generate

# 文生图
result1 = text_to_image(
    prompt="一只可爱的橘猫在阳光下",
    size="2K",
    watermark=False
)
print(f"生成图片: {result1['images'][0]['url']}")

# 图生图
result2 = image_to_image(
    prompt="换成赛博朋克风格",
    image=result1["images"][0]["url"],
    watermark=False
)
print(f"编辑后图片: {result2['images'][0]['url']}")

# 组图生成
result3 = text_to_image(
    prompt="春夏秋冬四季风景",
    sequential=True,
    max_images=4,
    watermark=False
)
for i, img in enumerate(result3["images"]):
    print(f"组图 {i+1}: {img['url']}")
```

## 故障排除

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `ValueError: ARK_API_KEY 必须配置` | 检查 API Key 是否正确配置 |
| `ImportError: 请安装依赖` | 运行 `pip install "volcengine-python-sdk[ark]"` |
| 图片 URL 过期 | 图片 URL 有效期 24 小时，请及时保存 |
| 生成失败 | 检查提示词是否符合规范，避免敏感词 |

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from skills.volcengine import text_to_image
result = text_to_image(prompt="测试")
```

## 相关链接

- [ARK 控制台](https://console.volcengine.com/ark) - 管理 API Key 和模型
- [API 文档](https://www.volcengine.com/docs/85621/1817045) - 官方 API 文档
- [火山引擎官网](https://www.volcengine.com/) - 火山引擎官网

---

🦞 Created by 亏贼马的强壮大龙虾 · MIT License · 2026-03-10
