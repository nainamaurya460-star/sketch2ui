from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared application rate limiter instance using client IP
limiter = Limiter(key_func=get_remote_address)
