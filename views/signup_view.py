from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QSizePolicy,
    QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QByteArray
from PyQt6.QtGui import QFont, QCursor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer


class SignupView(QWidget):
    def __init__(self, on_signup=None, on_go_login=None):
        super().__init__()
        self.on_signup    = on_signup
        self.on_go_login  = on_go_login
        self._field_errors = {}       # attr_name -> QLabel
        self._terms_accepted = False
        self.setWindowTitle("Medicine Monitoring System — Create Account")
        self.setMinimumSize(900, 680)
        self._apply_styles()
        self._build_ui()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget#SignupRoot {
                background-color: #DDE1F0;
            }
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QFrame#Card {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
            QLabel#Title {
                font-size: 22px;
                font-weight: 700;
                color: #1A1A2E;
            }
            QLabel#Subtitle {
                font-size: 13px;
                color: #6B7280;
            }
            QLabel#FieldLabel {
                font-size: 13px;
                font-weight: 600;
                color: #374151;
            }
            QLineEdit#Input {
                border: 1.5px solid #E5E7EB;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1F2937;
                background: #FFFFFF;
            }
            QLineEdit#Input:focus {
                border: 1.5px solid #4F46E5;
            }
            QLineEdit#InputError {
                border: 1.5px solid #DC2626;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1F2937;
                background: #FEF2F2;
            }
            QLineEdit#InputOk {
                border: 1.5px solid #16A34A;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1F2937;
                background: #FFFFFF;
            }

            QPushButton#BtnPrimary {
                background-color: #4F46E5;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                padding: 12px;
            }
            QPushButton#BtnPrimary:hover    { background-color: #4338CA; }
            QPushButton#BtnPrimary:pressed  { background-color: #3730A3; }
            QPushButton#BtnPrimary:disabled {
                background-color: #A5B4FC;
                color: #E0E7FF;
            }
            QLabel#InlineError {
                color: #DC2626;
                font-size: 11px;
            }
            QLabel#InlineOk {
                color: #16A34A;
                font-size: 11px;
            }
            QLabel#GlobalError {
                color: #DC2626;
                font-size: 12px;
                background: #FEF2F2;
                border: 1px solid #FECACA;
                border-radius: 7px;
                padding: 8px 12px;
            }
            QLabel#GlobalSuccess {
                color: #166534;
                font-size: 12px;
                background: #DCFCE7;
                border: 1px solid #86EFAC;
                border-radius: 7px;
                padding: 8px 12px;
            }
            QPushButton#ToggleBtn {
                background: transparent;
                border: none;
                padding: 0 6px;
                qproperty-iconSize: 18px;
            }
            QPushButton#ToggleBtn:hover { background: transparent; }
            QPushButton#LinkBtn {
                color: #4F46E5;
                font-size: 13px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 0;
            }
            QPushButton#LinkBtn:hover {
                color: #4338CA;
                text-decoration: underline;
            }
            QLabel#SwitchLabel { color: #6B7280; font-size: 13px; }
            QFrame#IconCircle {
                background-color: #4F46E5;
                border-radius: 32px;
            }
            QLabel#IconLabel  { color: #FFFFFF; font-size: 20px; }
            QLabel#StrengthLabel { font-size: 11px; }
            QFrame#StrengthBar {
                border-radius: 3px;
                min-height: 5px;
                max-height: 5px;
            }
            QCheckBox#TermsCheck {
                font-size: 12px;
                color: #374151;
                spacing: 8px;
            }
            QCheckBox#TermsCheck::indicator {
                width: 16px; height: 16px;
                border: 1.5px solid #D1D5DB;
                border-radius: 4px;
                background: #FFFFFF;
            }
            QCheckBox#TermsCheck::indicator:checked {
                background: #4F46E5;
                border-color: #4F46E5;
            }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        self.setObjectName("SignupRoot")

        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.setContentsMargins(0, 20, 0, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_content.setObjectName("SignupRoot")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.setContentsMargins(0, 20, 0, 20)

        # Card
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(480)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 36, 40, 36)
        cl.setSpacing(0)

        # Icon
        icon_wrap = QHBoxLayout()
        icon_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_circle = QFrame()
        icon_circle.setObjectName("IconCircle")
        icon_circle.setFixedSize(64, 64)
        icon_inner = QVBoxLayout(icon_circle)
        icon_inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl = QLabel("✚")
        icon_lbl.setObjectName("IconLabel")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        icon_inner.addWidget(icon_lbl)
        icon_wrap.addWidget(icon_circle)
        cl.addLayout(icon_wrap)
        cl.addSpacing(16)

        title = QLabel("Create Account")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(title)
        cl.addSpacing(5)

        subtitle = QLabel("Register to access Medicine Monitoring System")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        cl.addWidget(subtitle)
        cl.addSpacing(24)

        # ── Full Name ──────────────────────────────────────────
        self._add_field(cl, "Full Name", "full_name",
                        "Enter your full name",
                        validator=self._validate_full_name)
        cl.addSpacing(12)

        # ── Username ───────────────────────────────────────────
        self._add_field(cl, "Username", "username",
                        "Choose a username (min. 3 characters)",
                        validator=self._validate_username)
        cl.addSpacing(12)

        # ── Email ──────────────────────────────────────────────
        self._add_field(cl, "Email", "email",
                        "Enter your email address",
                        validator=self._validate_email)
        cl.addSpacing(12)

        # ── Password + strength ────────────────────────────────
        pw_lbl = QLabel("Password")
        pw_lbl.setObjectName("FieldLabel")
        cl.addWidget(pw_lbl)
        cl.addSpacing(5)

        pw_wrap = QHBoxLayout()
        pw_wrap.setSpacing(0)
        self.input_password = QLineEdit()
        self.input_password.setObjectName("Input")
        self.input_password.setPlaceholderText("Create a password (min. 8 characters)")
        self.input_password.setMinimumHeight(44)
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.textChanged.connect(self._on_password_changed)
        self.toggle_pw = self._make_eye_btn()
        self.toggle_pw.setObjectName("ToggleBtn")
        self.toggle_pw.setFixedSize(38, 44)
        self.toggle_pw.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_pw.setCheckable(True)
        self.toggle_pw.clicked.connect(
            lambda checked: self._toggle_echo(self.input_password, self.toggle_pw, checked))
        pw_wrap.addWidget(self.input_password)
        pw_wrap.addWidget(self.toggle_pw)
        cl.addLayout(pw_wrap)
        cl.addSpacing(5)

        # Strength bar row
        strength_row = QHBoxLayout()
        strength_row.setSpacing(4)
        self._strength_bars = []
        for _ in range(4):
            bar = QFrame()
            bar.setObjectName("StrengthBar")
            bar.setMinimumWidth(0)
            bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            bar.setStyleSheet("background: #E5E7EB; border-radius: 3px;")
            strength_row.addWidget(bar)
            self._strength_bars.append(bar)
        self.strength_lbl = QLabel("")
        self.strength_lbl.setObjectName("StrengthLabel")
        self.strength_lbl.setFixedWidth(70)
        self.strength_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        strength_row.addWidget(self.strength_lbl)
        cl.addLayout(strength_row)

        # Inline error for password
        self.pw_error_lbl = QLabel("")
        self.pw_error_lbl.setObjectName("InlineError")
        self.pw_error_lbl.setVisible(False)
        cl.addWidget(self.pw_error_lbl)
        cl.addSpacing(12)

        # ── Confirm Password ───────────────────────────────────
        cp_lbl = QLabel("Confirm Password")
        cp_lbl.setObjectName("FieldLabel")
        cl.addWidget(cp_lbl)
        cl.addSpacing(5)

        cp_wrap = QHBoxLayout()
        cp_wrap.setSpacing(0)
        self.input_confirm = QLineEdit()
        self.input_confirm.setObjectName("Input")
        self.input_confirm.setPlaceholderText("Repeat your password")
        self.input_confirm.setMinimumHeight(44)
        self.input_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_confirm.textChanged.connect(self._on_confirm_changed)
        self.input_confirm.returnPressed.connect(self._handle_signup)
        self.toggle_cp = self._make_eye_btn()
        self.toggle_cp.setObjectName("ToggleBtn")
        self.toggle_cp.setFixedSize(38, 44)
        self.toggle_cp.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_cp.setCheckable(True)
        self.toggle_cp.clicked.connect(
            lambda checked: self._toggle_echo(self.input_confirm, self.toggle_cp, checked))
        cp_wrap.addWidget(self.input_confirm)
        cp_wrap.addWidget(self.toggle_cp)
        cl.addLayout(cp_wrap)

        self.cp_error_lbl = QLabel("")
        self.cp_error_lbl.setObjectName("InlineError")
        self.cp_error_lbl.setVisible(False)
        cl.addWidget(self.cp_error_lbl)
        cl.addSpacing(16)

        # ── Terms checkbox ─────────────────────────────────────
        self.terms_check = QCheckBox(
            "I agree to the Terms of Service and Privacy Policy")
        self.terms_check.setObjectName("TermsCheck")
        self.terms_check.stateChanged.connect(self._on_terms_changed)
        cl.addWidget(self.terms_check)
        cl.addSpacing(18)

        # ── Submit button ──────────────────────────────────────
        self.btn_submit = QPushButton("Create Account")
        self.btn_submit.setObjectName("BtnPrimary")
        self.btn_submit.setMinimumHeight(48)
        self.btn_submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_submit.clicked.connect(self._handle_signup)
        cl.addWidget(self.btn_submit)
        cl.addSpacing(10)

        # Global feedback labels
        self.error_label = QLabel("")
        self.error_label.setObjectName("GlobalError")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        cl.addWidget(self.error_label)

        self.success_label = QLabel("")
        self.success_label.setObjectName("GlobalSuccess")
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_label.setWordWrap(True)
        self.success_label.setVisible(False)
        cl.addWidget(self.success_label)

        cl.addSpacing(14)

        # Switch to login
        switch_row = QHBoxLayout()
        switch_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch_lbl = QLabel("Already have an account?")
        switch_lbl.setObjectName("SwitchLabel")
        btn_login = QPushButton("Sign in")
        btn_login.setObjectName("LinkBtn")
        btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_login.clicked.connect(self._go_login)
        switch_row.addWidget(switch_lbl)
        switch_row.addSpacing(4)
        switch_row.addWidget(btn_login)
        cl.addLayout(switch_row)

        scroll_layout.addWidget(card)
        scroll.setWidget(scroll_content)
        root_layout.addWidget(scroll)

    # ── FIELD BUILDER ─────────────────────────────────────────
    def _add_field(self, layout, label_text, attr_name, placeholder,
                   password=False, enter_action=None, validator=None):
        lbl = QLabel(label_text)
        lbl.setObjectName("FieldLabel")
        layout.addWidget(lbl)
        layout.addSpacing(5)

        inp = QLineEdit()
        inp.setObjectName("Input")
        inp.setPlaceholderText(placeholder)
        inp.setMinimumHeight(44)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        if enter_action:
            inp.returnPressed.connect(enter_action)
        if validator:
            inp.textChanged.connect(lambda _, fn=validator, a=attr_name, w=inp:
                                    fn(w.text(), w))
        setattr(self, f"input_{attr_name}", inp)
        layout.addWidget(inp)

        # Inline error label per field
        err_lbl = QLabel("")
        err_lbl.setObjectName("InlineError")
        err_lbl.setVisible(False)
        layout.addWidget(err_lbl)
        self._field_errors[attr_name] = err_lbl

    # ── REAL-TIME VALIDATORS ──────────────────────────────────
    def _set_field_state(self, widget, error_lbl, ok, message=""):
        if not widget.text():
            widget.setObjectName("Input")
            error_lbl.setVisible(False)
        elif ok:
            widget.setObjectName("InputOk")
            error_lbl.setVisible(False)
        else:
            widget.setObjectName("InputError")
            error_lbl.setText(message)
            error_lbl.setObjectName("InlineError")
            error_lbl.setVisible(True)
        # Force stylesheet refresh
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _validate_full_name(self, text, widget):
        err = self._field_errors["full_name"]
        self._set_field_state(widget, err,
                              len(text.strip()) >= 2,
                              "Please enter your full name.")

    def _validate_username(self, text, widget):
        err = self._field_errors["username"]
        ok  = len(text.strip()) >= 3 and text.strip().isalnum() or \
              all(c.isalnum() or c in "_-" for c in text.strip()) and len(text.strip()) >= 3
        self._set_field_state(widget, err, ok,
                              "Username must be at least 3 characters (letters, numbers, _ -).")

    def _validate_email(self, text, widget):
        err = self._field_errors["email"]
        ok  = "@" in text and "." in text.split("@")[-1] if text else False
        self._set_field_state(widget, err, ok,
                              "Please enter a valid email address.")

    def _on_password_changed(self, text):
        score, label, colors = self._password_strength(text)
        bar_colors = ["#E5E7EB"] * 4
        for i in range(score):
            bar_colors[i] = colors
        for bar, color in zip(self._strength_bars, bar_colors):
            bar.setStyleSheet(f"background: {color}; border-radius: 3px;")
        self.strength_lbl.setText(label if text else "")
        strength_ok = score >= 2

        # Inline pw error
        if text and not strength_ok:
            self.input_password.setObjectName("InputError")
            self.pw_error_lbl.setText("Password too weak — add numbers or symbols.")
            self.pw_error_lbl.setVisible(True)
        elif text:
            self.input_password.setObjectName("InputOk")
            self.pw_error_lbl.setVisible(False)
        else:
            self.input_password.setObjectName("Input")
            self.pw_error_lbl.setVisible(False)
        self.input_password.style().unpolish(self.input_password)
        self.input_password.style().polish(self.input_password)

        # Re-validate confirm if already filled
        if self.input_confirm.text():
            self._on_confirm_changed(self.input_confirm.text())

    def _on_confirm_changed(self, text):
        pw = self.input_password.text()
        if not text:
            self.input_confirm.setObjectName("Input")
            self.cp_error_lbl.setVisible(False)
        elif text == pw:
            self.input_confirm.setObjectName("InputOk")
            self.cp_error_lbl.setVisible(False)
        else:
            self.input_confirm.setObjectName("InputError")
            self.cp_error_lbl.setText("Passwords do not match.")
            self.cp_error_lbl.setVisible(True)
        self.input_confirm.style().unpolish(self.input_confirm)
        self.input_confirm.style().polish(self.input_confirm)

    def _on_terms_changed(self, state):
        self._terms_accepted = (state == Qt.CheckState.Checked.value)

    @staticmethod
    def _password_strength(pw):
        """Returns (score 0-4, label, bar_color)."""
        if not pw:
            return 0, "", "#E5E7EB"
        score = 0
        if len(pw) >= 8:   score += 1
        if len(pw) >= 12:  score += 1
        if any(c.isdigit() for c in pw):  score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in pw):  score += 1
        labels = {1: "Weak", 2: "Fair", 3: "Good", 4: "Strong"}
        colors = {1: "#EF4444", 2: "#F59E0B", 3: "#3B82F6", 4: "#16A34A"}
        return score, labels.get(score, ""), colors.get(score, "#E5E7EB")

    # ── EYE ICON HELPERS ──────────────────────────────────────
    _SVG_EYE = b"""<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
        viewBox="0 0 24 24" fill="none" stroke="#9CA3AF"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
    </svg>"""

    _SVG_EYE_OFF = b"""<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
        viewBox="0 0 24 24" fill="none" stroke="#4F46E5"
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8
                 a18.45 18.45 0 0 1 5.06-5.94"/>
        <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8
                 a18.5 18.5 0 0 1-2.16 3.19"/>
        <line x1="1" y1="1" x2="23" y2="23"/>
    </svg>"""

    @classmethod
    def _svg_to_icon(cls, svg_bytes: bytes) -> QIcon:
        renderer = QSvgRenderer(QByteArray(svg_bytes))
        pixmap   = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter  = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)

    def _make_eye_btn(self) -> QPushButton:
        btn = QPushButton()
        btn.setIcon(self._svg_to_icon(self._SVG_EYE))
        btn.setIconSize(btn.sizeHint())
        btn.setFixedSize(38, 44)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setCheckable(True)
        return btn

    @staticmethod
    def _toggle_echo(widget, btn, checked):
        if checked:
            widget.setEchoMode(QLineEdit.EchoMode.Normal)
            btn.setIcon(SignupView._svg_to_icon(SignupView._SVG_EYE_OFF))
        else:
            widget.setEchoMode(QLineEdit.EchoMode.Password)
            btn.setIcon(SignupView._svg_to_icon(SignupView._SVG_EYE))

    # ── SUBMIT ────────────────────────────────────────────────
    def _handle_signup(self):
        full_name = self.input_full_name.text().strip()
        username  = self.input_username.text().strip()
        email     = self.input_email.text().strip()
        password  = self.input_password.text()
        confirm   = self.input_confirm.text()

        self.error_label.setVisible(False)
        self.success_label.setVisible(False)

        # Full validation on submit
        if not full_name or len(full_name) < 2:
            return self._show_error("Please enter your full name.")
        if len(username) < 3 or not all(c.isalnum() or c in "_-" for c in username):
            return self._show_error(
                "Username must be at least 3 characters (letters, numbers, _ -).")
        if "@" not in email or "." not in email.split("@")[-1]:
            return self._show_error("Please enter a valid email address.")
        score, _, _ = self._password_strength(password)
        if score < 2:
            return self._show_error(
                "Password is too weak. Use at least 8 characters with numbers or symbols.")
        if password != confirm:
            return self._show_error("Passwords do not match.")
        if not self._terms_accepted:
            return self._show_error(
                "You must accept the Terms of Service to create an account.")

        self.btn_submit.setEnabled(False)
        self.btn_submit.setText("Creating account…")

        if self.on_signup:
            result = self.on_signup(full_name, username, email, password)
            if result and result.get("error"):
                self._show_error(result["error"])
                self.btn_submit.setEnabled(True)
                self.btn_submit.setText("Create Account")
            else:
                self._show_success(
                    "Account created successfully! Redirecting to login…")
                QTimer.singleShot(1800, self._go_login)
        else:
            # No callback wired — restore button
            self.btn_submit.setEnabled(True)
            self.btn_submit.setText("Create Account")

    def _go_login(self):
        if self.on_go_login:
            self.on_go_login()

    def _show_error(self, msg: str):
        self.error_label.setText(msg)
        self.error_label.setVisible(True)
        self.success_label.setVisible(False)

    def _show_success(self, msg: str):
        self.success_label.setText(msg)
        self.success_label.setVisible(True)
        self.error_label.setVisible(False)

    # ── PUBLIC API ────────────────────────────────────────────
    def show_error(self, message: str):
        self._show_error(message)

    def clear(self):
        for attr in ["full_name", "username", "email", "password", "confirm"]:
            getattr(self, f"input_{attr}").clear()
        self.terms_check.setChecked(False)
        self.error_label.setVisible(False)
        self.success_label.setVisible(False)
        self.pw_error_lbl.setVisible(False)
        self.cp_error_lbl.setVisible(False)
        for lbl in self._field_errors.values():
            lbl.setVisible(False)
        for bar in self._strength_bars:
            bar.setStyleSheet("background: #E5E7EB; border-radius: 3px;")
        self.strength_lbl.setText("")
        self.btn_submit.setEnabled(True)
        self.btn_submit.setText("Create Account")


# ── Standalone preview ────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    def mock_signup(full_name, username, email, password):
        print(f"Signup → name={full_name}, user={username}, email={email}")
        # Simulate a duplicate username error:
        # return {"error": "Username already taken."}
        return {}   # success

    app = QApplication(sys.argv)
    win = SignupView(
        on_signup=mock_signup,
        on_go_login=lambda: print("Navigate to Login")
    )
    win.show()
    sys.exit(app.exec())