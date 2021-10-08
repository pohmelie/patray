import fractions
import random
import sys
from fnmatch import fnmatch
from functools import partial
from importlib import resources
from typing import Callable, List, Optional

from loguru import logger
from PySide2.QtCore import QLibraryInfo, QObject, QPoint, Qt, Signal
from PySide2.QtGui import QCursor, QIcon, QImage, QPixmap
from PySide2.QtWidgets import (QApplication, QButtonGroup, QComboBox, QHBoxLayout, QLabel, QMenu, QMessageBox,
                               QRadioButton, QSlider, QStyleOptionSlider, QSystemTrayIcon, QToolTip, QVBoxLayout,
                               QWidget, QWidgetAction)

from . import version
from .pa import EndType, Pulse

py_version_info = sys.version.strip("\n")
ABOUT = f"""<a href="https://github.com/pohmelie/patray">https://github.com/pohmelie/patray</a><br>
version: {version}<br>
python: {py_version_info}<br>
pyside2: {QLibraryInfo.version().toString()}<br>
<br>
Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a>
 from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>
"""


class CustomMenu(QMenu):

    def mouseReleaseEvent(self, e):
        return


class TipSlider(QSlider):

    def __init__(self, *args, tip_offset=QPoint(0, -45), **kwargs):
        super().__init__(*args, **kwargs)
        self.tip_offset = tip_offset
        self.style = QApplication.style()
        self.opt = QStyleOptionSlider()
        self.valueChanged.connect(self.show_tip)

    def show_tip(self, value):
        self.initStyleOption(self.opt)
        rectHandle = self.style.subControlRect(self.style.CC_Slider, self.opt, self.style.SC_SliderHandle)
        pos_local = rectHandle.topLeft() + self.tip_offset
        pos_global = self.mapToGlobal(pos_local)
        QToolTip.showText(pos_global, f"{value}%", self)


class Patray(QObject):

    rebuild_signal = Signal()
    SYMBOL_BY_TYPE = {
        EndType.sink: "🔊",
        EndType.source: "🎤",
    }

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.pulse = Pulse(config)
        self.menu = CustomMenu()
        self.build_tray()
        self.rebuild_signal.connect(self.rebuild_menu, type=Qt.QueuedConnection)

    def quit(self):
        logger.info("closing...")
        self.pulse.close()
        sys.exit()

    def about(self):
        QMessageBox.about(None, "About patray", ABOUT)

    def activated(self, reason):
        logger.debug("tray activated (reason {})", reason)
        self.set_icon()
        self.position = QCursor.pos()
        self.rebuild_menu()

    def get_icon(self):
        logger.debug("loading icon...")
        if self.config.icon_path:
            logger.debug("will use {!r} icon path", self.config.icon_path)
            return None, QIcon(self.config.icon_path)
        else:
            if self.config.icon_color == "random":
                color = f"#{random.randint(0, 2 ** 24):x}"
            else:
                color = self.config.icon_color
            logger.debug("will render icon with {!r} color", color)
            raw = resources.read_binary("patray", "icon.svg.template")
            rendered = raw.replace(b"{}", color.encode())
            image = QImage.fromData(rendered, "SVG")
            pixmap = QPixmap.fromImage(image)
            icon = QIcon(pixmap)
            return color, icon

    def set_icon(self):
        color, self.icon = self.get_icon()
        self.tray.setIcon(self.icon)
        if color:
            self.tray.setToolTip(f"patray ({color})")
        else:
            self.tray.setToolTip("patray")

    def build_tray(self):
        logger.info("building tray...")
        self.tray = QSystemTrayIcon()
        self.tray.activated.connect(self.activated)
        self.set_icon()
        menu = QMenu()
        menu.addAction("About").triggered.connect(self.about)
        menu.addAction("Quit").triggered.connect(self.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def rebuild_menu(self):
        logger.debug("rebuilding menu...")
        self.pulse.update()
        self.menu.hide()
        self.menu.clear()
        self._non_gc_bucket = []

        widget = QWidget()
        self.vbox = QVBoxLayout(widget)
        widget.setLayout(self.vbox)
        action = QWidgetAction(self.menu)
        action.setDefaultWidget(widget)
        self.menu.addAction(action)

        if self.config.profile_enabled:
            self.add_cards()
        self.add_ends()

        logger.debug("poping up widget at {}", self.position)
        self.menu.popup(self.position)

    def add_widget(self, w: QWidget, weight: float = 1.0) -> QWidget:
        if weight != 1.0:
            fraction = fractions.Fraction(1 - weight).limit_denominator(1000)
            outer_widget = QWidget()
            layout = QHBoxLayout(outer_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addStretch(stretch=fraction.numerator)
            layout.addWidget(w, stretch=fraction.denominator)
            w = outer_widget
        self.vbox.addWidget(w)
        return w

    def factory_combo(self, items: Optional[List[str]], active_id: Optional[int], handler: Callable,
                      hide_masks: List[str] = (), weight: float = 1.0):
        combo = QComboBox()
        for item in items:
            combo.addItem(item)
        if active_id is None:
            combo.setCurrentIndex(-1)
        else:
            combo.setCurrentIndex(active_id)
        combo.currentIndexChanged.connect(handler)
        self.add_widget(combo, weight=weight)

    def factory_radio(self, items: Optional[List[str]], active_id: Optional[int], handler: Callable,
                      hide_masks: List[str] = (), weight: float = 1.0):
        group = QButtonGroup()
        for i, item in enumerate(items):
            button = QRadioButton(item)
            if i == active_id:
                button.setChecked(True)
            group.addButton(button, i)
            widget = self.add_widget(button, weight=weight)
            if any(fnmatch(item, mask) for mask in hide_masks):
                widget.hide()
        group.idClicked.connect(handler)
        self._non_gc_bucket.append(group)

    def factory_by_name(self, name: str):
        if name == "combo":
            return self.factory_combo
        elif name == "radio":
            return self.factory_radio
        else:
            raise ValueError(f"Unknown factory {name!r}")

    def add_cards(self):
        for card in self.pulse.cards:
            logger.debug("add card {}", card)
            self.add_widget(QLabel(card.name))
            factory = self.factory_by_name(self.config.profile_style)
            factory(
                items=[f"{p.name} [{p.sinks_count}:{p.sources_count}]" for p in card.profiles],
                active_id=card.active_profile_id,
                handler=partial(self.profile_changed, card.profiles),
                weight=self.config.profile_weight,
            )

    def profile_changed(self, profiles, index):
        self.pulse.set_profile(profiles[index])
        self.rebuild_signal.emit()

    def add_ends(self):
        for end in self.pulse.ends:
            if not end.ports:
                logger.debug("skip end {}, since no ports", end)
                continue
            logger.debug("add end {}", end)
            section_name = f"{self.SYMBOL_BY_TYPE[end.type]} {end.name}"
            self.add_widget(QLabel(section_name))
            slider = TipSlider(Qt.Orientation.Horizontal)
            factory = self.factory_by_name(self.config.port_style)
            factory(
                items=[f"{p.name}" for p in end.ports],
                active_id=end.active_port_id,
                handler=partial(self.port_changed, end.ports, slider),
                hide_masks=self.config.port_hide_by_mask,
                weight=self.config.port_weight,
            )
            slider.setMinimum(0)
            slider.setMaximum(self.config.port_maximum_volume)
            slider.setSingleStep(1)
            slider.setValue(end.volume * 100)
            slider.valueChanged.connect(partial(self.volume_changed, end))
            self.add_widget(slider)

    def port_changed(self, ports, slider_to_propagate_volume, index):
        port = ports[index]
        self.pulse.set_port(port)
        self.pulse.update()
        end = self.pulse.ends[port.end_id]
        slider_to_propagate_volume.setValue(end.volume * 100)

    def volume_changed(self, end, volume):
        self.pulse.set_volume(end, volume / 100)
