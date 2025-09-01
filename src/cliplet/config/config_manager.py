"""Professional configuration manager with validation and migration"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from .defaults import DEFAULT_CONFIG, CONFIG_SCHEMA
from .paths import get_config_file, ensure_directories

logger = logging.getLogger(__name__)

class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass

class ConfigManager:
    """Production-ready configuration manager"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize configuration manager
        
        Args:
            config_file: Optional path to config file. Uses default if None.
        """
        self.config_file = config_file or get_config_file()
        self._config = DEFAULT_CONFIG.copy()
        self._loaded = False
        
        # Ensure directories exist
        ensure_directories()
        
        # Load existing configuration
        self.load()
    
    def load(self) -> bool:
        """Load configuration from file
        
        Returns:
            bool: True if loaded successfully, False if using defaults
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Validate and merge configuration
                validated_config = self._validate_config(loaded_config)
                self._config.update(validated_config)
                self._loaded = True
                
                logger.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                logger.info("No configuration file found, using defaults")
                self.save()  # Create default config file
                return False
                
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            return False
        except ConfigValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            logger.info("Using default configuration")
            return False
    
    def save(self) -> bool:
        """Save configuration to file
        
        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write configuration with nice formatting
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, sort_keys=True)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value with validation
        
        Args:
            key: Configuration key
            value: Value to set
            
        Returns:
            bool: True if set successfully
            
        Raises:
            ConfigValidationError: If validation fails
        """
        if key not in CONFIG_SCHEMA:
            logger.warning(f"Unknown configuration key: {key}")
        
        # Validate single value
        validated_value = self._validate_value(key, value)
        self._config[key] = validated_value
        
        logger.debug(f"Configuration updated: {key} = {validated_value}")
        return True
    
    def update(self, config_dict: Dict[str, Any]) -> bool:
        """Update multiple configuration values
        
        Args:
            config_dict: Dictionary of configuration updates
            
        Returns:
            bool: True if all updates successful
        """
        validated_config = self._validate_config(config_dict)
        self._config.update(validated_config)
        
        logger.debug(f"Configuration updated with {len(validated_config)} values")
        return True
    
    def reset(self, key: Optional[str] = None) -> bool:
        """Reset configuration to defaults
        
        Args:
            key: Specific key to reset, or None for all
            
        Returns:
            bool: True if reset successful
        """
        if key:
            if key in DEFAULT_CONFIG:
                self._config[key] = DEFAULT_CONFIG[key]
                logger.info(f"Configuration key '{key}' reset to default")
            else:
                logger.warning(f"Unknown configuration key: {key}")
                return False
        else:
            self._config = DEFAULT_CONFIG.copy()
            logger.info("All configuration reset to defaults")
        
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values
        
        Returns:
            dict: Complete configuration
        """
        return self._config.copy()
    
    def is_loaded(self) -> bool:
        """Check if configuration was loaded from file
        
        Returns:
            bool: True if loaded from file, False if using defaults
        """
        return self._loaded
    
    def validate(self) -> bool:
        """Validate current configuration
        
        Returns:
            bool: True if valid
            
        Raises:
            ConfigValidationError: If validation fails
        """
        try:
            self._validate_config(self._config)
            return True
        except ConfigValidationError:
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration dictionary
        
        Args:
            config: Configuration to validate
            
        Returns:
            dict: Validated configuration
            
        Raises:
            ConfigValidationError: If validation fails
        """
        validated = {}
        
        for key, value in config.items():
            if key in CONFIG_SCHEMA:
                validated[key] = self._validate_value(key, value)
            else:
                logger.warning(f"Ignoring unknown configuration key: {key}")
        
        return validated
    
    def _validate_value(self, key: str, value: Any) -> Any:
        """Validate single configuration value
        
        Args:
            key: Configuration key
            value: Value to validate
            
        Returns:
            Validated value
            
        Raises:
            ConfigValidationError: If validation fails
        """
        if key not in CONFIG_SCHEMA:
            return value  # Allow unknown keys for forward compatibility
        
        schema = CONFIG_SCHEMA[key]
        expected_type = schema['type']
        
        # Type validation
        if not isinstance(value, expected_type):
            try:
                # Try to convert to expected type
                if expected_type == int:
                    value = int(value)
                elif expected_type == float:
                    value = float(value)
                elif expected_type == bool:
                    value = bool(value)
                elif expected_type == str:
                    value = str(value)
                elif expected_type == list:
                    if not isinstance(value, list):
                        raise ValueError("Cannot convert to list")
                else:
                    raise ValueError(f"Cannot convert to {expected_type}")
            except (ValueError, TypeError):
                raise ConfigValidationError(
                    f"Invalid type for {key}: expected {expected_type.__name__}, got {type(value).__name__}"
                )
        
        # Range validation for numbers
        if expected_type in (int, float):
            if 'min' in schema and value < schema['min']:
                raise ConfigValidationError(f"{key} value {value} is below minimum {schema['min']}")
            if 'max' in schema and value > schema['max']:
                raise ConfigValidationError(f"{key} value {value} is above maximum {schema['max']}")
        
        # Choice validation
        if 'choices' in schema and value not in schema['choices']:
            raise ConfigValidationError(f"{key} value '{value}' not in allowed choices: {schema['choices']}")
        
        # Pattern validation for strings
        if expected_type == str and 'pattern' in schema:
            import re
            if not re.match(schema['pattern'], value):
                raise ConfigValidationError(f"{key} value '{value}' does not match required pattern")
        
        return value
    
    def get_schema(self, key: Optional[str] = None) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """Get configuration schema
        
        Args:
            key: Specific key schema, or None for all
            
        Returns:
            Schema dictionary
        """
        if key:
            return CONFIG_SCHEMA.get(key, {})
        return CONFIG_SCHEMA.copy()
    
    def export_config(self, file_path: Path) -> bool:
        """Export configuration to a file
        
        Args:
            file_path: Path to export file
            
        Returns:
            bool: True if exported successfully
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, sort_keys=True)
            logger.info(f"Configuration exported to {file_path}")
            return True
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, file_path: Path) -> bool:
        """Import configuration from a file
        
        Args:
            file_path: Path to import file
            
        Returns:
            bool: True if imported successfully
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            validated_config = self._validate_config(imported_config)
            self._config.update(validated_config)
            
            logger.info(f"Configuration imported from {file_path}")
            return True
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
        except ConfigValidationError as e:
            logger.error(f"Configuration validation failed during import: {e}")
            return False
    
    def clear_history(self) -> bool:
        """Clear clipboard history
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            from .paths import get_data_dir
            
            # Get data directory and history file
            data_dir = get_data_dir()
            history_file = data_dir / 'history.json'
            
            # Remove history file if it exists
            if history_file.exists():
                history_file.unlink()
                logger.info("Clipboard history cleared")
            else:
                logger.info("No history file found to clear")
            
            return True
            
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to clear history: {e}")
            return False