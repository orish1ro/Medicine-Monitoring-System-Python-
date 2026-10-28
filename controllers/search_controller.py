from controllers.medicine_controller import MedicineController
from models.inventory_model import get_all_categories


def controller_search(query="", category_id=None):
    """
    Search medicines by name, manufacturer, or batch number.
    Optionally filter by category_id.
    Returns list of matching medicine dicts.
    """
    return MedicineController.search_medicines(query.strip(), category_id)


def controller_get_search_filters():
    """Returns categories list for populating the filter dropdown."""
    return get_all_categories()