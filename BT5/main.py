import uvicorn
from fastapi import FastAPI, status, HTTPException, Depends, Request
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MedicalDeviceModel(Base):
    __tablename__ = "medical_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_code = Column(String(50), unique=True, nullable=False, index=True)
    device_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    status = Column(String(50), default='ACTIVE', nullable=False)

class LearningDocumentModel(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_url = Column(String(500), nullable=False)

class DiscountModel(Base):
    __tablename__ = "discounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Bài Tập Tổng Hợp Session 12")

class APIStandardResponse(BaseModel):
    statusCode: int
    message: str
    error: Optional[str] = None
    data: Optional[dict] = None
    path: str
    timestamp: str

class APIListStandardResponse(BaseModel):
    statusCode: int
    message: str
    error: Optional[str] = None
    data: List[dict]
    path: str
    timestamp: str

class MedicalDeviceCreate(BaseModel):
    device_code: str = Field(..., min_length=1)
    device_name: str = Field(..., min_length=3)
    department: str = Field(..., min_length=1)
    status: Literal['ACTIVE', 'INACTIVE'] = 'ACTIVE'

class DocumentCreate(BaseModel):
    title: str
    subject: str
    document_type: str
    file_url: str

class DocumentResponse(BaseModel):
    id: int
    title: str
    subject: str
    document_type: str
    file_url: str

@app.post("/devices", status_code=status.HTTP_201_CREATED, response_model=APIStandardResponse)
async def add_medical_device(request: Request, payload: MedicalDeviceCreate, db: Session = Depends(get_db)):
    existing = db.query(MedicalDeviceModel).filter(MedicalDeviceModel.device_code == payload.device_code.strip()).first()
    if existing:
        return APIStandardResponse(statusCode=400, message="Mã thiết bị y tế này đã tồn tại trên hệ thống", error="Bad Request", data=None, path=str(request.url.path), timestamp=datetime.utcnow().isoformat() + "Z")
    try:
        res = MedicalDeviceModel(device_code=payload.device_code.strip(), device_name=payload.device_name.strip(), department=payload.department.strip(), status=payload.status)
        db.add(res)
        db.commit()
        db.refresh(res)
        return APIStandardResponse(statusCode=201, message="Thêm thiết bị y tế thành công", data={"id": res.id, "device_code": res.device_code, "device_name": res.device_name, "department": res.department, "status": res.status}, path=str(request.url.path), timestamp=datetime.utcnow().isoformat() + "Z")
    except Exception as e:
        db.rollback()
        return APIStandardResponse(statusCode=500, message="Lỗi hệ thống", error=str(e), path=str(request.url.path), timestamp=datetime.utcnow().isoformat() + "Z")

@app.get("/devices", status_code=status.HTTP_200_OK, response_model=APIListStandardResponse)
async def list_medical_devices(request: Request, db: Session = Depends(get_db)):
    devices = db.query(MedicalDeviceModel).all()
    data_list = [{"id": d.id, "device_code": d.device_code, "device_name": d.device_name, "department": d.department, "status": d.status} for d in devices]
    return APIListStandardResponse(statusCode=200, message="Lấy danh sách thiết bị y tế thành công", data=data_list, path=str(request.url.path), timestamp=datetime.utcnow().isoformat() + "Z")

@app.get("/devices/{device_id}", status_code=status.HTTP_200_OK, response_model=APIStandardResponse)
async def detail_medical_device(device_id: int, request: Request, db: Session = Depends(get_db)):
    device = db.query(MedicalDeviceModel).filter(MedicalDeviceModel.id == device_id).first()
    if not device:
        return APIStandardResponse(statusCode=404, message="Device not found", error="Not Found", data=None, path=str(request.url.path), timestamp=datetime.utcnow().isoformat() + "Z")
    return APIStandardResponse(statusCode=200, message="Lấy thông tin chi tiết thiết bị thành công", data={"id": device.id, "device_code": device.device_code, "device_name": device.device_name, "department": device.department, "status": device.status}, path=str(request.url.path), timestamp=datetime.utcnow().isoformat() + "Z")

@app.get("/documents", status_code=status.HTTP_200_OK, response_model=List[DocumentResponse])
async def get_documents(db: Session = Depends(get_db)):
    res = db.query(LearningDocumentModel).all()
    return [DocumentResponse(id=d.id, title=d.title, subject=d.subject, document_type=d.document_type, file_url=d.file_url) for d in res]

@app.post("/documents", status_code=status.HTTP_201_CREATED, response_model=DocumentResponse)
async def add_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    try:
        d = LearningDocumentModel(title=payload.title.strip(), subject=payload.subject.strip(), document_type=payload.document_type.strip(), file_url=payload.file_url.strip())
        db.add(d)
        db.commit()
        db.refresh(d)
        return DocumentResponse(id=d.id, title=d.title, subject=d.subject, document_type=d.document_type, file_url=d.file_url)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}", status_code=status.HTTP_200_OK)
async def remove_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(LearningDocumentModel).filter(LearningDocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Tài liệu học tập không tồn tại")
    try:
        db.delete(doc)
        db.commit()
        return {"message": "Xóa tài liệu học tập thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/discounts/{discount_id}", status_code=status.HTTP_200_OK)
async def delete_discount_endpoint(discount_id: int, db: Session = Depends(get_db)):
    discount = db.query(DiscountModel).filter(DiscountModel.id == discount_id, DiscountModel.is_deleted == False).first()
    if not discount:
        raise HTTPException(status_code=404, detail="Mã giảm giá không tồn tại hoặc đã bị xóa trước đó")
    try:
        discount.is_deleted = True
        discount.deleted_at = datetime.utcnow()
        db.commit()
        return {"status": "success", "message": f"Xóa mềm mã giảm giá ID {discount_id} thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/init-discount-data", status_code=status.HTTP_201_CREATED)
async def init_discount_data(db: Session = Depends(get_db)):
    if db.query(DiscountModel).count() == 0:
        d1 = DiscountModel(code="KHOAHOC2026", amount=50000)
        d2 = DiscountModel(code="GIAMGIASOC", amount=100000)
        db.add_all([d1, d2])
        db.commit()
    return {"message": "Khởi tạo dữ liệu thành công!"}