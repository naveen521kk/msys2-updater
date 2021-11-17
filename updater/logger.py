import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
import os
logger = logging.getLogger("msys2-updator")

custom_theme = Theme(
    {
        "log.level": "magenta",
        "repr.number": "red",
        "log.message": "cyan",
        "logging.level.info": "green on black",
        "log.time":"green",
        "logging.level.notset":"red on black"
    },
)

console=Console(theme=custom_theme, force_terminal=True, color_system="truecolor", legacy_windows=False, width=120)

logger.addHandler(
    RichHandler(
        show_time=True,
        show_path=False,
        console=console,
        rich_tracebacks=True
    )
)
logger.info(console.options)
