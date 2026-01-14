import json
import base64
import sys
from datetime import datetime, timezone, timedelta

try:
    import nacl.signing
except ImportError:
    print("Error: PyNaCl belum terinstal. Jalankan: pip install PyNaCl")
    sys.exit(1)

# --- CONFIGURATION & HELPERS ---

def create_canonical_json(data: dict) -> str:
    """Memastikan format JSON sama persis dengan yang diharapkan server."""
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def get_now_gmt7_iso():
    """Generate timestamp ISO8601 dengan offset +07:00."""
    return datetime.now(timezone(timedelta(hours=7))).isoformat()

def sign_body(private_key_b64: str, body_dict: dict):
    """Proses signing: Dict -> Canonical -> Sign -> Base64."""
    priv_bytes = base64.b64decode(private_key_b64)
    signing_key = nacl.signing.SigningKey(priv_bytes)

    canonical_str = create_canonical_json(body_dict)
    signed = signing_key.sign(canonical_str.encode('utf-8'))

    return base64.b64encode(signed.signature).decode('utf-8')

# --- COMMANDS ---

def cmd_keygen():
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key

    priv = base64.b64encode(bytes(signing_key)).decode('utf-8')
    pub = base64.b64encode(bytes(verify_key)).decode('utf-8')

    print("\n[+] ED25519 KEYPAIR GENERATED")
    print(f"Private Key (Base64): {priv}")
    print(f"Public Key  (Base64): {pub}")
    print(f"\nTambahkan ke mapping MOCK_PUBLIC_KEYS di .env!")

def cmd_test_sign(priv_key, client_id):
    # Data dummy dinamis berdasarkan client_id
    body = {
        "clientId": client_id,
        "productId": "NTS15",
        "denomination": 15000,
        "transactionId": f"tx-{client_id}-{int(datetime.now().timestamp())}",
        "transactionDate": get_now_gmt7_iso(),
        "billNo": "081392002488",
        "stockType": "BULK",
        "terminalId": "TRM01",
        "storeId": "Store Kemang"
    }

    signature = sign_body(priv_key, body)

    print(f"\n[+] GENERATED REQUEST DATA FOR: {client_id}")
    print("-" * 30)
    print(f"Header x-signature:\n{signature}")
    print("-" * 30)
    print(f"Curl Command Example:")
    print(f"curl -X POST http://localhost:8000/airtimeRecharge \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -H 'x-signature: {signature}' \\")
    print(f"  -d '{json.dumps(body)}'")

def cmd_inquiry(priv_key, client_id):
    body = {
        "clientId": client_id,
        "transactionId": "T8blkJHf82K",
        "transactionDate": get_now_gmt7_iso()
    }
    signature = sign_body(priv_key, body)

    print(f"\n[+] INQUIRY REQUEST DATA FOR: {client_id}")
    print(f"Header x-signature: {signature}")
    print(f"\ncurl -X POST http://localhost:8000/inquiry \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -H 'x-signature: {signature}' \\")
    print(f"  -d '{json.dumps(body)}'")

# --- MAIN CLI ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python utils.py keygen")
        print("  python utils.py sign <privkey> <client_id>")
        print("  python utils.py inquiry <privkey> <client_id>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "keygen":
        cmd_keygen()
    elif cmd in ["sign", "inquiry"]:
        if len(sys.argv) < 4:
            # Default ke alpha-group kalau client_id tidak diisi
            client_id = "alpha-group"
            print(f"[*] No client_id provided, defaulting to '{client_id}'")
        else:
            client_id = sys.argv[3]

        if len(sys.argv) < 3:
            print(f"Error: Masukkan Private Key untuk {cmd}")
            sys.exit(1)

        priv_key = sys.argv[2]

        if cmd == "sign":
            cmd_test_sign(priv_key, client_id)
        else:
            cmd_inquiry(priv_key, client_id)
