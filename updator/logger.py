import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
import os
logger = logging.getLogger("msys2-updator")
ci = os.getenv("CI",None)
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
if ci:
    console=Console(theme=custom_theme, force_terminal=True, color_system="truecolor")
else:
    console=Console(theme=custom_theme)
logger.addHandler(
    RichHandler(
        show_time=False,
        show_path=False,
        console=console,
        rich_tracebacks=True
    )
)
