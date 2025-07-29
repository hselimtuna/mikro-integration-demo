import hashlib
from datetime import datetime

class MD5HashedPassword():

    def __init__(self, kullanici_kodu: str):
        today_str = datetime.today().strftime("%Y-%m-%d")
        text_to_encode: str = f"{today_str} {kullanici_kodu}"
        self.hashed_password = hashlib.md5(text_to_encode.encode()).hexdigest()

    def get_hashed_password(self):
        return self.hashed_password
