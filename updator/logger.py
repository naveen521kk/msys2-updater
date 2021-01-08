import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
import os
logger = logging.getLogger("msys2-updator")

custom_theme = Theme(
    {
        "log.level": "magenta",
        "repr.number": "bold green blink",
        "log.message": "white on red",
        "logging.level.info": "green on white",
        "log.time":"green dim",
        "logging.level.notset":"red on white"
    },
)

console=Console(theme=custom_theme, force_terminal=True, color_system="truecolor", legacy_windows=False, width=120)

logger.addHandler(
    RichHandler(
        show_time=False,
        show_path=False,
        console=console,
        rich_tracebacks=True
    )
)
