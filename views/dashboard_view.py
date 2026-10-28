import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QScrollArea, QStackedWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QCursor, QFont, QFontDatabase, QPixmap, QIcon


class DashboardView(QWidget):
    def __init__(self, username="User", on_navigate=None, on_logout=None):
        super().__init__()
        self.username    = username
        self.on_navigate = on_navigate
        self.on_logout   = on_logout
        self.setWindowTitle("Medicine Monitoring System")
        self.setMinimumSize(1100, 650)

        # ── Window icon ───────────────────────────────────────
        _icon_path = os.path.join(os.path.dirname(__file__), "icons", "logo.png")
        if os.path.exists(_icon_path):
            self.setWindowIcon(QIcon(_icon_path))

        self._apply_styles()
        self._build_ui()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            /* ── Global resets ─────────────────────────────── */
            QLabel {
                border: none;
                background: transparent;
            }

            /* ── Root ─────────────────────────────────────── */
            QWidget#DashRoot {
                background-color: #F7F8FC;
                font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
            }

            /* ── Sidebar ──────────────────────────────────── */
            QFrame#Sidebar {
                background-color: #1E3A5F;
                border-right: 1px solid #2A4A72;
            }
            QLabel#BrandLabel {
                color: #F1F5F9;
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 0.4px;
                font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
            }
            QLabel#BrandSub {
                color: #38BDF8;
                font-size: 9px;
                letter-spacing: 2.5px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
            }

            /* ── Nav section label ────────────────────────── */
            QLabel#NavSection {
                color: #6B90B8;
                font-size: 9px;
                letter-spacing: 2px;
                font-weight: 600;
                padding: 0px 20px 6px 20px;
                font-family: 'Segoe UI', sans-serif;
            }

            /* ── Nav: idle ────────────────────────────────── */
            QPushButton#NavBtn {
                color: #A8C4DC;
                background: transparent;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 400;
                font-family: 'Segoe UI', sans-serif;
                margin: 1px 12px;
            }
            QPushButton#NavBtn:hover {
                background-color: #254E7A;
                color: #EBF3FB;
            }

            /* ── Nav: active ──────────────────────────────── */
            QPushButton#NavBtnActive {
                color: #FFFFFF;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0EA5E9, stop:1 #0284C7);
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI', sans-serif;
                margin: 1px 12px;
            }

            /* ── Topbar ───────────────────────────────────── */
            QFrame#Topbar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #EAECF0;
            }
            QLabel#TopTitle {
                font-size: 14px;
                font-weight: 600;
                color: #18181B;
                letter-spacing: 0.1px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#WelcomeLabel {
                font-size: 13px;
                color: #71717A;
                font-family: 'Segoe UI', sans-serif;
            }

            /* ── Logout ───────────────────────────────────── */
            QPushButton#LogoutBtn {
                color: #DC2626;
                border: 1px solid #FECACA;
                border-radius: 7px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 500;
                background: #FFF8F8;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#LogoutBtn:hover {
                background-color: #FEE2E2;
                border-color: #FCA5A5;
                color: #B91C1C;
            }

            /* ── Scroll area ──────────────────────────────── */
            QScrollArea {
                border: none;
                background: #F7F8FC;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        self.setObjectName("DashRoot")
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Brand block
        brand_container = QWidget()
        brand_container.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 #1E3A5F, stop:1 #193252);"
            "border-bottom: 1px solid #2A4A72;"
        )
        brand_v = QVBoxLayout(brand_container)
        brand_v.setContentsMargins(20, 26, 20, 22)
        brand_v.setSpacing(3)

        # Logo row: custom logo.png + brand name
        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)

        _logo_path = os.path.join(os.path.dirname(__file__), "icons", "logo.png")
        _logo_pixmap = QPixmap(_logo_path)
        if not _logo_pixmap.isNull():
            pill = QLabel()
            pill.setPixmap(
                _logo_pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
            )
            pill.setFixedSize(30, 30)
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pill.setStyleSheet("background: transparent; border: none;")
        else:
            pill = QLabel("\u271a")
            pill.setFixedSize(30, 30)
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pill.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #0EA5E9, stop:1 #0284C7);"
                "border-radius: 8px; color:#FFFFFF; font-size:14px; font-weight:700; border:none;"
            )

        brand = QLabel("MediTrack")
        brand.setObjectName("BrandLabel")
        logo_row.addWidget(pill)
        logo_row.addWidget(brand)
        logo_row.addStretch()

        brand_sub = QLabel("MEDICINE MONITORING")
        brand_sub.setObjectName("BrandSub")

        brand_v.addLayout(logo_row)
        brand_v.addWidget(brand_sub)
        sb_layout.addWidget(brand_container)

        sb_layout.addSpacing(14)

        # Nav section label
        nav_section = QLabel("MENU")
        nav_section.setObjectName("NavSection")
        sb_layout.addWidget(nav_section)

        self._nav_buttons = {}
        nav_items = [
            ("dashboard", "Dashboard"),
            ("inventory",  "Inventory"),
            ("add",        "Add Medicine"),
            ("expiry",     "Check Expiry"),
            ("report",     "Reports"),
        ]
        for key, label in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("NavBtnActive" if key == "dashboard" else "NavBtn")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, k=key: self._navigate(k))
            btn.setMinimumHeight(42)
            sb_layout.addWidget(btn)
            self._nav_buttons[key] = btn

        sb_layout.addStretch()

        # Sidebar footer — user card
        footer = QWidget()
        footer.setStyleSheet(
            "background: #162E4D;"
            "border-top: 1px solid #2A4A72;"
            "border-radius: 0px;"
        )
        footer_l = QHBoxLayout(footer)
        footer_l.setContentsMargins(16, 14, 16, 14)
        footer_l.setSpacing(10)

        _first_letter = self.username[0].upper() if self.username else "U"
        self.avatar_lbl = QLabel(_first_letter)
        self.avatar_lbl.setFixedSize(32, 32)
        self.avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_lbl.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #0EA5E9, stop:1 #0284C7);"
            "border-radius: 16px; color:#FFFFFF; font-size:13px;"
            "font-weight:700; font-family:'Segoe UI', sans-serif; border:none;"
        )
        footer_l.addWidget(self.avatar_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(0)
        self.footer_user_lbl = QLabel(self.username)
        self.footer_user_lbl.setStyleSheet(
            "color:#E2E8F0; font-size:12px; font-weight:600;"
            "font-family:'Segoe UI', sans-serif;"
        )
        ver_lbl = QLabel("Medicine Monitoring System")
        ver_lbl.setStyleSheet(
            "color:#6B90B8; font-size:10px;"
            "font-family:'Segoe UI', sans-serif;"
        )
        info_col.addWidget(self.footer_user_lbl)
        info_col.addWidget(ver_lbl)
        footer_l.addLayout(info_col)
        footer_l.addStretch()
        sb_layout.addWidget(footer)

        main.addWidget(sidebar)

        # ── Right side ───────────────────────────────────────
        right = QWidget()
        right.setObjectName("DashRoot")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Topbar
        topbar = QFrame()
        topbar.setObjectName("Topbar")
        topbar.setFixedHeight(54)
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(24, 0, 24, 0)

        top_title = QLabel("Medicine Monitoring System")
        top_title.setObjectName("TopTitle")

        self.welcome_label = QLabel(f"Welcome back, {self.username}")
        self.welcome_label.setObjectName("WelcomeLabel")

        logout_btn = QPushButton("  Logout")
        logout_btn.setObjectName("LogoutBtn")
        logout_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        logout_btn.clicked.connect(self._handle_logout)

        tb.addWidget(top_title)
        tb.addStretch()
        tb.addWidget(self.welcome_label)
        tb.addSpacing(20)
        tb.addWidget(logout_btn)
        right_layout.addWidget(topbar)

        # ── Content area ──────────────────────────────────────
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setStyleSheet("QScrollArea{border:none;background:#F7F8FC;}")
        right_layout.addWidget(self.content_area)

        main.addWidget(right)

        self.show_dashboard_content()

    # ── SWAP CONTENT ─────────────────────────────────────────
    def set_content(self, widget: QWidget):
        self.content_area.setWidget(widget)

    def show_dashboard_content(self, stats=None):
        if stats is None:
            stats = {"total": 0, "expired": 0, "expiring": 0, "low_stock": 0}

        content = QWidget()
        content.setObjectName("DashRoot")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(0)

        # ── Header ───────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        title = QLabel("Dashboard Overview")
        title.setStyleSheet(
            "font-size:22px; font-weight:700; color:#18181B; "
            "letter-spacing:-0.5px; font-family:'Segoe UI', sans-serif;"
        )
        sub = QLabel(f"Today is {QDate.currentDate().toString('dddd, MMMM d yyyy')}  ·  Here's what's happening.")
        sub.setStyleSheet(
            "font-size:12px; color:#9CA3AF; margin-top:1px; "
            "font-family:'Segoe UI', sans-serif;"
        )
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header_row.addLayout(title_col)
        header_row.addStretch()
        layout.addLayout(header_row)
        layout.addSpacing(28)

        # ── Stat cards ───────────────────────────────────────
        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)

        # Replace the icon path strings with your own PNG file paths.
        # Use transparent PNGs for best results — they render on the soft-color badge.
        # Example: "icons/pill.png", "C:/images/expired.png", or "" to use fallback text.
        cards_data = [
            ("#6366F1", "#EEF2FF", "#C7D2FE", "views/icons/medicine_icon.png",  "⬡", stats["total"],     "Total Medicines", ""),
            ("#EF4444", "#FEF2F2", "#FECACA", "views/icons/expired.png",  "✕", stats["expired"],   "Expired",          ""),
            ("#F97316", "#FFF7ED", "#FED7AA", "views/icons/excla.png",  "◷", stats["expiring"],  "Expiring Soon",    ""),
            ("#F59E0B", "#FFFBEB", "#FDE68A", "views/icons/low.png",  "↓", stats["low_stock"], "Low Stock",        ""),
        ]
        #                                      ↑ Put your image path here per card

        for accent, soft, border_c, img_path, fallback_icon, val, lbl, hint in cards_data:
            # ── Outer wrapper: gives us the rounded border + clip ──────────
            wrapper = QFrame()
            wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            wrapper.setMinimumHeight(100)
            wrapper.setStyleSheet(
                "QFrame{"
                "  background:#FFFFFF;"
                "  border-radius:10px;"
                "  border:1px solid #EAECF0;"
                "}"
            )
            wrapper_h = QHBoxLayout(wrapper)
            wrapper_h.setContentsMargins(0, 0, 0, 0)
            wrapper_h.setSpacing(0)

            # ── Colored left accent strip ───────────────────────────────────
            strip = QFrame()
            strip.setFixedWidth(5)
            strip.setStyleSheet(
                f"QFrame{{"
                f"  background:{accent};"
                f"  border-radius:0px;"
                f"  border:none;"
                f"  border-top-left-radius:10px;"
                f"  border-bottom-left-radius:10px;"
                f"}}"
            )
            wrapper_h.addWidget(strip)

            # ── Inner card content ──────────────────────────────────────────
            card = QFrame()
            card.setObjectName("card")
            card.setStyleSheet(
                "QFrame#card{background:transparent; border:none;}"
                "QFrame#card QLabel{border:none; background:transparent;}"
            )
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            wrapper_h.addWidget(card)

            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 14, 16, 14)
            cl.setSpacing(0)

            # ── Icon badge ───────────────────────────────────
            top_row = QHBoxLayout()
            ic = QLabel()
            ic.setFixedSize(30, 30)
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic.setStyleSheet(
                f"background:{soft}; border-radius:7px; "
                f"color:{accent}; font-size:13px; "
                f"border: 1px solid {border_c};"
            )

            if img_path:
                # Load your custom transparent PNG, scaled to fit the badge
                pixmap = QPixmap(img_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        18, 18,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    ic.setPixmap(pixmap)
                else:
                    # File not found — fall back to the Unicode icon
                    ic.setText(fallback_icon)
            else:
                # No path set — use the Unicode fallback
                ic.setText(fallback_icon)

            top_row.addWidget(ic)
            top_row.addStretch()
            cl.addLayout(top_row)
            cl.addSpacing(8)

            val_lbl = QLabel(str(val))
            val_lbl.setStyleSheet(
                "color:#18181B; font-size:24px; font-weight:700; "
                "font-family:'Segoe UI', sans-serif; letter-spacing:-1px;"
            )
            name_lbl = QLabel(lbl)
            name_lbl.setStyleSheet(
                "color:#52525B; font-size:12px; font-weight:600; "
                "font-family:'Segoe UI', sans-serif; margin-top:1px;"
            )
            hint_lbl = QLabel(hint)
            hint_lbl.setStyleSheet(
                "color:#A1A1AA; font-size:11px; "
                "font-family:'Segoe UI', sans-serif; margin-top:1px;"
            )
            cl.addWidget(val_lbl)
            cl.addWidget(name_lbl)
            cl.addWidget(hint_lbl)

            stat_row.addWidget(wrapper)

        layout.addLayout(stat_row)
        layout.addSpacing(24)

        # ── Bottom row ────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        # Quick Actions card
        qc = QFrame()
        qc.setObjectName("qc")
        qc.setStyleSheet(
            "QFrame#qc{background:#FFFFFF;border-radius:12px;border:1px solid #EAECF0;}"
            "QFrame#qc QLabel{border:none;background:transparent;}"
        )
        ql = QVBoxLayout(qc)
        ql.setContentsMargins(26, 24, 26, 24)
        ql.setSpacing(0)

        qt = QLabel("Quick Actions")
        qt.setStyleSheet(
            "font-size:14px;font-weight:700;color:#18181B;"
            "font-family:'Segoe UI', sans-serif;"
        )
        ql.addWidget(qt)

        qt_sub = QLabel("Common tasks at a glance")
        qt_sub.setStyleSheet(
            "font-size:11px;color:#A1A1AA;font-family:'Segoe UI', sans-serif;margin-top:2px;"
        )
        ql.addWidget(qt_sub)
        ql.addSpacing(16)

        action_items = [
            ("+ Add New Medicine", "add", True),
            ("View Inventory",     "inventory", False),
            ("Generate Report",    "report", False),
        ]
        for label, key, primary in action_items:
            b = QPushButton(label)
            b.setMinimumHeight(40)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if primary:
                b.setStyleSheet(
                    "background:#6366F1;color:#fff;border:none;border-radius:8px;"
                    "font-size:13px;font-weight:600;font-family:'Segoe UI', sans-serif;"
                    "padding:0 16px;"
                )
            else:
                b.setStyleSheet(
                    "background:#FAFAFA;color:#3F3F46;border:1px solid #E4E4E7;"
                    "border-radius:8px;font-size:13px;font-weight:500;"
                    "font-family:'Segoe UI', sans-serif;padding:0 16px;"
                )
            b.clicked.connect(lambda _, k=key: self._navigate(k))
            ql.addWidget(b)
            ql.addSpacing(8)

        ql.addStretch()
        bottom.addWidget(qc)

        # System Info card
        sc = QFrame()
        sc.setObjectName("sc")
        sc.setFixedWidth(320)
        sc.setStyleSheet(
            "QFrame#sc{background:#FFFFFF;border-radius:12px;border:1px solid #EAECF0;}"
            "QFrame#sc QLabel{border:none;background:transparent;}"
        )
        sl = QVBoxLayout(sc)
        sl.setContentsMargins(26, 24, 26, 24)
        sl.setSpacing(0)

        st = QLabel("System Information")
        st.setStyleSheet(
            "font-size:14px;font-weight:700;color:#18181B;"
            "font-family:'Segoe UI', sans-serif;"
        )
        sl.addWidget(st)

        st_sub = QLabel("Current system status")
        st_sub.setStyleSheet(
            "font-size:11px;color:#A1A1AA;font-family:'Segoe UI', sans-serif;margin-top:2px;"
        )
        sl.addWidget(st_sub)
        sl.addSpacing(16)

        today = QDate.currentDate().toString("dd/MM/yyyy")
        info_rows = [
            ("Last Updated", today,            False),
            ("Storage",      "MySQL Database",  False),
            ("Status",       "● Active",        True),
        ]
        for k, v, is_status in info_rows:
            row_w = QWidget()
            row_w.setMinimumHeight(38)
            row_w.setStyleSheet("QWidget { border-bottom: 1px solid #F4F4F5; } QLabel { border: none; }")
            row = QHBoxLayout(row_w)
            row.setContentsMargins(0, 6, 0, 6)

            kl = QLabel(k)
            kl.setStyleSheet(
                "color:#71717A;font-size:12px;font-family:'Segoe UI', sans-serif;"
            )
            vl = QLabel(v)
            vl.setStyleSheet(
                f"color:{'#16A34A' if is_status else '#27272A'};"
                f"font-size:12px;font-weight:600;"
                f"font-family:'Segoe UI', sans-serif;"
            )
            row.addWidget(kl)
            row.addStretch()
            row.addWidget(vl)
            sl.addWidget(row_w)

        sl.addStretch()
        bottom.addWidget(sc)

        layout.addLayout(bottom)
        layout.addStretch()

        self.content_area.setWidget(content)

    # ── NAV ACTIVE STATE ─────────────────────────────────────
    def set_active_nav(self, key: str):
        for k, btn in self._nav_buttons.items():
            btn.setObjectName("NavBtnActive" if k == key else "NavBtn")
            btn.setStyle(btn.style())

    def set_username(self, username: str):
        self.username = username
        self.welcome_label.setText(f"Welcome back, {username}")
        if hasattr(self, "avatar_lbl"):
            self.avatar_lbl.setText(username[0].upper() if username else "U")
        if hasattr(self, "footer_user_lbl"):
            self.footer_user_lbl.setText(username)

    # ── HANDLERS ─────────────────────────────────────────────
    def _navigate(self, key: str):
        self.set_active_nav(key)
        if self.on_navigate:
            self.on_navigate(key)

    def _handle_logout(self):
        if self.on_logout:
            self.on_logout()


# ── Standalone preview ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import os
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = DashboardView(
        username="admin",
        on_navigate=lambda k: print(f"Navigate: {k}"),
        on_logout=lambda: print("Logout")
    )
    win.show_dashboard_content({
        "total": 24, "expired": 2, "expiring": 5, "low_stock": 3
    })
    win.show()
    sys.exit(app.exec())