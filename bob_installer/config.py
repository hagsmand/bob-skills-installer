"""Configuration management for Bob Skills."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional


class ConfigManager:
    """Manages Bob skills configuration."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.bob_dir = self.base_path / ".bob"
        self.config_file = self.bob_dir / "config.yaml"
        self.skills_dir = self.bob_dir / "skills"
        self.rules_dir = self.bob_dir / "rules"
        
    def is_initialized(self) -> bool:
        """Check if Bob skills are initialized."""
        return self.config_file.exists()
    
    def initialize(self):
        """Initialize Bob skills directory structure."""
        self.bob_dir.mkdir(exist_ok=True)
        self.skills_dir.mkdir(exist_ok=True)
        self.rules_dir.mkdir(exist_ok=True)
        
        if not self.config_file.exists():
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file."""
        config = {
            'version': '1.0.0',
            'skill_source': 'https://github.com/anthropics/skills',
            'installed_skills': [],
            'auto_update': False
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def load_config(self) -> Dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def save_config(self, config: Dict):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def add_installed_skill(self, skill_name: str, skill_info: Dict):
        """Add a skill to installed skills list."""
        config = self.load_config()
        
        if 'installed_skills' not in config:
            config['installed_skills'] = []
        
        # Remove if already exists
        config['installed_skills'] = [
            s for s in config['installed_skills']
            if s.get('name') != skill_name
        ]
        
        # Add new entry
        skill_entry = {
            'name': skill_name,
            'category': skill_info.get('category', 'unknown'),
            'description': skill_info.get('description', ''),
            'license': skill_info.get('license', 'unknown')
        }
        
        # Add custom flag if present
        if skill_info.get('custom'):
            skill_entry['custom'] = True
        
        config['installed_skills'].append(skill_entry)
        
        self.save_config(config)
    
    def remove_installed_skill(self, skill_name: str):
        """Remove a skill from installed skills list."""
        config = self.load_config()
        
        if 'installed_skills' in config:
            config['installed_skills'] = [
                s for s in config['installed_skills'] 
                if s.get('name') != skill_name
            ]
            
            self.save_config(config)
    
    def get_installed_skills(self) -> List[Dict]:
        """Get list of installed skills."""
        config = self.load_config()
        return config.get('installed_skills', [])
    
    def is_skill_installed(self, skill_name: str) -> bool:
        """Check if a skill is installed."""
        installed = self.get_installed_skills()
        return any(s.get('name') == skill_name for s in installed)