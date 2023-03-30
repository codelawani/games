try:
    import pygame
except ImportError:
    print("pygame not installed, install using 'pip install pygame'")
    exit(1)

try:
    import rich
except ImportError:
    print("rich not installed, install using 'pip' install rich'")
    exit(1)

from . import Ludo
