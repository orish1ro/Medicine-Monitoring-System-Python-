from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QAbstractItemView,
    QDoubleSpinBox, QSpinBox, QDateEdit, QFileDialog,
    QMessageBox, QSizePolicy, QToolButton, QMenu, QScrollArea,
)
from PyQt6.QtCore import Qt, QDate, QTimer, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QCursor, QFont, QAction

from controllers.search_controller import controller_search, controller_get_search_filters
from utils.helpers import format_currency, format_date, get_medicine_status

# Optional: import export controllers if they exist in your project
try:
    from controllers.report_controller import (
        controller_export_csv,
        controller_export_excel,
        controller_export_pdf,
    )
    HAS_EXPORT = True
except ImportError:
    HAS_EXPORT = False


class SearchView(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self._results = []          # current full result set
        self._sort_col = -1
        self._sort_asc = True
        self._advanced_visible = False

        # Debounce timer for live search
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(350)
        self._debounce.timeout.connect(self._handle_search)

        self._apply_styles()
        self._build_ui()
        self._load_categories()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #F3F4F8; font-size: 13px; }

            QFrame#SearchCard, QFrame#TableCard, QFrame#AdvancedCard {
                background-color: #FFFFFF;
                border-radius: 10px;
            }

            QLabel#PageTitle {
                font-size: 18px;
                font-weight: 700;
                color: #1A1A2E;
            }
            QLabel#PageSubtitle { font-size: 12px; color: #6B7280; }
            QLabel#FieldLabel   { font-size: 12px; font-weight: 600; color: #374151; }
            QLabel#CountLabel   { font-size: 12px; color: #6B7280; }
            QLabel#SectionLabel { font-size: 11px; font-weight: 600; color: #9CA3AF;
                                  letter-spacing: 0.5px; }

            QLineEdit#Input, QComboBox#Input,
            QDoubleSpinBox#Input, QSpinBox#Input, QDateEdit#Input {
                border: 1px solid #E5E7EB;
                border-radius: 7px;
                padding: 6px 10px;
                font-size: 13px;
                color: #1F2937;
                background: #FFFFFF;
                min-height: 32px;
            }
            QLineEdit#Input:focus, QComboBox#Input:focus,
            QDoubleSpinBox#Input:focus, QSpinBox#Input:focus,
            QDateEdit#Input:focus { border-color: #4F46E5; }
            QComboBox#Input::drop-down { border: none; }
            QDateEdit#Input::drop-down { border: none; }

            QPushButton#BtnSearch {
                background-color: #4F46E5; color: #FFFFFF;
                border: none; border-radius: 7px;
                font-size: 13px; font-weight: 600;
                padding: 7px 18px; min-height: 34px;
            }
            QPushButton#BtnSearch:hover   { background-color: #4338CA; }
            QPushButton#BtnSearch:pressed { background-color: #3730A3; }

            QPushButton#BtnClear {
                background-color: #FFFFFF; color: #374151;
                border: 1px solid #E5E7EB; border-radius: 7px;
                font-size: 13px; padding: 7px 14px; min-height: 34px;
            }
            QPushButton#BtnClear:hover { background-color: #F3F4F6; }

            QPushButton#BtnAdvanced {
                background-color: #FFFFFF; color: #4F46E5;
                border: 1px solid #C7D2FE; border-radius: 7px;
                font-size: 12px; font-weight: 600;
                padding: 6px 12px; min-height: 34px;
            }
            QPushButton#BtnAdvanced:hover { background-color: #EEF2FF; }

            QPushButton#BtnExport {
                background-color: #FFFFFF; color: #374151;
                border: 1px solid #E5E7EB; border-radius: 7px;
                font-size: 12px; padding: 6px 14px; min-height: 34px;
            }
            QPushButton#BtnExport:hover { background-color: #F3F4F6; }

            /* Row action buttons */
            QPushButton#BtnView {
                background-color: #EEF2FF; color: #4F46E5;
                border: none; border-radius: 5px;
                font-size: 11px; font-weight: 600;
                padding: 3px 6px;
                min-width: 42px;
            }
            QPushButton#BtnView:hover { background-color: #C7D2FE; }

            QPushButton#BtnEdit {
                background-color: #ECFDF5; color: #059669;
                border: none; border-radius: 5px;
                font-size: 11px; font-weight: 600;
                padding: 3px 6px;
                min-width: 42px;
            }
            QPushButton#BtnEdit:hover { background-color: #A7F3D0; }

            QPushButton#BtnDelete {
                background-color: #FEF2F2; color: #DC2626;
                border: none; border-radius: 5px;
                font-size: 11px; font-weight: 600;
                padding: 3px 6px;
                min-width: 48px;
            }
            QPushButton#BtnDelete:hover { background-color: #FECACA; }

            QTableWidget {
                background: #FFFFFF; border: none;
                font-size: 12px; gridline-color: #F3F4F6;
            }
            QTableWidget::item { padding: 4px 10px; color: #374151; }
            QTableWidget::item:selected {
                background-color: #EEF2FF; color: #1F2937;
            }
            QHeaderView::section {
                background-color: #F9FAFB; color: #6B7280;
                font-size: 11px; font-weight: 600;
                padding: 8px 10px; border: none;
                border-bottom: 1px solid #E5E7EB;
                cursor: pointer;
            }
            QHeaderView::section:hover { background-color: #EEF2FF; color: #4F46E5; }

            QFrame#TableCard { border-radius: 10px; }
            QScrollArea { border: none; }
            QScrollBar:vertical { width: 6px; background: transparent; }
            QScrollBar::handle:vertical {
                background: #D1D5DB; border-radius: 3px; min-height: 20px;
            }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Fixed header bar ──────────────────────────────────
        header_bar = QWidget()
        header_bar.setStyleSheet("background:#FFFFFF; border-bottom:1px solid #E5E7EB;")
        header_bar.setFixedHeight(52)
        hb = QHBoxLayout(header_bar)
        hb.setContentsMargins(20, 0, 20, 0)
        hb.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title = QLabel("Search Medicine")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Find medicines by name, category, status, and more")
        subtitle.setObjectName("PageSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self.count_label = QLabel("")
        self.count_label.setObjectName("CountLabel")

        # Export dropdown button
        btn_export = QPushButton("↓  Export")
        btn_export.setObjectName("BtnExport")
        btn_export.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        export_menu = QMenu(self)
        export_menu.addAction("Export as CSV",   self._export_csv)
        export_menu.addAction("Export as Excel", self._export_excel)
        export_menu.addAction("Export as PDF",   self._export_pdf)
        btn_export.setMenu(export_menu)

        hb.addLayout(title_col)
        hb.addStretch()
        hb.addWidget(self.count_label)
        hb.addWidget(btn_export)
        root.addWidget(header_bar)

        # ── Scrollable body ───────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # ── Basic search card ─────────────────────────────────
        search_card = QFrame()
        search_card.setObjectName("SearchCard")
        sc = QVBoxLayout(search_card)
        sc.setContentsMargins(16, 14, 16, 14)
        sc.setSpacing(10)

        # Row 1: keyword, category, status + buttons
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        # Keyword
        kw_col = QVBoxLayout(); kw_col.setSpacing(4)
        kw_col.addWidget(self._field_label("Keyword"))
        self.input_keyword = QLineEdit()
        self.input_keyword.setObjectName("Input")
        self.input_keyword.setPlaceholderText("Name, manufacturer, or batch number…")
        self.input_keyword.textChanged.connect(self._on_keyword_changed)
        self.input_keyword.returnPressed.connect(self._handle_search)
        kw_col.addWidget(self.input_keyword)
        row1.addLayout(kw_col, stretch=3)

        # Category
        cat_col = QVBoxLayout(); cat_col.setSpacing(4)
        cat_col.addWidget(self._field_label("Category"))
        self.combo_category = QComboBox()
        self.combo_category.setObjectName("Input")
        self.combo_category.currentIndexChanged.connect(lambda _: self._debounce.start())
        cat_col.addWidget(self.combo_category)
        row1.addLayout(cat_col, stretch=2)

        # Status
        st_col = QVBoxLayout(); st_col.setSpacing(4)
        st_col.addWidget(self._field_label("Status"))
        self.combo_status = QComboBox()
        self.combo_status.setObjectName("Input")
        self.combo_status.addItems(["All Statuses", "Good", "Expiring Soon", "Expired", "Low Stock"])
        self.combo_status.currentIndexChanged.connect(lambda _: self._debounce.start())
        st_col.addWidget(self.combo_status)
        row1.addLayout(st_col, stretch=2)

        # Buttons
        btn_col = QVBoxLayout(); btn_col.setSpacing(4)
        btn_col.addWidget(QLabel(""))   # spacer to align with inputs
        btn_row = QHBoxLayout(); btn_row.setSpacing(6)
        btn_search = QPushButton("⌕  Search")
        btn_search.setObjectName("BtnSearch")
        btn_search.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_search.clicked.connect(self._handle_search)
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("BtnClear")
        btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_clear.clicked.connect(self._handle_clear)
        self.btn_advanced = QPushButton("▾  Filters")
        self.btn_advanced.setObjectName("BtnAdvanced")
        self.btn_advanced.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_advanced.clicked.connect(self._toggle_advanced)
        btn_row.addWidget(btn_search)
        btn_row.addWidget(btn_clear)
        btn_row.addWidget(self.btn_advanced)
        btn_col.addLayout(btn_row)
        row1.addLayout(btn_col)

        sc.addLayout(row1)

        # ── Advanced filters (collapsible) ────────────────────
        self.advanced_frame = QFrame()
        self.advanced_frame.setObjectName("AdvancedCard")
        self.advanced_frame.setStyleSheet(
            "QFrame#AdvancedCard { background:#F9FAFB; border-radius:8px; }"
        )
        self.advanced_frame.setVisible(False)
        adv = QHBoxLayout(self.advanced_frame)
        adv.setContentsMargins(14, 12, 14, 12)
        adv.setSpacing(16)

        # Price range
        price_col = QVBoxLayout(); price_col.setSpacing(4)
        price_col.addWidget(self._field_label("Price Range"))
        pr = QHBoxLayout(); pr.setSpacing(6)
        self.price_min = QDoubleSpinBox()
        self.price_min.setObjectName("Input")
        self.price_min.setPrefix("₱ ")
        self.price_min.setRange(0, 999999)
        self.price_min.setDecimals(2)
        self.price_min.setValue(0)
        self.price_min.setMaximumWidth(110)
        self.price_max = QDoubleSpinBox()
        self.price_max.setObjectName("Input")
        self.price_max.setPrefix("₱ ")
        self.price_max.setRange(0, 999999)
        self.price_max.setDecimals(2)
        self.price_max.setValue(999999)
        self.price_max.setMaximumWidth(110)
        pr.addWidget(self.price_min)
        pr.addWidget(QLabel("–"))
        pr.addWidget(self.price_max)
        price_col.addLayout(pr)
        adv.addLayout(price_col)

        # Quantity range
        qty_col = QVBoxLayout(); qty_col.setSpacing(4)
        qty_col.addWidget(self._field_label("Qty Range"))
        qr = QHBoxLayout(); qr.setSpacing(6)
        self.qty_min = QSpinBox()
        self.qty_min.setObjectName("Input")
        self.qty_min.setRange(0, 99999)
        self.qty_min.setValue(0)
        self.qty_min.setMaximumWidth(90)
        self.qty_max = QSpinBox()
        self.qty_max.setObjectName("Input")
        self.qty_max.setRange(0, 99999)
        self.qty_max.setValue(99999)
        self.qty_max.setMaximumWidth(90)
        qr.addWidget(self.qty_min)
        qr.addWidget(QLabel("–"))
        qr.addWidget(self.qty_max)
        qty_col.addLayout(qr)
        adv.addLayout(qty_col)

        # Expiry date range
        exp_col = QVBoxLayout(); exp_col.setSpacing(4)
        exp_col.addWidget(self._field_label("Expiry Date Range"))
        er = QHBoxLayout(); er.setSpacing(6)
        self.exp_from = QDateEdit()
        self.exp_from.setObjectName("Input")
        self.exp_from.setCalendarPopup(True)
        self.exp_from.setDisplayFormat("MMM dd, yyyy")
        self.exp_from.setDate(QDate(2000, 1, 1))
        self.exp_from.setMaximumWidth(130)
        self.exp_to = QDateEdit()
        self.exp_to.setObjectName("Input")
        self.exp_to.setCalendarPopup(True)
        self.exp_to.setDisplayFormat("MMM dd, yyyy")
        self.exp_to.setDate(QDate(2099, 12, 31))
        self.exp_to.setMaximumWidth(130)
        er.addWidget(self.exp_from)
        er.addWidget(QLabel("→"))
        er.addWidget(self.exp_to)
        exp_col.addLayout(er)
        adv.addLayout(exp_col)

        adv.addStretch()

        btn_reset_adv = QPushButton("Reset Filters")
        btn_reset_adv.setObjectName("BtnClear")
        btn_reset_adv.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_reset_adv.clicked.connect(self._reset_advanced)
        btn_reset_adv.setFixedWidth(110)
        adv.addWidget(btn_reset_adv, alignment=Qt.AlignmentFlag.AlignBottom)

        sc.addWidget(self.advanced_frame)
        layout.addWidget(search_card)

        # ── Results table ─────────────────────────────────────
        table_card = QFrame()
        table_card.setObjectName("TableCard")
        tl = QVBoxLayout(table_card)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)

        self.table = QTableWidget()
        # 9 data cols + 1 actions col
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Name", "Category", "Qty", "Unit",
            "Expiry Date", "Price", "Batch No.", "Status", "Actions"
        ])
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(8, 200)
        hh.sectionClicked.connect(self._on_header_clicked)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget{alternate-background-color:#F9FAFB;}")
        self.table.setSortingEnabled(False)   # manual sort for full control

        tl.addWidget(self.table)
        layout.addWidget(table_card, stretch=1)

        scroll.setWidget(content)
        root.addWidget(scroll)

    # ── HELPERS ───────────────────────────────────────────────
    @staticmethod
    def _field_label(text):
        lbl = QLabel(text)
        lbl.setObjectName("FieldLabel")
        return lbl

    def _toggle_advanced(self):
        self._advanced_visible = not self._advanced_visible
        self.advanced_frame.setVisible(self._advanced_visible)
        self.btn_advanced.setText("▴  Filters" if self._advanced_visible else "▾  Filters")

    def _reset_advanced(self):
        self.price_min.setValue(0)
        self.price_max.setValue(999999)
        self.qty_min.setValue(0)
        self.qty_max.setValue(99999)
        self.exp_from.setDate(QDate(2000, 1, 1))
        self.exp_to.setDate(QDate(2099, 12, 31))
        self._debounce.start()

    def _on_keyword_changed(self):
        self._debounce.start()

    # ── LOAD CATEGORIES ───────────────────────────────────────
    def _load_categories(self):
        try:
            categories = controller_get_search_filters()
        except Exception:
            categories = []
        self.combo_category.clear()
        self.combo_category.addItem("All Categories", None)
        for c in categories:
            self.combo_category.addItem(c["name"], c["id"])

    # ── SEARCH ────────────────────────────────────────────────
    def _handle_search(self):
        keyword     = self.input_keyword.text().strip()
        category_id = self.combo_category.currentData()

        try:
            results = controller_search(keyword, category_id)
        except Exception as e:
            self.count_label.setText(f"Error: {e}")
            return

        # Client-side advanced filtering
        results = self._apply_advanced_filters(results)

        # Client-side status filter
        status_sel = self.combo_status.currentText()
        STATUS_MAP = {
            "Good":          "ok",
            "Expiring Soon": "expiring_soon",
            "Expired":       "expired",
            "Low Stock":     "low_stock",
        }
        if status_sel != "All Statuses":
            key = STATUS_MAP.get(status_sel)
            if key:
                results = [r for r in results if get_medicine_status(r) == key]

        self._results = results
        self._populate_table(results)

    def _apply_advanced_filters(self, results):
        if not self._advanced_visible:
            return results
        p_min = self.price_min.value()
        p_max = self.price_max.value()
        q_min = self.qty_min.value()
        q_max = self.qty_max.value()
        d_from = self.exp_from.date().toPyDate()
        d_to   = self.exp_to.date().toPyDate()

        filtered = []
        for m in results:
            try:
                price = float(m.get("price", 0) or 0)
                qty   = int(m.get("quantity", 0) or 0)
            except (ValueError, TypeError):
                continue
            if not (p_min <= price <= p_max):
                continue
            if not (q_min <= qty <= q_max):
                continue
            # expiry date
            raw_exp = m.get("expiry_date")
            if raw_exp:
                try:
                    from datetime import date
                    if isinstance(raw_exp, str):
                        exp_date = date.fromisoformat(raw_exp)
                    else:
                        exp_date = raw_exp
                    if not (d_from <= exp_date <= d_to):
                        continue
                except Exception:
                    pass
            filtered.append(m)
        return filtered

    def _handle_clear(self):
        self.input_keyword.clear()
        self.combo_category.setCurrentIndex(0)
        self.combo_status.setCurrentIndex(0)
        self._reset_advanced()
        self.table.setRowCount(0)
        self.count_label.setText("")
        self._results = []
        self._sort_col = -1
        self._sort_asc = True

    # ── SORT ──────────────────────────────────────────────────
    def _on_header_clicked(self, col):
        if col == 8:    # actions column — not sortable
            return
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        self._populate_table(self._results)

    def _sorted_results(self, results):
        col = self._sort_col
        if col < 0:
            return results

        KEY_MAP = {
            0: lambda m: (m.get("name") or "").lower(),
            1: lambda m: (m.get("category") or "").lower(),
            2: lambda m: int(m.get("quantity") or 0),
            3: lambda m: (m.get("unit") or "").lower(),
            4: lambda m: str(m.get("expiry_date") or ""),
            5: lambda m: float(m.get("price") or 0),
            6: lambda m: (m.get("batch_number") or "").lower(),
            7: lambda m: get_medicine_status(m),
        }
        key_fn = KEY_MAP.get(col)
        if not key_fn:
            return results
        try:
            return sorted(results, key=key_fn, reverse=not self._sort_asc)
        except Exception:
            return results

    # ── POPULATE TABLE ────────────────────────────────────────
    def _populate_table(self, results):
        self.table.setRowCount(0)

        if not results:
            n = len(self._results)
            self.count_label.setText(
                "No results found." if n == 0 else f"0 of {n} results (filtered)"
            )
            self.table.setRowCount(1)
            empty = QTableWidgetItem("No medicines matched your search.")
            empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setForeground(QColor("#9CA3AF"))
            self.table.setItem(0, 0, empty)
            self.table.setSpan(0, 0, 1, 9)
            return

        self.table.setSpan(0, 0, 1, 1)
        n = len(results)
        total = len(self._results)
        suffix = "" if n == total else f" of {total}"
        self.count_label.setText(f"{n}{suffix} result{'s' if n != 1 else ''} found")

        # Update header labels with sort arrows
        BASE_LABELS = ["Name", "Category", "Qty", "Unit",
                       "Expiry Date", "Price", "Batch No.", "Status", "Actions"]
        for i, lbl in enumerate(BASE_LABELS):
            if i == self._sort_col:
                arrow = " ▲" if self._sort_asc else " ▼"
                self.table.horizontalHeaderItem(i).setText(lbl + arrow)
            else:
                self.table.horizontalHeaderItem(i).setText(lbl)

        STATUS_COLORS = {
            "expired":       {"text": "#991B1B", "bg": "#FEE2E2"},
            "expiring_soon": {"text": "#92400E", "bg": "#FEF3C7"},
            "low_stock":     {"text": "#92400E", "bg": "#FEF3C7"},
            "ok":            {"text": "#166534", "bg": "#DCFCE7"},
        }
        STATUS_LABELS = {
            "expired":       "Expired",
            "expiring_soon": "Expiring Soon",
            "low_stock":     "Low Stock",
            "ok":            "Good",
        }

        sorted_results = self._sorted_results(results)

        for row_idx, m in enumerate(sorted_results):
            self.table.insertRow(row_idx)
            status_key = get_medicine_status(m)
            colors     = STATUS_COLORS.get(status_key, STATUS_COLORS["ok"])
            status_lbl = STATUS_LABELS.get(status_key, status_key)

            def _item(text, bold=False, align=None):
                it = QTableWidgetItem(str(text))
                if bold:
                    f = it.font(); f.setBold(True); it.setFont(f)
                if align:
                    it.setTextAlignment(align)
                return it

            self.table.setItem(row_idx, 0, _item(m["name"], bold=True))
            self.table.setItem(row_idx, 1, _item(m.get("category", "")))
            self.table.setItem(row_idx, 2, _item(
                m["quantity"],
                align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            ))
            self.table.setItem(row_idx, 3, _item(m.get("unit", "")))
            self.table.setItem(row_idx, 4, _item(format_date(m["expiry_date"])))
            self.table.setItem(row_idx, 5, _item(
                format_currency(m["price"]),
                align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            ))
            self.table.setItem(row_idx, 6, _item(m.get("batch_number", "")))

            status_item = QTableWidgetItem(status_lbl)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QColor(colors["text"]))
            status_item.setBackground(QColor(colors["bg"]))
            self.table.setItem(row_idx, 7, status_item)

            # Action buttons
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background: transparent;")
            ab = QHBoxLayout(actions_widget)
            ab.setContentsMargins(4, 2, 4, 2)
            ab.setSpacing(4)

            btn_view = QPushButton("View")
            btn_view.setObjectName("BtnView")
            btn_view.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_view.clicked.connect(lambda _, med=m: self._on_view(med))

            btn_edit = QPushButton("Edit")
            btn_edit.setObjectName("BtnEdit")
            btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_edit.clicked.connect(lambda _, med=m: self._on_edit(med))

            btn_del = QPushButton("Delete")
            btn_del.setObjectName("BtnDelete")
            btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_del.clicked.connect(lambda _, med=m: self._on_delete(med))

            ab.addWidget(btn_view)
            ab.addWidget(btn_edit)
            ab.addWidget(btn_del)
            self.table.setCellWidget(row_idx, 8, actions_widget)

            self.table.setRowHeight(row_idx, 42)

    # ── ROW ACTIONS ───────────────────────────────────────────
    def _on_view(self, medicine):
        lines = [
            f"<b>Name:</b> {medicine.get('name', '')}",
            f"<b>Category:</b> {medicine.get('category', '')}",
            f"<b>Quantity:</b> {medicine.get('quantity', '')} {medicine.get('unit', '')}",
            f"<b>Price:</b> {format_currency(medicine.get('price', 0))}",
            f"<b>Expiry Date:</b> {format_date(medicine.get('expiry_date', ''))}",
            f"<b>Batch No.:</b> {medicine.get('batch_number', '')}",
            f"<b>Status:</b> {get_medicine_status(medicine).replace('_', ' ').title()}",
        ]

        msg_style = """
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
            QPushButton:hover { background: #F3F4F6; border-color: #9CA3AF; }
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Medicine Details")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText("<br>".join(lines))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet(msg_style)
        msg.exec()

    def _on_edit(self, medicine):
        # Emit signal or open edit dialog — wire to your existing edit view here.

        msg_style = """
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
            QPushButton:hover { background: #F3F4F6; border-color: #9CA3AF; }
        """
        msg = QMessageBox(self)
        msg.setWindowTitle("Edit")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(f"Open edit dialog for:\n{medicine.get('name', '')}\n\nConnect this to your inventory edit view.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet(msg_style)
        msg.exec()

    def _on_delete(self, medicine):

        msg_style = """
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
            QPushButton:hover { background: #F3F4F6; border-color: #9CA3AF; }
        """
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirm Delete")
        dlg.setText(f"Delete '{medicine.get('name', '')}'?\nThis action cannot be undone.")
        dlg.setIcon(QMessageBox.Icon.Question)
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setDefaultButton(QMessageBox.StandardButton.No)
        dlg.setStyleSheet(msg_style)
        reply = dlg.exec()
        reply = QMessageBox.StandardButton(reply)
        if reply == QMessageBox.StandardButton.Yes:
            # Wire to your delete controller here, then refresh:
            QMessageBox.information(self, "Deleted",
                f"'{medicine.get('name', '')}' has been deleted.\n"
                "Connect this to your delete controller.")
            self._handle_search()

    # ── EXPORT ────────────────────────────────────────────────
    def _export_csv(self):
        if not HAS_EXPORT:
            QMessageBox.warning(self, "Unavailable",
                "Export controller not found. Connect controller_export_csv.")
            return
        fp, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "search_results.csv", "CSV Files (*.csv)")
        if not fp:
            return
        try:
            result = controller_export_csv(fp)
            if result:
                QMessageBox.information(self, "Exported", f"Saved to:\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _export_excel(self):
        if not HAS_EXPORT:
            QMessageBox.warning(self, "Unavailable",
                "Export controller not found. Connect controller_export_excel.")
            return
        fp, _ = QFileDialog.getSaveFileName(
            self, "Export to Excel", "search_results.xls", "Excel Files (*.xls)")
        if not fp:
            return
        try:
            result = controller_export_excel(fp)
            if result:
                QMessageBox.information(self, "Exported", f"Saved to:\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))

    def _export_pdf(self):
        if not HAS_EXPORT:
            QMessageBox.warning(self, "Unavailable",
                "Export controller not found. Connect controller_export_pdf.")
            return
        fp, _ = QFileDialog.getSaveFileName(
            self, "Export to PDF", "search_results.pdf", "PDF Files (*.pdf)")
        if not fp:
            return
        try:
            result = controller_export_pdf(fp)
            if result:
                QMessageBox.information(self, "Exported", f"Saved to:\n{result}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", str(e))


# ── Standalone preview ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = SearchView(user_id=1)
    win.setWindowTitle("Search Medicine")
    win.resize(1200, 760)
    win.show()
    sys.exit(app.exec())