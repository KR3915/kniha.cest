import tkinter as tk
import customtkinter as ctk
from typing import Any, Callable, Dict
from .base import (
    BaseFrame,
    StyledButton,
    StyledEntry,
    StyledLabel,
    MessageBox,
    COLORS,
    FONTS
)
from database import db

class LoginFrame(BaseFrame):
    """Login interface."""
    def __init__(self, master: Any, on_login: Callable[[str, int, bool], None]):
        super().__init__(master)
        self.on_login = on_login
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create login widgets."""
        # Center content
        content = BaseFrame(self)
        content.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        StyledLabel(
            content,
            text="Route Planner",
            font_style="heading"
        ).pack(pady=(0, 30))
        
        # Login form
        form = BaseFrame(content)
        form.pack(padx=40, pady=20)
        
        # Username field
        username_container = BaseFrame(form)
        username_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            username_container,
            text="Username",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.username_entry = StyledEntry(
            username_container,
            placeholder="Enter username",
            width=300
        )
        self.username_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Password field
        password_container = BaseFrame(form)
        password_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            password_container,
            text="Password",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.password_entry = StyledEntry(
            password_container,
            placeholder="Enter password",
            show="•",
            width=300
        )
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Login button
        StyledButton(
            form,
            text="Login",
            command=self._handle_login,
            width=300
        ).pack(pady=20)
        
        # Register link
        register_container = BaseFrame(form)
        register_container.pack(fill=tk.X)
        
        StyledLabel(
            register_container,
            text="Don't have an account? ",
            font_style="small"
        ).pack(side=tk.LEFT)
        
        register_link = StyledLabel(
            register_container,
            text="Register",
            font_style="small",
            text_color=COLORS['primary']
        )
        register_link.pack(side=tk.LEFT)
        register_link.bind("<Button-1>", lambda e: self._show_register())
        
    def _handle_login(self):
        """Handle login attempt."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            MessageBox(
                "Error",
                "Please enter both username and password",
                type_="warning",
                parent=self
            )
            return
            
        # Check credentials
        user = db.check_credentials(username, password)
        if user:
            self.on_login(
                user['username'],
                user['id'],
                user['is_admin']
            )
        else:
            MessageBox(
                "Error",
                "Invalid username or password",
                type_="danger",
                parent=self
            )
            
    def _show_register(self):
        """Show registration form."""
        RegisterForm(self, self._handle_registration)
        
    def _handle_registration(self, username: str, password: str):
        """Handle successful registration."""
        if db.add_user(username, password):
            MessageBox(
                "Success",
                "Registration successful! You can now login.",
                type_="success",
                parent=self
            )
        else:
            MessageBox(
                "Error",
                "Username already exists",
                type_="danger",
                parent=self
            )

class RegisterForm(ctk.CTkToplevel):
    """Registration form."""
    def __init__(
        self,
        master: Any,
        on_register: Callable[[str, str], None]
    ):
        super().__init__(master)
        self.on_register = on_register
        
        # Window setup
        self.title("Register")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Center on parent
        x = master.winfo_x() + (master.winfo_width() - 400) // 2
        y = master.winfo_y() + (master.winfo_height() - 500) // 2
        self.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create registration form widgets."""
        # Main container
        container = BaseFrame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        StyledLabel(
            container,
            text="Create Account",
            font_style="heading"
        ).pack(pady=(0, 30))
        
        # Form
        form = BaseFrame(container)
        form.pack(padx=20)
        
        # Username field
        username_container = BaseFrame(form)
        username_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            username_container,
            text="Username",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.username_entry = StyledEntry(
            username_container,
            placeholder="Choose a username",
            width=300
        )
        self.username_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Password field
        password_container = BaseFrame(form)
        password_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            password_container,
            text="Password",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.password_entry = StyledEntry(
            password_container,
            placeholder="Choose a password",
            show="•",
            width=300
        )
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Confirm password field
        confirm_container = BaseFrame(form)
        confirm_container.pack(fill=tk.X, pady=5)
        
        StyledLabel(
            confirm_container,
            text="Confirm Password",
            font_style="default"
        ).pack(anchor=tk.W)
        
        self.confirm_entry = StyledEntry(
            confirm_container,
            placeholder="Confirm your password",
            show="•",
            width=300
        )
        self.confirm_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_container = BaseFrame(form)
        button_container.pack(fill=tk.X, pady=20)
        
        StyledButton(
            button_container,
            text="Cancel",
            command=self.destroy,
            color="secondary",
            width=145
        ).pack(side=tk.LEFT)
        
        StyledButton(
            button_container,
            text="Register",
            command=self._handle_register,
            width=145
        ).pack(side=tk.RIGHT)
        
    def _handle_register(self):
        """Handle registration attempt."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        
        if not all([username, password, confirm]):
            MessageBox(
                "Error",
                "Please fill in all fields",
                type_="warning",
                parent=self
            )
            return
            
        if password != confirm:
            MessageBox(
                "Error",
                "Passwords do not match",
                type_="warning",
                parent=self
            )
            return
            
        self.destroy()
        self.on_register(username, password) 