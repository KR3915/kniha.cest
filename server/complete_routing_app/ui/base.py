import tkinter as tk
import customtkinter as ctk
from typing import Any, Callable, Optional

# Modern color scheme
COLORS = {
    'primary': '#2196F3',      # Blue
    'secondary': '#FFC107',    # Amber
    'success': '#4CAF50',      # Green
    'danger': '#F44336',       # Red
    'warning': '#FF9800',      # Orange
    'info': '#00BCD4',         # Cyan
    'light': '#F5F5F5',       # Light Gray
    'dark': '#212121',        # Dark Gray
    'white': '#FFFFFF',       # White
    'black': '#000000'        # Black
}

# Font configurations
FONTS = {
    'heading': ('Segoe UI', 24, 'bold'),
    'subheading': ('Segoe UI', 18),
    'default': ('Segoe UI', 12),
    'small': ('Segoe UI', 10)
}

class BaseFrame(ctk.CTkFrame):
    """Base frame with common styling."""
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=COLORS['white'],
            corner_radius=10,
            border_width=1,
            border_color=COLORS['light']
        )

class StyledButton(ctk.CTkButton):
    """Button with consistent styling."""
    def __init__(
        self,
        master: Any,
        text: str,
        command: Callable,
        color: str = 'primary',
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=COLORS[color],
            hover_color=self._adjust_color(COLORS[color], -20),
            text_color=COLORS['white'],
            font=FONTS['default'],
            corner_radius=6,
            height=36,
            **kwargs
        )
        
    def _adjust_color(self, hex_color: str, factor: int) -> str:
        """Adjust color brightness."""
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Adjust values
        r = max(0, min(255, r + factor))
        g = max(0, min(255, g + factor))
        b = max(0, min(255, b + factor))
        
        return f'#{r:02x}{g:02x}{b:02x}'

class StyledEntry(ctk.CTkEntry):
    """Entry field with consistent styling."""
    def __init__(self, master: Any, placeholder: str = "", **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            fg_color=COLORS['white'],
            border_color=COLORS['light'],
            text_color=COLORS['dark'],
            placeholder_text_color=COLORS['dark'],
            font=FONTS['default'],
            height=36,
            corner_radius=6,
            **kwargs
        )

class StyledLabel(ctk.CTkLabel):
    """Label with consistent styling."""
    def __init__(
        self,
        master: Any,
        text: str,
        font_style: str = 'default',
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            font=FONTS[font_style],
            text_color=COLORS['dark'],
            **kwargs
        )

class ScrollableFrame(ctk.CTkScrollableFrame):
    """Scrollable frame with consistent styling."""
    def __init__(self, master: Any, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS['white'],
            corner_radius=10,
            border_width=1,
            border_color=COLORS['light'],
            scrollbar_button_color=COLORS['primary'],
            scrollbar_button_hover_color=COLORS['info'],
            **kwargs
        )

class MessageBox(ctk.CTkToplevel):
    """Styled message box for notifications and confirmations."""
    def __init__(
        self,
        title: str,
        message: str,
        type_: str = 'info',
        parent: Optional[Any] = None
    ):
        super().__init__(parent)
        
        # Window setup
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center on parent/screen
        if parent:
            x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
            y = parent.winfo_y() + (parent.winfo_height() - 200) // 2
            self.geometry(f"+{x}+{y}")
        
        # Content
        content = BaseFrame(self)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        StyledLabel(
            content,
            text=message,
            font_style='default',
            wraplength=360
        ).pack(pady=(20, 30))
        
        StyledButton(
            content,
            text="OK",
            command=self.destroy,
            color=type_
        ).pack() 