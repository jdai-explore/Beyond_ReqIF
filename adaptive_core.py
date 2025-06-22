#!/usr/bin/env python3
"""
Adaptive Core - Smart Theme Adaptation Engine
Handles system preference detection, automatic mode switching, and smooth transitions.
"""

import tkinter as tk
import platform
import subprocess
import threading
import time
from typing import Optional, Callable, Dict, Any
from enum import Enum


class AdaptiveMode(Enum):
    """Theme adaptation modes"""
    AUTO = "auto"          # Follow system preferences
    LIGHT = "light"        # Force light mode
    DARK = "dark"          # Force dark mode


class SystemThemeDetector:
    """
    Detects system theme preferences across different operating systems
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self._cached_preference = None
        self._cache_time = 0
        self._cache_duration = 5  # Cache for 5 seconds to avoid excessive system calls
    
    def get_system_preference(self) -> str:
        """
        Get system dark mode preference
        
        Returns:
            'dark' if system is in dark mode, 'light' otherwise
        """
        current_time = time.time()
        
        # Use cached result if still valid
        if (self._cached_preference and 
            current_time - self._cache_time < self._cache_duration):
            return self._cached_preference
        
        try:
            if self.platform == "darwin":  # macOS
                preference = self._detect_macos_theme()
            elif self.platform == "windows":  # Windows
                preference = self._detect_windows_theme()
            elif self.platform == "linux":  # Linux
                preference = self._detect_linux_theme()
            else:
                preference = "light"  # Default fallback
                
            # Cache the result
            self._cached_preference = preference
            self._cache_time = current_time
            
            return preference
            
        except Exception:
            # Fallback to light mode if detection fails
            return "light"
    
    def _detect_macos_theme(self) -> str:
        """Detect macOS system theme"""
        try:
            # Check macOS dark mode setting
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # If the command succeeds and returns "Dark", system is in dark mode
            if result.returncode == 0 and "Dark" in result.stdout:
                return "dark"
            else:
                return "light"
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return "light"
    
    def _detect_windows_theme(self) -> str:
        """Detect Windows system theme"""
        try:
            import winreg
            
            # Check Windows registry for dark mode setting
            registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                # AppsUseLightTheme: 0 = dark mode, 1 = light mode
                apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "light" if apps_use_light_theme else "dark"
                
        except (ImportError, OSError, FileNotFoundError):
            # Fallback: Try alternative detection methods
            try:
                # Alternative: Check for dark mode via PowerShell
                result = subprocess.run([
                    "powershell", "-Command",
                    "Get-ItemProperty -Path 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name 'AppsUseLightTheme'"
                ], capture_output=True, text=True, timeout=3)
                
                if "AppsUseLightTheme" in result.stdout and "0" in result.stdout:
                    return "dark"
                    
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                pass
                
            return "light"
    
    def _detect_linux_theme(self) -> str:
        """Detect Linux desktop environment theme"""
        try:
            # Try GNOME settings first
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                theme_name = result.stdout.strip().lower()
                # Common dark theme indicators
                dark_indicators = ["dark", "adwaita-dark", "breeze-dark", "arc-dark", "numix-dark"]
                if any(indicator in theme_name for indicator in dark_indicators):
                    return "dark"
                return "light"
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        try:
            # Try KDE settings
            result = subprocess.run(
                ["kreadconfig5", "--group", "General", "--key", "ColorScheme"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                color_scheme = result.stdout.strip().lower()
                if "dark" in color_scheme or "breezedark" in color_scheme:
                    return "dark"
                return "light"
                
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Fallback to light mode
        return "light"
    
    def is_dark_mode_supported(self) -> bool:
        """Check if the current system supports dark mode detection"""
        try:
            # Try to detect current theme - if it works, detection is supported
            self.get_system_preference()
            return True
        except Exception:
            return False


class AdaptiveCore:
    """
    Core adaptive theme management system
    Handles automatic theme switching and smooth transitions
    """
    
    def __init__(self):
        self.detector = SystemThemeDetector()
        self.mode = AdaptiveMode.AUTO
        self._manual_override = None
        self._monitoring_thread = None
        self._monitoring_active = False
        self._callbacks = []
        self._current_system_preference = None
        
        # Transition settings
        self.transition_duration = 0.3  # seconds
        self.transition_steps = 10
        
        # Initialize with current system preference
        self._update_system_preference()
    
    def set_mode(self, mode: AdaptiveMode, manual_preference: str = None):
        """
        Set the adaptive mode
        
        Args:
            mode: AdaptiveMode enum value
            manual_preference: 'light' or 'dark' for manual modes
        """
        self.mode = mode
        
        if mode in [AdaptiveMode.LIGHT, AdaptiveMode.DARK]:
            self._manual_override = mode.value
        else:
            self._manual_override = None
        
        # Notify listeners of mode change
        self._notify_theme_change()
    
    def get_current_theme(self) -> str:
        """
        Get the current theme that should be applied
        
        Returns:
            'light' or 'dark'
        """
        if self.mode == AdaptiveMode.AUTO:
            return self._current_system_preference or "light"
        elif self.mode == AdaptiveMode.LIGHT:
            return "light"
        elif self.mode == AdaptiveMode.DARK:
            return "dark"
        else:
            return "light"  # Fallback
    
    def get_mode_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about current adaptive mode
        
        Returns:
            Dictionary with mode information
        """
        return {
            "mode": self.mode.value,
            "current_theme": self.get_current_theme(),
            "system_preference": self._current_system_preference,
            "manual_override": self._manual_override,
            "is_auto": self.mode == AdaptiveMode.AUTO,
            "dark_mode_supported": self.detector.is_dark_mode_supported(),
            "monitoring_active": self._monitoring_active
        }
    
    def start_monitoring(self):
        """Start monitoring system theme changes (for AUTO mode)"""
        if self._monitoring_active:
            return
            
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitor_system_changes,
            daemon=True
        )
        self._monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring system theme changes"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1)
    
    def add_change_callback(self, callback: Callable[[str], None]):
        """
        Add callback to be notified of theme changes
        
        Args:
            callback: Function that takes theme name ('light'/'dark') as parameter
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[str], None]):
        """Remove theme change callback"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _monitor_system_changes(self):
        """Background thread to monitor system theme changes"""
        while self._monitoring_active:
            try:
                # Check for system preference changes
                if self.mode == AdaptiveMode.AUTO:
                    old_preference = self._current_system_preference
                    self._update_system_preference()
                    
                    # If preference changed, notify listeners
                    if (old_preference != self._current_system_preference and 
                        old_preference is not None):
                        self._notify_theme_change()
                
                # Check every 2 seconds
                time.sleep(2)
                
            except Exception:
                # Continue monitoring even if an error occurs
                time.sleep(5)
    
    def _update_system_preference(self):
        """Update the cached system preference"""
        self._current_system_preference = self.detector.get_system_preference()
    
    def _notify_theme_change(self):
        """Notify all callbacks of theme change"""
        current_theme = self.get_current_theme()
        
        for callback in self._callbacks[:]:  # Copy list to avoid modification during iteration
            try:
                callback(current_theme)
            except Exception:
                # Remove callbacks that cause errors
                self.remove_change_callback(callback)
    
    def create_smooth_transition(self, widget: tk.Widget, 
                                start_color: str, end_color: str,
                                property_name: str = "bg") -> threading.Thread:
        """
        Create a smooth color transition for a widget
        
        Args:
            widget: Tkinter widget to animate
            start_color: Starting color (hex)
            end_color: Ending color (hex)
            property_name: Widget property to animate ('bg', 'fg', etc.)
            
        Returns:
            Thread object for the animation (already started)
        """
        def animate():
            try:
                # Parse colors
                start_rgb = self._hex_to_rgb(start_color)
                end_rgb = self._hex_to_rgb(end_color)
                
                # Calculate step size for each color component
                steps = self.transition_steps
                step_delay = self.transition_duration / steps
                
                for step in range(steps + 1):
                    # Calculate intermediate color
                    progress = step / steps
                    current_rgb = tuple(
                        int(start + (end - start) * progress)
                        for start, end in zip(start_rgb, end_rgb)
                    )
                    current_color = self._rgb_to_hex(current_rgb)
                    
                    # Update widget (must be done on main thread)
                    def update_widget():
                        try:
                            widget.configure(**{property_name: current_color})
                        except (tk.TclError, AttributeError):
                            pass  # Widget might be destroyed during animation
                    
                    widget.after_idle(update_widget)
                    
                    # Wait for next step (except on last step)
                    if step < steps:
                        time.sleep(step_delay)
                        
            except Exception:
                # If animation fails, just set final color
                try:
                    widget.configure(**{property_name: end_color})
                except (tk.TclError, AttributeError):
                    pass
        
        # Start animation in background thread
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
        return animation_thread
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB tuple to hex color"""
        return "#{:02x}{:02x}{:02x}".format(*rgb)


class TransitionManager:
    """
    Manages smooth transitions between themes
    """
    
    def __init__(self, adaptive_core: AdaptiveCore):
        self.adaptive_core = adaptive_core
        self._active_transitions = []
    
    def transition_widget(self, widget: tk.Widget, 
                         old_theme_colors: dict, new_theme_colors: dict):
        """
        Smoothly transition a widget from old theme to new theme
        
        Args:
            widget: Widget to transition
            old_theme_colors: Dictionary of old theme colors
            new_theme_colors: Dictionary of new theme colors
        """
        try:
            # Common properties to animate
            properties_to_animate = ['bg', 'fg', 'activebackground', 'activeforeground']
            
            for prop in properties_to_animate:
                # Get widget's current color for this property
                try:
                    current_color = widget.cget(prop)
                    if current_color and current_color in old_theme_colors.values():
                        # Find corresponding new color
                        new_color = self._find_corresponding_color(
                            current_color, old_theme_colors, new_theme_colors
                        )
                        
                        if new_color and new_color != current_color:
                            # Start smooth transition
                            transition = self.adaptive_core.create_smooth_transition(
                                widget, current_color, new_color, prop
                            )
                            self._active_transitions.append(transition)
                            
                except (tk.TclError, AttributeError):
                    # Widget doesn't support this property
                    continue
                    
        except Exception:
            # If transition fails, apply new theme directly
            self._apply_theme_directly(widget, new_theme_colors)
    
    def _find_corresponding_color(self, current_color: str, 
                                 old_colors: dict, new_colors: dict) -> str:
        """Find the corresponding color in the new theme"""
        # Find which token the current color corresponds to
        for token, color in old_colors.items():
            if color == current_color:
                return new_colors.get(token, current_color)
        return current_color
    
    def _apply_theme_directly(self, widget: tk.Widget, theme_colors: dict):
        """Apply theme colors directly without transition"""
        try:
            # Apply common theme properties
            if 'bg_primary' in theme_colors:
                widget.configure(bg=theme_colors['bg_primary'])
            if 'text_primary' in theme_colors:
                widget.configure(fg=theme_colors['text_primary'])
        except (tk.TclError, AttributeError):
            pass
    
    def cleanup_finished_transitions(self):
        """Remove completed transition threads"""
        self._active_transitions = [
            t for t in self._active_transitions 
            if t.is_alive()
        ]


# Global instances for easy access
adaptive_core = AdaptiveCore()
transition_manager = TransitionManager(adaptive_core)


# Convenience functions
def get_current_theme() -> str:
    """Get the currently active theme"""
    return adaptive_core.get_current_theme()


def set_adaptive_mode(mode: str, manual_preference: str = None):
    """
    Set the adaptive mode
    
    Args:
        mode: 'auto', 'light', or 'dark'
        manual_preference: For manual modes, the specific preference
    """
    if mode == "auto":
        adaptive_core.set_mode(AdaptiveMode.AUTO)
    elif mode == "light":
        adaptive_core.set_mode(AdaptiveMode.LIGHT, "light")
    elif mode == "dark":
        adaptive_core.set_mode(AdaptiveMode.DARK, "dark")


def start_system_monitoring():
    """Start monitoring system theme changes"""
    adaptive_core.start_monitoring()


def stop_system_monitoring():
    """Stop monitoring system theme changes"""
    adaptive_core.stop_monitoring()


def add_theme_change_listener(callback: Callable[[str], None]):
    """Add callback for theme changes"""
    adaptive_core.add_change_callback(callback)


def remove_theme_change_listener(callback: Callable[[str], None]):
    """Remove theme change callback"""
    adaptive_core.remove_change_callback(callback)


def get_adaptive_info() -> Dict[str, Any]:
    """Get information about current adaptive state"""
    return adaptive_core.get_mode_info()


def is_dark_mode_supported() -> bool:
    """Check if system dark mode detection is supported"""
    return adaptive_core.detector.is_dark_mode_supported()


def transition_widget_smoothly(widget: tk.Widget, old_colors: dict, new_colors: dict):
    """Create smooth transition for a widget"""
    transition_manager.transition_widget(widget, old_colors, new_colors)


# Example usage and testing
if __name__ == "__main__":
    print("🔄 Adaptive Core - Smart Theme Adaptation Engine")
    print("=" * 50)
    
    # Test system detection
    detector = SystemThemeDetector()
    current_system = detector.get_system_preference()
    is_supported = detector.is_dark_mode_supported()
    
    print(f"Platform: {platform.system()}")
    print(f"Dark mode detection supported: {is_supported}")
    print(f"Current system preference: {current_system}")
    
    # Test adaptive core
    print(f"\nAdaptive Core Status:")
    info = get_adaptive_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test mode switching
    print(f"\nTesting mode switching:")
    
    original_theme = get_current_theme()
    print(f"  Original theme: {original_theme}")
    
    # Switch to light mode
    set_adaptive_mode("light")
    print(f"  After setting light mode: {get_current_theme()}")
    
    # Switch to dark mode
    set_adaptive_mode("dark")
    print(f"  After setting dark mode: {get_current_theme()}")
    
    # Switch back to auto
    set_adaptive_mode("auto")
    print(f"  After setting auto mode: {get_current_theme()}")
    
    print("\n✅ Adaptive core system ready for integration!")
    
    # Note: In real usage, start_system_monitoring() would be called
    # to begin monitoring system theme changes