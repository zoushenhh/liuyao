import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from ai_module import AIInterpretationModule


def interpret(question: str, pan_result: str, settings: dict) -> str:
    module = AIInterpretationModule()
    return module.call_llm_api(
        question=question,
        pan_result=pan_result,
        settings=settings,
    )


def validate_api_key(base_url: str, api_key: str, model: str) -> tuple[bool, str]:
    try:
        settings = {
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
            "temperature": 0.1,
            "system_prompt": "Reply with exactly the word: OK",
            "user_prompt_template": "test",
            "max_tokens": 5,
            "timeout": 15.0,
            "max_retries": 1,
        }
        result = interpret(question="test", pan_result="test", settings=settings)
        ok = "OK" in result
        return ok, "API Key 可用" if ok else f"响应异常: {result[:100]}"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"API Key 验证失败: {e}"
