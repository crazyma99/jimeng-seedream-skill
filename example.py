"""
即梦 AI 生图技能 - 使用示例
Jimeng Seedream Image Generation - Usage Examples
"""

from skills.volcengine import text_to_image, image_to_image, generate


def example_text_to_image():
    """文生图示例"""
    print("=== 文生图示例 ===")
    
    result = text_to_image(
        prompt="4K超高清猫咪，橘色，可爱，温暖阳光",
        size="2K",
        watermark=False
    )
    
    if result["success"]:
        print(f"✅ 生成成功！")
        print(f"图片数量: {len(result['images'])}")
        for i, img in enumerate(result["images"]):
            print(f"  图片 {i+1}: {img['url'][:80]}...")
    else:
        print("❌ 生成失败")
    
    return result


def example_image_to_image():
    """图生图示例"""
    print("\n=== 图生图示例 ===")
    
    # 先生成一张图片作为参考图
    base_result = text_to_image(
        prompt="一只可爱的橘猫在阳光下",
        watermark=False
    )
    
    if not base_result["success"]:
        print("❌ 基础图片生成失败")
        return None
    
    ref_url = base_result["images"][0]["url"]
    print(f"参考图: {ref_url[:80]}...")
    
    # 图生图
    result = image_to_image(
        prompt="换成赛博朋克风格，霓虹灯光效果",
        image=ref_url,
        watermark=False
    )
    
    if result["success"]:
        print(f"✅ 编辑成功！")
        print(f"结果图: {result['images'][0]['url'][:80]}...")
    else:
        print("❌ 编辑失败")
    
    return result


def example_sequential():
    """组图生成示例"""
    print("\n=== 组图生成示例 ===")
    
    result = text_to_image(
        prompt="春夏秋冬四季风景插画",
        sequential=True,
        max_images=4,
        watermark=False
    )
    
    if result["success"]:
        print(f"✅ 组图生成成功！共 {len(result['images'])} 张")
        for i, img in enumerate(result["images"]):
            print(f"  图片 {i+1}: {img['url'][:80]}...")
    else:
        print("❌ 组图生成失败")
    
    return result


def example_generate_auto():
    """通用函数示例（自动判断文生图/图生图）"""
    print("\n=== 通用函数示例 ===")
    
    # 文生图模式（无 image 参数）
    result1 = generate(prompt="科幻城市夜景", watermark=False)
    print(f"文生图: {result1['images'][0]['url'][:80]}...")
    
    # 图生图模式（有 image 参数）
    result2 = generate(
        prompt="添加星空背景",
        image=result1["images"][0]["url"],
        watermark=False
    )
    print(f"图生图: {result2['images'][0]['url'][:80]}...")
    
    return result1, result2


def example_multi_reference():
    """多参考图示例"""
    print("\n=== 多参考图示例 ===")
    
    # 生成两张参考图
    ref1 = text_to_image(prompt="红色玫瑰花", watermark=False)
    ref2 = text_to_image(prompt="蓝色绣球花", watermark=False)
    
    refs = [ref1["images"][0]["url"], ref2["images"][0]["url"]]
    
    # 多参考图生成
    result = image_to_image(
        prompt="将两朵花融合在一起，梦幻风格",
        image=refs,
        watermark=False
    )
    
    if result["success"]:
        print(f"✅ 多参考图生成成功！")
        print(f"结果图: {result['images'][0]['url'][:80]}...")
    else:
        print("❌ 生成失败")
    
    return result


if __name__ == "__main__":
    print("🎨 即梦 AI 生图技能 - 示例代码")
    print("=" * 50)
    
    # 运行所有示例
    example_text_to_image()
    example_image_to_image()
    example_sequential()
    example_generate_auto()
    example_multi_reference()
    
    print("\n✅ 所有示例运行完成！")
