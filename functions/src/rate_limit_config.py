"""
Rate limiting configuration for Firebase Functions.
This file defines rate limits for different types of functions based on their sensitivity and resource usage.
"""

# Rate limit configurations for different function types
RATE_LIMIT_CONFIG = {
    # Authentication and user management functions
    "auth": {
        "user_rate_limit": {
            "max_requests": 10,
            "window_seconds": 300,
        },  # 10 requests per 5 minutes per user
        "global_rate_limit": {
            "max_requests": 100,
            "window_seconds": 60,
        },  # 100 requests per minute globally
    },
    # Organization management functions
    "org_management": {
        "user_rate_limit": {
            "max_requests": 20,
            "window_seconds": 300,
        },  # 20 requests per 5 minutes per user
        "global_rate_limit": {
            "max_requests": 200,
            "window_seconds": 60,
        },  # 200 requests per minute globally
    },
    # Device management functions
    "device_management": {
        "user_rate_limit": {
            "max_requests": 50,
            "window_seconds": 300,
        },  # 50 requests per 5 minutes per user
        "global_rate_limit": {
            "max_requests": 500,
            "window_seconds": 60,
        },  # 500 requests per minute globally
    },
    # Verkada integration functions (resource-intensive)
    "verkada_integration": {
        "user_rate_limit": {
            "max_requests": 5,
            "window_seconds": 300,
        },  # 5 requests per 5 minutes per user
        "global_rate_limit": {
            "max_requests": 50,
            "window_seconds": 60,
        },  # 50 requests per minute globally
    },
    # Read-only functions (less restrictive)
    "read_only": {
        "user_rate_limit": {
            "max_requests": 100,
            "window_seconds": 300,
        },  # 100 requests per 5 minutes per user
        "global_rate_limit": {
            "max_requests": 1000,
            "window_seconds": 60,
        },  # 1000 requests per minute globally
    },
    # Default configuration
    "default": {
        "user_rate_limit": {
            "max_requests": 30,
            "window_seconds": 300,
        },  # 30 requests per 5 minutes per user
        "global_rate_limit": {
            "max_requests": 300,
            "window_seconds": 60,
        },  # 300 requests per minute globally
    },
}


def get_rate_limit_config(function_type: str = "default"):
    """
    Get rate limit configuration for a specific function type.

    Args:
        function_type: The type of function ('auth', 'org_management', 'device_management', etc.)

    Returns:
        Dictionary containing rate limit configuration
    """
    return RATE_LIMIT_CONFIG.get(function_type, RATE_LIMIT_CONFIG["default"])


# Function type mappings for easy application
FUNCTION_TYPE_MAPPINGS = {
    # Authentication functions
    "create_global_user_profile_callable": "auth",
    "delete_global_user_callable": "auth",
    "update_global_user_display_name_callable": "auth",
    "update_global_user_photo_url_callable": "auth",
    # Organization management functions
    "create_organization_callable": "org_management",
    "delete_org_callable": "org_management",
    "update_org_background_image_callable": "org_management",
    "update_org_name_callable": "org_management",
    "update_org_device_regex_callable": "org_management",
    # User management functions
    "create_users_callable": "org_management",
    "delete_org_member_callable": "org_management",
    "update_user_role_callable": "org_management",
    # Device management functions
    "create_devices_callable": "device_management",
    "delete_device_callable": "device_management",
    "update_device_checkout_status_callable": "device_management",
    # Verkada integration functions
    "sync_with_verkada_callable": "verkada_integration",
    "update_verkada_integration_status_callable": "verkada_integration",
    "update_verkada_product_site_designations_callable": "verkada_integration",
    "update_verkada_user_group_whitelists_callable": "verkada_integration",
    "update_verkada_site_cleaner_status_callable": "verkada_integration",
}


def get_function_type(function_name: str) -> str:
    """
    Get the function type for a given function name.

    Args:
        function_name: The name of the function

    Returns:
        The function type string
    """
    return FUNCTION_TYPE_MAPPINGS.get(function_name, "default")
