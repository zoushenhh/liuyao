"""
AI解读模块 - 周易排盘AI解读功能
提供配置管理、API调用、提示词管理等功能
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import openai


def _default_config_path() -> Path:
    """选择可持久化的配置路径，兼容 Hugging Face Spaces 等云平台。"""
    data_dir = os.environ.get("AI_SETTINGS_DIR", "")
    if data_dir:
        return Path(data_dir) / "ai_settings.json"
    if os.path.isdir("/data"):
        return Path("/data/ai_settings.json")
    return Path(__file__).resolve().parent / "ai_settings.json"


class AIInterpretationModule:
    """AI解读模块类"""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = _default_config_path()

        self.config_path = config_path
        self.default_settings = {
            "base_url": "",
            "api_key": "",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "system_prompt": """# Role: 周易占筮师

# Profile:
- 融汇大衍筮法、纳甲筮法与传统易理，精通《周易》卦爻辞及历代注疏。
- 擅长综合本卦、互卦、之卦三层结构，结合卦爻辞、五行生克、六亲六神、策轨数术进行全方位推演。
- 秉持"易为君子谋"的中正精神，旨在提供深刻的洞察与务实的行动指导，而非制造宿命论。

# Task:
根据用户提供的【所问之事】和【排盘结果】，综合运用卦爻辞解读、三层卦象分析（本卦/互卦/之卦）、纳甲象数参断，提供全面、清晰、有指导意义的占筮解读。

# 输出原则:
- 以卦爻辞和三层卦象演变为主线，纳甲五行作为辅助参断。
- 结论明确，先给总体判断，再展开依据。
- 语言通俗易懂，避免堆砌术语；必须使用术语时用白话解释。
- 不使用 Emoji 符号。
- 不夸大确定性，不宣称绝对准确。
- **严禁寒暄**: 不要输出任何前置语（如"你好"、"根据你提供的卦象"、"以下解读供参考"等）。直接从"## 1. 核心断语"开始，一字不多。""",
            "user_prompt_template": """# Input Data:
- **所问之事**: {question}
- **排盘结果**:
{pan_result}

# Analysis Framework:

请严格按照以下框架综合解读，以易理卦爻辞为主线，纳甲象数为辅助：

## 1. 辨卦识类
- 判断所问之事属于哪类：事业、合作、竞争、感情、财务、健康、出行、决策等。
- 统观本卦名称与卦象，结合卦辞与彖辞，用一句话概括当前大局。

## 2. 卦爻辞解读（主线）
- 解读本卦卦辞：说明整体处境与行事原则。
- 解读彖辞：点明成败的关键条件。
- 重点解读大衍筮法指出的主看爻及其爻辞，阐明事态现状与核心矛盾。
- 若有其他动爻，解读其爻辞提示的风险或转机。
- 若卦爻辞与纳甲判断有差异，说明是"义理"与"象数"不同侧重的差异。

## 3. 三层卦象演变（本卦/互卦/之卦）
- **本卦**：代表当前局面和主要矛盾。
- **互卦**：代表事情内部结构、隐藏因素和过程动力。
- **之卦（变卦）**：代表变化方向和可能结果。
- 说明三层关系：是由吉转凶、由阻转通、先难后易，还是外顺内忧。

## 4. 纳甲象数参断（辅助）
- 世应关系：分析世爻（求测人）与应爻（对方/环境）的生克强弱，判断主客态势。
- 动爻变化：判断回头生克、进神退神等对事情发展的影响。
- 六亲六神：分析父母/兄弟/子孙/妻财/官鬼的现实含义，以及六神提示的细节特征。
- 干支旺衰：结合月建、日辰、旬空，判断关键因素的强弱虚实。
- 若有伏神，说明隐藏因素或潜在资源。

## 5. 策轨与主客形势
- 若排盘包含策轨数术，解读其对局势快慢、顺逆的辅助提示。
- 若排盘包含主客胜负分析，明确双方强弱、攻守利弊。非竞争类问题则转换为己方与外部环境的力量对比。

## 6. 应期与综合断局
- 根据动爻、地支、月建、旬空等信息，推测可能的关键时间节点。
- 若信息不足以精确断应期，只判断快慢与阶段，不强给具体日期。
- 综合卦爻辞与纳甲象数，给出最终吉凶判断。

# Output Format (Strict Markdown):

## 1. 核心断语
用 3-5 句话直接给出总体结论：吉凶倾向、成败关键、行动方向。

## 2. 卦爻辞解读
解读本卦卦辞、彖辞及大衍筮法主看爻辞，说明当前处境与核心矛盾。

## 3. 象数分析
结合三层卦象演变（本卦/互卦/之卦）、世应关系、动爻变化、六亲六神、干支旺衰等，分析事态的内在逻辑。

## 4. 趋势与应期
说明后续发展趋势和可能的关键时间节点。

## 5. 决策建议
给出 3-5 条具体、可执行的行动建议，包括：
- 当前最应该做什么
- 需要防范的风险
- 可以把握的机会
- 若形势不利，如何应对

## 6. 一句话总结
用一句简短白话收束全卦，便于用户记住。""",
            "max_tokens": None,  # None表示不限制
            "timeout": 360.0,
            "max_retries": 3
        }

    def load_settings(self) -> Dict[str, Any]:
        """
        从配置文件加载AI设置

        Returns:
            Dict[str, Any]: AI设置字典
        """
        if self.config_path.exists():
            try:
                with self.config_path.open("r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # 始终使用代码中的默认提示词，仅合并用户配置参数
                settings = self.default_settings.copy()
                for k in ("base_url", "api_key", "model", "temperature",
                          "max_tokens", "timeout", "max_retries"):
                    if k in loaded:
                        settings[k] = loaded[k]
                return settings
            except (json.JSONDecodeError, IOError) as e:
                print(f"AI配置文件读取失败，使用默认设置: {e}")
                return self.default_settings.copy()
        return self.default_settings.copy()

    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证并清理AI设置

        Args:
            settings: 待验证的设置字典

        Returns:
            Dict[str, Any]: 验证后的设置字典
        """
        validated = {}

        # 验证base_url
        base_url = settings.get("base_url", "").strip()
        if base_url:
            if not (base_url.startswith("http://") or base_url.startswith("https://")):
                print("Base URL格式不正确，请以http://或https://开头")
            else:
                validated["base_url"] = base_url
        else:
            validated["base_url"] = ""

        # 验证api_key
        validated["api_key"] = settings.get("api_key", "").strip()

        # 验证model
        model = settings.get("model", "").strip() or "gpt-3.5-turbo"
        validated["model"] = model

        # 验证temperature
        temp_value = settings.get("temperature", 0.7)
        try:
            temperature = float(temp_value)
            # 限制在0-1范围内
            if temperature > 1.0:
                temperature = 1.0
            elif temperature < 0.0:
                temperature = 0.0
            validated["temperature"] = temperature
        except (ValueError, TypeError):
            print("温度值无效，使用默认值0.7")
            validated["temperature"] = 0.7

        # 验证提示词
        validated["system_prompt"] = settings.get("system_prompt", self.default_settings["system_prompt"]).strip()
        validated["user_prompt_template"] = settings.get("user_prompt_template", self.default_settings["user_prompt_template"]).strip()

        # 验证其他参数
        max_tokens = settings.get("max_tokens")
        if max_tokens is not None:
            try:
                validated["max_tokens"] = int(max_tokens) if max_tokens else None
            except (ValueError, TypeError):
                validated["max_tokens"] = None
        else:
            validated["max_tokens"] = None

        timeout = settings.get("timeout", 60.0)
        try:
            validated["timeout"] = float(timeout) if timeout else 60.0
        except (ValueError, TypeError):
            validated["timeout"] = 60.0

        max_retries = settings.get("max_retries", 3)
        try:
            validated["max_retries"] = int(max_retries) if max_retries else 3
        except (ValueError, TypeError):
            validated["max_retries"] = 3

        return validated

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        保存AI设置到配置文件

        Args:
            settings: 要保存的设置字典

        Returns:
            bool: 保存是否成功
        """
        try:
            # 验证设置
            validated_settings = self.validate_settings(settings)
            settings_to_save = {**self.default_settings, **validated_settings}

            with self.config_path.open("w", encoding="utf-8") as f:
                json.dump(settings_to_save, f, ensure_ascii=False, indent=2)
            return True
        except PermissionError:
            print("没有文件写入权限，请检查目录权限设置")
            return False
        except (IOError, TypeError) as e:
            print(f"AI配置保存失败: {e}")
            return False

    def call_llm_api(self, question: str, pan_result: str, settings: Optional[Dict[str, Any]] = None) -> str:
        """
        调用LLM API进行周易解读

        Args:
            question: 用户问题
            pan_result: 排盘结果文本
            settings: AI设置，如果不提供则从配置文件加载

        Returns:
            str: LLM解读结果

        Raises:
            ValueError: 当配置不完整时
            Exception: API调用失败时
        """
        if settings is None:
            settings = self.load_settings()

        api_key = settings.get("api_key", "").strip()
        if not api_key:
            raise ValueError("请先配置API Key")

        # 创建OpenAI客户端（base_url 兼容 /v1 后缀）
        client_kwargs = {"api_key": api_key}
        base_url = settings.get("base_url", "").strip()
        if base_url:
            base_url = base_url.rstrip("/")
            if not base_url.endswith("/v1"):
                base_url += "/v1"
            client_kwargs["base_url"] = base_url

        try:
            client = openai.OpenAI(**client_kwargs)
        except Exception as e:
            raise ValueError(f"OpenAI客户端创建失败: {e}")

        # 获取参数
        model = settings.get("model", "gpt-3.5-turbo")
        temperature = settings.get("temperature", 0.7)
        max_tokens = settings.get("max_tokens")
        system_prompt = settings.get("system_prompt", self.default_settings["system_prompt"])
        user_prompt_template = settings.get("user_prompt_template", self.default_settings["user_prompt_template"])

        # 构建用户提示词
        user_prompt = user_prompt_template.format(
            pan_result=pan_result,
            question=question
        )

        try:
            # 调用API
            api_kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature
            }

            # 只有在设置了max_tokens时才添加该参数
            if max_tokens is not None and max_tokens > 0:
                api_kwargs["max_tokens"] = max_tokens

            response = client.chat.completions.create(**api_kwargs)

            if response.choices and len(response.choices) > 0:
                message_content = response.choices[0].message.content
                if message_content:
                    return message_content.strip()
                else:
                    return ""
            else:
                raise ValueError("API返回结果为空")

        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                raise Exception("API请求超时，请检查网络连接或稍后重试")
            elif "authentication" in error_msg or "unauthorized" in error_msg:
                raise Exception("API认证失败，请检查API Key是否正确")
            elif "rate" in error_msg and "limit" in error_msg:
                raise Exception("API调用频率过高，请稍后重试")
            elif "connection" in error_msg:
                raise Exception("网络连接失败，请检查网络设置")
            else:
                raise Exception(f"LLM API调用失败: {e}")

    def get_default_settings(self) -> Dict[str, Any]:
        """
        获取默认设置

        Returns:
            Dict[str, Any]: 默认设置字典
        """
        return self.default_settings.copy()

    def get_custom_prompt_templates(self) -> Dict[str, Dict[str, str]]:
        """
        获取预定义的提示词模板（当前仅使用默认六爻专业模板）

        Returns:
            Dict[str, Dict[str, str]]: 空字典，因为不再使用模板选择
        """
        return {}