"""SAMTTS

A Python port of Software Automatic Mouth Test-To-Speech program.

- Ported by: Quan Lin
- License: None
"""

from .reciter import Reciter
from .processor import Processor
from .renderer import Renderer
from .samtts import SamTTS

__all__ = [
    "Reciter",
    "Processor",
    "Renderer",
    "SamTTS",
]

# Project version
__version__ = "0.2.0"
