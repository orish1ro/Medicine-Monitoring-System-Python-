from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QStackedWidget, QAbstractItemView,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QCursor
from controllers.expiry_controller import (
    controller_get_expired,
    controller_get_expiring_soon,
    controller_get_alerts,
    controller_resolve_alert,
)
from utils.helpers import format_date, days_until_expiry


class ExpiryView(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id  = user_id
        self._days    = 30
        self._tab_idx = 0
        self._apply_styles()
        self._build_ui()
        self._load_data()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #F3F4F8; }

            /* ── Tables ── */
            QTableWidget {
                background: #FFFFFF;
                border: none;
                font-size: 13px;
                outline: none;
                selection-background-color: #EEF2FF;
                border-radius: 12px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 0px 12px;
                color: #1E293B;
                border-bottom: 1px solid #F1F5F9;
            }
            QTableWidget::item:selected {
                background-color: #EEF2FF;
                color: #111827;
            }
            QTableWidget::item:hover { background-color: #F8FAFC; }

            QHeaderView::section {
                background-color: #F8FAFC;
                color: #64748B;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.6px;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                text-transform: uppercase;
                font-family: 'Segoe UI', sans-serif;
            }

            /* ── Page title / labels ── */
            QLabel#PageTitle {
                font-size: 20px;
                font-weight: 700;
                color: #18181B;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#CountLabel {
                font-size: 12px;
                color: #6B7280;
                font-family: 'Segoe UI', sans-serif;
                background: #F3F4F6;
                border-radius: 10px;
                padding: 3px 10px;
            }
            QLabel#FieldLabel {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#DaysValue {
                font-size: 15px;
                font-weight: 700;
                color: #4F46E5;
                font-family: 'Segoe UI', sans-serif;
                background: #EEF2FF;
                border-radius: 8px;
                padding: 2px 12px;
                min-width: 36px;
                qproperty-alignment: AlignCenter;
            }

            /* ── Stepper buttons (±) ── */
            QPushButton#BtnStep {
                background: transparent;
                color: #1F2937;
                border: none;
                font-size: 18px;
                font-weight: 700;
                padding: 0px 4px;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnStep:hover { color: #1F2937; }
            QPushButton#BtnStep:pressed { color: #1F2937; }

            /* ── Refresh button ── */
            QPushButton#BtnRefresh {
                background: #FFFFFF;
                color: #4F46E5;
                border: 1px solid #C7D2FE;
                border-radius: 7px;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 16px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnRefresh:hover { background: #EEF2FF; }

            /* ── Tab buttons (custom) ── */
            QPushButton#BtnTab {
                background: #F3F4F6;
                color: #1F2937;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 18px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnTab:hover { background: #E9EAF0; color: #1F2937; }
            QPushButton#BtnTab:pressed { background: #E9EAF0; color: #1F2937; }
            QPushButton#BtnTabActive {
                background: #4F46E5;
                color: #1F2937;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 8px 18px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnTabActive:hover { background: #4338CA; color: #1F2937; }
            QPushButton#BtnTabActive:pressed { background: #3730A3; color: #1F2937; }

            /* ── Resolve button ── */
            QPushButton#BtnResolve {
                background: #F0FDF4;
                color: #15803D;
                border: 1.5px solid #BBF7D0;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 14px;
                min-width: 80px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnResolve:hover { background: #DCFCE7; border-color: #4ADE80; }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)

        # ── Header row ───────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(0)

        title = QLabel("Check Expiry")
        title.setObjectName("PageTitle")
        self.count_label = QLabel("— medicines")
        self.count_label.setObjectName("CountLabel")

        # "Expiring within" stepper
        lbl_within = QLabel("Expiring within")
        lbl_within.setObjectName("FieldLabel")

        btn_minus = QPushButton("−")
        btn_minus.setObjectName("BtnStep")
        btn_minus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_minus.clicked.connect(self._days_down)

        self.lbl_days_val = QLabel("30")
        self.lbl_days_val.setObjectName("DaysValue")

        btn_plus = QPushButton("+")
        btn_plus.setObjectName("BtnStep")
        btn_plus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_plus.clicked.connect(self._days_up)

        lbl_days = QLabel("days")
        lbl_days.setObjectName("FieldLabel")

        btn_refresh = QPushButton("⟳  Refresh")
        btn_refresh.setObjectName("BtnRefresh")
        btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_refresh.clicked.connect(self._load_data)

        header_row.addWidget(title)
        header_row.addSpacing(12)
        header_row.addWidget(self.count_label)
        header_row.addStretch()
        header_row.addWidget(lbl_within)
        header_row.addSpacing(8)
        header_row.addWidget(btn_minus)
        header_row.addSpacing(6)
        header_row.addWidget(self.lbl_days_val)
        header_row.addSpacing(6)
        header_row.addWidget(btn_plus)
        header_row.addSpacing(6)
        header_row.addWidget(lbl_days)
        header_row.addSpacing(14)
        header_row.addWidget(btn_refresh)
        root.addLayout(header_row)

        # ── Card ─────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("TableCard")
        card.setStyleSheet(
            "QFrame#TableCard{"
            "  background:#FFFFFF;"
            "  border-radius:12px;"
            "  border:1px solid #E5E7EB;"
            "}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── Custom tab bar (right-aligned) ───────────────────
        tab_bar_frame = QFrame()
        tab_bar_frame.setStyleSheet(
            "background:#F8FAFC; border-bottom:1px solid #E5E7EB;"
            "border-top-left-radius:12px; border-top-right-radius:12px;"
        )
        tab_bar_layout = QHBoxLayout(tab_bar_frame)
        tab_bar_layout.setContentsMargins(16, 10, 16, 10)
        tab_bar_layout.setSpacing(6)
        tab_bar_layout.addStretch()   # pushes buttons to the right

        self._tab_buttons = []
        tab_defs = [
            ("⚠  Expired",       0),
            ("◷  Expiring Soon", 1),
            ("🔔  Alerts",        2),
        ]
        for label, idx in tab_defs:
            btn = QPushButton(label)
            btn.setObjectName("BtnTabActive" if idx == 0 else "BtnTab")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, i=idx: self._switch_tab(i))
            self._tab_buttons.append(btn)
            tab_bar_layout.addWidget(btn)

        card_layout.addWidget(tab_bar_frame)

        # ── Stacked pages ────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:#FFFFFF;")

        self.table_expired  = self._make_table(
            ["Medicine", "Category", "Qty", "Unit", "Expiry Date", "Days Overdue"]
        )
        self.table_expiring = self._make_table(
            ["Medicine", "Category", "Qty", "Unit", "Expiry Date", "Days Left"]
        )
        self.table_alerts   = self._make_table(
            ["ID", "Type", "Medicine", "Message", "Action"]
        )
        self.table_alerts.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Fixed
        )
        self.table_alerts.setColumnWidth(4, 130)

        for tbl in (self.table_expired, self.table_expiring, self.table_alerts):
            w = QWidget()
            w.setStyleSheet("background:#FFFFFF;")
            l = QVBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(0)
            l.addWidget(tbl)
            self.stack.addWidget(w)

        card_layout.addWidget(self.stack)
        root.addWidget(card)

    # ── TAB SWITCHING ─────────────────────────────────────────
    def _switch_tab(self, idx):
        self._tab_idx = idx
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._tab_buttons):
            btn.setObjectName("BtnTabActive" if i == idx else "BtnTab")
            btn.setStyle(btn.style())   # force style refresh

    # ── STEPPER ───────────────────────────────────────────────
    def _days_down(self):
        if self._days > 1:
            self._days = max(1, self._days - (10 if self._days > 10 else 1))
            self.lbl_days_val.setText(str(self._days))

    def _days_up(self):
        if self._days < 365:
            self._days = min(365, self._days + (10 if self._days >= 10 else 1))
            self.lbl_days_val.setText(str(self._days))

    # ── TABLE FACTORY ─────────────────────────────────────────
    def _make_table(self, headers):
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.setShowGrid(False)
        t.setAlternatingRowColors(False)
        t.setMouseTracking(True)
        t.verticalHeader().setDefaultSectionSize(46)
        # Right-align headers for numeric/date columns
        for col in self._RIGHT_COLS:
            if col < len(headers):
                item = t.horizontalHeaderItem(col)
                if item:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
                    )
        return t

    # ── LOAD DATA ─────────────────────────────────────────────
    def _load_data(self):
        try:
            expired  = controller_get_expired()
            expiring = controller_get_expiring_soon(self._days)
            alerts   = controller_get_alerts()
        except Exception:
            return

        self._populate_expired(expired)
        self._populate_expiring(expiring)
        self._populate_alerts(alerts)

        total = len(expired) + len(expiring)
        self.count_label.setText(
            f"{total} medicine{'s' if total != 1 else ''} flagged"
        )

        # Update tab button labels with counts
        labels = [
            f"⚠  Expired  ({len(expired)})",
            f"◷  Expiring Soon  ({len(expiring)})",
            f"🔔  Alerts  ({len(alerts)})",
        ]
        for btn, lbl in zip(self._tab_buttons, labels):
            btn.setText(lbl)

    # ── POPULATE: EXPIRED ─────────────────────────────────────
    def _populate_expired(self, medicines):
        self.table_expired.setRowCount(0)
        if not medicines:
            self._set_empty(self.table_expired, "No expired medicines — great!", 6)
            return
        for i, m in enumerate(medicines):
            self.table_expired.insertRow(i)
            days_over = abs(days_until_expiry(m["expiry_date"]))
            self._set_row(self.table_expired, i, [
                m["name"], m.get("category_name", ""),
                str(m["quantity"]), m.get("unit_name", ""),
                format_date(m["expiry_date"]), str(days_over)
            ], bold_col=0)
            for col in range(6):
                item = self.table_expired.item(i, col)
                if item:
                    item.setForeground(QColor("#991B1B"))
                    item.setBackground(QColor("#FFF5F5"))

    # ── POPULATE: EXPIRING SOON ───────────────────────────────
    def _populate_expiring(self, medicines):
        self.table_expiring.setRowCount(0)
        if not medicines:
            self._set_empty(self.table_expiring, "No medicines expiring in this window.", 6)
            return
        for i, m in enumerate(medicines):
            self.table_expiring.insertRow(i)
            days_left = days_until_expiry(m["expiry_date"])
            self._set_row(self.table_expiring, i, [
                m["name"], m.get("category_name", ""),
                str(m["quantity"]), m.get("unit_name", ""),
                format_date(m["expiry_date"]), str(days_left)
            ], bold_col=0)
            for col in range(6):
                item = self.table_expiring.item(i, col)
                if item:
                    item.setForeground(QColor("#92400E"))
                    item.setBackground(QColor("#FFFBEB"))

    # ── POPULATE: ALERTS ──────────────────────────────────────
    def _populate_alerts(self, alerts):
        self.table_alerts.setRowCount(0)
        if not alerts:
            self._set_empty(self.table_alerts, "No unresolved alerts.", 5)
            return
        for i, a in enumerate(alerts):
            self.table_alerts.insertRow(i)
            self._set_row(self.table_alerts, i, [
                str(a["id"]),
                str(a.get("alert_type", "")),
                str(a.get("medicine_name", "")),
                str(a.get("message", "")),
            ])
            btn_wrap = QWidget()
            btn_wrap.setStyleSheet("background:#FFFFFF;")
            btn_layout = QHBoxLayout(btn_wrap)
            btn_layout.setContentsMargins(8, 4, 8, 4)
            btn = QPushButton("Resolve")
            btn.setObjectName("BtnResolve")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, aid=a["id"]: self._resolve_alert(aid))
            btn_layout.addWidget(btn)
            self.table_alerts.setCellWidget(i, 4, btn_wrap)

    # ── HELPERS ───────────────────────────────────────────────
    # Right-align numeric/date columns (Qty=2, Expiry Date=4, Days Left/Overdue=5)
    _RIGHT_COLS = {2, 4, 5}

    def _set_row(self, table, row_idx, values, bold_col=None):
        for col, val in enumerate(values):
            item = QTableWidgetItem(str(val))
            if col in self._RIGHT_COLS:
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
                )
            else:
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                )
            if col == bold_col:
                f = item.font()
                f.setBold(True)
                f.setPointSize(13)
                item.setFont(f)
            table.setItem(row_idx, col, item)

    def _set_empty(self, table, msg, col_span):
        table.setRowCount(1)
        item = QTableWidgetItem(msg)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(QColor("#9CA3AF"))
        table.setItem(0, 0, item)
        table.setSpan(0, 0, 1, col_span)
        table.setRowHeight(0, 80)

    def _resolve_alert(self, alert_id):
        try:
            success = controller_resolve_alert(alert_id)
            if success:
                QMessageBox.information(
                    self, "Resolved", f"Alert #{alert_id} has been resolved."
                )
                self._load_data()
            else:
                QMessageBox.warning(
                    self, "Error", f"Could not resolve alert #{alert_id}."
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ── Standalone preview ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = ExpiryView(user_id=1)
    win.setWindowTitle("Check Expiry")
    win.resize(1100, 650)
    win.show()
    sys.exit(app.exec())