def validate_code_structure(user_input: str, code: str):
    """
    Performs lightweight structural validation
    based on user request.
    Returns (is_valid: bool, reason: str)
    """

    lower_request = user_input.lower()

    # If class requested
    if "class" in lower_request:
        if "class " not in code:
            return False, "Class definition missing."
        if "__init__" not in code:
            return False, "__init__ method missing."

    # If print requested
    if "print" in lower_request:
        if "print(" not in code:
            return False, "print() statement missing."

    # Basic function request
    if "function" in lower_request or "def " in lower_request:
        if "def " not in code:
            return False, "Function definition missing."

    # Prevent markdown artifacts
    if "[PYTHON]" in code or "```" in code:
        return False, "Formatting artifacts detected."

    return True, "Structure valid."
