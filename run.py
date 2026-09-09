import uvicorn
import sys
import io
from pathlib import Path

# Safe UTF-8 encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

if __name__ == "__main__":
    print("=" * 65)
    print(">>>  UZRETRO.UZ — Video & Audio Kassetalar Raqamlashtirish")
    print("=" * 65)
    print(">>>  Sayt manzili:        http://127.0.0.1:8000")
    print(">>>  Admin Panel:         http://127.0.0.1:8000/admin")
    print(">>>  Payme Webhook:       http://127.0.0.1:8000/payme")
    print(">>>  Click Webhook:       http://127.0.0.1:8000/click/prepare")
    print(">>>  Buyurtmani kuzatish: http://127.0.0.1:8000/tracking")
    print("=" * 65)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
