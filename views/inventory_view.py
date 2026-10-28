from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QComboBox,
    QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox,
    QAbstractItemView, QButtonGroup, QRadioButton,
    QSizePolicy, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QColor, QFont, QCursor
from controllers.medicine_controller import MedicineController


class InventoryView(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self._apply_styles()
        self._build_ui()
        self.load_data()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #F3F4F8; }

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

            QTableWidget::item:hover {
                background-color: #F8FAFC;
            }

            QHeaderView::section {
                background-color: #F8FAFC;
                color: #64748B;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.6px;
                padding: 10px 10px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                text-transform: uppercase;
            }

            QPushButton#BtnStock {
                font-family: 'Segoe UI', sans-serif;
                background: #EFF6FF;
                color: #1D4ED8;
                border: 1.5px solid #BFDBFE;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 14px;
                min-width: 70px;
            }
            QPushButton#BtnStock:hover {
                background: #DBEAFE;
                border-color: #60A5FA;
            }
            QPushButton#BtnStock:disabled {
                background: #F1F5F9;
                color: #94A3B8;
                border-color: #E2E8F0;
            }

            QPushButton#BtnDispense {
                font-family: 'Segoe UI', sans-serif;
                background: #FFFBEB;
                color: #B45309;
                border: 1.5px solid #FDE68A;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 14px;
                min-width: 70px;
            }
            QPushButton#BtnDispense:hover {
                background: #FEF3C7;
                border-color: #FCD34D;
            }
            QPushButton#BtnDispense:disabled {
                background: #F1F5F9;
                color: #94A3B8;
                border-color: #E2E8F0;
            }

            QPushButton#BtnEdit {
                font-family: 'Segoe UI', sans-serif;
                background: #F0FDF4;
                color: #15803D;
                border: 1.5px solid #BBF7D0;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 14px;
                min-width: 70px;
            }
            QPushButton#BtnEdit:hover {
                background: #DCFCE7;
                border-color: #4ADE80;
            }
            QPushButton#BtnEdit:disabled {
                background: #F1F5F9;
                color: #94A3B8;
                border-color: #E2E8F0;
            }

            QPushButton#BtnDelete {
                font-family: 'Segoe UI', sans-serif;
                background: #FFF1F2;
                color: #B91C1C;
                border: 1.5px solid #FECACA;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 700;
                padding: 6px 14px;
                min-width: 70px;
            }
            QPushButton#BtnDelete:hover {
                background: #FEE2E2;
                border-color: #F87171;
            }
            QPushButton#BtnDelete:disabled {
                background: #F1F5F9;
                color: #94A3B8;
                border-color: #E2E8F0;
            }

            QPushButton#BtnRefresh {
                background: #FFFFFF;
                color: #4F46E5;
                border: 1px solid #C7D2FE;
                border-radius: 7px;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 16px;
            }
            QPushButton#BtnRefresh:hover {
                background: #EEF2FF;
            }

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
            QLineEdit#SearchInput {
                background: #FFFFFF;
                border: 1.5px solid #E5E7EB;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                color: #1E293B;
                font-family: 'Segoe UI', sans-serif;
                min-width: 220px;
            }
            QLineEdit#SearchInput:focus {
                border-color: #A5B4FC;
            }
            QComboBox#FilterCombo {
                background: #FFFFFF;
                border: 1.5px solid #E5E7EB;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                color: #1E293B;
                font-family: 'Segoe UI', sans-serif;
                min-width: 130px;
            }
            QComboBox#FilterCombo:focus {
                border-color: #A5B4FC;
            }
            QComboBox#FilterCombo::drop-down {
                border: none; width: 20px;
            }
            QComboBox#FilterCombo QAbstractItemView {
                background: #FFFFFF;
                color: #111827;
                selection-background-color: #EEF2FF;
                selection-color: #111827;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 4px;
                outline: none;
            }
            QLabel#LowStockWarning {
                background: #FFFBEB;
                color: #92400E;
                border: 1px solid #FDE68A;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 500;
            }

            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #111827;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
            }
            QMessageBox QPushButton {
                background: #4F46E5; color: #FFFFFF;
                border: none; border-radius: 7px;
                font-size: 12px; font-weight: 600;
                padding: 6px 20px; min-width: 70px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMessageBox QPushButton:hover { background: #4338CA; }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("View Inventory")
        title.setObjectName("PageTitle")
        self.count_label = QLabel("0 medicines")
        self.count_label.setObjectName("CountLabel")
        btn_refresh = QPushButton("⟳  Refresh")
        btn_refresh.setObjectName("BtnRefresh")
        btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_refresh.clicked.connect(self.load_data)
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(self.count_label)
        header_row.addSpacing(12)
        header_row.addWidget(btn_refresh)
        root.addLayout(header_row)

        # Low stock warning banner (hidden by default)
        self.low_stock_banner = QLabel("⚠  Some medicines are low on stock! Please restock soon.")
        self.low_stock_banner.setObjectName("LowStockWarning")
        self.low_stock_banner.setVisible(False)
        root.addWidget(self.low_stock_banner)

        # ── Search / filter bar ──────────────────────────────
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Search by name, manufacturer, or batch...")
        self.search_input.setClearButtonEnabled(True)

        self.filter_category = QComboBox()
        self.filter_category.setObjectName("FilterCombo")
        self.filter_category.addItem("All Categories", None)

        self.filter_status = QComboBox()
        self.filter_status.setObjectName("FilterCombo")
        for s in ["All Statuses", "Good", "Expiring Soon", "Low Stock", "Expired"]:
            self.filter_status.addItem(s)

        search_row.addWidget(self.search_input, 3)
        search_row.addWidget(self.filter_category, 1)
        search_row.addWidget(self.filter_status, 1)
        root.addLayout(search_row)

        # debounce timer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._apply_filter)
        self.search_input.textChanged.connect(lambda: self._search_timer.start())
        self.filter_category.currentIndexChanged.connect(self._apply_filter)
        self.filter_status.currentIndexChanged.connect(self._apply_filter)

        # Table card
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

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
        "Medicine", "Category", "Stock", "Unit",
        "Expiry", "Price", "Manufacturer", "Batch", "Status"
        ])

        header = self.table.horizontalHeader()

# Cleaner sizing
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)   # Medicine
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(8, 130)

# Better spacing
        self.table.verticalHeader().setDefaultSectionSize(62)

# Smooth modern feel
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)

# Hover highlight
        self.table.setMouseTracking(True)

# Cleaner row behavior
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

# Alternate rows
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)

        # ── Action toolbar (above table) ──────────────────────
        toolbar = QWidget()
        toolbar.setStyleSheet("background:#F8FAFC; border-bottom:1px solid #E5E7EB;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(14, 10, 14, 10)
        toolbar_layout.setSpacing(8)

        lbl_hint = QLabel("")
        lbl_hint.setStyleSheet(
            "font-size:12px; color:#6B7280; font-family:'Segoe UI',sans-serif; background:transparent;"
        )
        toolbar_layout.addWidget(lbl_hint)
        toolbar_layout.addStretch()

        self.btn_tb_stock = QPushButton("± Stock")
        self.btn_tb_stock.setObjectName("BtnStock")
        self.btn_tb_stock.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tb_stock.setEnabled(False)
        self.btn_tb_stock.clicked.connect(self._toolbar_stock)

        self.btn_tb_dispense = QPushButton("Dispense")
        self.btn_tb_dispense.setObjectName("BtnDispense")
        self.btn_tb_dispense.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tb_dispense.setEnabled(False)
        self.btn_tb_dispense.clicked.connect(self._toolbar_dispense)

        self.btn_tb_edit = QPushButton("Edit")
        self.btn_tb_edit.setObjectName("BtnEdit")
        self.btn_tb_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tb_edit.setEnabled(False)
        self.btn_tb_edit.clicked.connect(self._toolbar_edit)

        self.btn_tb_delete = QPushButton("Delete")
        self.btn_tb_delete.setObjectName("BtnDelete")
        self.btn_tb_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tb_delete.setEnabled(False)
        self.btn_tb_delete.clicked.connect(self._toolbar_delete)

        for btn in (self.btn_tb_stock, self.btn_tb_dispense,
                    self.btn_tb_edit, self.btn_tb_delete):
            btn.setMinimumHeight(32)
            btn.setMinimumWidth(80)
            toolbar_layout.addWidget(btn)

        card_layout.addWidget(toolbar)
        card_layout.addWidget(self.table)
        root.addWidget(card)

        # Enable toolbar buttons when a row is selected
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    # ── LOAD DATA ─────────────────────────────────────────────
    def load_data(self):
        medicines = MedicineController.get_all_medicines()
        self._medicines = medicines  # store for toolbar actions

        # Populate category filter (keep current selection)
        current_cat = self.filter_category.currentData()
        self.filter_category.blockSignals(True)
        self.filter_category.clear()
        self.filter_category.addItem("All Categories", None)
        seen = set()
        for m in medicines:
            cat = m.get("category", "")
            if cat and cat not in seen:
                seen.add(cat)
                self.filter_category.addItem(cat, cat)
        # restore selection
        for i in range(self.filter_category.count()):
            if self.filter_category.itemData(i) == current_cat:
                self.filter_category.setCurrentIndex(i)
                break
        self.filter_category.blockSignals(False)
        self.table.setRowCount(0)
        self.count_label.setText(f"{len(medicines)} medicine{'s' if len(medicines)!=1 else ''}")

        # Check low stock for banner
        low_count = sum(1 for m in medicines
                        if m["quantity"] <= m.get("low_stock_threshold", 10))
        self.low_stock_banner.setVisible(low_count > 0)
        if low_count > 0:
            self.low_stock_banner.setText(
                f"⚠  {low_count} medicine{'s' if low_count>1 else ''} "
                f"{'are' if low_count>1 else 'is'} low on stock! Please restock soon."
            )

        if not medicines:
            self.table.setRowCount(1)
            empty = QTableWidgetItem("No medicines in inventory. Add your first medicine.")
            empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setForeground(QColor("#9CA3AF"))
            self.table.setItem(0, 0, empty)
            self.table.setSpan(0, 0, 1, 9)
            return

        self.table.setSpan(0, 0, 1, 1)

        for row_idx, med in enumerate(medicines):
            self.table.insertRow(row_idx)
            expiry     = med["expiry_date"]
            qty        = med["quantity"]
            threshold  = med.get("low_stock_threshold", 10)
            status, color = self._get_status(expiry, qty, threshold)
            is_low     = (status == "Low Stock")
            is_expired = (status == "Expired")

            # ── Row background highlight ──────────────────────
            row_bg = None
            if is_expired:
                row_bg = QColor("#FFF5F5")
            elif is_low:
                row_bg = QColor("#FFFBEB")

            self._set_item(row_idx, 0, med["name"],         bold=True,  row_bg=row_bg)
            self._set_item(row_idx, 1, med["category"],                  row_bg=row_bg)

            # Stock — colored red if low
            bg = row_bg.name() if row_bg else '#FFFFFF'
            stock_color = "#EF4444" if is_low else "#1E293B"
            stock_weight = "700" if is_low else "400"
            stock_label = QLabel(str(qty))
            stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stock_label.setStyleSheet(
                f"background-color: {bg}; color: {stock_color}; "
                f"font-weight: {stock_weight}; font-size: 13px; "
                f"font-family: 'Segoe UI', sans-serif;"
            )
            self.table.setCellWidget(row_idx, 2, stock_label)

            self._set_item(row_idx, 3, med["unit"],                      row_bg=row_bg)
            self._set_item(row_idx, 4, str(expiry),                      row_bg=row_bg)
            self._set_item(row_idx, 5, f"₱{float(med['price']):.2f}",   row_bg=row_bg)
            self._set_item(row_idx, 6, med["manufacturer"],              row_bg=row_bg)
            self._set_item(row_idx, 7, med["batch_number"],              row_bg=row_bg)

            # Status badge — compact pill
            badge_widget = QWidget()
            badge_widget.setStyleSheet(f"background: {row_bg.name() if row_bg else '#FFFFFF'};")
            badge_layout = QHBoxLayout(badge_widget)
            badge_layout.setContentsMargins(4, 0, 4, 0)
            badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge_label = QLabel(status)
            badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge_label.setStyleSheet(f"""
                background-color: {color['bg']};
                color: {color['text']};
                border-radius: 8px;
                padding: 3px 6px;
                font-size: 11px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
                min-width: 90px;
            """)
            badge_layout.addWidget(badge_label)
            self.table.setCellWidget(row_idx, 8, badge_widget)

            self.table.setRowHeight(row_idx, 46)

    # ── FILTER ───────────────────────────────────────────────
    def _apply_filter(self):
        keyword  = self.search_input.text().strip().lower()
        cat      = self.filter_category.currentData()       # None = all
        status_f = self.filter_status.currentText()

        if not hasattr(self, '_medicines'):
            return

        for row in range(self.table.rowCount()):
            med = self._medicines[row] if row < len(self._medicines) else None
            if med is None:
                self.table.setRowHidden(row, False)
                continue

            # keyword match
            if keyword:
                haystack = " ".join([
                    str(med.get("name", "")),
                    str(med.get("manufacturer", "")),
                    str(med.get("batch_number", "")),
                ]).lower()
                if keyword not in haystack:
                    self.table.setRowHidden(row, True)
                    continue

            # category match
            if cat and med.get("category", "") != cat:
                self.table.setRowHidden(row, True)
                continue

            # status match
            if status_f != "All Statuses":
                expiry    = med["expiry_date"]
                qty       = med["quantity"]
                threshold = med.get("low_stock_threshold", 10)
                row_status, _ = self._get_status(expiry, qty, threshold)
                if row_status != status_f:
                    self.table.setRowHidden(row, True)
                    continue

            self.table.setRowHidden(row, False)

    # ── HELPERS ───────────────────────────────────────────────
    def _set_item(self, row, col, text, bold=False, row_bg=None, fg=None):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        if bold:
            f = item.font(); f.setPointSize(13); f.setBold(True); item.setFont(f)
        if row_bg:
            item.setBackground(row_bg)
        if fg:
            item.setForeground(QColor(fg))
        self.table.setItem(row, col, item)

    def _get_status(self, expiry_date, qty, threshold=10):
        from datetime import date
        today = date.today()
        expiry = expiry_date if not hasattr(expiry_date, 'toPyDate') else expiry_date.toPyDate()
        if expiry < today:
            return "Expired",       {"text": "#991B1B", "bg": "#FEE2E2"}
        if (expiry - today).days <= 30:
            return "Expiring Soon", {"text": "#9A3412", "bg": "#FFEDD5"}
        if qty <= threshold:
            return "Low Stock",     {"text": "#92400E", "bg": "#FEF3C7"}
        return "Good",              {"text": "#166534", "bg": "#DCFCE7"}

    # ── TOOLBAR SELECTION ─────────────────────────────────────
    def _on_selection_changed(self):
        has_selection = bool(self.table.selectedItems())
        for btn in (self.btn_tb_stock, self.btn_tb_dispense,
                    self.btn_tb_edit, self.btn_tb_delete):
            btn.setEnabled(has_selection)

    def _selected_medicine(self):
        rows = self.table.selectedItems()
        if not rows:
            return None
        row = self.table.currentRow()
        if hasattr(self, '_medicines') and row < len(self._medicines):
            return self._medicines[row]
        return None

    def _toolbar_stock(self):
        med = self._selected_medicine()
        if med:
            self._open_stock_adjust(med)

    def _toolbar_dispense(self):
        med = self._selected_medicine()
        if med:
            self._open_dispense(med)

    def _toolbar_edit(self):
        med = self._selected_medicine()
        if med:
            self._open_edit(med)

    def _toolbar_delete(self):
        med = self._selected_medicine()
        if med:
            self._confirm_delete(med)


    def _open_stock_adjust(self, med):
        dialog = StockAdjustDialog(med, user_id=self.user_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    # ── 2. DISPENSE DIALOG ────────────────────────────────────
    def _open_dispense(self, med):
        dialog = DispenseDialog(med, user_id=self.user_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    # ── 3. EDIT DIALOG ────────────────────────────────────────
    def _open_edit(self, med):
        dialog = EditMedicineDialog(med, user_id=self.user_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    # ── DELETE ────────────────────────────────────────────────
    def _confirm_delete(self, med):
        reply = QMessageBox.question(
            self, "Delete Medicine",
            f"Are you sure you want to delete '{med['name']}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = MedicineController.delete_medicine(med["id"], user_id=self.user_id)
            if result.get("success"):
                QMessageBox.information(self, "Deleted", f"'{med['name']}' deleted.")
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", result.get("error", "Delete failed."))


# ══════════════════════════════════════════════════════════════
# 1. STOCK ADJUSTMENT DIALOG
# ══════════════════════════════════════════════════════════════
class StockAdjustDialog(QDialog):
    def __init__(self, medicine, user_id=None, parent=None):
        super().__init__(parent)
        self.medicine = medicine
        self.user_id  = user_id
        self.setWindowTitle(f"Adjust Stock — {medicine['name']}")
        self.setFixedWidth(400)
        self._apply_styles()
        self._build_ui()

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#DlgTitle {
                font-size: 16px; font-weight: 700; color: #18181B;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#DlgSub {
                font-size: 12px; color: #6B7280;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#CurrentStock {
                font-size: 32px; font-weight: 800; color: #4F46E5;
                font-family: 'Segoe UI', sans-serif;
                qproperty-alignment: AlignCenter;
            }
            QLabel#StockSub {
                font-size: 11px; color: #6B7280;
                font-family: 'Segoe UI', sans-serif;
                qproperty-alignment: AlignCenter;
            }
            QLabel#FieldLabel {
                font-size: 12px; font-weight: 600; color: #374151;
                font-family: 'Segoe UI', sans-serif;
            }
            QSpinBox#Input, QLineEdit#Input {
                border: 1.5px solid #E5E7EB; border-radius: 8px;
                padding: 9px 12px; font-size: 14px; font-weight: 500;
                color: #1F2937; background: #FFFFFF; min-height: 38px;
                font-family: 'Segoe UI', sans-serif;
            }
            QSpinBox#Input:focus, QLineEdit#Input:focus {
                border-color: #6366F1;
                background: #FAFAFE;
            }
            QSpinBox#Input::up-button, QDoubleSpinBox#Input::up-button,
            QSpinBox#Input::down-button, QDoubleSpinBox#Input::down-button {
                width: 18px;
                border: none;
                background: #F3F4F6;
                border-radius: 4px;
                margin: 2px 2px;
            }
            QSpinBox#Input::up-button:hover, QDoubleSpinBox#Input::up-button:hover,
            QSpinBox#Input::down-button:hover, QDoubleSpinBox#Input::down-button:hover {
                background: #E5E7EB;
            }
            QSpinBox#Input::up-arrow, QDoubleSpinBox#Input::up-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #6B7280;
            }
            QSpinBox#Input::down-arrow, QDoubleSpinBox#Input::down-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #6B7280;
            }
            QRadioButton {
                font-size: 13px; color: #374151; padding: 4px 8px;
                font-family: 'Segoe UI', sans-serif;
            }
            QRadioButton::indicator { width: 16px; height: 16px; }
            QPushButton#BtnAdd {
                background: #FFFFFF; color: #111827;
                border: 2px solid #111827; border-radius: 9px;
                font-size: 14px; font-weight: 700;
                padding: 12px 0px; min-height: 44px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnAdd:hover   { background: #F3F4F6; color: #111827; }
            QPushButton#BtnAdd:pressed { background: #E5E7EB; color: #111827; }
            QPushButton#BtnDeduct {
                background: #FFFFFF; color: #111827;
                border: 2px solid #111827; border-radius: 9px;
                font-size: 14px; font-weight: 700;
                padding: 12px 0px; min-height: 44px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnDeduct:hover   { background: #F3F4F6; color: #111827; }
            QPushButton#BtnDeduct:pressed { background: #E5E7EB; color: #111827; }
            QPushButton#BtnCancel {
                background: #FFFFFF; color: #111827;
                border: 1.5px solid #D1D5DB; border-radius: 9px;
                font-size: 14px; font-weight: 500;
                padding: 10px 0px; min-height: 44px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnCancel:hover   { background: #F9FAFB; color: #111827; }
            QPushButton#BtnCancel:pressed { background: #F3F4F6; color: #111827; }
        """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Colored header strip ──────────────────────────────
        header = QFrame()
        header.setStyleSheet("background:#4F46E5; border-radius:0px;")
        header.setFixedHeight(72)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(22, 14, 22, 14)
        h_layout.setSpacing(2)
        title = QLabel("± Stock Adjustment")
        title.setStyleSheet(
            "color:#FFFFFF; font-size:16px; font-weight:700;"
            " font-family:'Segoe UI', sans-serif; background:transparent;"
        )
        sub = QLabel(self.medicine["name"])
        sub.setStyleSheet(
            "color:#C7D2FE; font-size:12px;"
            " font-family:'Segoe UI', sans-serif; background:transparent;"
        )
        h_layout.addWidget(title)
        h_layout.addWidget(sub)
        layout.addWidget(header)

        # ── Body ─────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background:#FFFFFF;")
        b_layout = QVBoxLayout(body)
        b_layout.setContentsMargins(22, 18, 22, 20)
        b_layout.setSpacing(12)

        # Current stock card
        stock_frame = QFrame()
        stock_frame.setStyleSheet(
            "background:#EEF2FF; border-radius:10px; border:1px solid #C7D2FE;"
        )
        sf_layout = QVBoxLayout(stock_frame)
        sf_layout.setContentsMargins(14, 12, 14, 12)
        sf_layout.setSpacing(2)
        stock_num = QLabel(str(self.medicine["quantity"]))
        stock_num.setObjectName("CurrentStock")
        stock_sub = QLabel(f"units currently in stock  ·  {self.medicine['unit']}")
        stock_sub.setObjectName("StockSub")
        sf_layout.addWidget(stock_num)
        sf_layout.addWidget(stock_sub)
        b_layout.addWidget(stock_frame)

        # Amount input
        amt_lbl = QLabel("Amount")
        amt_lbl.setObjectName("FieldLabel")
        b_layout.addWidget(amt_lbl)
        self.spin_amount = QSpinBox()
        self.spin_amount.setObjectName("Input")
        self.spin_amount.setRange(1, 999999)
        self.spin_amount.setValue(1)
        b_layout.addWidget(self.spin_amount)

        # Reason
        reason_lbl = QLabel("Reason  (optional)")
        reason_lbl.setObjectName("FieldLabel")
        b_layout.addWidget(reason_lbl)
        self.input_reason = QLineEdit()
        self.input_reason.setObjectName("Input")
        self.input_reason.setPlaceholderText("e.g., Restock, Damaged, Return...")
        b_layout.addWidget(self.input_reason)

        b_layout.addSpacing(4)

        # Add / Deduct row
        btn_add = QPushButton("＋  Add Stock")
        btn_add.setObjectName("BtnAdd")
        btn_add.setMinimumHeight(44)
        btn_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_add.clicked.connect(lambda: self._adjust("add"))
        b_layout.addWidget(btn_add)

        btn_deduct = QPushButton("－  Deduct Stock")
        btn_deduct.setObjectName("BtnDeduct")
        btn_deduct.setMinimumHeight(44)
        btn_deduct.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_deduct.clicked.connect(lambda: self._adjust("deduct"))
        b_layout.addWidget(btn_deduct)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("BtnCancel")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        b_layout.addWidget(btn_cancel)

        layout.addWidget(body)

    def _adjust(self, mode):
        amount  = self.spin_amount.value()
        reason  = self.input_reason.text().strip() or ("Restock" if mode == "add" else "Stock deduction")
        current = self.medicine["quantity"]

        if mode == "deduct" and amount > current:
            QMessageBox.warning(self, "Invalid",
                f"Cannot deduct {amount}. Only {current} in stock.")
            return

        new_qty = current + amount if mode == "add" else current - amount

        result = MedicineController.update_medicine(
            medicine_id     = self.medicine["id"],
            name            = self.medicine["name"],
            category_id     = self.medicine["category_id"],
            manufacturer_id = self.medicine["manufacturer_id"],
            unit_id         = self.medicine["unit_id"],
            quantity        = new_qty,
            expiry_date     = str(self.medicine["expiry_date"]),
            price           = float(self.medicine["price"]),
            batch_number    = self.medicine["batch_number"],
            low_stock_threshold = self.medicine.get("low_stock_threshold", 10),
            user_id         = self.user_id
        )

        if result.get("success"):
            action = "Added" if mode == "add" else "Deducted"
            QMessageBox.information(self, "Success",
                f"✅ {action} {amount} {self.medicine['unit']}.\n"
                f"New stock: {new_qty} {self.medicine['unit']}\n"
                f"Reason: {reason}")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", result.get("error", "Update failed."))


# ══════════════════════════════════════════════════════════════
# 2. DISPENSE DIALOG
# ══════════════════════════════════════════════════════════════
class DispenseDialog(QDialog):
    def __init__(self, medicine, user_id=None, parent=None):
        super().__init__(parent)
        self.medicine = medicine
        self.user_id  = user_id
        self.setWindowTitle(f"Dispense — {medicine['name']}")
        self.setFixedWidth(400)
        self._apply_styles()
        self._build_ui()

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog { background: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QLabel#FieldLabel {
                font-size: 12px; font-weight: 600; color: #374151;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#TotalLabel {
                font-size: 15px; font-weight: 700; color: #D97706;
                background: #FFFBEB; border-radius: 8px; padding: 10px 14px;
                border: 1px solid #FDE68A;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit#Input, QSpinBox#Input {
                border: 1.5px solid #E5E7EB; border-radius: 8px;
                padding: 9px 12px; font-size: 13px;
                color: #1F2937; background: #FFFFFF; min-height: 38px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit#Input:focus, QSpinBox#Input:focus {
                border-color: #F59E0B; background: #FFFDF7;
            }
            QSpinBox#Input::up-button, QDoubleSpinBox#Input::up-button,
            QSpinBox#Input::down-button, QDoubleSpinBox#Input::down-button {
                width: 18px;
                border: none;
                background: #F3F4F6;
                border-radius: 4px;
                margin: 2px 2px;
            }
            QSpinBox#Input::up-button:hover, QDoubleSpinBox#Input::up-button:hover,
            QSpinBox#Input::down-button:hover, QDoubleSpinBox#Input::down-button:hover {
                background: #E5E7EB;
            }
            QSpinBox#Input::up-arrow, QDoubleSpinBox#Input::up-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #6B7280;
            }
            QSpinBox#Input::down-arrow, QDoubleSpinBox#Input::down-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #6B7280;
            }
            QPushButton#BtnDispense {
                background: #FFFFFF; color: #111827;
                border: 2px solid #111827; border-radius: 9px;
                font-size: 14px; font-weight: 700; padding: 13px 0px; min-height: 44px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnDispense:hover   { background: #F3F4F6; color: #111827; }
            QPushButton#BtnDispense:pressed { background: #E5E7EB; color: #111827; }
            QPushButton#BtnCancel {
                background: #FFFFFF; color: #111827;
                border: 2px solid #D1D5DB; border-radius: 9px;
                font-size: 14px; font-weight: 600; padding: 10px 0px; min-height: 38px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnCancel:hover   { background: #F3F4F6; color: #111827; }
            QPushButton#BtnCancel:pressed { background: #E5E7EB; color: #111827; }
        """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Colored header strip ──────────────────────────────
        header = QFrame()
        header.setStyleSheet("background:#D97706; border-radius:0px;")
        header.setFixedHeight(72)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(22, 14, 22, 14)
        h_layout.setSpacing(2)
        h_title = QLabel("💊  Dispense Medicine")
        h_title.setStyleSheet(
            "color:#FFFFFF; font-size:16px; font-weight:700;"
            " font-family:'Segoe UI', sans-serif; background:transparent;"
        )
        h_sub = QLabel(f"{self.medicine['name']}  ·  {self.medicine['quantity']} {self.medicine['unit']} available")
        h_sub.setStyleSheet(
            "color:#FEF3C7; font-size:12px;"
            " font-family:'Segoe UI', sans-serif; background:transparent;"
        )
        h_layout.addWidget(h_title)
        h_layout.addWidget(h_sub)
        layout.addWidget(header)

        # ── Body ─────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background:#FFFFFF;")
        b_layout = QVBoxLayout(body)
        b_layout.setContentsMargins(22, 18, 22, 20)
        b_layout.setSpacing(11)

        # Patient name
        pt_lbl = QLabel("Patient / Customer Name *")
        pt_lbl.setObjectName("FieldLabel")
        b_layout.addWidget(pt_lbl)
        self.input_patient = QLineEdit()
        self.input_patient.setObjectName("Input")
        self.input_patient.setPlaceholderText("e.g., Juan Dela Cruz")
        b_layout.addWidget(self.input_patient)

        # Quantity row
        qty_row = QHBoxLayout(); qty_row.setSpacing(12)

        qty_col = QVBoxLayout(); qty_col.setSpacing(5)
        qty_lbl = QLabel("Quantity *")
        qty_lbl.setObjectName("FieldLabel")
        self.spin_qty = QSpinBox()
        self.spin_qty.setObjectName("Input")
        self.spin_qty.setRange(1, self.medicine["quantity"] or 1)
        self.spin_qty.setValue(1)
        qty_col.addWidget(qty_lbl)
        qty_col.addWidget(self.spin_qty)
        qty_row.addLayout(qty_col)

        b_layout.addLayout(qty_row)

        # Live total
        self.total_label = QLabel("Total: ₱0.00")
        self.total_label.setObjectName("TotalLabel")
        self.spin_qty.valueChanged.connect(self._update_total)
        self._update_total(1)
        b_layout.addWidget(self.total_label)

        # Notes
        notes_lbl = QLabel("Notes  (optional)")
        notes_lbl.setObjectName("FieldLabel")
        b_layout.addWidget(notes_lbl)
        self.input_notes = QLineEdit()
        self.input_notes.setObjectName("Input")
        self.input_notes.setPlaceholderText("e.g., Prescription #12345")
        b_layout.addWidget(self.input_notes)

        b_layout.addSpacing(4)

        # Buttons
        btn_dispense = QPushButton("✔  Confirm Dispense")
        btn_dispense.setObjectName("BtnDispense")
        btn_dispense.setMinimumHeight(44)
        btn_dispense.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_dispense.clicked.connect(self._handle_dispense)
        b_layout.addWidget(btn_dispense)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("BtnCancel")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        b_layout.addWidget(btn_cancel)

        layout.addWidget(body)

    def _update_total(self, qty):
        total = qty * float(self.medicine["price"])
        self.total_label.setText(f"  Total: ₱{total:.2f}")

    def _handle_dispense(self):
        patient = self.input_patient.text().strip()
        qty     = self.spin_qty.value()
        notes   = self.input_notes.text().strip()

        if not patient:
            QMessageBox.warning(self, "Required", "Please enter patient/customer name.")
            return

        if qty > self.medicine["quantity"]:
            QMessageBox.warning(self, "Insufficient Stock",
                f"Only {self.medicine['quantity']} {self.medicine['unit']} available.")
            return

        new_qty = self.medicine["quantity"] - qty
        total   = qty * float(self.medicine["price"])
        changes = (f"Dispensed {qty} {self.medicine['unit']} to {patient}. "
                   f"Total: ₱{total:.2f}. Notes: {notes or 'None'}")

        result = MedicineController.update_medicine(
            medicine_id     = self.medicine["id"],
            name            = self.medicine["name"],
            category_id     = self.medicine["category_id"],
            manufacturer_id = self.medicine["manufacturer_id"],
            unit_id         = self.medicine["unit_id"],
            quantity        = new_qty,
            expiry_date     = str(self.medicine["expiry_date"]),
            price           = float(self.medicine["price"]),
            batch_number    = self.medicine["batch_number"],
            low_stock_threshold = self.medicine.get("low_stock_threshold", 10),
            user_id         = self.user_id
        )

        if result.get("success"):
            # Log to audit
            from database.db_connection import get_connection, close_connection
            conn = get_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO audit_log (user_id, medicine_id, action, changes)
                        VALUES (%s, %s, %s, %s)
                    """, (self.user_id, self.medicine["id"], "DISPENSE", changes))
                    conn.commit()
                    cur.close()
                except Exception as e:
                    print(f"[Dispense] audit log error: {e}")
                finally:
                    close_connection(conn)

            QMessageBox.information(self, "Dispensed",
                f"✅ Successfully dispensed!\n\n"
                f"Patient:   {patient}\n"
                f"Medicine:  {self.medicine['name']}\n"
                f"Quantity:  {qty} {self.medicine['unit']}\n"
                f"Total:     ₱{total:.2f}\n"
                f"Remaining: {new_qty} {self.medicine['unit']}")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", result.get("error", "Dispense failed."))


# ══════════════════════════════════════════════════════════════
# 3. EDIT DIALOG (unchanged, kept here)
# ══════════════════════════════════════════════════════════════
class EditMedicineDialog(QDialog):
    def __init__(self, medicine, user_id=None, parent=None):
        super().__init__(parent)
        self.medicine = medicine
        self.user_id  = user_id
        self.setWindowTitle(f"Edit — {medicine['name']}")
        self.setMinimumWidth(560)
        self._categories    = MedicineController.get_categories()
        self._manufacturers = MedicineController.get_manufacturers()
        self._units         = MedicineController.get_units()
        self._apply_styles()
        self._build_ui()
        self._fill_data()

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog { background: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QLabel#FieldLabel {
                font-size: 12px; font-weight: 600; color: #374151;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit#Input, QComboBox#Input, QDateEdit#Input,
            QDoubleSpinBox#Input, QSpinBox#Input {
                border: 1.5px solid #E5E7EB; border-radius: 8px;
                padding: 8px 12px; font-size: 13px; color: #1F2937;
                background: #FFFFFF; min-height: 36px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit#Input:focus, QComboBox#Input:focus,
            QDateEdit#Input:focus, QDoubleSpinBox#Input:focus,
            QSpinBox#Input:focus {
                border-color: #6366F1;
                background: #FAFAFE;
            }
            QSpinBox#Input::up-button, QDoubleSpinBox#Input::up-button,
            QSpinBox#Input::down-button, QDoubleSpinBox#Input::down-button {
                width: 18px;
                border: none;
                background: #F3F4F6;
                border-radius: 4px;
                margin: 2px 2px;
            }
            QSpinBox#Input::up-button:hover, QDoubleSpinBox#Input::up-button:hover,
            QSpinBox#Input::down-button:hover, QDoubleSpinBox#Input::down-button:hover {
                background: #E5E7EB;
            }
            QSpinBox#Input::up-arrow, QDoubleSpinBox#Input::up-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #6B7280;
            }
            QSpinBox#Input::down-arrow, QDoubleSpinBox#Input::down-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #6B7280;
            }
            QComboBox#Input::drop-down { border: none; width: 20px; }
            QPushButton#BtnSave {
                background: #FFFFFF; color: #111827;
                border: 2px solid #111827; border-radius: 9px;
                font-size: 14px; font-weight: 700;
                padding: 13px 32px; min-height: 44px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnSave:hover   { background: #F3F4F6; color: #111827; }
            QPushButton#BtnSave:pressed { background: #E5E7EB; color: #111827; }
            QPushButton#BtnCancel {
                background: #FFFFFF; color: #111827;
                border: 2px solid #D1D5DB; border-radius: 9px;
                font-size: 14px; font-weight: 600;
                padding: 10px 20px; min-height: 38px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnCancel:hover   { background: #F3F4F6; color: #111827; }
            QPushButton#BtnCancel:pressed { background: #E5E7EB; color: #111827; }
            QFrame#Divider {
                background: #F1F5F9;
                max-height: 1px;
                border: none;
            }

            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #111827;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                background: transparent;
            }
            QMessageBox QPushButton {
                background: #4F46E5; color: #FFFFFF;
                border: none; border-radius: 7px;
                font-size: 12px; font-weight: 600;
                padding: 6px 20px; min-width: 70px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMessageBox QPushButton:hover { background: #4338CA; }
        """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Colored header strip ──────────────────────────────
        header = QFrame()
        header.setStyleSheet("background:#4F46E5; border-radius:0px;")
        header.setFixedHeight(72)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(24, 14, 24, 14)
        h_layout.setSpacing(2)
        h_title = QLabel("✏  Edit Medicine")
        h_title.setStyleSheet(
            "color:#FFFFFF; font-size:16px; font-weight:700;"
            " font-family:'Segoe UI', sans-serif; background:transparent;"
        )
        h_sub = QLabel(self.medicine["name"])
        h_sub.setStyleSheet(
            "color:#C7D2FE; font-size:12px;"
            " font-family:'Segoe UI', sans-serif; background:transparent;"
        )
        h_layout.addWidget(h_title)
        h_layout.addWidget(h_sub)
        layout.addWidget(header)

        # ── Body ─────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet("background:#FFFFFF;")
        b_layout = QVBoxLayout(body)
        b_layout.setContentsMargins(24, 18, 24, 20)
        b_layout.setSpacing(12)

        g1 = QHBoxLayout(); g1.setSpacing(14)
        g2 = QHBoxLayout(); g2.setSpacing(14)
        g3 = QHBoxLayout(); g3.setSpacing(14)
        g4 = QHBoxLayout(); g4.setSpacing(14)

        self.e_name         = self._field(g1, "Medicine Name *", QLineEdit)
        self.e_category     = self._combo_field(g1, "Category *",     self._categories)
        self.e_qty          = self._spin_field(g2, "Quantity *",      QSpinBox,       0, 999999)
        self.e_unit         = self._combo_field(g2, "Unit *",         self._units)
        self.e_expiry       = self._date_field(g3, "Expiry Date *")
        self.e_price        = self._spin_field(g3, "Price (₱) *",    QDoubleSpinBox, 0, 9999999, decimals=2)
        self.e_manufacturer = self._combo_field(g4, "Manufacturer *", self._manufacturers)
        self.e_batch        = self._field(g4, "Batch Number *",       QLineEdit)

        b_layout.addLayout(g1); b_layout.addLayout(g2)
        b_layout.addLayout(g3); b_layout.addLayout(g4)

        # Divider
        div = QFrame(); div.setObjectName("Divider")
        div.setFrameShape(QFrame.Shape.HLine)
        b_layout.addSpacing(4)
        b_layout.addWidget(div)
        b_layout.addSpacing(4)

        # Buttons
        btn_save = QPushButton("💾  Save Changes")
        btn_save.setObjectName("BtnSave")
        btn_save.setMinimumHeight(44)
        btn_save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_save.clicked.connect(self._handle_save)
        b_layout.addWidget(btn_save)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("BtnCancel")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        b_layout.addWidget(btn_cancel)

        layout.addWidget(body)

    def _field(self, grid, label, widget_cls):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        w = widget_cls(); w.setObjectName("Input")
        wrap.addWidget(lbl); wrap.addWidget(w)
        grid.addLayout(wrap); return w

    def _combo_field(self, grid, label, items):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        cb = QComboBox(); cb.setObjectName("Input")
        for row in items: cb.addItem(row["name"], row["id"])
        wrap.addWidget(lbl); wrap.addWidget(cb)
        grid.addLayout(wrap); return cb

    def _spin_field(self, grid, label, cls, min_v, max_v, decimals=None):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        sb = cls(); sb.setObjectName("Input"); sb.setRange(min_v, max_v)
        if decimals is not None: sb.setDecimals(decimals)
        wrap.addWidget(lbl); wrap.addWidget(sb)
        grid.addLayout(wrap); return sb

    def _date_field(self, grid, label):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        de = QDateEdit(); de.setObjectName("Input")
        de.setCalendarPopup(True); de.setDisplayFormat("MM/dd/yyyy")
        wrap.addWidget(lbl); wrap.addWidget(de)
        grid.addLayout(wrap); return de

    def _fill_data(self):
        m = self.medicine
        self.e_name.setText(m["name"])
        self.e_batch.setText(m["batch_number"])
        self.e_qty.setValue(int(m["quantity"]))
        self.e_price.setValue(float(m["price"]))
        expiry = m["expiry_date"]
        if hasattr(expiry, 'toPyDate'): expiry = expiry.toPyDate()
        self.e_expiry.setDate(QDate(expiry.year, expiry.month, expiry.day))
        self._set_combo(self.e_category,     m["category_id"])
        self._set_combo(self.e_manufacturer, m["manufacturer_id"])
        self._set_combo(self.e_unit,         m["unit_id"])

    def _set_combo(self, combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i); return

    def _handle_save(self):
        result = MedicineController.update_medicine(
            medicine_id     = self.medicine["id"],
            name            = self.e_name.text().strip(),
            category_id     = self.e_category.currentData(),
            manufacturer_id = self.e_manufacturer.currentData(),
            unit_id         = self.e_unit.currentData(),
            quantity        = self.e_qty.value(),
            expiry_date     = self.e_expiry.date().toString("yyyy-MM-dd"),
            price           = self.e_price.value(),
            batch_number    = self.e_batch.text().strip(),
            user_id         = self.user_id
        )
        if result.get("success"):
            QMessageBox.information(self, "Updated", "Medicine updated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", result.get("error", "Update failed."))


# ── Standalone preview ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = InventoryView(user_id=1)
    win.setWindowTitle("View Inventory")
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec())