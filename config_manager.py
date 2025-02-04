import json
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_file = Path.home() / '.password_analyzer_config.json'
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file or create default if not exists."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self.get_default_config()
        return self.get_default_config()

    def get_default_config(self):
        """Return default configuration."""
        return {
            'last_export_path': str(Path.home()),
            'selected_columns': [],
            'export_format': 'csv',
            'last_used_filters': {
                'domain': '',
                'email': ''
            }
        }

    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def update_last_export_path(self, path):
        """Update the last used export path."""
        self.config['last_export_path'] = str(path)
        self.save_config()

    def update_selected_columns(self, columns):
        """Update the list of selected columns."""
        self.config['selected_columns'] = columns
        self.save_config()

    def update_export_format(self, format_):
        """Update the preferred export format."""
        self.config['export_format'] = format_
        self.save_config()

    def update_last_filters(self, domain='', email=''):
        """Update the last used filters."""
        self.config['last_used_filters']['domain'] = domain
        self.config['last_used_filters']['email'] = email
        self.save_config()

    def get_last_export_path(self):
        """Get the last used export path."""
        return self.config['last_export_path']

    def get_selected_columns(self):
        """Get the list of selected columns."""
        return self.config['selected_columns']

    def get_export_format(self):
        """Get the preferred export format."""
        return self.config['export_format']

    def get_last_filters(self):
        """Get the last used filters."""
        return self.config['last_used_filters'] 