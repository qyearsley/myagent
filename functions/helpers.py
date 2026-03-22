# NOTE: Each tool function validates that file paths stay within the sandbox
# working directory using os.path.commonpath. This prevents the model from
# accessing files outside the permitted area via path traversal (e.g. "../../").


def log_errors(func):
    """Decorator that catches exceptions in tool functions and prints them
    instead of crashing, so the agent can report the error to the model."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"  Error: {e}")

    return wrapper
