import base64
import hashlib
from pyDes import *
from loguru import logger
import warnings
import license_key
warnings.filterwarnings('ignore')

LICENSE_URL = "https://gist.githubusercontent.com/sychen6192/82a0a3e2428d2dee0e55df2cdf95050b/raw"
def Encrypted(code):
    Des_key = "posdvsgt"
    Des_IV = "\x11\2\x2a\3\1\x27\2\0"
    k = des(Des_key, CBC, Des_IV, pad=None, padmode=PAD_PKCS5)
    EncryptStr = k.encrypt(code)
    base64_code = base64.b32encode(EncryptStr)
    md5_code = hashlib.md5(base64_code).hexdigest().upper()
    return md5_code

def init_license(key):
    license = license_key.init(license_json_url = LICENSE_URL)
    return license.check(license_key = key)

if __name__ == "__main__":
    print(init_license("QNFUN-HQXLL-C3M1A-K7J9C-UMKGT"))