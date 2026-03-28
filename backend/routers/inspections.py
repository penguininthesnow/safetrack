from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_ # 年度統計 #紀錄編號
from backend.database import get_db
from backend.models import Inspection # 巡檢紀錄表
from backend import models, schemas
from backend.auth import get_current_user
from backend.services.s3 import upload_to_s3
from backend.utils.line_message import send_line_message
from datetime import date #紀錄編號
import time



router = APIRouter(prefix="/api/inspections", tags=["inspections"])

# 建立巡檢紀錄 #加入紀錄編號
@router.post("/", response_model=schemas.InspectionOut)
async def create_inspection(
    background_tasks: BackgroundTasks,
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
    start_total = time.time()

    # 1. 生成年份與巡檢編號
    t1 = time.time()
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

    print("編號產生耗時:", time.time() - t1)


    # 2. 上傳 s3
    t2 = time.time()

    image_urls = []
    image_url_string = None

    # 存照片並上傳到s3
    for file in files:
        if file and file.filename:
            try:
                image_url = upload_to_s3(file)
                image_urls.append(image_url)
            except Exception as e:
                print("S3 上傳失敗", e)

    image_url_string = ",".join(image_urls) if image_urls else None
    print("s3 上傳耗時:", time.time() - t2)


    # # 將多張照片時存成字串
    # if image_urls:
    #     image_url_string = ",".join(image_urls)

    # 3. 寫入 DB
    t3 = time.time()

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

    print("DB commit 耗時:", time.time() - t3)

    # 4. 背景送 LINE
    t4 = time.time()  
        
    # LINE Notify 異常提醒
    if new_inspection.is_abnormal:
        setting = db.query(models.NotificationSetting).first()

        print("new_inspection.is_abnormal =", new_inspection.is_abnormal)
        print("setting =", setting)

        if setting:
            print("setting.is_enabled =", setting.is_enabled)
            print("setting.notify_abnormal =", setting.notify_abnormal)
            print("setting.line_group_id =", setting.line_group_id)

        if setting and setting.is_enabled and setting.notify_abnormal and setting.line_group_id:
            inspection_url = f"https://penguinthesnow.com/inspection-detail.html?number={new_inspection.inspection_number}"

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

            print("準備送 LINE")
            print("LINE group id =", setting.line_group_id)
            print("LINE image_url =", new_inspection.image_url)

            background_tasks.add_task(
                send_line_message,
                message=message,
                image_url=new_inspection.image_url.split(",") if new_inspection.image_url else [],
                to_id=setting.line_group_id
            )
            print("LINE 背景任務已加入")
        else:
            print("未發送 LINE：通知設定未開啟、未勾選異常通知，或 line_group_id 為空")
    else:
        print("此筆為正常紀錄，不發送 LINE")
    
    print("加入背景任務耗時:", time.time() - t4)
    print("API 總耗時:", time.time() - start_total)

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
    abnormal = db.query(models.Inspection).filter(
        models.Inspection.year == year,
        models.Inspection.is_abnormal == True
    ).count()

    normal = db.query(models.Inspection).filter(
        models.Inspection.year == year,
        models.Inspection.is_abnormal == False
    ).count()

    return {
        "year": year,
        "normal": normal,
        "abnormal": abnormal
    }


# 主畫面
# 查詢歷史巡檢紀錄 (支援篩選)
@router.get("/", response_model=list[schemas.InspectionOut])
def get_inspections(
    year: Optional[int] = None,
    location: Optional[str] = None,
    item: Optional[str] = None,
    is_abnormal: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Inspection)

    if year:
        query = query.filter(models.Inspection.year == year)
    if location:
        query = query.filter(models.Inspection.location.contains(location))
    if item:
        query = query.filter(models.Inspection.item.contains(item))
    if is_abnormal is not None:
        query = query.filter(models.Inspection.is_abnormal == is_abnormal)
    return query.order_by(models.Inspection.date.desc()).all()


# 會員頁面
@router.get("/member", response_model=list[schemas.InspectionOut])
def get_my_inspections(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Inspection).filter(models.Inspection.created_by == current_user.id).all()


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


# GET 異常通知頁面 + 修改資料頁面
@router.get("/{inspection_id}", response_model=schemas.InspectionOut)
def get_inspection_by_id(
    inspection_id: int, 
    db: Session = Depends(get_db),
):
    inspection = db.query(models.Inspection).filter(models.Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection

# PUT /api/inspections/{id}
@router.put("/{inspection_id}", response_model=schemas.InspectionOut)
def update_inspection(
    inspection_id: int,
    location: str = Form(...),
    item: str = Form(...),
    description: str = Form(...),
    is_abnormal: bool = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    inspection = db.query(models.Inspection).filter(models.Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.created_by !=current_user.id and current_user.role !="admin":
        raise HTTPException(status_code=403, detail="無權限修改此紀錄!")

    inspection.location = location
    inspection.item = item
    inspection.description = description
    inspection.is_abnormal = is_abnormal

    db.commit()
    db.refresh(inspection)

    # LINE_Notify 異常提醒(更新後若變成異常)
    # Line Message API 設定
    # 先讀資料庫設定，再決定要不要送通知
    if inspection.is_abnormal is True:
        setting = db.query(models.NotificationSetting).first()

        print("inspection.is_abnormal =", inspection.is_abnormal)
        print("setting =", setting)

        if setting and setting.is_enabled and setting.notify_abnormal and setting.line_group_id:
            message = f"""
    Safetrack 巡檢異常!
    巡檢編號: {inspection.inspection_number}
    地點: {inspection.location}
    項目: {inspection.item}
    日期: {inspection.date}

    請立即改善/處理~
    """
            send_line_message(
                message=message,
                image_url=inspection.image_url,
                to_id=setting.line_group_id
            )

    return inspection


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



# 測試用
# @router.get("/test")
# def test(db: Session = Depends(get_db)):
#     inspections = db.query(models.Inspection).all()
#     return inspections