from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QComboBox, QDateEdit,
    QMessageBox, QFileDialog, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QColor, QCursor
from controllers.report_controller import (
    get_transaction_log, get_summary_stats,
    get_action_types, get_top_dispensed
)
from datetime import datetime


# ── PDF export (reuses reportlab like csv_exporter.py) ────────

def export_report_pdf(path, title, headers, rows, summary=None):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer, HRFlowable)
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        doc = SimpleDocTemplate(path, pagesize=landscape(A4),
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        story  = []

        # Title
        story.append(Paragraph(f"<b>{title}</b>",
            ParagraphStyle("T", fontSize=16, spaceAfter=4,
                           textColor=colors.HexColor("#18181B"))))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}",
            ParagraphStyle("S", fontSize=9, spaceAfter=10, textColor=colors.grey)))
        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#E5E7EB"), spaceAfter=10))

        # Summary cards row
        if summary:
            sum_data = [[
                Paragraph(f"<b>{k}</b><br/><font size=13><b>{v}</b></font>",
                          ParagraphStyle("SC", fontSize=9, alignment=TA_CENTER))
                for k, v in summary.items()
            ]]
            col_w = [4*cm] * len(summary)
            sum_tbl = Table(sum_data, colWidths=col_w)
            sum_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#F8FAFC")),
                ("BOX",           (0,0),(-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                ("INNERGRID",     (0,0),(-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                ("ALIGN",         (0,0),(-1,-1), "CENTER"),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
                ("TOPPADDING",    (0,0),(-1,-1), 10),
                ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ]))
            story.append(sum_tbl)
            story.append(Spacer(1, 14))

        # Data table
        page_w = landscape(A4)[0] - 3*cm
        col_w  = [page_w / len(headers)] * len(headers)

        hdr_style  = ParagraphStyle("H", fontSize=8, textColor=colors.white,
                                    fontName="Helvetica-Bold", alignment=TA_CENTER)
        cell_style = ParagraphStyle("C", fontSize=8,
                                    textColor=colors.HexColor("#1E293B"))

        tbl_data = [[Paragraph(h, hdr_style) for h in headers]]
        for r in rows:
            tbl_data.append([
                Paragraph(str(c) if c is not None else "—", cell_style) for c in r
            ])

        tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  colors.HexColor("#4F46E5")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("ALIGN",         (0,0),(-1,-1), "LEFT"),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("GRID",          (0,0),(-1,-1), 0.25, colors.HexColor("#E5E7EB")),
        ]))
        story.append(tbl)
        doc.build(story)
        return True, None

    except ImportError:
        return False, "reportlab not installed.\nRun: py -m pip install reportlab"
    except Exception as e:
        return False, str(e)


# ── Main View ─────────────────────────────────────────────────

class ReportView(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id      = user_id
        self._tab_idx     = 0
        self._log_rows    = []   # full data cache
        self._disp_rows   = []
        self._page_log    = 0
        self._page_disp   = 0
        self._page_size   = 15
        self._apply_styles()
        self._build_ui()
        self._load()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #F3F4F8; }

            QTableWidget {
                background: #FFFFFF; border: none; font-size: 13px;
                outline: none; selection-background-color: #EEF2FF;
                border-radius: 12px; gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 0px 12px; color: #1E293B;
                border-bottom: 1px solid #F1F5F9;
            }
            QTableWidget::item:selected { background-color: #EEF2FF; color: #111827; }
            QTableWidget::item:hover    { background-color: #F8FAFC; }

            QHeaderView::section {
                background-color: #F8FAFC; color: #64748B;
                font-size: 10px; font-weight: 700; letter-spacing: 0.6px;
                padding: 10px 12px; border: none;
                border-bottom: 2px solid #E5E7EB;
                font-family: 'Segoe UI', sans-serif;
            }

            QLabel#PageTitle {
                font-size: 20px; font-weight: 700; color: #18181B;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#CountLabel {
                font-size: 12px; color: #6B7280;
                background: #F3F4F6; border-radius: 10px; padding: 3px 10px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#FilterLabel {
                font-size: 12px; color: #6B7280;
                font-family: 'Segoe UI', sans-serif; background: transparent;
            }

            QPushButton#BtnTab {
                background: #F3F4F6; color: #111827; border: 1.5px solid #D1D5DB;
                border-radius: 8px; font-size: 13px; font-weight: 600;
                padding: 7px 16px; font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnTab:hover { background: #E5E7EB; color: #111827; }
            QPushButton#BtnTabActive {
                background: #EEF2FF; color: #111827; border: 2px solid #4F46E5;
                border-radius: 8px; font-size: 13px; font-weight: 700;
                padding: 7px 16px; font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnTabActive:hover { background: #E0E7FF; color: #111827; }

            QPushButton#BtnExport {
                background: #4F46E5; color: #FFFFFF; border: none;
                border-radius: 7px; font-size: 12px; font-weight: 600;
                padding: 7px 18px; font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnExport:hover { background: #4338CA; }

            QPushButton#BtnRefresh {
                background: #FFFFFF; color: #4F46E5;
                border: 1px solid #C7D2FE; border-radius: 7px;
                font-size: 12px; font-weight: 600; padding: 6px 16px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnRefresh:hover { background: #EEF2FF; }

            QDateEdit#DateFilter, QComboBox#TypeFilter {
                background: #FFFFFF; border: 1.5px solid #E5E7EB;
                border-radius: 8px; padding: 5px 10px; font-size: 12px;
                color: #1E293B; font-family: 'Segoe UI', sans-serif;
                min-width: 120px;
            }
            QDateEdit#DateFilter:focus, QComboBox#TypeFilter:focus {
                border-color: #A5B4FC;
            }
            QComboBox#TypeFilter::drop-down { border: none; width: 20px; }
            QComboBox#TypeFilter QAbstractItemView {
                background: #FFFFFF; color: #111827;
                selection-background-color: #EEF2FF;
                border: 1px solid #E5E7EB; border-radius: 8px; outline: none;
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

            QCalendarWidget QWidget {
                background-color: #FFFFFF; color: #111827;
                font-family: 'Segoe UI', sans-serif;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #FFFFFF; color: #111827;
                selection-background-color: #4F46E5;
                selection-color: #FFFFFF;
                font-size: 12px;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #9CA3AF; }
            QCalendarWidget QToolButton {
                background: #FFFFFF; color: #111827;
                border: none; border-radius: 4px;
                font-size: 13px; font-weight: 600; padding: 4px 8px;
            }
            QCalendarWidget QToolButton:hover { background: #EEF2FF; color: #111827; }
            QCalendarWidget QToolButton::menu-indicator { image: none; }
            QCalendarWidget QSpinBox {
                color: #111827; background: #FFFFFF;
                border: 1px solid #E5E7EB; border-radius: 4px;
                font-size: 12px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: #F8FAFC;
                border-bottom: 1px solid #E5E7EB;
            }

            QPushButton#BtnPage, QPushButton#BtnPageActive {
                color: #111827;
                border-radius: 6px; font-size: 12px; font-weight: 600;
                padding: 4px 10px; min-width: 32px; min-height: 28px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton#BtnPage {
                background: #FFFFFF; border: 1px solid #D1D5DB;
            }
            QPushButton#BtnPage:hover   { background: #F3F4F6; color: #111827; }
            QPushButton#BtnPage:pressed { background: #F3F4F6; color: #111827; }
            QPushButton#BtnPageActive {
                background: #EEF2FF; border: 2px solid #4F46E5; font-weight: 700;
            }
            QPushButton#BtnPageActive:hover   { background: #E0E7FF; color: #111827; }
            QPushButton#BtnPageActive:pressed { background: #E0E7FF; color: #111827; }
            QLabel#PageInfo {
                font-size: 12px; color: #6B7280;
                font-family: 'Segoe UI', sans-serif; background: transparent;
            }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(10)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Generate Report")
        title.setObjectName("PageTitle")
        self.count_label = QLabel("—")
        self.count_label.setObjectName("CountLabel")

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setObjectName("BtnRefresh")
        btn_refresh.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_refresh.clicked.connect(self._load)

        btn_export = QPushButton("Export PDF")
        btn_export.setObjectName("BtnExport")
        btn_export.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_export.clicked.connect(self._export_pdf)

        hdr.addWidget(title)
        hdr.addSpacing(10)
        hdr.addWidget(self.count_label)
        hdr.addStretch()
        hdr.addWidget(btn_refresh)
        hdr.addSpacing(8)
        hdr.addWidget(btn_export)
        root.addLayout(hdr)

        # ── Stat cards ───────────────────────────────────────
        stat_row = QHBoxLayout()
        stat_row.setSpacing(10)
        self._stat_labels = {}
        stat_defs = [
            ("total_meds", "Total Medicines", "#4F46E5", "#EEF2FF"),
            ("added",      "Added",            "#166534", "#DCFCE7"),
            ("updated",    "Updated",          "#1D4ED8", "#DBEAFE"),
            ("deleted",    "Deleted",          "#991B1B", "#FEE2E2"),
            ("dispensed",  "Dispensed",        "#B45309", "#FFFBEB"),
        ]
        for key, label, color, bg in stat_defs:
            card = QFrame()
            card.setStyleSheet(
                f"QFrame{{background:{bg};border-radius:10px;border:1px solid #E5E7EB;}}"
                f"QLabel{{background:transparent;border:none;}}"
            )
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            cl.setSpacing(2)
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet(
                f"color:{color};font-size:22px;font-weight:700;"
                f"font-family:'Segoe UI',sans-serif;"
            )
            name_lbl = QLabel(label)
            name_lbl.setStyleSheet(
                "color:#52525B;font-size:11px;font-weight:500;"
                "font-family:'Segoe UI',sans-serif;"
            )
            cl.addWidget(val_lbl)
            cl.addWidget(name_lbl)
            self._stat_labels[key] = val_lbl
            stat_row.addWidget(card)
        root.addLayout(stat_row)

        # ── Filter row ───────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)

        lbl_from = QLabel("From:")
        lbl_from.setObjectName("FilterLabel")
        self.date_from = QDateEdit()
        self.date_from.setObjectName("DateFilter")
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setDate(QDate.currentDate().addMonths(-1))

        lbl_to = QLabel("To:")
        lbl_to.setObjectName("FilterLabel")
        self.date_to = QDateEdit()
        self.date_to.setObjectName("DateFilter")
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setDate(QDate.currentDate())

        self.type_filter = QComboBox()
        self.type_filter.setObjectName("TypeFilter")
        self.type_filter.addItems(["All Types", "ADD", "UPDATE", "DELETE", "DISPENSE"])

        filter_row.addWidget(lbl_from)
        filter_row.addWidget(self.date_from)
        filter_row.addSpacing(4)
        filter_row.addWidget(lbl_to)
        filter_row.addWidget(self.date_to)
        filter_row.addSpacing(8)
        filter_row.addWidget(self.type_filter)
        filter_row.addStretch()

        self._filter_timer = QTimer()
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(300)
        self._filter_timer.timeout.connect(self._load)
        self.date_from.dateChanged.connect(lambda: self._filter_timer.start())
        self.date_to.dateChanged.connect(lambda: self._filter_timer.start())
        self.type_filter.currentIndexChanged.connect(self._load)

        root.addLayout(filter_row)

        # ── Card + tabs ──────────────────────────────────────
        card = QFrame()
        card.setObjectName("TableCard")
        card.setStyleSheet(
            "QFrame#TableCard{background:#FFFFFF;border-radius:12px;"
            "border:1px solid #E5E7EB;}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # Tab bar
        tab_bar = QFrame()
        tab_bar.setStyleSheet(
            "background:#F8FAFC;border-bottom:1px solid #E5E7EB;"
            "border-top-left-radius:12px;border-top-right-radius:12px;"
        )
        tab_layout = QHBoxLayout(tab_bar)
        tab_layout.setContentsMargins(16, 8, 16, 8)
        tab_layout.setSpacing(8)

        self._tab_buttons = []
        for label, idx in [("Audit Log", 0), ("Top Dispensed", 1)]:
            btn = QPushButton(label)
            btn.setObjectName("BtnTabActive" if idx == 0 else "BtnTab")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, i=idx: self._switch_tab(i))
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setMinimumWidth(120)
            self._tab_buttons.append(btn)
            tab_layout.addWidget(btn)
        tab_layout.addStretch()
        card_layout.addWidget(tab_bar)

        # Tables
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:#FFFFFF;")

        self.table_log = self._make_table(
            ["ID", "Action", "Medicine", "Notes", "Performed By", "Date & Time"]
        )
        self.table_dispense = self._make_table(["Medicine", "Times Dispensed"])

        for tbl in (self.table_log, self.table_dispense):
            w = QWidget(); w.setStyleSheet("background:#FFFFFF;")
            l = QVBoxLayout(w); l.setContentsMargins(0,0,0,0); l.setSpacing(0)
            l.addWidget(tbl)
            self.stack.addWidget(w)

        card_layout.addWidget(self.stack)

        # Pagination bar for Audit Log
        self._pag_log = self._make_pagination_bar("log")
        card_layout.addWidget(self._pag_log)

        # Pagination bar for Top Dispensed
        self._pag_disp = self._make_pagination_bar("disp")
        card_layout.addWidget(self._pag_disp)

        root.addWidget(card)

    # ── TAB SWITCH ────────────────────────────────────────────
    def _switch_tab(self, idx):
        self._tab_idx = idx
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._tab_buttons):
            btn.setObjectName("BtnTabActive" if i == idx else "BtnTab")
            btn.setStyle(btn.style())

    # ── TABLE FACTORY ─────────────────────────────────────────
    def _make_table(self, headers):
        t = QTableWidget()
        t.setColumnCount(len(headers))
        for col, h in enumerate(headers):
            item = QTableWidgetItem(h)
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            t.setHorizontalHeaderItem(col, item)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.verticalHeader().setVisible(False)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.setShowGrid(False)
        t.setMouseTracking(True)
        t.verticalHeader().setDefaultSectionSize(46)
        return t

    # ── LOAD ──────────────────────────────────────────────────
    def _load(self):
        try:
            d_from   = self.date_from.date().toPyDate()
            d_to     = self.date_to.date().toPyDate()
            action   = self.type_filter.currentText()

            stats = get_summary_stats(d_from, d_to)
            for key, lbl in self._stat_labels.items():
                lbl.setText(str(stats.get(key, 0)))

            logs = get_transaction_log(d_from, d_to, action)
            self._populate_log(logs)

            top = get_top_dispensed(d_from, d_to)
            self._populate_dispensed(top)

            self.count_label.setText(
                f"{len(logs)} record{'s' if len(logs)!=1 else ''}"
            )
        except Exception as e:
            print(f"[ReportView] load error: {e}")
            self.count_label.setText("Error loading")

    # ── POPULATE LOG ──────────────────────────────────────────
    def _populate_log(self, rows):
        self._log_rows = rows
        self._page_log = 0
        self._render_log_page()

    def _render_log_page(self):
        rows = self._log_rows
        self.table_log.setRowCount(0)
        if not rows:
            self._set_empty(self.table_log, "No records found for this period.", 6)
            self._refresh_pagination("log")
            return

        action_colors = {
            "ADD":      ("#166534", "#DCFCE7"),
            "UPDATE":   ("#1D4ED8", "#DBEAFE"),
            "DELETE":   ("#991B1B", "#FEE2E2"),
            "DISPENSE": ("#9A3412", "#FFEDD5"),
            "STOCK":    ("#52525B", "#F3F4F6"),
        }

        start = self._page_log * self._page_size
        page_rows = rows[start: start + self._page_size]

        for i, r in enumerate(page_rows):
            self.table_log.insertRow(i)
            action = str(r.get("action", "")).upper()
            tc, bg = action_colors.get(action, ("#1E293B", "#FFFFFF"))
            vals = [
                str(r.get("id", "")),
                action,
                str(r.get("medicine", "") or "—"),
                str(r.get("notes", "") or "—"),
                str(r.get("performed_by", "") or "—"),
                str(r.get("performed_at", ""))[:19],
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                if col == 1:
                    item.setForeground(QColor(tc))
                    f = item.font(); f.setBold(True); item.setFont(f)
                self.table_log.setItem(i, col, item)
            self.table_log.setRowHeight(i, 46)
        self._refresh_pagination("log")

    # ── POPULATE DISPENSED ────────────────────────────────────
    def _populate_dispensed(self, rows):
        self._disp_rows = rows
        self._page_disp = 0
        self._render_disp_page()

    def _render_disp_page(self):
        rows = self._disp_rows
        self.table_dispense.setRowCount(0)
        if not rows:
            self._set_empty(self.table_dispense, "No dispense records for this period.", 2)
            self._refresh_pagination("disp")
            return

        start = self._page_disp * self._page_size
        page_rows = rows[start: start + self._page_size]

        for i, r in enumerate(page_rows):
            self.table_dispense.insertRow(i)
            name = QTableWidgetItem(str(r.get("name", "")))
            name.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            f = name.font(); f.setBold(True); f.setPointSize(13); name.setFont(f)

            qty = QTableWidgetItem(str(r.get("total_dispensed", "")))
            qty.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
            qty.setForeground(QColor("#B45309"))
            f2 = qty.font(); f2.setBold(True); qty.setFont(f2)

            self.table_dispense.setItem(i, 0, name)
            self.table_dispense.setItem(i, 1, qty)
            self.table_dispense.setRowHeight(i, 46)
        self._refresh_pagination("disp")

    # ── PAGINATION ───────────────────────────────────────────
    def _make_pagination_bar(self, which):
        bar = QFrame()
        bar.setStyleSheet(
            "QFrame{background:#FAFAFA;border-top:1px solid #F1F5F9;"
            "border-bottom-left-radius:12px;border-bottom-right-radius:12px;}"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(4)

        lbl = QLabel("")
        lbl.setObjectName("PageInfo")
        layout.addWidget(lbl)
        layout.addStretch()

        prev_btn = QPushButton("‹ Prev")
        prev_btn.setObjectName("BtnPage")
        prev_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        prev_btn.clicked.connect(lambda: self._prev_page(which))
        layout.addWidget(prev_btn)

        # Page number buttons container
        num_container = QWidget()
        num_container.setStyleSheet("background:transparent;")
        num_layout = QHBoxLayout(num_container)
        num_layout.setContentsMargins(0,0,0,0)
        num_layout.setSpacing(4)
        layout.addWidget(num_container)

        next_btn = QPushButton("Next ›")
        next_btn.setObjectName("BtnPage")
        next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        next_btn.clicked.connect(lambda: self._next_page(which))
        layout.addWidget(next_btn)

        bar._lbl       = lbl
        bar._prev_btn  = prev_btn
        bar._next_btn  = next_btn
        bar._num_layout = num_layout
        bar._num_container = num_container
        return bar

    def _refresh_pagination(self, which):
        if which == "log":
            rows   = self._log_rows
            page   = self._page_log
            bar    = self._pag_log
        else:
            rows   = self._disp_rows
            page   = self._page_disp
            bar    = self._pag_disp

        total      = len(rows)
        total_pages = max(1, (total + self._page_size - 1) // self._page_size)
        start      = page * self._page_size + 1 if total else 0
        end        = min((page + 1) * self._page_size, total)

        bar._lbl.setText(f"Showing {start}–{end} of {total} records")
        bar._prev_btn.setEnabled(page > 0)
        bar._next_btn.setEnabled(page < total_pages - 1)

        # Rebuild page number buttons
        while bar._num_layout.count():
            item = bar._num_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Show up to 5 page numbers around current
        window_start = max(0, page - 2)
        window_end   = min(total_pages, window_start + 5)
        window_start = max(0, window_end - 5)

        for p in range(window_start, window_end):
            btn = QPushButton(str(p + 1))
            btn.setObjectName("BtnPageActive" if p == page else "BtnPage")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedWidth(32)
            btn.clicked.connect(lambda _, pg=p: self._goto_page(which, pg))
            bar._num_layout.addWidget(btn)

        bar.setVisible(total_pages > 1)

    def _prev_page(self, which):
        if which == "log" and self._page_log > 0:
            self._page_log -= 1
            self._render_log_page()
        elif which == "disp" and self._page_disp > 0:
            self._page_disp -= 1
            self._render_disp_page()

    def _next_page(self, which):
        if which == "log":
            total_pages = max(1, (len(self._log_rows) + self._page_size - 1) // self._page_size)
            if self._page_log < total_pages - 1:
                self._page_log += 1
                self._render_log_page()
        else:
            total_pages = max(1, (len(self._disp_rows) + self._page_size - 1) // self._page_size)
            if self._page_disp < total_pages - 1:
                self._page_disp += 1
                self._render_disp_page()

    def _goto_page(self, which, page):
        if which == "log":
            self._page_log = page
            self._render_log_page()
        else:
            self._page_disp = page
            self._render_disp_page()

    # ── HELPERS ───────────────────────────────────────────────
    def _set_empty(self, table, msg, col_span):
        table.setRowCount(1)
        item = QTableWidgetItem(msg)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(QColor("#9CA3AF"))
        table.setItem(0, 0, item)
        table.setSpan(0, 0, 1, col_span)
        table.setRowHeight(0, 80)

    # ── EXPORT PDF ────────────────────────────────────────────
    def _export_pdf(self):
        d_from  = self.date_from.date().toPyDate()
        d_to    = self.date_to.date().toPyDate()
        action  = self.type_filter.currentText()

        if self._tab_idx == 0:
            tab_title = "Audit Log Report"
            headers   = ["ID", "Action", "Medicine", "Notes", "Performed By", "Date & Time"]
            data      = get_transaction_log(d_from, d_to, action)
            rows      = [[r.get("id"), r.get("action"), r.get("medicine","") or "—",
                          r.get("notes","") or "—", r.get("performed_by","") or "—",
                          str(r.get("performed_at",""))[:19]] for r in data]
        else:
            tab_title = "Top Dispensed Medicines"
            headers   = ["Medicine", "Times Dispensed"]
            data      = get_top_dispensed(d_from, d_to)
            rows      = [[r.get("name"), r.get("total_dispensed")] for r in data]

        if not rows:
            QMessageBox.information(self, "No Data", "No data to export.")
            return

        stats = get_summary_stats(d_from, d_to)
        summary = {
            "Total Medicines": stats["total_meds"],
            "Added":           stats["added"],
            "Updated":         stats["updated"],
            "Deleted":         stats["deleted"],
            "Dispensed":       stats["dispensed"],
        }

        title = f"MediTrack — {tab_title}  ({d_from} to {d_to})"

        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report",
            f"meditrack_{tab_title.lower().replace(' ','_')}_{d_from}_{d_to}.pdf",
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        ok, err = export_report_pdf(path, title, headers, rows, summary)
        if ok:
            QMessageBox.information(self, "Exported", f"PDF saved to:\n{path}")
        else:
            QMessageBox.critical(self, "Export Failed",
                f"Could not export PDF.\n\n{err}")


# ── Standalone preview ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = ReportView(user_id=1)
    win.setWindowTitle("Generate Report")
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec())