from rich import print
from rich.table import Table
from rich import box
from rich.panel import Panel
from circle import circle


style = circle((
    "bold white on blue",
    "bold white on red"
))
grid = Table.grid()
for i in range(8):
    grid.add_column()
for i in range(8):
    style = style.next()
    panels = []
    for i in range(8):
        panels.append(Panel('0', style=next(style)))
    grid.add_row(*panels)

print(Panel.fit(grid))
