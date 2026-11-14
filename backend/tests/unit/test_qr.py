from app.utils.qr_generator import generate_qr_image

def test_qr_generation():
    img = generate_qr_image("sample-token")
    assert img.startswith("data:image/png;base64,")
