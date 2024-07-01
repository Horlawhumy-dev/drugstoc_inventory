import logging

logger = logging.getLogger(__name__)

def log_user_logged_in_failure(request, email=None):
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    logger.error(f"Login failed for user: {email} from IP: {ip_address}")


def log_user_logged_out(request):
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    logger.info(f"User: {request.user.email} logs out from IP: {ip_address}")

def log_user_login_success(request):
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
    logger.info(f"User: {request.user.email} logs in from IP: {ip_address}")