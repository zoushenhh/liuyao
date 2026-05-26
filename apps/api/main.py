import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from apps.api.schemas import (
    CastRequest,
    CastResponse,
    InterpretRequest,
    InterpretResponse,
    ValidateKeyRequest,
    ValidateKeyResponse,
    TextsResponse,
    TextContentResponse,
)
from apps.api.services.cast_service import generate_cast
from apps.api.services.ai_service import interpret, validate_api_key
from apps.api.services.text_service import list_texts, get_text
from apps.api.security import validate_base_url, check_rate_limit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("liuyao-api")

app = FastAPI(title="坚六爻 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/cast", response_model=CastResponse)
def api_cast(req: CastRequest):
    try:
        return generate_cast(req.date, req.time, req.yao_code, req.question)
    except Exception as e:
        logger.exception("Cast generation failed")
        raise HTTPException(status_code=500, detail="排盘生成失败，请稍后重试")


@app.post("/api/interpret", response_model=InterpretResponse)
def api_interpret(req: InterpretRequest):
    if not check_rate_limit():
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")

    try:
        validate_base_url(req.settings.base_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        content = interpret(
            question=req.question,
            pan_result=req.pan_result,
            settings=req.settings.model_dump(),
        )
        return InterpretResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("AI interpretation failed")
        raise HTTPException(status_code=500, detail="AI 解读失败，请稍后重试")


@app.post("/api/validate-api-key", response_model=ValidateKeyResponse)
def api_validate_key(req: ValidateKeyRequest):
    try:
        validate_base_url(req.base_url)
    except ValueError as e:
        return ValidateKeyResponse(valid=False, message=str(e))

    try:
        valid, message = validate_api_key(req.base_url, req.api_key, req.model)
        return ValidateKeyResponse(valid=valid, message=message)
    except Exception as e:
        return ValidateKeyResponse(valid=False, message=str(e))


@app.get("/api/texts", response_model=TextsResponse)
def api_texts():
    return TextsResponse(texts=list_texts())


@app.get("/api/texts/{name}", response_model=TextContentResponse)
def api_text(name: str):
    result = get_text(name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"文档 {name} 不存在")
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
