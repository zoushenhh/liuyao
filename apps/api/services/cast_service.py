import sys
import uuid
from pathlib import Path

root = Path(__file__).resolve().parents[3]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from ichingshifa import ichingshifa


def generate_cast(date: str, time_str: str, yao_code: str, question: str) -> dict:
    y, m, d = map(int, date.split("-"))
    h, minute = map(int, time_str.split(":"))

    pan_result = ichingshifa.Iching().display_pan_m(y, m, d, h, minute, yao_code)

    return {
        "cast_id": uuid.uuid4().hex[:12],
        "date": date,
        "time": time_str,
        "yao_code": yao_code,
        "question": question,
        "pan_result": str(pan_result),
    }
