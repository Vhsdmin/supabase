#!/usr/bin/env python3
"""Generate a private .env for a NEW EasyPanel installation."""
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import time


def b64(data):
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def main():
    root = Path(__file__).resolve().parent
    target = root / '.env'
    if target.exists():
        raise SystemExit('Existing .env found. No changes made. Never regenerate keys for an existing database.')
    jwt_secret = secrets.token_hex(32)
    now = int(time.time())

    def jwt(role):
        header = b64(json.dumps({'alg': 'HS256', 'typ': 'JWT'}, separators=(',', ':')).encode())
        payload = b64(json.dumps({'role': role, 'iss': 'supabase', 'iat': now,
                                 'exp': now + 5 * 365 * 86400}, separators=(',', ':')).encode())
        message = header + '.' + payload
        return message + '.' + b64(hmac.new(jwt_secret.encode(), message.encode(), hashlib.sha256).digest())

    values = {
        'POSTGRES_PASSWORD': secrets.token_hex(32),
        'JWT_SECRET': jwt_secret,
        'ANON_KEY': jwt('anon'),
        'SERVICE_ROLE_KEY': jwt('service_role'),
        'DASHBOARD_PASSWORD': secrets.token_hex(24),
        'SECRET_KEY_BASE': base64.b64encode(secrets.token_bytes(48)).decode(),
        'REALTIME_DB_ENC_KEY': secrets.token_hex(8),
        'VAULT_ENC_KEY': secrets.token_hex(16),
        'PG_META_CRYPTO_KEY': secrets.token_hex(32),
        'LOGFLARE_PUBLIC_ACCESS_TOKEN': secrets.token_hex(32),
        'LOGFLARE_PRIVATE_ACCESS_TOKEN': secrets.token_hex(32),
        'S3_PROTOCOL_ACCESS_KEY_ID': secrets.token_hex(16),
        'S3_PROTOCOL_ACCESS_KEY_SECRET': secrets.token_hex(32),
        'MINIO_ROOT_PASSWORD': secrets.token_hex(24),
    }
    content = (root / '.env.easypanel.example').read_text(encoding='utf-8')
    for key, value in values.items():
        content, count = re.subn(r'^' + key + r'=.*$', lambda _: key + '=' + value,
                                content, flags=re.M)
        if count != 1:
            raise SystemExit('Invalid template: ' + key)
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as output:
        output.write(content)
    print('.env created. Copy its contents to EasyPanel Environment. Never publish .env on GitHub.')


if __name__ == '__main__':
    main()
