#!/usr/bin/env python3
"""
Comparison Profile Data Model
Manages user-defined comparison settings including attribute selection and weights.
Phase 1: Advanced Comparison Feature
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AttributeConfig:
    """Configuration for a single attribute in comparison"""
    name: str
    display_name: str
    enabled: bool = True
    weight: float = 1.0
    field_type: str = "standard"  # "standard", "attribute", "custom"
    data_type: str = "text"  # "text", "number", "date", "boolean"
    coverage: float = 0.0  # Percentage of requirements that have this field
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttributeConfig':
        """Create from dictionary"""
        return cls(**data)


class ComparisonProfile:
    """
    Manages comparison settings and profiles for advanced requirement comparison
    """
    
    def __init__(self, name: str = "Default Profile"):
        self.name = name
        self.description = ""
        self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
        self.version = "1.0"
        
        # Attribute configurations
        self.attributes: Dict[str, AttributeConfig] = {}
        
        # Comparison settings
        self.similarity_threshold = 0.9  # 90% similarity threshold
        self.ignore_case = True
        self.ignore_whitespace = True
        self.treat_empty_as_null = True
        self.use_fuzzy_matching = False
        
        # Profile metadata
        self.is_default = False
        self.is_system_profile = False
        self.tags: List[str] = []
        
        # Initialize with standard fields
        self._initialize_standard_fields()
    
    def _initialize_standard_fields(self):
        """Initialize with standard ReqIF fields"""
        standard_fields = [
            ("id", "Requirement ID", "standard", "text"),
            ("title", "Title", "standard", "text"),
            ("description", "Description", "standard", "text"),
            ("type", "Type", "standard", "text"),
            ("priority", "Priority", "standard", "text"),
            ("status", "Status", "standard", "text"),
        ]
        
        for field_name, display_name, field_type, data_type in standard_fields:
            self.attributes[field_name] = AttributeConfig(
                name=field_name,
                display_name=display_name,
                enabled=True,
                weight=1.0,
                field_type=field_type,
                data_type=data_type,
                coverage=1.0  # Assume standard fields are always present
            )
    
    def add_attribute(self, name: str, display_name: str = None, 
                     field_type: str = "attribute", data_type: str = "text",
                     enabled: bool = True, weight: float = 1.0, coverage: float = 0.0):
        """Add or update an attribute configuration"""
        if display_name is None:
            display_name = name.replace('_', ' ').title()
        
        self.attributes[name] = AttributeConfig(
            name=name,
            display_name=display_name,
            enabled=enabled,
            weight=weight,
            field_type=field_type,
            data_type=data_type,
            coverage=coverage
        )
        self._update_modified_date()
    
    def remove_attribute(self, name: str):
        """Remove an attribute from the profile"""
        if name in self.attributes and not self.attributes[name].field_type == "standard":
            del self.attributes[name]
            self._update_modified_date()
    
    def set_attribute_enabled(self, name: str, enabled: bool):
        """Enable or disable an attribute"""
        if name in self.attributes:
            self.attributes[name].enabled = enabled
            self._update_modified_date()
    
    def set_attribute_weight(self, name: str, weight: float):
        """Set the weight for an attribute (0.0 to 1.0)"""
        if name in self.attributes:
            # Clamp weight between 0.0 and 1.0
            weight = max(0.0, min(1.0, weight))
            self.attributes[name].weight = weight
            self._update_modified_date()
    
    def get_enabled_attributes(self) -> Dict[str, AttributeConfig]:
        """Get all enabled attributes"""
        return {name: config for name, config in self.attributes.items() if config.enabled}
    
    def get_weighted_attributes(self) -> Dict[str, float]:
        """Get enabled attributes with their weights"""
        return {name: config.weight for name, config in self.attributes.items() 
                if config.enabled and config.weight > 0.0}
    
    def get_standard_fields(self) -> List[str]:
        """Get list of standard field names"""
        return [name for name, config in self.attributes.items() 
                if config.field_type == "standard"]
    
    def get_custom_attributes(self) -> List[str]:
        """Get list of custom attribute names"""
        return [name for name, config in self.attributes.items() 
                if config.field_type == "attribute"]
    
    def calculate_total_weight(self) -> float:
        """Calculate total weight of all enabled attributes"""
        return sum(config.weight for config in self.attributes.values() 
                  if config.enabled)
    
    def normalize_weights(self):
        """Normalize all weights so they sum to 1.0"""
        total_weight = self.calculate_total_weight()
        if total_weight > 0:
            for config in self.attributes.values():
                if config.enabled:
                    config.weight = config.weight / total_weight
            self._update_modified_date()
    
    def reset_to_defaults(self):
        """Reset profile to default settings"""
        # Reset all weights to 1.0
        for config in self.attributes.values():
            config.weight = 1.0
            if config.field_type == "standard":
                config.enabled = True
        
        # Reset comparison settings
        self.similarity_threshold = 0.9
        self.ignore_case = True
        self.ignore_whitespace = True
        self.treat_empty_as_null = True
        self.use_fuzzy_matching = False
        
        self._update_modified_date()
    
    def clone(self, new_name: str = None) -> 'ComparisonProfile':
        """Create a copy of this profile"""
        new_profile = ComparisonProfile(new_name or f"{self.name} (Copy)")
        new_profile.description = self.description
        new_profile.attributes = {name: AttributeConfig(**asdict(config)) 
                                 for name, config in self.attributes.items()}
        new_profile.similarity_threshold = self.similarity_threshold
        new_profile.ignore_case = self.ignore_case
        new_profile.ignore_whitespace = self.ignore_whitespace
        new_profile.treat_empty_as_null = self.treat_empty_as_null
        new_profile.use_fuzzy_matching = self.use_fuzzy_matching
        new_profile.tags = self.tags.copy()
        return new_profile
    
    def validate(self) -> List[str]:
        """Validate profile configuration and return list of issues"""
        issues = []
        
        # Check if any attributes are enabled
        enabled_count = sum(1 for config in self.attributes.values() if config.enabled)
        if enabled_count == 0:
            issues.append("No attributes are enabled for comparison")
        
        # Check if weights are reasonable
        total_weight = self.calculate_total_weight()
        if total_weight == 0:
            issues.append("Total weight of enabled attributes is zero")
        
        # Check threshold range
        if not (0.0 <= self.similarity_threshold <= 1.0):
            issues.append("Similarity threshold must be between 0.0 and 1.0")
        
        # Check for duplicate attribute names
        names = [config.name for config in self.attributes.values()]
        if len(names) != len(set(names)):
            issues.append("Duplicate attribute names found")
        
        return issues
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the profile configuration"""
        enabled_attrs = self.get_enabled_attributes()
        
        return {
            "name": self.name,
            "description": self.description,
            "total_attributes": len(self.attributes),
            "enabled_attributes": len(enabled_attrs),
            "total_weight": self.calculate_total_weight(),
            "similarity_threshold": self.similarity_threshold,
            "ignore_settings": {
                "case": self.ignore_case,
                "whitespace": self.ignore_whitespace,
                "empty_as_null": self.treat_empty_as_null
            },
            "fuzzy_matching": self.use_fuzzy_matching,
            "created": self.created_date,
            "modified": self.modified_date
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "version": self.version,
            "attributes": {name: config.to_dict() for name, config in self.attributes.items()},
            "similarity_threshold": self.similarity_threshold,
            "ignore_case": self.ignore_case,
            "ignore_whitespace": self.ignore_whitespace,
            "treat_empty_as_null": self.treat_empty_as_null,
            "use_fuzzy_matching": self.use_fuzzy_matching,
            "is_default": self.is_default,
            "is_system_profile": self.is_system_profile,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComparisonProfile':
        """Create profile from dictionary"""
        profile = cls(data.get("name", "Unnamed Profile"))
        profile.description = data.get("description", "")
        profile.created_date = data.get("created_date", datetime.now().isoformat())
        profile.modified_date = data.get("modified_date", datetime.now().isoformat())
        profile.version = data.get("version", "1.0")
        
        # Load attributes
        profile.attributes = {}
        for name, attr_data in data.get("attributes", {}).items():
            profile.attributes[name] = AttributeConfig.from_dict(attr_data)
        
        # Load settings
        profile.similarity_threshold = data.get("similarity_threshold", 0.9)
        profile.ignore_case = data.get("ignore_case", True)
        profile.ignore_whitespace = data.get("ignore_whitespace", True)
        profile.treat_empty_as_null = data.get("treat_empty_as_null", True)
        profile.use_fuzzy_matching = data.get("use_fuzzy_matching", False)
        profile.is_default = data.get("is_default", False)
        profile.is_system_profile = data.get("is_system_profile", False)
        profile.tags = data.get("tags", [])
        
        return profile
    
    def save_to_file(self, filename: str):
        """Save profile to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"Failed to save profile to {filename}: {str(e)}")
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'ComparisonProfile':
        """Load profile from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise Exception(f"Failed to load profile from {filename}: {str(e)}")
    
    def _update_modified_date(self):
        """Update the modified timestamp"""
        self.modified_date = datetime.now().isoformat()


class ProfileManager:
    """
    Manages multiple comparison profiles
    """
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        self.profiles: Dict[str, ComparisonProfile] = {}
        self._ensure_profiles_dir()
        self._create_default_profiles()
    
    def _ensure_profiles_dir(self):
        """Ensure profiles directory exists"""
        os.makedirs(self.profiles_dir, exist_ok=True)
    
    def _create_default_profiles(self):
        """Create default system profiles"""
        # Basic profile - only essential fields
        basic = ComparisonProfile("Basic Comparison")
        basic.description = "Compare only essential fields (ID, Title, Description)"
        basic.is_system_profile = True
        basic.set_attribute_enabled("type", False)
        basic.set_attribute_enabled("priority", False)
        basic.set_attribute_enabled("status", False)
        basic.tags = ["system", "basic"]
        self.profiles["basic"] = basic
        
        # Detailed profile - all standard fields
        detailed = ComparisonProfile("Detailed Comparison")
        detailed.description = "Compare all standard fields with equal weight"
        detailed.is_system_profile = True
        detailed.tags = ["system", "detailed"]
        self.profiles["detailed"] = detailed
        
        # Priority-focused profile
        priority = ComparisonProfile("Priority-Focused")
        priority.description = "Emphasize priority and status changes"
        priority.is_system_profile = True
        priority.set_attribute_weight("priority", 1.0)
        priority.set_attribute_weight("status", 1.0)
        priority.set_attribute_weight("title", 0.6)
        priority.set_attribute_weight("description", 0.4)
        priority.set_attribute_weight("type", 0.2)
        priority.tags = ["system", "priority"]
        self.profiles["priority"] = priority
    
    def add_profile(self, profile: ComparisonProfile) -> bool:
        """Add a profile to the manager"""
        if profile.name in self.profiles:
            return False  # Profile already exists
        
        self.profiles[profile.name] = profile
        return True
    
    def get_profile(self, name: str) -> Optional[ComparisonProfile]:
        """Get a profile by name"""
        return self.profiles.get(name)
    
    def remove_profile(self, name: str) -> bool:
        """Remove a profile (cannot remove system profiles)"""
        if name in self.profiles and not self.profiles[name].is_system_profile:
            del self.profiles[name]
            # Also remove file if it exists
            filename = os.path.join(self.profiles_dir, f"{name}.json")
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass
            return True
        return False
    
    def list_profiles(self) -> List[str]:
        """Get list of all profile names"""
        return list(self.profiles.keys())
    
    def get_user_profiles(self) -> List[str]:
        """Get list of user-created profile names"""
        return [name for name, profile in self.profiles.items() 
                if not profile.is_system_profile]
    
    def get_system_profiles(self) -> List[str]:
        """Get list of system profile names"""
        return [name for name, profile in self.profiles.items() 
                if profile.is_system_profile]
    
    def save_profile(self, profile: ComparisonProfile):
        """Save a profile to file"""
        if not profile.is_system_profile:
            filename = os.path.join(self.profiles_dir, f"{profile.name}.json")
            profile.save_to_file(filename)
            self.profiles[profile.name] = profile
    
    def load_profiles_from_directory(self):
        """Load all profiles from the profiles directory"""
        if not os.path.exists(self.profiles_dir):
            return
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.profiles_dir, filename)
                    profile = ComparisonProfile.load_from_file(filepath)
                    self.profiles[profile.name] = profile
                except Exception as e:
                    print(f"Error loading profile {filename}: {e}")
    
    def export_profile(self, name: str, export_path: str):
        """Export a profile to a specific location"""
        if name in self.profiles:
            self.profiles[name].save_to_file(export_path)
    
    def import_profile(self, import_path: str) -> Optional[ComparisonProfile]:
        """Import a profile from a file"""
        try:
            profile = ComparisonProfile.load_from_file(import_path)
            
            # Handle name conflicts
            original_name = profile.name
            counter = 1
            while profile.name in self.profiles:
                profile.name = f"{original_name} ({counter})"
                counter += 1
            
            profile.is_system_profile = False  # Imported profiles are never system profiles
            self.profiles[profile.name] = profile
            return profile
        except Exception as e:
            print(f"Error importing profile: {e}")
            return None


# Example usage and testing
if __name__ == "__main__":
    print("Comparison Profile - Testing")
    
    # Create a test profile
    profile = ComparisonProfile("Test Profile")
    profile.description = "A test profile for development"
    
    # Add some custom attributes
    profile.add_attribute("safety_level", "Safety Level", weight=1.0, coverage=0.8)
    profile.add_attribute("verification_method", "Verification Method", weight=0.6, coverage=0.5)
    profile.add_attribute("source_document", "Source Document", weight=0.3, coverage=0.9)
    
    # Adjust standard field weights
    profile.set_attribute_weight("title", 0.9)
    profile.set_attribute_weight("description", 1.0)
    profile.set_attribute_weight("priority", 0.4)
    
    # Test serialization
    print("\nProfile Summary:")
    summary = profile.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Test validation
    print(f"\nValidation issues: {profile.validate()}")
    
    # Test profile manager
    print("\nTesting Profile Manager:")
    manager = ProfileManager()
    manager.add_profile(profile)
    
    print(f"System profiles: {manager.get_system_profiles()}")
    print(f"User profiles: {manager.get_user_profiles()}")
    
    # Test getting weighted attributes
    print(f"\nWeighted attributes: {profile.get_weighted_attributes()}")
    print(f"Total weight: {profile.calculate_total_weight():.2f}")
    
    print("\nComparison Profile testing completed successfully!")