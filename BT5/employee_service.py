from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from BT6.database import Base

class SmartHomePlanModel(Base):
    __tablename__ = "smart_home_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_code = Column(String(50), unique=True, nullable=False, index=True)
    plan_name = Column(String(255), nullable=False)
    device_quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

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