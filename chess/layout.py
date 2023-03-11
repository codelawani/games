from rich.layout import Layout
from rich.layout import Column, Row
from rich.console import Console

console = Console()

layout = Layout()

# Define header
header = Row(
    Column(
        justify="center",
        style="cyan",
        padding=(1, 2),
        renderable="Header",
    )
)
layout.split(header)

# Define main section
main_section = Column(
    Row(
        Column(
            justify="center",
            style="blue",
            padding=(1, 2),
            renderable="Left Column",
        ),
        Column(
            justify="center",
            style="magenta",
            padding=(1, 2),
            renderable="Right Column",
        ),
    ),
    style="green",
    padding=1,
)
layout.split(main_section)

# Define footer
footer = Row(
    Column(
        justify="center",
        style="yellow",
        padding=(1, 2),
        renderable="Footer",
    )
)
layout.split(footer)

console.print(layout)

