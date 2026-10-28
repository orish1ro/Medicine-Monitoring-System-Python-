from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QComboBox,
    QDateEdit, QDoubleSpinBox, QSpinBox, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QCursor
from controllers.medicine_controller import MedicineController


class AddMedicineView(QWidget):
    def __init__(self, user_id=None, on_success=None):
        super().__init__()
        self.user_id    = user_id
        self.on_success = on_success
        self._categories    = []
        self._manufacturers = []
        self._units         = []
        self._apply_styles()
        self._build_ui()
        self._load_lookups()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            /* ── Root background: soft sky gradient ── */
            QWidget {
                background-color: #F7F8FA;
            }
            QScrollArea { border: none; background: transparent; }

            /* ── Card ── */
            QFrame#FormCard {
                background: #FFFFFF;
                border-radius: 16px;
                border: 1.5px solid #BDE3F7;
            }

            /* ── Divider ── */
            QFrame#Divider {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #BDE3F7, stop:0.5 #7EC8E3, stop:1 #BDE3F7);
                max-height: 2px;
                border: none;
                border-radius: 1px;
            }

            /* ── Page title ── */
            QLabel#PageTitle {
                font-size: 22px;
                font-weight: 700;
                color: #0C4A6E;
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: -0.3px;
            }

            /* ── Section label ── */
            QLabel#SectionTitle {
                font-size: 10px;
                font-weight: 700;
                color: #0EA5E9;
                letter-spacing: 2px;
                font-family: 'Segoe UI', sans-serif;
            }

            /* ── Field labels ── */
            QLabel#FieldLabel {
                font-size: 12px;
                font-weight: 600;
                color: #1E4A6B;
                font-family: 'Segoe UI', sans-serif;
            }

            /* ── Inputs ── */
            QLineEdit#Input, QComboBox#Input,
            QDateEdit#Input, QDoubleSpinBox#Input,
            QSpinBox#Input {
                border: 1.5px solid #BAD9F0;
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 13px;
                color: #0C2D48;
                background: #FFFFFF;
                min-height: 36px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit#Input:focus, QComboBox#Input:focus,
            QDateEdit#Input:focus, QDoubleSpinBox#Input:focus,
            QSpinBox#Input:focus {
                border-color: #0EA5E9;
                background: #FFFFFF;
                border-width: 2px;
            }
            QLineEdit#Input::placeholder { color: #93C5D8; }

            QComboBox#Input::drop-down { border: none; width: 20px; }
            QDateEdit#Input::drop-down { border: none; width: 20px; }

            /* ── Dropdown list ── */
            QComboBox QAbstractItemView {
                color: #0C2D48;
                background: #FFFFFF;
                selection-background-color: #BAE6FD;
                selection-color: #0C4A6E;
                outline: none;
                border: 1px solid #BAD9F0;
                border-radius: 6px;
            }
            QListView {
                color: #0C2D48;
                background: #FFFFFF;
            }

            /* ── Calendar ── */
            QCalendarWidget QAbstractItemView {
                color: #000000;
                selection-background-color: #0EA5E9;
                selection-color: #FFFFFF;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #9CA3AF; }
            QCalendarWidget QToolButton { color: #000000; font-weight: 600; }
            QCalendarWidget QSpinBox    { color: #000000; }

            /* ── Spin arrows ── */
            QSpinBox#Input::up-button,   QDoubleSpinBox#Input::up-button,
            QSpinBox#Input::down-button, QDoubleSpinBox#Input::down-button {
                width: 16px; border: none; background: transparent; margin: 2px 2px;
            }
            QSpinBox#Input::up-button:hover,   QDoubleSpinBox#Input::up-button:hover,
            QSpinBox#Input::down-button:hover, QDoubleSpinBox#Input::down-button:hover {
                background: #E0F2FE; border-radius: 3px;
            }
            QSpinBox#Input::up-arrow, QDoubleSpinBox#Input::up-arrow {
                image: none; width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #0EA5E9;
            }
            QSpinBox#Input::down-arrow, QDoubleSpinBox#Input::down-arrow {
                image: none; width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #0EA5E9;
            }

            /* ── Add button — green ── */
            QPushButton#BtnAdd {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #22C55E, stop:1 #16A34A);
                color: #111827;
                border: 2px solid #16A34A;
                border-radius: 9px;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 32px;
                min-height: 40px;
                font-family: 'Segoe UI', sans-serif;
                letter-spacing: 0.3px;
            }
            QPushButton#BtnAdd:hover   {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #4ADE80, stop:1 #22C55E);
                border-color: #22C55E;
            }
            QPushButton#BtnAdd:pressed {
                background: #15803D;
                border-color: #14532D;
            }

            /* ── Reset button ── */
            QPushButton#BtnReset {
                background: #FFFFFF;
                color: #1E4A6B;
                border: 1.5px solid #BAD9F0;
                border-radius: 9px;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 22px;
                min-height: 40px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnReset:hover {
                background: #EBF5FB;
                border-color: #7EC8E3;
                color: #0C4A6E;
            }

            /* ── Scrollbar ── */
            QScrollBar:vertical {
                background: transparent; width: 6px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #BAD9F0; border-radius: 3px; min-height: 30px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: #F7F8FA;")
        outer = QVBoxLayout(content)
        outer.setContentsMargins(28, 24, 28, 28)
        outer.setSpacing(12)
        outer.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Header row ────────────────────────────────────────
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Add Medicine")
        title.setObjectName("PageTitle")
        sub = QLabel("Fill in the details below to register a new medicine.")
        sub.setStyleSheet(
            "font-size:12px; color:#5BA4C7; font-family:'Segoe UI', sans-serif;"
        )
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header_row.addLayout(title_col)
        header_row.addStretch()
        outer.addLayout(header_row)

        # ── Form card ─────────────────────────────────────────
        card = QFrame()
        card.setObjectName("FormCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 32)
        card_layout.setSpacing(0)

        # Section: Medicine Info
        self._section_label(card_layout, "MEDICINE INFO")
        card_layout.addSpacing(10)

        row1 = QHBoxLayout(); row1.setSpacing(14)
        self.input_name     = self._field(row1, "Medicine Name *",  QLineEdit,      placeholder="e.g. Paracetamol")
        self.combo_category = self._combo(row1, "Category *")
        card_layout.addLayout(row1)
        card_layout.addSpacing(12)

        row2 = QHBoxLayout(); row2.setSpacing(14)
        self.spin_qty   = self._spinbox(row2,  "Quantity *",   QSpinBox,       0, 999999)
        self.combo_unit = self._combo(row2,    "Unit *")
        card_layout.addLayout(row2)
        card_layout.addSpacing(20)

        # Divider
        div1 = QFrame(); div1.setObjectName("Divider")
        div1.setFrameShape(QFrame.Shape.HLine)
        card_layout.addWidget(div1)
        card_layout.addSpacing(20)

        # Section: Details
        self._section_label(card_layout, "DETAILS")
        card_layout.addSpacing(10)

        row3 = QHBoxLayout(); row3.setSpacing(14)
        self.date_expiry = self._dateedit(row3, "Expiry Date *")
        self.spin_price  = self._spinbox(row3,  "Price (₱) *",  QDoubleSpinBox, 0, 9999999, decimals=2)
        card_layout.addLayout(row3)
        card_layout.addSpacing(12)

        row4 = QHBoxLayout(); row4.setSpacing(14)
        self.combo_manufacturer = self._combo(row4,  "Manufacturer *")
        self.input_batch        = self._field(row4,  "Batch Number *", QLineEdit, placeholder="e.g. BN2024-001")
        card_layout.addLayout(row4)
        card_layout.addSpacing(24)

        # Divider
        div2 = QFrame(); div2.setObjectName("Divider")
        div2.setFrameShape(QFrame.Shape.HLine)
        card_layout.addWidget(div2)
        card_layout.addSpacing(18)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        btn_reset = QPushButton("Reset")
        btn_reset.setObjectName("BtnReset")
        btn_reset.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_reset.clicked.connect(self._reset_form)

        btn_add = QPushButton("Save")
        btn_add.setObjectName("BtnAdd")
        btn_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_add.clicked.connect(self._handle_add)

        btn_row.addWidget(btn_reset)
        btn_row.addWidget(btn_add)
        card_layout.addLayout(btn_row)

        outer.addWidget(card)
        scroll.setWidget(content)
        root.addWidget(scroll)

    # ── HELPERS ───────────────────────────────────────────────
    def _section_label(self, layout, text):
        lbl = QLabel(text)
        lbl.setObjectName("SectionTitle")
        layout.addWidget(lbl)

    def _field(self, grid, label, widget_cls, placeholder=""):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        w = widget_cls(); w.setObjectName("Input")
        if placeholder and isinstance(w, QLineEdit):
            w.setPlaceholderText(placeholder)
        wrap.addWidget(lbl); wrap.addWidget(w)
        grid.addLayout(wrap)
        return w

    def _combo(self, grid, label):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        cb = QComboBox(); cb.setObjectName("Input")
        # Force black text in dropdown list
        view = cb.view()
        view.setStyleSheet("color: #000000; background: #FFFFFF;")
        wrap.addWidget(lbl); wrap.addWidget(cb)
        grid.addLayout(wrap)
        return cb

    def _spinbox(self, grid, label, cls, min_v, max_v, decimals=None):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        sb = cls(); sb.setObjectName("Input")
        sb.setRange(min_v, max_v)
        if decimals is not None:
            sb.setDecimals(decimals)
        wrap.addWidget(lbl); wrap.addWidget(sb)
        grid.addLayout(wrap)
        return sb

    def _dateedit(self, grid, label):
        wrap = QVBoxLayout(); wrap.setSpacing(5)
        lbl = QLabel(label); lbl.setObjectName("FieldLabel")
        de = QDateEdit(); de.setObjectName("Input")
        de.setCalendarPopup(True)
        de.setDate(QDate.currentDate().addYears(1))
        de.setDisplayFormat("MM/dd/yyyy")
        wrap.addWidget(lbl); wrap.addWidget(de)
        grid.addLayout(wrap)
        return de

    # ── LOAD LOOKUPS ──────────────────────────────────────────
    def _load_lookups(self):
        self._categories    = MedicineController.get_categories()
        self._manufacturers = MedicineController.get_manufacturers()
        self._units         = MedicineController.get_units()

        self.combo_category.clear()
        self.combo_category.addItem("Select category", None)
        for r in self._categories:
            self.combo_category.addItem(r["name"], r["id"])

        self.combo_manufacturer.clear()
        self.combo_manufacturer.addItem("Select manufacturer", None)
        for r in self._manufacturers:
            self.combo_manufacturer.addItem(r["name"], r["id"])

        self.combo_unit.clear()
        self.combo_unit.addItem("Select unit", None)
        for r in self._units:
            self.combo_unit.addItem(r["name"], r["id"])

    # ── ADD HANDLER ───────────────────────────────────────────
    def _handle_add(self):
        name        = self.input_name.text().strip()
        category_id = self.combo_category.currentData()
        mfg_id      = self.combo_manufacturer.currentData()
        unit_id     = self.combo_unit.currentData()
        quantity    = self.spin_qty.value()
        expiry_date = self.date_expiry.date().toString("yyyy-MM-dd")
        price       = self.spin_price.value()
        batch       = self.input_batch.text().strip()

        if not name:        return self._msg("Medicine name is required.", "warning")
        if not category_id: return self._msg("Please select a category.", "warning")
        if not mfg_id:      return self._msg("Please select a manufacturer.", "warning")
        if not unit_id:     return self._msg("Please select a unit.", "warning")
        if not batch:       return self._msg("Batch number is required.", "warning")

        result = MedicineController.add_medicine(
            name=name, category_id=category_id, manufacturer_id=mfg_id,
            unit_id=unit_id, quantity=quantity, expiry_date=expiry_date,
            price=price, batch_number=batch, user_id=self.user_id
        )
        if result.get("success"):
            self._msg(f"'{name}' added successfully!", "info")
            self._reset_form()
            if self.on_success:
                self.on_success()
        else:
            self._msg(f"Error: {result.get('error')}", "critical")

    # ── RESET ─────────────────────────────────────────────────
    def _reset_form(self):
        self.input_name.clear()
        self.input_batch.clear()
        self.spin_qty.setValue(0)
        self.spin_price.setValue(0)
        self.date_expiry.setDate(QDate.currentDate().addYears(1))
        self.combo_category.setCurrentIndex(0)
        self.combo_manufacturer.setCurrentIndex(0)
        self.combo_unit.setCurrentIndex(0)

    # ── MESSAGE ───────────────────────────────────────────────
    def _msg(self, text, kind="info"):
        box = QMessageBox(self)
        box.setText(text)
        if kind == "info":
            box.setIcon(QMessageBox.Icon.Information)
            box.setWindowTitle("Success")
        elif kind == "warning":
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle("Validation")
        else:
            box.setIcon(QMessageBox.Icon.Critical)
            box.setWindowTitle("Error")
        box.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #111827;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background: #FFFFFF;
                color: #111827;
                border: 1.5px solid #D1D5DB;
                border-radius: 6px;
                padding: 5px 18px;
                font-size: 12px;
                font-weight: 600;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #F3F4F6;
                border-color: #9CA3AF;
            }
        """)
        box.exec()


# ── Standalone preview ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = AddMedicineView(user_id=1, on_success=lambda: print("Medicine added!"))
    win.setWindowTitle("Add Medicine")
    win.resize(900, 650)
    win.show()
    sys.exit(app.exec())