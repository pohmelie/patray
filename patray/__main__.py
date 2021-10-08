import sys

from click import Choice, Path, option, version_option
from cock import build_entrypoint
from loguru import logger
from PySide2.QtWidgets import QApplication

from . import version
from .logging import configure_logging
from .qt import Patray


def main(config):
    configure_logging(config.log_level)
    logger.info("patray: version {}, config {}", version, config)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    _ = Patray(config)
    sys.exit(app.exec_())


style = Choice(["combo", "radio"])
options = [
    option("--profile-enabled", default=True, type=bool),
    option("--profile-style", default="combo", type=style),
    option("--profile-weight", default=1.0, type=float),
    option("--port-enabled", default=True, type=bool),
    option("--port-style", default="radio", type=style),
    option("--port-maximum-volume", default=100, type=int),
    option("--port-hide-by-mask", multiple=True),
    option("--port-weight", default=1.0, type=float),

    option("--log-level", default="INFO"),
    option("--icon-path", default=None, required=False,
           type=Path(exists=True, dir_okay=False, readable=True, resolve_path=True)),
    option("--icon-color", default="#fff", help="Use `random` value for random color on each click"),
    version_option(version, message="%(version)s"),
]
entrypoint = build_entrypoint(main, options, auto_envvar_prefix="PATRAY", show_default=True)
entrypoint(prog_name="patray")
