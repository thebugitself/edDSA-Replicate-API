import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse

from .schemas import AirtimeRequest, InquiryRequest
from .security import verify_signature
from .config import SETTINGS

app = FastAPI(title="edDSA API Implementation")

async def get_client_public_key(body_bytes: bytes):
    try:
        body_json = json.loads(body_bytes)
        client_id = body_json.get("clientId")

        public_key = SETTINGS.public_keys_map.get(client_id)
        return public_key
    except Exception:
        return None

# --- Endpoints ---

@app.post("/airtimeRecharge")
async def airtime_recharge(
    request: Request,
    x_signature: str = Header(...)
):
    try:
        return await asyncio.wait_for(
            process_recharge(request, x_signature),
            timeout=SETTINGS.REQUEST_TIMEOUT
        )
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={"resultCode": "31"}
        )

async def process_recharge(request: Request, x_signature: str):
    body_bytes = await request.body()

    public_key = await get_client_public_key(body_bytes)

    if not public_key:
        return JSONResponse(
            status_code=401,
            content={"resultCode": "10", "resultDescription": "Unauthorized Client ID."}
        )

    is_valid = verify_signature(body_bytes, x_signature, public_key)
    if not is_valid:
        return JSONResponse(
            status_code=401,
            content={"resultCode": "10", "resultDescription": "Signature is wrong."}
        )

    try:
        data = json.loads(body_bytes)
        validated_data = AirtimeRequest(**data)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "resultCode": "21",
                "resultDescription": str(e),
                "billerResponseDate": datetime.now(timezone(timedelta(hours=7))).isoformat()
            }
        )

    # await asyncio.sleep(35) # Simulasi delay untuk test 408

    return {
        "resultCode": "00",
        "referenceId": str(uuid.uuid4()),
        "serialNumber": "03851100000648014491",
        "billerResponseDate": datetime.now(timezone(timedelta(hours=7))).isoformat(),
        "description": "Approved by Telkomsel"
    }

@app.post("/inquiry")
async def transaction_inquiry(
    request: Request,
    x_signature: str = Header(...)
):
    body_bytes = await request.body()

    public_key = await get_client_public_key(body_bytes)

    if not public_key:
        return JSONResponse(
            status_code=401,
            content={"resultCode": "10", "resultDescription": "Unauthorized Client ID."}
        )

    is_valid = verify_signature(body_bytes, x_signature, public_key)
    if not is_valid:
        return JSONResponse(
            status_code=401,
            content={"resultCode": "10", "resultDescription": "Signature is wrong."}
        )

    try:
        data = json.loads(body_bytes)
        validated_req = InquiryRequest(**data)
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "referenceId": "N/A",
                "productId": "N/A",
                "denomination": "0",
                "billNo": "N/A",
                "stockType": "N/A",
                "terminalId": "N/A",
                "statusCode": "06",
                "description": str(e)
            }
        )

    return {
        "referenceId": str(uuid.uuid4()),
        "productId": "pulsa-reg-15k",
        "denomination": 50000,
        "billNo": "081385720155",
        "stockType": "FIXED",
        "terminalId": "KOX-19255",
        "statusCode": "00",
        "serialNumber": "03851100000650220471",
        "description": "Transaction Successful"
    }
