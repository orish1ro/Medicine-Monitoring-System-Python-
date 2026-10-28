import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QSizePolicy, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor, QPixmap, QIcon


class LoginView(QWidget):
    def __init__(self, on_login=None, on_go_signup=None):
        super().__init__()
        self.on_login = on_login
        self.on_go_signup = on_go_signup
        self.setWindowTitle("Medicine Monitoring System")
        self.setMinimumSize(900, 600)

        # ── Window icon (top-left title bar & taskbar) ────────
        _icon_path = os.path.join(os.path.dirname(__file__), "icons", "logo.png")
        if os.path.exists(_icon_path):
            self.setWindowIcon(QIcon(_icon_path))

        self._apply_styles()
        self._build_ui()

    # ── STYLES ────────────────────────────────────────────────
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget#LoginRoot {
                background-color: #DDE1F0;
            }
            QFrame#Card {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
            QLabel#Subtitle {
                font-size: 13px;
                color: #6B7280;
            }
            QLabel#FieldLabel {
                font-size: 13px;
                font-weight: 500;
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
            QLineEdit#InputValid {
                border: 1.5px solid #10B981;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1F2937;
                background: #FFFFFF;
            }
            QLineEdit#InputError {
                border: 1.5px solid #DC2626;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #1F2937;
                background: #FFFFFF;
            }
            QFrame#PassFrame {
                border: 1.5px solid #E5E7EB;
                border-radius: 8px;
                background: #FFFFFF;
            }
            QFrame#PassFrameFocus {
                border: 1.5px solid #4F46E5;
                border-radius: 8px;
                background: #FFFFFF;
            }
            QFrame#PassFrameError {
                border: 1.5px solid #DC2626;
                border-radius: 8px;
                background: #FFFFFF;
            }
            QLineEdit#PassInput {
                border: none;
                background: transparent;
                font-size: 14px;
                color: #1F2937;
                padding: 0px;
            }
            QLineEdit#PassInput:focus {
                border: none;
            }
            QPushButton#TogglePassBtn {
                color: #6B7280;
                font-size: 12px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 2px 8px;
                border-radius: 4px;
            }
            QPushButton#TogglePassBtn:hover {
                color: #4F46E5;
                background: #EEF2FF;
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
            QPushButton#BtnPrimary:hover {
                background-color: #4338CA;
            }
            QPushButton#BtnPrimary:pressed {
                background-color: #3730A3;
            }
            QPushButton#BtnPrimary:disabled {
                background-color: #A5B4FC;
            }
            QLabel#ErrorLabel {
                color: #DC2626;
                font-size: 12px;
            }
            QLabel#CapsLabel {
                color: #F59E0B;
                font-size: 11px;
            }
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
            QLabel#SwitchLabel {
                color: #6B7280;
                font-size: 13px;
            }
            QLabel#DividerLabel {
                color: #9CA3AF;
                font-size: 12px;
            }
            QCheckBox#RememberCheck {
                font-size: 13px;
                color: #374151;
                spacing: 6px;
            }
            QCheckBox#RememberCheck::indicator {
                width: 15px;
                height: 15px;
                border: 1.5px solid #D1D5DB;
                border-radius: 4px;
                background: #FFFFFF;
            }
            QCheckBox#RememberCheck::indicator:checked {
                background-color: #4F46E5;
                border-color: #4F46E5;
            }
        """)

    # ── UI BUILD ──────────────────────────────────────────────
    def _build_ui(self):
        self.setObjectName("LoginRoot")

        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(460)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 32, 40, 40)
        card_layout.setSpacing(0)

        # ── Logo (views/icons/logo.png) ───────────────────────
        logo_path = os.path.join(os.path.dirname(__file__), "icons", "logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_lbl = QLabel()
            logo_lbl.setPixmap(
                pixmap.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
            )
            logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_lbl.setStyleSheet("background: transparent; border: none;")
            card_layout.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        card_layout.addSpacing(6)

        # ── Subtitle ──────────────────────────────────────────
        subtitle = QLabel("Sign in to manage inventory")
        subtitle.setObjectName("Subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(28)

        # ── Username ──────────────────────────────────────────
        user_label_row = QHBoxLayout()
        lbl_user = QLabel("Username")
        lbl_user.setObjectName("FieldLabel")
        self.user_valid_icon = QLabel("✓")
        self.user_valid_icon.setStyleSheet("color: #10B981; font-size: 14px;")
        self.user_valid_icon.setVisible(False)
        user_label_row.addWidget(lbl_user)
        user_label_row.addWidget(self.user_valid_icon)
        user_label_row.addStretch()
        card_layout.addLayout(user_label_row)
        card_layout.addSpacing(6)

        self.input_user = QLineEdit()
        self.input_user.setObjectName("Input")
        self.input_user.setPlaceholderText("Enter your username")
        self.input_user.setMinimumHeight(44)
        self.input_user.textChanged.connect(self._on_username_changed)
        self.input_user.returnPressed.connect(lambda: self.input_pass.setFocus())
        card_layout.addWidget(self.input_user)
        card_layout.addSpacing(16)

        # ── Password ──────────────────────────────────────────
        lbl_pass = QLabel("Password")
        lbl_pass.setObjectName("FieldLabel")
        card_layout.addWidget(lbl_pass)
        card_layout.addSpacing(6)

        self.pass_frame = QFrame()
        self.pass_frame.setObjectName("PassFrame")
        self.pass_frame.setMinimumHeight(44)
        pass_frame_layout = QHBoxLayout(self.pass_frame)
        pass_frame_layout.setContentsMargins(14, 0, 8, 0)
        pass_frame_layout.setSpacing(0)

        self.input_pass = QLineEdit()
        self.input_pass.setObjectName("PassInput")
        self.input_pass.setPlaceholderText("Enter your password")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setMinimumHeight(42)
        self.input_pass.returnPressed.connect(self._handle_login)
        self.input_pass.installEventFilter(self)

        # Focus in/out to change frame border color
        self.input_pass.focusInEvent  = self._pass_focus_in
        self.input_pass.focusOutEvent = self._pass_focus_out

        self.toggle_pass_btn = QPushButton("Show")
        self.toggle_pass_btn.setObjectName("TogglePassBtn")
        self.toggle_pass_btn.setFixedSize(44, 32)
        self.toggle_pass_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_pass_btn.clicked.connect(self._toggle_password_visibility)
        self._pass_visible = False

        pass_frame_layout.addWidget(self.input_pass)
        pass_frame_layout.addWidget(self.toggle_pass_btn)
        card_layout.addWidget(self.pass_frame)

        # ── Caps Lock warning ─────────────────────────────────
        self.caps_label = QLabel("⚠  Caps Lock is on")
        self.caps_label.setObjectName("CapsLabel")
        self.caps_label.setVisible(False)
        card_layout.addWidget(self.caps_label)
        card_layout.addSpacing(16)

        # ── Remember me ───────────────────────────────────────
        self.remember_check = QCheckBox("Remember me")
        self.remember_check.setObjectName("RememberCheck")
        self.remember_check.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card_layout.addWidget(self.remember_check)
        card_layout.addSpacing(20)

        # ── Sign In button ────────────────────────────────────
        self.btn_login = QPushButton("Sign In")
        self.btn_login.setObjectName("BtnPrimary")
        self.btn_login.setMinimumHeight(48)
        self.btn_login.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_login.clicked.connect(self._handle_login)
        card_layout.addWidget(self.btn_login)
        card_layout.addSpacing(10)

        # ── Error label ───────────────────────────────────────
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(18)

        # ── Divider ───────────────────────────────────────────
        divider_row = QHBoxLayout()
        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("color: #E5E7EB;")
        divider_lbl = QLabel("New here?")
        divider_lbl.setObjectName("DividerLabel")
        divider_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("color: #E5E7EB;")
        divider_row.addWidget(line1)
        divider_row.addSpacing(8)
        divider_row.addWidget(divider_lbl)
        divider_row.addSpacing(8)
        divider_row.addWidget(line2)
        card_layout.addLayout(divider_row)
        card_layout.addSpacing(12)

        # ── Sign up row ───────────────────────────────────────
        switch_row = QHBoxLayout()
        switch_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        switch_lbl = QLabel("Don't have an account?")
        switch_lbl.setObjectName("SwitchLabel")
        btn_signup = QPushButton("Sign up")
        btn_signup.setObjectName("LinkBtn")
        btn_signup.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_signup.clicked.connect(self._go_signup)
        switch_row.addWidget(switch_lbl)
        switch_row.addSpacing(4)
        switch_row.addWidget(btn_signup)
        card_layout.addLayout(switch_row)

        root_layout.addWidget(card)

    # ── PASS FRAME FOCUS BORDER ───────────────────────────────
    def _pass_focus_in(self, event):
        self.pass_frame.setObjectName("PassFrameFocus")
        self.pass_frame.style().unpolish(self.pass_frame)
        self.pass_frame.style().polish(self.pass_frame)
        QLineEdit.focusInEvent(self.input_pass, event)

    def _pass_focus_out(self, event):
        # Only reset if not in error state
        if self.pass_frame.objectName() != "PassFrameError":
            self.pass_frame.setObjectName("PassFrame")
            self.pass_frame.style().unpolish(self.pass_frame)
            self.pass_frame.style().polish(self.pass_frame)
        QLineEdit.focusOutEvent(self.input_pass, event)

    # ── EVENT FILTER (Caps Lock) ──────────────────────────────
    def eventFilter(self, obj, event):
        if obj == self.input_pass and event.type() == event.Type.KeyPress:
            text = event.text()
            if text and text.isalpha():
                caps_on = text.isupper() and not (
                    event.modifiers() & Qt.KeyboardModifier.ShiftModifier
                )
                self.caps_label.setVisible(caps_on)
        return super().eventFilter(obj, event)

    # ── HANDLERS ──────────────────────────────────────────────
    def _on_username_changed(self, text):
        valid = len(text.strip()) >= 3
        self.user_valid_icon.setVisible(valid)
        self.input_user.setObjectName("InputValid" if valid else "Input")
        self.input_user.style().unpolish(self.input_user)
        self.input_user.style().polish(self.input_user)

    def _toggle_password_visibility(self):
        self._pass_visible = not self._pass_visible
        self.input_pass.setEchoMode(
            QLineEdit.EchoMode.Normal if self._pass_visible
            else QLineEdit.EchoMode.Password
        )
        self.toggle_pass_btn.setText("Hide" if self._pass_visible else "Show")

    def _handle_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()

        if len(username) < 3:
            self._show_error("Username must be at least 3 characters.")
            self.input_user.setObjectName("InputError")
            self.input_user.style().unpolish(self.input_user)
            self.input_user.style().polish(self.input_user)
            self.input_user.setFocus()
            return

        if len(password) < 4:
            self._show_error("Password must be at least 4 characters.")
            self.pass_frame.setObjectName("PassFrameError")
            self.pass_frame.style().unpolish(self.pass_frame)
            self.pass_frame.style().polish(self.pass_frame)
            self.input_pass.setFocus()
            return

        self.error_label.setVisible(False)
        self.btn_login.setEnabled(False)
        self.btn_login.setText("Signing in...")
        QTimer.singleShot(1500, lambda: self._finish_login(username, password))

    def _finish_login(self, username, password):
        self.btn_login.setEnabled(True)
        self.btn_login.setText("Sign In")
        if self.on_login:
            self.on_login(username, password)

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def _go_signup(self):
        if self.on_go_signup:
            self.on_go_signup()

    def show_error(self, message: str):
        self._show_error(message)

    def clear(self):
        self.input_user.clear()
        self.input_pass.clear()
        self.error_label.setVisible(False)
        self.caps_label.setVisible(False)
        self.user_valid_icon.setVisible(False)
        self.remember_check.setChecked(False)
        self.input_user.setObjectName("Input")
        self.input_user.style().unpolish(self.input_user)
        self.input_user.style().polish(self.input_user)
        self.pass_frame.setObjectName("PassFrame")
        self.pass_frame.style().unpolish(self.pass_frame)
        self.pass_frame.style().polish(self.pass_frame)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = LoginView(
        on_login=lambda u, p: print(f"Login: {u} / {p}"),
        on_go_signup=lambda: print("Go to signup"),
    )
    win.show()
    sys.exit(app.exec())