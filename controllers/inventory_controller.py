from models.inventory_model import (
    get_all_categories, get_all_units, get_all_manufacturers,
    get_inventory_summary, get_category_breakdown, get_total_inventory_value
)


def controller_get_categories():
    return get_all_categories()


def controller_get_units():
    return get_all_units()


def controller_get_manufacturers():
    return get_all_manufacturers()


def controller_get_dashboard_stats():
    """
    Returns a dict suitable for the dashboard stat cards:
    total, expired, expiring_soon, low_stock, inventory_value.
    """
    summary = get_inventory_summary() or {}
    return {
        'total':          int(summary.get('total', 0) or 0),
        'expired':        int(summary.get('expired', 0) or 0),
        'expiring_soon':  int(summary.get('expiring_soon', 0) or 0),
        'low_stock':      int(summary.get('low_stock', 0) or 0),
        'inventory_value': get_total_inventory_value(),
    }


def controller_get_category_breakdown():
    return get_category_breakdown()
