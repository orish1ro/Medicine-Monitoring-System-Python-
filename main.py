import sys
from PyQt6.QtWidgets import QApplication
from views.login_view import LoginView
from views.signup_view import SignupView
from views.dashboard_view import DashboardView
from views.add_medicine_view import AddMedicineView
from views.inventory_view import InventoryView
from views.search_view import SearchView
from views.expiry_view import ExpiryView
from views.report_view import ReportView


class App:
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.current_user_id  = None
        self.current_username = None

        self.login_win     = None
        self.signup_win    = None
        self.dashboard_win = None

        self._show_login()

    # ── SHOW LOGIN ────────────────────────────────────────────
    def _show_login(self):
        self._hide_all()
        self.login_win = LoginView(
            on_login=self._handle_login,
            on_go_signup=self._show_signup
        )
        self.login_win.show()

    # ── SHOW SIGNUP ───────────────────────────────────────────
    def _show_signup(self):
        self._hide_all()
        self.signup_win = SignupView(
            on_signup=self._handle_signup,
            on_go_login=self._show_login
        )
        self.signup_win.show()

    # ── SHOW DASHBOARD ────────────────────────────────────────
    def _show_dashboard(self, username):
        self._hide_all()
        self.dashboard_win = DashboardView(
            username=username,
            on_navigate=self._handle_navigate,
            on_logout=self._handle_logout
        )
        # Load real stats then show dashboard overview
        self._navigate_dashboard()
        self.dashboard_win.show()

    # ── NAVIGATE ─────────────────────────────────────────────
    def _handle_navigate(self, key):
        if key == "dashboard":
            self._navigate_dashboard()

        elif key == "add":
            self.dashboard_win.set_content(
                AddMedicineView(
                    user_id=self.current_user_id,
                    on_success=self._navigate_dashboard
                )
            )

        elif key == "inventory":
            self.dashboard_win.set_content(
                InventoryView(user_id=self.current_user_id)
            )

        elif key == "search":
            self.dashboard_win.set_content(
                SearchView(user_id=self.current_user_id)
            )

        elif key == "expiry":
            self.dashboard_win.set_content(
                ExpiryView(user_id=self.current_user_id)
            )

        elif key == "report":
            self.dashboard_win.set_content(
                ReportView(user_id=self.current_user_id)
            )

        else:
            print(f"[Navigation] '{key}' not implemented.")

    # ── DASHBOARD OVERVIEW ────────────────────────────────────
    def _navigate_dashboard(self):
        """Fetch fresh stats and rebuild the dashboard overview."""
        if not self.dashboard_win:
            return
        from controllers.medicine_controller import MedicineController
        stats = MedicineController.get_dashboard_stats()
        self.dashboard_win.show_dashboard_content(stats)
        self.dashboard_win.set_active_nav("dashboard")

    # ── AUTH HANDLERS ─────────────────────────────────────────
    def _handle_login(self, username, password):
        from controllers.auth_controller import AuthController
        result = AuthController.login(username, password)
        if result.get("success"):
            self.current_user_id  = result["user_id"]
            self.current_username = result["username"]
            self._show_dashboard(self.current_username)
        else:
            if self.login_win:
                self.login_win.show_error(result.get("error", "Invalid credentials."))

    def _handle_signup(self, full_name, username, email, password):
        from controllers.auth_controller import AuthController
        result = AuthController.register(full_name, username, email, password)
        if result.get("success"):
            return None
        return {"error": result.get("error", "Registration failed.")}

    def _handle_logout(self):
        self.current_user_id  = None
        self.current_username = None
        self._show_login()

    # ── HIDE ALL ──────────────────────────────────────────────
    def _hide_all(self):
        for win in [self.login_win, self.signup_win, self.dashboard_win]:
            if win:
                win.hide()

    # ── RUN ───────────────────────────────────────────────────
    def run(self):
        sys.exit(self.qt_app.exec())


if __name__ == "__main__":
    app = App()
    app.run()