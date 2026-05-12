import re
import subprocess
from typing import Dict, Any

def parse_swww_help() -> Dict[str, Any]:
    """
    动态解析 swww img --help 输出，自动提取所有 transition 参数
    无需硬编码, swww 更新后自动同步新参数
    """
    try:
        result = subprocess.run(
            ["swww", "img", "--help"],
            capture_output=True,
            text=True,
            check=True,
        )
        help_text = result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[swww_auto_gui] Failed to get swww help: {e}")
        return {}
    
    # 精准匹配每个 --transition-* 参数
    param_pattern = re.compile(
        r"--transition-(?P<name>[a-zA-Z0-9_]+)\s+"
        r"(?P<arg><[A-Z_]+>)?\s*"
        r"(?P<desc>.*?)"
        r"(?=\n\s*--|\Z)",  # 终止条件：下一个 -- 开头的行，或文件末尾
        re.DOTALL
    )
    params = {}

    for match in param_pattern.finditer(help_text):
        name = match.group("name")
        arg = match.group("arg")
        desc_raw = match.group("desc").strip()

        # 1. 提取默认值（兼容 [default: xxx] 格式）
        default_match = re.search(r"\[default:\s*(?P<default>.*?)\s*\]", desc_raw)
        default = default_match.group("default") if default_match else None

        # 2. 提取可选值（仅 transition-type）
        choices = []
        if name == "type":
            choices_match = re.search(
                r"Possible transitions are:\s*(?P<choices>.*?)(?=\n\s*The 'left')",
                desc_raw,
                re.DOTALL
            )
            if choices_match:
                choices_str = choices_match.group("choices")
                choices = [c.strip() for c in choices_str.split("|") if c.strip()]

        # 3. 自动判断参数类型
        param_type = "string"
        if any(k in name for k in ["step", "fps", "angle"]):
            param_type = "int"
        elif "duration" in name:
            param_type = "float"
        elif choices:
            param_type = "choice"
        elif "bezier" in name or "wave" in name or "pos" in name:
            param_type = "string"

        # 4. 优化说明文档：顶部明确配置项、删除多余换行、清理占位符
        # 第一步：拆分描述，提取核心说明
        desc_lines = [line.strip() for line in desc_raw.split("\n") if line.strip()]
        clean_desc = []
        # 顶部明确配置项（如：transition-pos: 配置说明）
        clean_desc.append(f"--transition-{name}: {desc_lines[0]}")

        # 第二步：过滤掉 env、default 等冗余行，只保留核心功能说明
        for line in desc_lines[1:]:
            if not line.startswith("[env:") and not line.startswith("[default:"):
                # 替换多余的占位符（如 <TRANSITION_POS>）
                line = re.sub(r"<[A-Z_]+>", "", line)
                clean_desc.append(line)
        # 第三步：合并为单行，删除多余空格
        final_desc = " ".join(clean_desc)
        # 清理连续空格
        final_desc = re.sub(r"\s+", " ", final_desc).strip()

        # 5. 生成配置项
        key = f"swww_transition_{name}"
        params[key] = {
            "name": name,
            "display": name.replace("_", " ").title(),
            "default": default,
            "choices": choices,
            "type": param_type,
            "desc": final_desc  # 优化后的干净说明
        }

    return params
