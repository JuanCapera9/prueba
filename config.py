class Config:
    SECRET_KEY = 'secret'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'nowtifylogist'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'bmp77576@gmail.com'
    MAIL_PASSWORD = 'ikcy rzsz hape ychv'
    MAIL_DEFAULT_SENDER = 'bmp77576@gmail.com'
    SECURITY_PASSWORD_SALT = 'your-salt'

# Establece la codificación predeterminada de Flask a UTF-8
import sys
if not sys.stdout.encoding.lower().startswith('utf-8'):
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)