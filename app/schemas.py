from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone, timedelta
import re

class AirtimeRequest(BaseModel):
    clientId: str
    productId: str
    denomination: int
    transactionId: str
    transactionDate: str
    billNo: str
    stockType: str
    terminalId: str
    storeId: str

    @field_validator('transactionDate')
    @classmethod
    def validate_time(cls, v):
        try:
            # Parse format ISO dengan offset (+07:00)
            dt = datetime.fromisoformat(v)
            now = datetime.now(timezone(timedelta(hours=7)))
            diff = abs((now - dt).total_seconds())

            if diff > 100000: # 5 menit
                raise ValueError('Transaction date older than 5-minutes')
            return v
        except Exception:
            raise ValueError('Invalid date format or expired')

    @field_validator('billNo')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^08[0-9]{9,12}$', v):
            raise ValueError('billNo must start with 08 and be 11-14 digits')
        return v

class InquiryRequest(BaseModel):
    clientId: str
    transactionId: str
    transactionDate: str

    @field_validator('transactionDate')
    @classmethod
    def validate_12_hours(cls, v):
        try:
            dt = datetime.fromisoformat(v)
            now = datetime.now(timezone(timedelta(hours=7)))
            diff = now - dt
            # Hanya transaksi 12 jam terakhir yang bisa dicek
            if diff > timedelta(hours=12):
                raise ValueError('Transaction is older than 12 hours')
            return v
        except Exception:
            raise ValueError('Invalid date format or transaction too old')

class InquiryResponse(BaseModel):
    referenceId: str
    productId: str
    denomination: int
    billNo: str
    stockType: str
    terminalId: str
    statusCode: str
    serialNumber: str
    description: str
