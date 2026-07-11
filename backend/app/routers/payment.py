"""付费路由."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.services import payment_service
from app.config import ENABLE_DEMO_RECHARGE

router = APIRouter(prefix="/api/payment", tags=["payment"])


class RechargeRequest(BaseModel):
    amount: float = Field(..., description="充值金额")


class BuyVipRequest(BaseModel):
    level: str = Field(..., pattern="^(vip|svip)$", description="VIP等级")


@router.get("/balance", summary="余额+VIP信息")
async def get_balance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取余额、会员状态、今日免费次数."""
    return payment_service.get_balance_info(db, user)


@router.post("/recharge", summary="充值")
async def recharge(
    request: RechargeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """模拟充值."""
    if not ENABLE_DEMO_RECHARGE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="充值功能未在当前环境启用")
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于0")
    new_balance = payment_service.recharge(db, user, request.amount)
    return {"message": f"充值成功", "balance": new_balance}


@router.post("/buy-vip", summary="购买VIP")
async def buy_vip(
    request: BuyVipRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """购买VIP会员."""
    try:
        result = payment_service.buy_vip(db, user, request.level)
        return {"message": f"购买{request.level.upper()}成功", **result}
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))


@router.get("/transactions", summary="交易记录")
async def get_transactions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """交易记录列表."""
    query = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
    )
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    items = [
        {
            "id": r.id,
            "amount": r.amount,
            "type": r.type,
            "detail": r.detail,
            "balance_after": r.balance_after,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in records
    ]
    return {"total": total, "items": items}
