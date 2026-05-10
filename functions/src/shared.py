from firebase_functions import options
from firebase_admin import firestore
import logging
import time
from functools import wraps
from firebase_functions import https_fn
from typing import Optional, Callable, Any

# Define CORS options for HTTP functions
try:
    POSTcorsrules = options.CorsOptions(
        cors_origins=[
            "https://inventory.webbpulse.com",
            "http://localhost:3000",
            "http://localhost:8080",
        ],
        cors_methods=["get", "post", "put", "delete", "options"],
    )
except Exception:
    # Handle case where Firebase Functions is not properly initialized (e.g., during testing)
    POSTcorsrules = None

# Initialize Firestore client
try:
    db = firestore.client()
except ValueError:
    # Handle case where Firebase app is not initialized (e.g., during testing)
    db = None

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create a logger instance
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    A rate limiter implementation using Firestore to track request counts.
    Supports both per-user and global rate limiting.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds for rate limiting
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _get_rate_limit_key(self, identifier: str) -> str:
        """Generate a rate limit key for the given identifier."""
        current_window = int(time.time() // self.window_seconds)
        return f"rate_limit:{identifier}:{current_window}"

    def _cleanup_old_windows(self, identifier: str):
        """Clean up old rate limit windows to prevent Firestore bloat."""
        try:
            current_window = int(time.time() // self.window_seconds)
            # Keep only the current and previous window
            for window in range(current_window - 2, current_window):
                old_key = f"rate_limit:{identifier}:{window}"
                db.collection("rateLimits").document(old_key).delete()
        except Exception as e:
            logger.warning(f"Failed to cleanup old rate limit windows: {e}")

    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if the request is within rate limits.

        Args:
            identifier: Unique identifier for rate limiting (e.g., user ID, IP, or 'global')

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        try:
            # Handle case where db is not initialized (e.g., during testing)
            if db is None:
                return True

            key = self._get_rate_limit_key(identifier)
            doc_ref = db.collection("rateLimits").document(key)

            # Use transaction to ensure atomic increment
            @db.transactional
            def update_count(transaction, doc_ref):
                doc = doc_ref.get(transaction=transaction)
                if doc.exists:
                    current_count = doc.to_dict().get("count", 0)
                    if current_count >= self.max_requests:
                        return False
                    transaction.update(doc_ref, {"count": current_count + 1})
                else:
                    transaction.set(
                        doc_ref,
                        {"count": 1, "window": int(time.time() // self.window_seconds)},
                    )
                return True

            transaction = db.transaction()
            result = update_count(transaction, doc_ref)

            # Cleanup old windows periodically (every 10th request)
            if result and int(time.time()) % 10 == 0:
                self._cleanup_old_windows(identifier)

            return result

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # On error, allow the request to proceed
            return True


def apply_rate_limiting(
    req: https_fn.CallableRequest, function_name: str = None
) -> None:
    """
    Apply rate limiting to a function call. This is the new non-decorator approach.

    Args:
        req: The Firebase Functions request object
        function_name: The name of the function for rate limiting configuration

    Raises:
        https_fn.HttpsError: If rate limit is exceeded
    """
    try:
        from src.rate_limit_config import get_function_type, get_rate_limit_config

        # Get the function type from the mapping
        function_type = get_function_type(function_name)

        # Get the rate limit configuration for this function type
        config = get_rate_limit_config(function_type)

        user_config = config["user_rate_limit"]
        global_config = config["global_rate_limit"]

        # Create rate limiters
        user_limiter = RateLimiter(**user_config)
        global_limiter = RateLimiter(**global_config)

        # Check user rate limit
        user_identifier = req.auth.uid if req.auth else "anonymous"
        if not user_limiter.check_rate_limit(user_identifier):
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED,
                message=f"User rate limit exceeded. Maximum {user_config['max_requests']} requests per {user_config['window_seconds']} seconds.",
            )

        # Check global rate limit
        if not global_limiter.check_rate_limit("global"):
            raise https_fn.HttpsError(
                code=https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED,
                message=f"Global rate limit exceeded. Maximum {global_config['max_requests']} requests per {global_config['window_seconds']} seconds.",
            )

    except ImportError as e:
        logger.warning(f"Rate limit config not available, skipping rate limiting: {e}")
        # If config is not available, skip rate limiting
        pass
    except Exception as e:
        logger.error(f"Error applying rate limiting: {e}")
        # On error, allow the request to proceed
        pass


# Legacy decorator functions (kept for backward compatibility but deprecated)
def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
    identifier_func: Optional[Callable] = None,
):
    """
    DEPRECATED: Use apply_rate_limiting() function instead.
    Decorator to apply rate limiting to Firebase Functions.
    """
    logger.warning(
        "rate_limit decorator is deprecated. Use apply_rate_limiting() function instead."
    )

    def decorator(func: Callable) -> Callable:
        limiter = RateLimiter(max_requests, window_seconds)

        @wraps(func)
        def wrapper(req: https_fn.CallableRequest) -> Any:
            # Determine the identifier for rate limiting
            if identifier_func:
                identifier = identifier_func(req)
            else:
                # Default: use user ID if authenticated, otherwise 'anonymous'
                identifier = req.auth.uid if req.auth else "anonymous"

            # Check rate limit
            if not limiter.check_rate_limit(identifier):
                raise https_fn.HttpsError(
                    code=https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED,
                    message=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                )

            return func(req)

        return wrapper

    return decorator


def user_rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """DEPRECATED: Use apply_rate_limiting() function instead."""
    logger.warning(
        "user_rate_limit decorator is deprecated. Use apply_rate_limiting() function instead."
    )
    return rate_limit(
        max_requests,
        window_seconds,
        lambda req: req.auth.uid if req.auth else "anonymous",
    )


def global_rate_limit(max_requests: int = 1000, window_seconds: int = 60):
    """DEPRECATED: Use apply_rate_limiting() function instead."""
    logger.warning(
        "global_rate_limit decorator is deprecated. Use apply_rate_limiting() function instead."
    )
    return rate_limit(max_requests, window_seconds, lambda req: "global")


def ip_rate_limit(max_requests: int = 50, window_seconds: int = 60):
    """DEPRECATED: Use apply_rate_limiting() function instead."""
    logger.warning(
        "ip_rate_limit decorator is deprecated. Use apply_rate_limiting() function instead."
    )

    def get_ip(req):
        # Note: Firebase Functions don't directly expose client IP
        # This would need to be passed from the client or extracted from headers
        return req.data.get("client_ip", "unknown")

    return rate_limit(max_requests, window_seconds, get_ip)


def apply_rate_limiting_legacy(function_type: str = "default"):
    """
    DEPRECATED: Use apply_rate_limiting() function instead.
    Apply rate limiting based on function type configuration.
    """
    logger.warning(
        "apply_rate_limiting_legacy decorator is deprecated. Use apply_rate_limiting() function instead."
    )

    try:
        from src.rate_limit_config import get_rate_limit_config

        config = get_rate_limit_config(function_type)

        user_config = config["user_rate_limit"]
        global_config = config["global_rate_limit"]

        def decorator(func: Callable) -> Callable:
            # Apply both user and global rate limiting
            func = user_rate_limit(**user_config)(func)
            func = global_rate_limit(**global_config)(func)
            return func

        return decorator
    except ImportError:
        # Fallback to default rate limiting if config is not available
        logger.warning("Rate limit config not available, using default rate limiting")
        return user_rate_limit(30, 300)


def configurable_rate_limit(function_name: str = None):
    """
    DEPRECATED: Use apply_rate_limiting() function instead.
    Apply rate limiting based on function name using the rate_limit_config.py configuration.
    """
    logger.warning(
        "configurable_rate_limit decorator is deprecated. Use apply_rate_limiting() function instead."
    )

    def decorator(func: Callable) -> Callable:
        try:
            from src.rate_limit_config import get_function_type, get_rate_limit_config

            # Get the function name if not provided
            if function_name is None:
                func_name = func.__name__
            else:
                func_name = function_name

            # Get the function type from the mapping
            function_type = get_function_type(func_name)

            # Get the rate limit configuration for this function type
            config = get_rate_limit_config(function_type)

            user_config = config["user_rate_limit"]
            global_config = config["global_rate_limit"]

            # Create rate limiters
            user_limiter = RateLimiter(**user_config)
            global_limiter = RateLimiter(**global_config)

            def wrapper(req: https_fn.CallableRequest) -> Any:
                # Check user rate limit
                user_identifier = req.auth.uid if req.auth else "anonymous"
                if not user_limiter.check_rate_limit(user_identifier):
                    raise https_fn.HttpsError(
                        code=https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED,
                        message=f"User rate limit exceeded. Maximum {user_config['max_requests']} requests per {user_config['window_seconds']} seconds.",
                    )

                # Check global rate limit
                if not global_limiter.check_rate_limit("global"):
                    raise https_fn.HttpsError(
                        code=https_fn.FunctionsErrorCode.RESOURCE_EXHAUSTED,
                        message=f"Global rate limit exceeded. Maximum {global_config['max_requests']} requests per {global_config['window_seconds']} seconds.",
                    )

                return func(req)

            # Copy function attributes manually to avoid __annotations__ issues
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            wrapper.__module__ = func.__module__

            return wrapper

        except ImportError as e:
            logger.warning(
                f"Rate limit config not available, using default rate limiting: {e}"
            )
            # Fallback to default rate limiting
            return user_rate_limit(30, 300)
        except Exception as e:
            logger.error(f"Error applying configurable rate limiting: {e}")
            # Fallback to default rate limiting
            return user_rate_limit(30, 300)

    return decorator
