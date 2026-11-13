"""Scroll sync manager — synchronizes scrolling between QTextEdit and QWebEngineView.

Encapsulates the JS tracker, QWebChannel bridge, and scroll synchronization logic
that connects the editor's vertical scrollbar with the preview's scroll position.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PyQt6.QtCore import QObject, QTimer, pyqtSlot
from PyQt6.QtWebChannel import QWebChannel

if TYPE_CHECKING:
    from markdown_editor_pkg.editor import MarkdownEditorPyQt

logger = logging.getLogger(__name__)

_SCROLL_JS = """
(function() {
    var lastPct = -1;
    var bridge = null;
    var scrollPollingStarted = false;

    function startPolling() {
        if (scrollPollingStarted) return;
        scrollPollingStarted = true;

        // Опрос скролла каждые 100мс вместо событий scroll
        setInterval(function() {
            var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            var scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            var pct = scrollHeight > 0 ? scrollTop / scrollHeight : 0;

            if (Math.abs(pct - lastPct) > 0.001) {
                lastPct = pct;
                // Не отправляем событие, если скролл инициирован из редактора
                if (bridge && typeof bridge.onPreviewScroll === 'function' && !bridge._isScrolling) {
                    try {
                        bridge.onPreviewScroll(pct);
                    } catch(e) {
                        // Игнорируем ошибки
                    }
                }
            }
        }, 100);
    }

    // Ждём появления qt_object из QWebChannel
    function waitForBridge() {
        try {
            if (typeof qt_object !== 'undefined' && typeof qt_object.onPreviewScroll === 'function') {
                bridge = qt_object;
                startPolling();
            } else {
                setTimeout(waitForBridge, 50);
            }
        } catch(e) {
            setTimeout(waitForBridge, 50);
        }
    }

    // Запускаем ожидание
    waitForBridge();
})();
"""


class ScrollBridge(QObject):
    """Мост между JavaScript и PyQt для событий скролла."""

    _handler: object
    _isScrolling: bool = False

    @pyqtSlot(float)
    def onPreviewScroll(self, scroll_pct: float) -> None:
        self._handler.on_preview_scroll(scroll_pct)  # type: ignore[attr-defined]

    @pyqtSlot()
    def onScrollFromEditor(self) -> None:
        """Устанавливает флаг, что скролл инициирован из редактора."""
        self._handler._scroll_from_editor = True  # type: ignore[attr-defined]


class ScrollSyncManager(QObject):
    """Управляет синхронизацией прокрутки между QTextEdit и QWebEngineView.

    Инкапсулирует:
    - QWebChannel и ScrollBridge для передачи событий из JS в PyQt
    - JS-трекер для опроса позиции скролла в превью
    - Подключение скроллбара редактора к обработчику синхронизации
    """

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._editor: MarkdownEditorPyQt | None = None
        self._scroll_bridge: ScrollBridge | None = None
        self._scroll_channel: QWebChannel | None = None
        self._init_scroll_timer: QTimer | None = None
        self._scroll_js_timer: QTimer | None = None

    @property
    def scroll_bridge(self) -> ScrollBridge | None:
        """Возвращает мост ScrollBridge или None."""
        return self._scroll_bridge

    @property
    def scroll_channel(self) -> QWebChannel | None:
        """Возвращает QWebChannel или None."""
        return self._scroll_channel

    def init(self) -> None:
        """Инициализация синхронизации прокрутки.

        Подключает скроллбар редактора и инжектит JS-трекер в превью.
        """
        self._editor = self.parent()  # type: ignore[assignment]
        if self._editor is None:
            return
        editor = self._editor
        # Подключаем скролл редактора
        vbar = editor.editor.verticalScrollBar()
        if vbar is not None:
            vbar.valueChanged.connect(editor.event_handler.sync_scroll_from_editor)

        # Инжектим JavaScript для отслеживания скролла в превью
        self._inject_scroll_tracker_js()

    def _inject_scroll_tracker_js(self) -> None:
        """Инжектит JavaScript для отслеживания скролла в QWebEngineView."""
        assert self._editor is not None
        editor = self._editor
        if editor.preview is None:
            return

        page = editor.preview.page()
        if page is None:
            return

        # Создаём объект-мост для передачи событий из JS в PyQt
        self._scroll_bridge = ScrollBridge()
        self._scroll_bridge._handler = editor.event_handler

        # Создаём QWebChannel и регистрируем объект
        self._scroll_channel = QWebChannel()
        self._scroll_channel.registerObject("qt_object", self._scroll_bridge)

        # Запускаем JS-трекер сразу (без ожидания loadFinished)
        # Это нужно, потому что setHtml не вызывает loadFinished
        self._init_scroll_timer = QTimer(self)
        self._init_scroll_timer.setSingleShot(True)
        self._init_scroll_timer.timeout.connect(lambda: self._init_scroll_tracker(delay=500))
        self._init_scroll_timer.start(500)

    def _init_scroll_tracker(self, delay: int = 100) -> None:
        """Запускает JS-трекер скролла с заданной задержкой.

        Args:
            delay: Задержка в мс перед запуском трекера.
        """
        assert self._editor is not None
        editor = self._editor
        if editor.preview is None:
            return

        page = editor.preview.page()
        if page is None:
            return

        # Регистрируем QWebChannel
        if self._scroll_channel is not None:
            page.setWebChannel(self._scroll_channel)

        # Запускаем JS-трекер (он сам подождёт появления qt_object)
        self._scroll_js_timer = QTimer(self)
        self._scroll_js_timer.setSingleShot(True)
        self._scroll_js_timer.timeout.connect(
            lambda: page.runJavaScript(_SCROLL_JS)  # type: ignore[arg-type]
        )
        self._scroll_js_timer.start(delay)

    def get_scroll_js(self) -> str:
        """Возвращает JavaScript-код для отслеживания скролла."""
        return _SCROLL_JS

    def stop_timers(self) -> None:
        """Останавливает все таймеры."""
        for timer in (self._init_scroll_timer, self._scroll_js_timer):
            if timer is not None:
                timer.stop()
                timer.deleteLater()
        self._init_scroll_timer = None
        self._scroll_js_timer = None
