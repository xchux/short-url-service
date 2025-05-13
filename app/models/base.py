import hashlib


def get_url_hash(original_url: str) -> bytes:
    # 使用 SHA256 並轉成 32 bytes binary（與 MySQL 中的 UNHEX(SHA2(...)) 一致）
    return bytes.fromhex(hashlib.sha256(original_url.encode("utf-8")).hexdigest())
