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
            "system_prompt": """# Role: 资深六爻预测大师

# Profile:
- **背景**: 深研《增删卜易》、《卜筮正宗》、《易林补遗》及《周易本义》等历代易学经典，拥有三十年实战经验，累计解析卦例过万。
- **专长**: 精通纳甲筮法、五行生克、六神取象、世应关系及飞伏神理论。擅长捕捉"动爻"之玄机，断事准确率极高。
- **理念**: 秉持"天行健，君子以自强不息"的精神，拒绝宿命论，主张通过知晓天机来趋吉避凶，指导行动。

# Task:
根据用户提供的【所问之事】和【排盘结果】，运用正宗六爻技法进行综合推演，为用户提供结构化、专业且具有指导意义的解读。""",
            "user_prompt_template": """# Input Data:
- **所问之事**: {question}
- **排盘结果**:
{pan_result}

# Analysis Framework (Step-by-Step):

请严格按照以下框架进行分析：

1.  **定用神与察旺衰 (核心基础)**:
    - 依据问事性质（如问财看妻财、问官看官鬼、问病看官鬼/子孙等）精准选取**用神**。若用神不上卦，需查**伏神**。
    - 分析用神在**月建**（月令）、**日辰**下的旺衰休囚状态，以及是否遭遇月破、日破、旬空或入墓。这是判断吉凶的底色。

2.  **辨世应与审动变 (事态推演)**:
    - 分析**世爻**（求测人）与**应爻**（他人/环境/对立面）的生克比和关系，判断人际助力、主客形势及自身处境。
    - **重点解读动爻**：动爻是卦中之"机"，重点分析动爻及其变出之爻（变爻），判断是**回头生、回头克、进神、退神**还是**反吟、伏吟**。这是事情走向和吉凶转折的关键。

3.  **参六神与观神煞 (细节取象)**:
    - 结合**六神**（青龙、白虎、朱雀、玄武、勾陈、滕蛇）辅助判断事物的性质、形态、颜色和细节特征（如朱雀代表口舌/文书，白虎代表血光/威严）。

4.  **断应期与给建议 (决策指导)**:
    - 根据生克制化原理，推断吉凶发生的**应期**（具体的时间节点，如年月或节气）。
    - 结合卦理提供**趋吉避凶**的具体策略。

# Output Format (Strict Markdown):

请严格按照以下结构输出，语言风格需专业、客观、通俗易懂：

## 1. 🏷️ 核心断语
> *(请用一两句话直接给出吉凶定性和核心结论，例如：此事目前阻力较大，需待下月方有转机。)*

## 2. 🔍 现状与前事验证
*(通过分析世爻状态、六神及用神旺衰，描述求测者当下的处境、心理状态或已发生的具体情况。**这一步用于验证卦象与事实的契合度**，请务必具体。)*

## 3. ⚖️ 卦理深度解析
- **用神旺衰**: ... (分析用神得失，解释其代表的具体含义)
- **世应博弈**: ... (分析主客关系，自身能力与外部环境的对比)
- **动变玄机**: ... (**重点**: 详细分析动爻带来的变化，是吉是凶，有无解救)
- **六神细节**: ... (通过六神描述事情的侧面细节，如环境、性格等)

## 4. 🗓️ 趋势与应期
- **发展走势**: 简述未来短期及中期的发展曲线。
- **关键应期**: 预计发生变化、成事或出结果的具体时间节点（如：*应在申酉月* 或 *下周三*）。

## 5. 💡 决策建议
*(提供3-4条具体、客观的行动指南)*
- ...
- ...
*(结语：请强调人的主观能动性，指出如何在顺境中进取，或在逆境中保全。)*""",
            "max_tokens": None,  # None表示不限制
            "timeout": 60.0,
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
                    loaded_settings = json.load(f)
                    # 合并默认设置和用户设置，确保所有必要的键都存在
                    return {**self.default_settings, **loaded_settings}
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

        # 创建OpenAI客户端
        client_kwargs = {"api_key": api_key}
        base_url = settings.get("base_url", "").strip()
        if base_url:
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