"""
QR Code image generator for SmartAttend.

Generates QR codes encoding only the token value.
Never encodes student identity or session details in QR.
"""
import base64
import io
import qrcode
from qrcode.constants import ERROR_CORRECT_M


def generate_qr_image(token: str) -> str:
    """
    Generate a QR code image for the given token.

    Args:
        token: The URL-safe token string to encode

    Returns:
        Base64-encoded PNG data URI (data:image/png;base64,...)
        Ready to use as <img src="..."> in HTML/React
    """
    qr = qrcode.QRCode(
        version=None,  # Auto-determine version
        error_correction=ERROR_CORRECT_M,  # Medium error correction (~15% recovery)
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"
