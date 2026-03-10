"""
即梦 AI 生图技能 - Jimeng Seedream Image Generation
使用火山引擎方舟官方 SDK (volcenginesdkarkruntime)
支持：文生图、图生图、单图/组图生成
"""

import os
import json
from typing import Optional, List, Dict, Any, Union

try:
    from volcenginesdkarkruntime import Ark
    from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions
except ImportError:
    raise ImportError("请安装依赖：pip install 'volcengine-python-sdk[ark]'")


# ============================================================
# 1. 配置与客户端初始化
# ============================================================
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MODEL = "doubao-seedream-4-5-251128"


def load_api_key() -> str:
    """从环境变量或 OpenClaw 配置加载 API Key"""
    api_key = os.getenv("ARK_API_KEY") or os.getenv("VOLCENGINE_API_KEY")
    
    if not api_key:
        try:
            config_path = os.path.expanduser("~/.openclaw/openclaw.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            skill_conf = config.get('skills', {}).get('entries', {}).get('jimeng-seedream', {})
            api_key = skill_conf.get('apiKey', '')
        except Exception:
            pass
    
    if not api_key:
        raise ValueError("ARK_API_KEY 必须配置（环境变量或 OpenClaw 技能配置）")
    
    return api_key


def get_client() -> Ark:
    """初始化 Ark 客户端"""
    api_key = load_api_key()
    return Ark(
        base_url=os.getenv("VOLCENGINE_BASE_URL", DEFAULT_BASE_URL),
        api_key=api_key,
    )


# ============================================================
# 2. 文生图
# ============================================================
def text_to_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: str = "2K",
    watermark: bool = True,
    sequential: bool = False,
    max_images: int = 4,
) -> Dict[str, Any]:
    """
    文生图
    
    Args:
        prompt: 生成提示词
        model: 模型 ID
        size: 图片尺寸 (如 "2K", "1024x1024")
        watermark: 是否添加水印
        sequential: 是否生成组图
        max_images: 组图最大数量
    
    Returns:
        {
            "success": True,
            "images": [{"url": "...", "size": "..."}, ...],
            "usage": {...}
        }
    """
    client = get_client()
    
    kwargs = {
        "model": model,
        "prompt": prompt,
        "response_format": "url",
        "size": size,
        "watermark": watermark,
    }
    
    if sequential:
        kwargs["sequential_image_generation"] = "auto"
        kwargs["sequential_image_generation_options"] = SequentialImageGenerationOptions(max_images=max_images)
        kwargs["stream"] = True
        
        images = []
        for event in client.images.generate(**kwargs):
            if event is None:
                continue
            if event.type == "image_generation.partial_succeeded":
                if event.error is None and event.url:
                    images.append({"url": event.url, "size": event.size})
            elif event.type == "image_generation.completed":
                return {
                    "success": True,
                    "images": images,
                    "usage": event.usage if hasattr(event, 'usage') else None,
                }
        return {"success": True, "images": images, "usage": None}
    else:
        kwargs["sequential_image_generation"] = "disabled"
        kwargs["stream"] = False
        
        response = client.images.generate(**kwargs)
        return {
            "success": True,
            "images": [{"url": img.url, "size": img.size if hasattr(img, 'size') else None} for img in response.data],
            "usage": response.usage if hasattr(response, 'usage') else None,
        }


# ============================================================
# 3. 图生图
# ============================================================
def image_to_image(
    prompt: str,
    image: Union[str, List[str]],
    model: str = DEFAULT_MODEL,
    size: str = "2K",
    watermark: bool = True,
    sequential: bool = False,
    max_images: int = 4,
) -> Dict[str, Any]:
    """
    图生图
    
    Args:
        prompt: 编辑/生成提示词
        image: 参考图 URL (单张字符串或多张列表)
        model: 模型 ID
        size: 图片尺寸
        watermark: 是否添加水印
        sequential: 是否生成组图
        max_images: 组图最大数量
    
    Returns:
        {
            "success": True,
            "images": [{"url": "...", "size": "..."}, ...],
            "usage": {...}
        }
    """
    client = get_client()
    
    kwargs = {
        "model": model,
        "prompt": prompt,
        "image": image,
        "response_format": "url",
        "size": size,
        "watermark": watermark,
    }
    
    if sequential:
        kwargs["sequential_image_generation"] = "auto"
        kwargs["sequential_image_generation_options"] = SequentialImageGenerationOptions(max_images=max_images)
        kwargs["stream"] = True
        
        images = []
        for event in client.images.generate(**kwargs):
            if event is None:
                continue
            if event.type == "image_generation.partial_succeeded":
                if event.error is None and event.url:
                    images.append({"url": event.url, "size": event.size})
            elif event.type == "image_generation.completed":
                return {
                    "success": True,
                    "images": images,
                    "usage": event.usage if hasattr(event, 'usage') else None,
                }
        return {"success": True, "images": images, "usage": None}
    else:
        kwargs["sequential_image_generation"] = "disabled"
        kwargs["stream"] = False
        
        response = client.images.generate(**kwargs)
        return {
            "success": True,
            "images": [{"url": img.url, "size": img.size if hasattr(img, 'size') else None} for img in response.data],
            "usage": response.usage if hasattr(response, 'usage') else None,
        }


# ============================================================
# 4. 便捷函数
# ============================================================
def generate(
    prompt: str,
    image: Optional[Union[str, List[str]]] = None,
    model: str = DEFAULT_MODEL,
    size: str = "2K",
    watermark: bool = True,
    sequential: bool = False,
    max_images: int = 4,
) -> Dict[str, Any]:
    """
    通用生成函数（自动判断文生图/图生图）
    
    Args:
        prompt: 生成提示词
        image: 参考图 URL（可选，有则图生图，无则文生图）
        model: 模型 ID
        size: 图片尺寸
        watermark: 是否添加水印
        sequential: 是否生成组图
        max_images: 组图最大数量
    
    Returns:
        {
            "success": True,
            "images": [{"url": "...", "size": "..."}, ...],
            "usage": {...}
        }
    """
    if image:
        return image_to_image(
            prompt=prompt,
            image=image,
            model=model,
            size=size,
            watermark=watermark,
            sequential=sequential,
            max_images=max_images,
        )
    else:
        return text_to_image(
            prompt=prompt,
            model=model,
            size=size,
            watermark=watermark,
            sequential=sequential,
            max_images=max_images,
        )


# ============================================================
# 5. 导出
# ============================================================
__all__ = [
    "Ark",
    "get_client",
    "load_api_key",
    "text_to_image",
    "image_to_image",
    "generate",
    "DEFAULT_MODEL",
]
