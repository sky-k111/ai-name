"""取名相关路由 — 难度2：JWT 鉴权 + 历史记录."""
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.naming_history import NamingHistory
from app.models.user import User
from app.services.naming_service import NamingService
from app.services.payment_service import check_and_deduct
from app.utils.deepseek import DeepSeekError

router = APIRouter()
_service = NamingService()


# ── Request/Response Models ──────────────────────────────────


class GenerateRequest(BaseModel):
    surname: str = Field(..., min_length=1, max_length=5, description="姓氏")
    gender: str = Field(..., pattern="^(male|female)$", description="性别")
    birthday: str | None = Field(None, description="出生日期 YYYY-MM-DD")
    birth_time: str | None = Field(None, max_length=10, description="出生时辰")
    style: str | None = Field(None, max_length=50, description="期望风格")
    expectations: str | None = Field(None, max_length=200, description="其他期望")


class NameItem(BaseModel):
    full_name: str
    meaning: str
    wuxing: str
    source: str


class GenerateResponse(BaseModel):
    conversation_id: str
    names: list[NameItem]


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class RefineRequest(BaseModel):
    conversation_id: str | None = Field(None, description="会话 ID")
    original_request: GenerateRequest
    history: list[ChatMessage] = Field(default_factory=list)
    feedback: str = Field(..., min_length=1, max_length=500, description="反馈意见")


class RefineResponse(BaseModel):
    names: list[NameItem]


class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    code: str


class HistoryItem(BaseModel):
    id: int
    surname: str
    gender: str
    names: list[NameItem]
    record_type: str
    created_at: str


class HistoryListResponse(BaseModel):
    total: int
    items: list[HistoryItem]


# ── Helpers ──────────────────────────────────────────────────


def _save_history(
    db: Session,
    user_id: int,
    request: GenerateRequest,
    result: dict,
    feedback_json: str | None = None,
) -> NamingHistory:
    """保存取名记录到数据库."""
    record = NamingHistory(
        user_id=user_id,
        surname=request.surname,
        gender=request.gender,
        birthday=request.birthday,
        birth_time=request.birth_time,
        style=request.style,
        expectations=request.expectations,
        result_json=json.dumps(result.get("names", []), ensure_ascii=False),
        feedback=feedback_json,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── Routes ───────────────────────────────────────────────────


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="首次生成名字（需登录）",
)
async def generate_names(
    request: GenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据用户需求首次生成名字，自动保存历史."""
    try:
        result = await _service.generate(request.model_dump())
    except DeepSeekError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": True, "message": str(e), "code": "LLM_ERROR"},
        )
    _save_history(db, user.id, request, result)
    return result


@router.post(
    "/refine",
    response_model=RefineResponse,
    summary="微调名字（需登录）",
)
async def refine_names(
    request: RefineRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """根据用户反馈微调名字，自动保存历史."""
    try:
        result = await _service.refine(
            original_request=request.original_request.model_dump(),
            history=[msg.model_dump() for msg in request.history],
            feedback=request.feedback,
        )
    except DeepSeekError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": True, "message": str(e), "code": "LLM_ERROR"},
        )
    # 保存历史，附带完整微调对话 JSON（包含当前 feedback）
    full_history = [msg.model_dump() for msg in request.history]
    full_history.append({"role": "user", "content": request.feedback})
    history_json = json.dumps(full_history, ensure_ascii=False)
    _save_history(db, user.id, request.original_request, result, feedback_json=history_json)
    return result


@router.get(
    "/history",
    response_model=HistoryListResponse,
    summary="取名历史列表（需登录）",
)
async def history_list(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    record_type: str | None = None,
):
    """获取当前用户的取名历史（不含已删除），支持类型筛选，按时间倒序."""
    filters = [NamingHistory.user_id == user.id, NamingHistory.is_deleted == False]
    if record_type:
        filters.append(NamingHistory.record_type == record_type)
    query = (
        db.query(NamingHistory)
        .filter(*filters)
        .order_by(NamingHistory.created_at.desc())
    )
    total = query.count()
    records = query.offset(skip).limit(limit).all()

    items = []
    for r in records:
        try:
            raw_names = json.loads(r.result_json)
        except (json.JSONDecodeError, TypeError):
            raw_names = []
        # 对比记录格式不同，转换一下
        if r.record_type == "compare" and isinstance(raw_names, list):
            names = [NameItem(full_name=n.get("full_name",""), meaning=n.get("summary",""), wuxing="", source="") for n in raw_names]
        else:
            names = raw_names if isinstance(raw_names, list) else []
        items.append(
            HistoryItem(
                id=r.id,
                surname=r.surname,
                gender=r.gender,
                names=names,
                record_type=r.record_type or "naming",
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
        )
    return {"total": total, "items": items}


@router.get(
    "/history/{history_id}",
    response_model=HistoryItem,
    summary="取名历史详情（需登录）",
)
async def history_detail(
    history_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查看某条取名历史的详细信息."""
    record = (
        db.query(NamingHistory)
        .filter(NamingHistory.id == history_id, NamingHistory.user_id == user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    try:
        raw_names = json.loads(record.result_json)
    except (json.JSONDecodeError, TypeError):
        raw_names = []
    if record.record_type == "compare" and isinstance(raw_names, list):
        names = [NameItem(full_name=n.get("full_name",""), meaning=n.get("summary",""), wuxing="", source="") for n in raw_names]
    else:
        names = raw_names if isinstance(raw_names, list) else []
    return HistoryItem(
        id=record.id,
        surname=record.surname,
        gender=record.gender,
        names=names,
        record_type=record.record_type or "naming",
        created_at=record.created_at.isoformat() if record.created_at else "",
    )


class AnalyzeRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=10, description="要分析的名字")
    gender: str = Field(default="male", pattern="^(male|female)$", description="性别")


@router.post("/analyze", summary="分析名字（需登录）")
async def analyze_name(
    request: AnalyzeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 分析已有名字的寓意、五行、评分，并保存历史."""
    try:
        result = await _service.analyze(request.full_name, request.gender)
    except DeepSeekError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail={"error": True, "message": str(e), "code": "LLM_ERROR"},
        )
    # 保存分析历史
    record = NamingHistory(
        user_id=user.id,
        surname=request.full_name,
        gender=request.gender,
        result_json=json.dumps([{"full_name": request.full_name, **result}], ensure_ascii=False),
        record_type="analyze",
    )
    db.add(record)
    db.commit()
    return result


@router.delete("/history", summary="一键清空所有取名历史")
async def clear_all_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """软删除当前用户的所有取名记录."""
    updated = (
        db.query(NamingHistory)
        .filter(NamingHistory.user_id == user.id, NamingHistory.is_deleted == False)
        .update({"is_deleted": True}, synchronize_session=False)
    )
    db.commit()
    return {"message": f"已清空 {updated} 条记录", "deleted_count": updated}


class CompareRequest(BaseModel):
    names: list[str] = Field(..., min_length=2, max_length=5, description="要对比的名字列表")
    gender: str = Field(default="male", pattern="^(male|female)$")


class PremiumRequest(BaseModel):
    surname: str = Field(..., min_length=1, max_length=5)
    gender: str = Field(..., pattern="^(male|female)$")
    birthday: str | None = None
    birth_time: str | None = None
    style: str | None = None
    expectations: str | None = None


@router.post("/compare", summary="名字对比（付费）")
async def compare_names(
    request: CompareRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 横向对比多个名字，1元/次."""
    check = check_and_deduct(db, user, "compare")
    if not check["allowed"]:
        raise HTTPException(
            status_code=402,
            detail={"error": True, "message": f"余额不足（需{check.get('price',1)}元，余额{check.get('balance',0)}元）", "code": "INSUFFICIENT_BALANCE"},
        )
    try:
        result = await _service.compare(request.names, request.gender)
    except DeepSeekError as e:
        raise HTTPException(status_code=e.status_code or 500, detail={"error": True, "message": str(e), "code": "LLM_ERROR"})
    # 保存历史
    names_str = " vs ".join(request.names)
    _save_compare_history(db, user.id, names_str, request.gender, result)
    return result


@router.post("/premium", summary="精品取名（付费）")
async def premium_naming(
    request: PremiumRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI 精品取名（含八字/音律/字形/重名），2元/次."""
    check = check_and_deduct(db, user, "premium")
    if not check["allowed"]:
        raise HTTPException(
            status_code=402,
            detail={"error": True, "message": f"余额不足（需{check.get('price',2)}元，余额{check.get('balance',0)}元）", "code": "INSUFFICIENT_BALANCE"},
        )
    try:
        result = await _service.premium(request.model_dump())
    except DeepSeekError as e:
        raise HTTPException(status_code=e.status_code or 500, detail={"error": True, "message": str(e), "code": "LLM_ERROR"})
    _save_history(db, user.id, request, result)
    return result


def _save_compare_history(db: Session, user_id: int, names_str: str, gender: str, result: dict):
    record = NamingHistory(
        user_id=user_id,
        surname=names_str,
        gender=gender,
        result_json=json.dumps(result.get("rankings", []), ensure_ascii=False),
        record_type="compare",
    )
    db.add(record)
    db.commit()


class BatchDeleteRequest(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=100, description="要删除的记录 ID 列表")


@router.delete(
    "/history/{history_id}",
    summary="删除单条取名历史（软删除）",
)
async def delete_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """软删除自己的某条取名记录."""
    record = (
        db.query(NamingHistory)
        .filter(NamingHistory.id == history_id, NamingHistory.user_id == user.id, NamingHistory.is_deleted == False)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在或已删除")
    record.is_deleted = True
    db.commit()
    return {"message": "已删除"}


@router.post(
    "/history/batch-delete",
    summary="批量删除取名历史（软删除）",
)
async def batch_delete_history(
    request: BatchDeleteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批量软删除自己的取名记录."""
    updated = (
        db.query(NamingHistory)
        .filter(
            NamingHistory.id.in_(request.ids),
            NamingHistory.user_id == user.id,
            NamingHistory.is_deleted == False,
        )
        .update({"is_deleted": True}, synchronize_session=False)
    )
    db.commit()
    return {"message": f"已删除 {updated} 条记录", "deleted_count": updated}
