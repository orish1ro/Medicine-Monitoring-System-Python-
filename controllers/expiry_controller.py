from models.medicine_model import get_expired_medicines, get_expiring_soon_medicines
from models.report_model import create_alert, get_unresolved_alerts, resolve_alert


def controller_get_expired():
    return get_expired_medicines()


def controller_get_expiring_soon(days=30):
    return get_expiring_soon_medicines(days)


def controller_check_and_create_alerts():
    """
    Scan inventory and insert alert rows for expired/expiring/low stock.
    Call this on login or on a scheduled basis.
    """
    from models.medicine_model import get_all_medicines
    from utils.helpers import get_medicine_status

    medicines = get_all_medicines()
    created = 0
    for med in medicines:
        status = get_medicine_status(med)
        if status == 'expired':
            create_alert(med['id'], 'EXPIRED', f"{med['name']} has expired.")
            created += 1
        elif status == 'expiring_soon':
            create_alert(med['id'], 'EXPIRING_SOON',
                         f"{med['name']} expires on {med['expiry_date']}.")
            created += 1
        elif status == 'low_stock':
            create_alert(med['id'], 'LOW_STOCK',
                         f"{med['name']} has only {med['quantity']} left.")
            created += 1
    return created


def controller_get_alerts():
    return get_unresolved_alerts()


def controller_resolve_alert(alert_id):
    return resolve_alert(alert_id)
