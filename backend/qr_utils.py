import io
import qrcode
import hashlib
from backend.config import get_config

cfg = get_config()


def sign_batch(batch_number: str) -> str:
    return hashlib.sha256((batch_number + cfg.QR_SIGNING_SECRET).encode()).hexdigest()


def generate_qr_png(batch_number: str) -> io.BytesIO:
    signed_data = f"{batch_number}|{sign_batch(batch_number)}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(signed_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
