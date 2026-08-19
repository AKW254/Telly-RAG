def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number")

    if not any(c.isalpha() for c in password):
        raise ValueError("Password must contain letters")

    if not any(c.isupper() for c in password):
        raise ValueError("Must contain uppercase letter")

    if not any(c.islower() for c in password):
        raise ValueError("Must contain lowercase letter")

    return password