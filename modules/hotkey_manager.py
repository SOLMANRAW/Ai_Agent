import threading
import logging
from typing import Callable
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

logger = logging.getLogger(__name__)


class HotkeyManager:
    def __init__(self, config, activation_callback: Callable):
        self.config = config
        self.activation_callback = activation_callback
        self.listener = None
        self.is_active = False
        self.pressed_keys = set()
        self.hotkey_combination = set(self.config.HOTKEY_COMBINATION)

    def start(self):
        # Start listening for hotkeys
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            logger.info(
                f"Hotkey listener started. Press {'+'.join(self.hotkey_combination)} to activate"
            )
        except Exception as e:
            logger.error(f"Error starting hotkey listener: {e}")

    def stop(self):
        # Stop listening for hotkeys
        if self.listener:
            self.listener.stop()
            self.listener = None
            logger.info("Hotkey listener stopped")

    def _on_press(self, key):
        # Handle key press events
        try:
            # Convert key to string representation
            key_str = self._key_to_string(key)
            if key_str:
                self.pressed_keys.add(key_str)
                # Check if hotkey combination is pressed
                if self.pressed_keys == self.hotkey_combination:
                    if not self.is_active:
                        self.is_active = True
                        logger.info("Hotkey activated!")
                        self._trigger_activation()
        except Exception as e:
            logger.error(f"Error in key press handler: {e}")

    def _on_release(self, key):
        # Handle key release events
        try:
            key_str = self._key_to_string(key)
            if key_str in self.pressed_keys:
                self.pressed_keys.remove(key_str)
                # Reset activation state when any key is released
                if self.is_active:
                    self.is_active = False
        except Exception as e:
            logger.error(f"Error in key release handler: {e}")

    def _key_to_string(self, key):
        # Convert pynput key to string representation
        if isinstance(key, Key):
            return key.name
        elif isinstance(key, KeyCode):
            return key.char
        return None

    def _trigger_activation(self):
        # Trigger the activation callback
        try:
            # Run callback in a separate thread to avoid blocking
            threading.Thread(target=self.activation_callback, daemon=True).start()
        except Exception as e:
            logger.error(f"Error triggering activation callback: {e}")

    def set_hotkey_combination(self, combination: list):
        # Set a new hotkey combination
        self.hotkey_combination = set(combination)
        logger.info(f"Hotkey combination changed to: {'+'.join(combination)}")

    def get_current_combination(self) -> str:
        # Get current hotkey combination as string
        return '+'.join(self.hotkey_combination)

    def is_listening(self) -> bool:
        # Check if hotkey listener is active
        return self.listener is not None and self.listener.is_alive()



