from sqlalchemy.orm import Session
from BT6.model import SmartHomePlanModel, MedicalDeviceModel, LearningDocumentModel, DiscountModel
from datetime import datetime

def get_plan_by_code(db: Session, plan_code: str):
    return db.query(SmartHomePlanModel).filter(SmartHomePlanModel.plan_code == plan_code).first()

def get_plan_by_id(db: Session, plan_id: int):
    return db.query(SmartHomePlanModel).filter(SmartHomePlanModel.id == plan_id).first()

def get_all_plans(db: Session):
    return db.query(SmartHomePlanModel).all()

def create_smart_home_plan(db: Session, plan_code: str, plan_name: str, device_quantity: int, price: float):
    new_plan = SmartHomePlanModel(plan_code=plan_code, plan_name=plan_name, device_quantity=device_quantity, price=price)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

def get_device_by_code(db: Session, device_code: str):
    return db.query(MedicalDeviceModel).filter(MedicalDeviceModel.device_code == device_code).first()

def get_device_by_id(db: Session, device_id: int):
    return db.query(MedicalDeviceModel).filter(MedicalDeviceModel.id == device_id).first()

def get_all_devices(db: Session):
    return db.query(MedicalDeviceModel).all()

def create_medical_device(db: Session, device_code: str, device_name: str, department: str, status: str):
    new_device = MedicalDeviceModel(device_code=device_code, device_name=device_name, department=department, status=status)
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

def get_all_documents(db: Session):
    return db.query(LearningDocumentModel).all()

def get_document_by_id(db: Session, document_id: int):
    return db.query(LearningDocumentModel).filter(LearningDocumentModel.id == document_id).first()

def create_document(db: Session, title: str, subject: str, document_type: str, file_url: str):
    new_doc = LearningDocumentModel(title=title, subject=subject, document_type=document_type, file_url=file_url)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

def delete_document(db: Session, document_id: int):
    doc = db.query(LearningDocumentModel).filter(LearningDocumentModel.id == document_id).first()
    if doc:
        db.delete(doc)
        db.commit()
        return True
    return False

def get_active_discount_by_id(db: Session, discount_id: int):
    return db.query(DiscountModel).filter(DiscountModel.id == discount_id, DiscountModel.is_deleted == False).first()

def soft_delete_discount(db: Session, discount_id: int):
    discount = db.query(DiscountModel).filter(DiscountModel.id == discount_id).first()
    if discount:
        discount.is_deleted = True
        discount.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(discount)
        return discount
    return None

def create_discount_sample(db: Session, code: str, amount: int):
    new_discount = DiscountModel(code=code, amount=amount)
    db.add(new_discount)
    db.commit()
    db.refresh(new_discount)
    return new_discount