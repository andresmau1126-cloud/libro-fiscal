"""
Custom exception handler for DRF.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        # Normalize error format to {"error": "..."}
        if isinstance(response.data, dict) and "detail" in response.data:
            response.data = {"error": str(response.data["detail"])}
        elif isinstance(response.data, dict):
            errors = []
            for field, msgs in response.data.items():
                if isinstance(msgs, list):
                    errors.extend([f"{field}: {m}" for m in msgs])
                else:
                    errors.append(f"{field}: {msgs}")
            response.data = {"error": "; ".join(errors)}
    return response
