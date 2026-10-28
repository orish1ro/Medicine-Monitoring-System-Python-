from datetime import date


def days_until_expiry(expiry_date):
    """Return number of days until expiry. Negative = already expired."""
    if isinstance(expiry_date, str):
        expiry_date = date.fromisoformat(expiry_date)
    return (expiry_date - date.today()).days


def get_medicine_status(medicine):
    """
    Returns 'expired', 'expiring_soon', 'low_stock', or 'ok'
    based on expiry date and quantity vs threshold.
    """
    days = days_until_expiry(medicine['expiry_date'])
    threshold = medicine.get('low_stock_threshold', 10)

    if days < 0:
        return 'expired'
    if days <= 30:
        return 'expiring_soon'
    if medicine['quantity'] <= threshold:
        return 'low_stock'
    return 'ok'


def format_currency(value):
    return f"${float(value):.2f}"


def format_date(d):
    if isinstance(d, str):
        return d
    return d.strftime('%Y-%m-%d') if d else ''


def paginate(items, page=1, per_page=20):
    """Simple in-memory pagination helper."""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        'items': items[start:end],
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': (total + per_page - 1) // per_page,
    }
