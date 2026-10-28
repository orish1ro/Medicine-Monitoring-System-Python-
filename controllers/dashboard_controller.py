from controllers.inventory_controller import controller_get_dashboard_stats
from controllers.expiry_controller import controller_check_and_create_alerts
from controllers.auth_controller import get_current_user
from datetime import datetime


def controller_get_dashboard():
    """
    Returns everything needed to render the dashboard:
    stats, current user, date, and any new alerts created.
    """
    alerts_created = controller_check_and_create_alerts()
    stats = controller_get_dashboard_stats()
    user = get_current_user()

    return {
        'stats':          stats,
        'user':           user,
        'date':           datetime.now().strftime('%d/%m/%Y'),
        'alerts_created': alerts_created,
    }
