import sys
import ctypes
import ctypes.wintypes
from ctypes import cast, POINTER

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect, QRectF, QPoint, QPointF, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

HWND_TOPMOST = ctypes.wintypes.HWND(-1)
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SW_SHOW = 5
SWP_SHOWWINDOW = 0x0040

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32
_SetWindowPos = _user32.SetWindowPos
_FindWindow = _user32.FindWindowW
_ShowWindow = _user32.ShowWindow
_CreateMutex = _kernel32.CreateMutexW
_GetLastError = _kernel32.GetLastError

MUTEX_NAME = "Global\\StreamerMicIcon_SingleInstance"
WINDOW_TITLE = "StreamerMicIcon_Overlay"
ERROR_ALREADY_EXISTS = 183


def get_default_mic_mute_state():
    """Return True if default microphone is muted, False otherwise."""
    try:
        devices = AudioUtilities.GetMicrophone()
        if devices is None:
            return None
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return bool(volume.GetMute())
    except Exception:
        return None


class MicOverlay(QWidget):
    ICON_SIZE = 128
    PADDING = 16

    def __init__(self):
        super().__init__()
        self.is_muted = None
        self._drag_pos = None
        self._flash_opacity = 1.0
        self._init_window()
        self._init_flash_animation()
        self._start_polling()

    # --- Flash animation property ---
    def _get_flash_opacity(self):
        return self._flash_opacity

    def _set_flash_opacity(self, value):
        self._flash_opacity = value
        self.update()

    flash_opacity = pyqtProperty(float, _get_flash_opacity, _set_flash_opacity)

    def _init_flash_animation(self):
        self._flash_anim = QPropertyAnimation(self, b"flash_opacity")
        self._flash_anim.setDuration(700)
        self._flash_anim.setStartValue(1.0)
        self._flash_anim.setEndValue(0.15)
        self._flash_anim.setLoopCount(-1)
        from PyQt5.QtCore import QEasingCurve
        self._flash_anim.setEasingCurve(QEasingCurve.InOutSine)

    def _update_flash(self):
        if self.is_muted:
            if self._flash_anim.state() != QPropertyAnimation.Running:
                self._flash_anim.start()
        else:
            self._flash_anim.stop()
            self._flash_opacity = 1.0

    def _init_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle(WINDOW_TITLE)
        size = self.ICON_SIZE + self.PADDING * 2
        self.setFixedSize(size, size)

        self.move(self._default_position())

    def _force_topmost(self):
        if not self.isVisible():
            self.show()
        hwnd = int(self.winId())
        _SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
        )
        self._ensure_on_screen()

    def _ensure_on_screen(self):
        """If the window has drifted offscreen (e.g. monitor disconnected), reset position."""
        if self._drag_pos is not None:
            return

        window_rect = QRect(self.pos(), self.size())
        if not any(window_rect.intersects(screen.geometry())
                   for screen in QApplication.screens()):
            self.move(self._default_position())

    def _default_position(self):
        """Return the default bottom-right position on the primary screen."""
        screen = QApplication.primaryScreen()
        geometry = screen.availableGeometry() if screen else QApplication.desktop().availableGeometry()
        size = self.width()
        x = max(geometry.left(), geometry.left() + geometry.width() - size - 30)
        y = max(geometry.top(), geometry.top() + geometry.height() - size - 80)
        return QPoint(x, y)

    def _start_polling(self):
        self._poll_mic()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._poll_mic)
        self.timer.start(250)

        self._topmost_timer = QTimer(self)
        self._topmost_timer.timeout.connect(self._force_topmost)
        self._topmost_timer.start(1000)

    def _poll_mic(self):
        state = get_default_mic_mute_state()
        if state != self.is_muted:
            self.is_muted = state
            self._update_flash()
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        opacity = self._flash_opacity if self.is_muted else 1.0
        p.setOpacity(opacity)

        cx = self.width() / 2
        cy = self.height() / 2
        s = self.ICON_SIZE

        if self.is_muted is None:
            color = QColor(180, 180, 180)
        elif self.is_muted:
            color = QColor(220, 50, 50)
        else:
            color = QColor(50, 200, 80)

        shadow = QColor(0, 0, 0, 60)
        p.setBrush(QBrush(shadow))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx + 2, cy + 2), s * 0.46, s * 0.46)

        bg = QColor(30, 30, 30, 210)
        p.setBrush(QBrush(bg))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), s * 0.46, s * 0.46)

        self._draw_mic(p, cx, cy, s, color)

        if self.is_muted:
            self._draw_slash(p, cx, cy, s)

        p.end()

    def _draw_mic(self, p, cx, cy, s, color):
        pen = QPen(color, s * 0.045, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)

        # Mic body (rounded rect)
        body_w = s * 0.18
        body_h = s * 0.30
        body_x = cx - body_w
        body_y = cy - s * 0.24
        body_rect = QRectF(body_x, body_y, body_w * 2, body_h)
        p.setBrush(QBrush(color))
        p.drawRoundedRect(body_rect, body_w, body_w)

        # Arc (the "cup" around the mic)
        p.setBrush(Qt.NoBrush)
        arc_w = s * 0.26
        arc_h = s * 0.22
        arc_rect = QRectF(cx - arc_w, cy - s * 0.14, arc_w * 2, arc_h * 2)
        p.drawArc(arc_rect, 0, -180 * 16)

        # Stem line down from arc
        stem_top = cy - s * 0.14 + arc_h * 2
        stem_bot = stem_top + s * 0.08
        p.drawLine(QPointF(cx, stem_top), QPointF(cx, stem_bot))

        # Base line
        base_w = s * 0.12
        p.drawLine(QPointF(cx - base_w, stem_bot), QPointF(cx + base_w, stem_bot))

    def _draw_slash(self, p, cx, cy, s):
        pen = QPen(QColor(220, 50, 50), s * 0.06, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        offset = s * 0.30
        p.drawLine(QPointF(cx - offset, cy - offset), QPointF(cx + offset, cy + offset))

    # --- Drag support ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        """Double-click to quit."""
        QApplication.quit()


def _bring_existing_to_front():
    """Find the already-running instance's window and force it visible."""
    hwnd = _FindWindow(None, WINDOW_TITLE)
    if hwnd:
        _ShowWindow(hwnd, SW_SHOW)
        _SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW,
        )


def main():
    _user32.SetProcessDPIAware()

    _mutex = _CreateMutex(None, False, WINDOW_TITLE)
    if _GetLastError() == ERROR_ALREADY_EXISTS:
        _bring_existing_to_front()
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    overlay = MicOverlay()
    overlay.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
