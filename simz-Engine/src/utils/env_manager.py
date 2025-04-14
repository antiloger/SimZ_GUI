import os
from typing import Dict, Any, Optional


class EnvManager:
    """
    EnvManager loads and manages environment variables for the SimZ Engine.
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        'HOST': '0.0.0.0',
        'PORT': 5000,
        'PROJECT_DIR': './projects',
        'DEBUG': False,
        'CORS_ALLOWED_ORIGINS': '*'
    }
    
    def __init__(self):
        """Initialize the environment manager with values from environment variables."""
        self.config = self._load_from_env()
    
    def _load_from_env(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Returns:
            Dictionary containing configuration values
        """
        config = self.DEFAULT_CONFIG.copy()
        
        # Load from environment with SIMZ_ prefix
        for key in config:
            env_key = f"SIMZ_{key}"
            if env_key in os.environ:
                # Convert specific values to the correct type
                if key == 'PORT':
                    config[key] = int(os.environ[env_key])
                elif key == 'DEBUG':
                    config[key] = os.environ[env_key].lower() in ('true', 'yes', '1')
                else:
                    config[key] = os.environ[env_key]
        
        return config
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if the key is not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary containing all configuration values
        """
        return self.config.copy()
    
    def print_config(self) -> None:
        """Print the current configuration values."""
        print("Current Configuration:")
        for key, value in self.config.items():
            print(f"  {key}: {value}")


# Create a singleton instance
env_manager = EnvManager() 