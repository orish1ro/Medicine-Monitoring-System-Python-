from datetime import date


def validate_medicine(data):
    """
    Validates medicine form data.
    Returns (True, None) if valid, or (False, error_message).
    """
    required = ['name', 'category_id', 'manufacturer_id',
                'unit_id', 'expiry_date', 'batch_number']

    for field in required:
        if not data.get(field):
            return False, f"'{field}' is required."

    if len(str(data['name']).strip()) < 2:
        return False, "Medicine name must be at least 2 characters."

    try:
        qty = int(data.get('quantity', 0))
        if qty < 0:
            return False, "Quantity cannot be negative."
    except (ValueError, TypeError):
        return False, "Quantity must be a whole number."

    try:
        price = float(data.get('price', 0))
        if price < 0:
            return False, "Price cannot be negative."
    except (ValueError, TypeError):
        return False, "Price must be a number."

    try:
        expiry = data['expiry_date']
        if isinstance(expiry, str):
            expiry = date.fromisoformat(expiry)
    except ValueError:
        return False, "Expiry date must be in YYYY-MM-DD format."

    return True, None


def validate_user(data, is_signup=False):
    """
    Validates user login/signup data.
    Returns (True, None) or (False, error_message).
    """
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    if is_signup:
        email = str(data.get('email', '')).strip()
        if email and '@' not in email:
            return False, "Invalid email address."

    return True, None
