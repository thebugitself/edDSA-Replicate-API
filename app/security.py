import json
import base64
import nacl.signing
import nacl.exceptions
from typing import Any, Dict

def create_canonical_json(data: Dict[str, Any]) -> bytes:
    # Memastikan urutan key alfabetis & tanpa spasi (compact)
    # Penting: ensure_ascii=False agar karakter unik tidak berubah
    canonical_str = json.dumps(
        data,
        sort_keys=True,
        separators=(',', ':'),
        ensure_ascii=False
    )
    return canonical_str.encode('utf-8')

def verify_signature(body_bytes: bytes, signature_b64: str, public_key_b64: str) -> bool:
    try:
        body_json = json.loads(body_bytes)
        canonical_data = create_canonical_json(body_json)

        # Decode signature & public key
        sig_bytes = base64.b64decode(signature_b64)
        pk_bytes = base64.b64decode(public_key_b64)

        verify_key = nacl.signing.VerifyKey(pk_bytes)

        # Verifikasi
        verify_key.verify(canonical_data, sig_bytes)
        return True
    except Exception as e:
        print(f"Verification Detail: {e}") # Log untuk server
        return False
