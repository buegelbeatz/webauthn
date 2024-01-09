import qrcode
from qrcode.image.pure import PyPNGImage
from io import BytesIO
from PIL import Image

class Qr:

    def __init__(self,protocol,domain,path):
        self.url = f"{protocol}://{domain}{path}"
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

    def create(self):
        self.qr.add_data(f"{self.url}")
        self.qr.make(fit=True)
        img = self.qr.make_image(fill_color='black', back_color='white')
        _bytes = BytesIO()
        img.save(_bytes, format="PNG")
        retval = _bytes.getvalue()

        return(retval)
