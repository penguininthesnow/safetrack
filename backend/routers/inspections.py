from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_ # 年度統計 #紀錄編號
from backend.database import get_db
from backend.models import Inspection # 巡檢紀錄表
from backend import models, schemas
from backend.auth import get_current_user
from backend.services.s3 import upload_to_s3
from backend.utils.line_message import send_line_message
from datetime import date, datetime #紀錄編號
import shutil
import os
import time
import uuid



router = APIRouter(prefix="/api/inspections", tags=["inspections"])

# 建立巡檢紀錄 #加入紀錄編號
@router.post("/", response_model=schemas.InspectionOut)
async def create_inspection(
    date_value: date = Form(...),
    location: str = Form(...),
    item: str = Form(...),
    description: str = Form(...),
    is_abnormal: bool = Form(...),
    abnormal_count: int = Form(0),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # 自動抓年份、動態生成
    year = date_value.year

    #日期字串
    date_str = date_value.strftime("%Y%m%d")
    # 狀態碼
    status_code = "2" if is_abnormal else "1"

    # 查詢今天同狀態已有幾筆
    count_today = db.query(models.Inspection).filter(
        and_(
            models.Inspection.date ==date_value,
            models.Inspection.is_abnormal == is_abnormal
        )
    ).count()
    # 流水號固定4碼
    sequence = str(count_today + 1).zfill(4)
    
    # 最終巡檢編號
    inspection_number = f"{date_str}{status_code}{sequence}"

    # 避免同一時間，兩個人同時送出紀錄
    while db.query(models.Inspection).filter(
        models.Inspection.inspection_number == inspection_number
    ).first():
        count_today += 1
        sequence = str(count_today + 1).zfill(4)
        inspection_number = f"{date_str}{status_code}{sequence}"

    image_urls = []

    # 存照片並上傳到s3
    for file in files:
        if file:
            try:
                image_url = upload_to_s3(file)
                image_urls.append(image_url)
            except Exception as e:
                print("S3 上傳失敗", e)

            # 將多張照片時存成字串
            image_url_string = ",".join(image_urls)

    new_inspection = models.Inspection(
        year = year,
        date=date_value,
        location=location,
        item=item,
        description=description,
        is_abnormal=is_abnormal,
        abnormal_count=abnormal_count,
        image_url=image_url_string,
        created_by=current_user.id,
        inspection_number=inspection_number,
    )

    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)
        
        
    # LINE Notify 異常提醒
    if new_inspection.is_abnormal:
        inspection_url = f"https://penguinthesnow.com/inspection-history?number={new_inspection.inspection_number}"
        # inspection_url = f"http://127.0.0.1:8000/static/inspection-history?number={new_inspection.inspection_number}"

        message = f"""
        Safetrack 巡檢異常!
        巡檢編號: {new_inspection.inspection_number}
        地點: {new_inspection.location}
        項目: {new_inspection.item}
        日期: {new_inspection.date}

        請立即改善/處理~
        查看完整記錄:
        {inspection_url}
        """
        send_line_message(message, new_inspection.image_url)

    return new_inspection

# 動態新增年份
@router.get("/years")
def get_years(db: Session = Depends(get_db)):
    years = db.query(models.Inspection.year)\
        .distinct()\
        .order_by(models.Inspection.year.desc())\
        .all()

    return [y[0] for y in years]

# 年度查詢
@router.get("/year/{year}", response_model=list[schemas.InspectionOut])
def get_by_year(
    year: int,
    db: Session = Depends(get_db),
):
    return db.query(models.Inspection).filter(
        models.Inspection.year == year
    ).all()

# 新增年度統計 API
@router.get("/year/{year}/stats")
def get_year_stats(
    year: int,
    db: Session = Depends(get_db),
):
    total_abnormal = db.query(
        func.sum(models.Inspection.abnormal_count)
    ).filter(
        models.Inspection.year == year
    ).scalar()

    return {
        "year": year,
        "total_abnormal": total_abnormal or 0
    }



# 主畫面
@router.get("/", response_model=list[schemas.InspectionOut])
def get_all_inspections(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return db.query(models.Inspection).offset(skip).limit(limit).all()

# 會員頁面
@router.get("/member", response_model=list[schemas.InspectionOut])
def get_my_inspections(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Inspection).filter(models.Inspection.created_by == current_user.id).all()


# GET 異常通知頁面
@router.get("/{inspection_id}", response_model=schemas.InspectionOut)
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    inspection = db.query(models.Inspection).filter(models.Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection

# PUT
@router.put("/{inspection_id}", response_model=schemas.InspectionOut)
def update_inspection(
    inspection_id: int,
    update_data: schemas.InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    inspection = db.query(models.Inspection).filter(models.Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.created_by !=current_user.id and current_user.role !="admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(inspection, field, value)

    db.commit()
    db.refresh(inspection)

    # LINE_Notify 異常提醒(更新後若變成異常)
    # Line Message API 設定
    if inspection.is_abnormal == True:

        message = f"""
    Safetrack 巡檢異常!
    巡檢編號: {inspection.inspection_number}
    地點: {inspection.location}
    項目: {inspection.item}
    日期: {inspection.date}

    請立即改善/處理~
    """
        send_line_message(message, inspection.image_url)



@router.delete("/{inspection_id}")
def delete_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    inspection = db.query(models.Inspection).filter(models.Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.created_by !=current_user.id and current_user.role !="admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    
    db.delete(inspection)
    db.commit()
    return {"detail": "Inspection deleted successfully"}


# 巡檢紀錄查詢介面
@router.get(
        "/number/{inspection_number}", 
        response_model=schemas.InspectionOut
)
def get_inspection_by_number(
    inspection_number: str,
    db: Session = Depends(get_db)
):
    inspection = db.query(models.Inspection).filter(
        models.Inspection.inspection_number == inspection_number
    ).first()

    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found!")
    return inspection

# 測試用
@router.get("/test")
def test(db: Session = Depends(get_db)):
    inspections = db.query(models.Inspection).all()
    return inspections