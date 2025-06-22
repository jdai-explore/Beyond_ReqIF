#!/usr/bin/env python3
"""
Attribute Analyzer for ReqIF Files
Analyzes requirement files to discover available attributes and their characteristics.
Phase 1: Advanced Comparison Feature
"""

import re
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass
import statistics


@dataclass
class AttributeStats:
    """Statistics about a single attribute"""
    name: str
    display_name: str
    field_type: str  # "standard", "attribute", "custom"
    data_type: str   # "text", "number", "date", "boolean", "enum"
    coverage: float  # Percentage of requirements that have this field (0.0 to 1.0)
    sample_values: List[str]  # Sample values for preview
    unique_values: int  # Number of unique values
    avg_length: float  # Average character length of values
    max_length: int   # Maximum character length
    is_nullable: bool # Whether field can be empty/null
    suggested_weight: float  # Suggested default weight (0.0 to 1.0)


class AttributeAnalyzer:
    """
    Analyzes ReqIF requirements to discover and characterize available attributes
    """
    
    def __init__(self):
        self.standard_fields = {
            'id': ('Requirement ID', 'text'),
            'identifier': ('Identifier', 'text'), 
            'title': ('Title', 'text'),
            'description': ('Description', 'text'),
            'type': ('Type', 'enum'),
            'priority': ('Priority', 'enum'),
            'status': ('Status', 'enum'),
            'content': ('Content', 'text')
        }
        
        # Patterns for detecting data types
        self.number_pattern = re.compile(r'^-?\d+(\.\d+)?$')
        self.date_patterns = [
            re.compile(r'\d{4}-\d{2}-\d{2}'),  # ISO date
            re.compile(r'\d{2}/\d{2}/\d{4}'),  # US date
            re.compile(r'\d{2}-\d{2}-\d{4}'),  # EU date
        ]
        self.boolean_values = {'true', 'false', 'yes', 'no', '1', '0', 'on', 'off'}
    
    def analyze_requirements(self, requirements: List[Dict[str, Any]]) -> Dict[str, AttributeStats]:
        """
        Analyze a list of requirements and return attribute statistics
        
        Args:
            requirements: List of requirement dictionaries
            
        Returns:
            Dictionary mapping attribute names to their statistics
        """
        if not requirements:
            return {}
        
        print(f"Analyzing {len(requirements)} requirements for attributes...")
        
        # Collect all attribute data
        attribute_data = self._collect_attribute_data(requirements)
        
        # Analyze each attribute
        attribute_stats = {}
        for attr_name, data in attribute_data.items():
            stats = self._analyze_attribute(attr_name, data, len(requirements))
            attribute_stats[attr_name] = stats
        
        print(f"Found {len(attribute_stats)} attributes")
        return attribute_stats
    
    def _collect_attribute_data(self, requirements: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Collect all values for each attribute across all requirements"""
        attribute_data = defaultdict(list)
        
        for req in requirements:
            # Process standard fields
            for field_name in self.standard_fields.keys():
                value = req.get(field_name, '')
                if value is not None:
                    attribute_data[field_name].append(str(value).strip())
                else:
                    attribute_data[field_name].append('')
            
            # Process custom attributes
            attributes = req.get('attributes', {})
            if isinstance(attributes, dict):
                for attr_name, attr_value in attributes.items():
                    if attr_value is not None:
                        attribute_data[f"attr_{attr_name}"].append(str(attr_value).strip())
                    else:
                        attribute_data[f"attr_{attr_name}"].append('')
            
            # Process raw attributes if available
            raw_attributes = req.get('raw_attributes', {})
            if isinstance(raw_attributes, dict):
                for attr_name, attr_value in raw_attributes.items():
                    if attr_name not in attributes:  # Don't duplicate
                        if attr_value is not None:
                            attribute_data[f"raw_{attr_name}"].append(str(attr_value).strip())
                        else:
                            attribute_data[f"raw_{attr_name}"].append('')
        
        return attribute_data
    
    def _analyze_attribute(self, attr_name: str, values: List[str], total_count: int) -> AttributeStats:
        """Analyze a single attribute and return its statistics"""
        
        # Determine field type and display name
        field_type, display_name = self._determine_field_type_and_name(attr_name)
        
        # Filter out empty values for analysis
        non_empty_values = [v for v in values if v.strip()]
        
        # Calculate coverage
        coverage = len(non_empty_values) / total_count if total_count > 0 else 0.0
        
        # Determine data type
        data_type = self._determine_data_type(non_empty_values)
        
        # Calculate statistics
        unique_values = len(set(non_empty_values))
        avg_length = statistics.mean([len(v) for v in non_empty_values]) if non_empty_values else 0.0
        max_length = max([len(v) for v in non_empty_values]) if non_empty_values else 0
        is_nullable = len(non_empty_values) < len(values)
        
        # Get sample values (up to 5 unique values)
        sample_values = list(set(non_empty_values))[:5]
        
        # Calculate suggested weight
        suggested_weight = self._calculate_suggested_weight(
            attr_name, field_type, data_type, coverage, unique_values, total_count
        )
        
        return AttributeStats(
            name=attr_name,
            display_name=display_name,
            field_type=field_type,
            data_type=data_type,
            coverage=coverage,
            sample_values=sample_values,
            unique_values=unique_values,
            avg_length=avg_length,
            max_length=max_length,
            is_nullable=is_nullable,
            suggested_weight=suggested_weight
        )
    
    def _determine_field_type_and_name(self, attr_name: str) -> Tuple[str, str]:
        """Determine field type (standard/attribute/custom) and display name"""
        
        # Standard fields
        if attr_name in self.standard_fields:
            display_name, _ = self.standard_fields[attr_name]
            return "standard", display_name
        
        # Custom attributes (prefixed)
        if attr_name.startswith('attr_'):
            clean_name = attr_name[5:]  # Remove 'attr_' prefix
            display_name = clean_name.replace('_', ' ').title()
            return "attribute", display_name
        
        if attr_name.startswith('raw_'):
            clean_name = attr_name[4:]  # Remove 'raw_' prefix
            display_name = f"Raw: {clean_name.replace('_', ' ').title()}"
            return "attribute", display_name
        
        # Other custom fields
        display_name = attr_name.replace('_', ' ').title()
        return "custom", display_name
    
    def _determine_data_type(self, values: List[str]) -> str:
        """Determine the most likely data type for the values"""
        if not values:
            return "text"
        
        # Sample up to 100 values for performance
        sample_values = values[:100] if len(values) > 100 else values
        
        # Check for boolean
        if self._is_boolean_field(sample_values):
            return "boolean"
        
        # Check for numbers
        if self._is_numeric_field(sample_values):
            return "number"
        
        # Check for dates
        if self._is_date_field(sample_values):
            return "date"
        
        # Check for enums (limited unique values)
        unique_count = len(set(sample_values))
        if unique_count <= 10 and len(sample_values) > unique_count * 3:
            return "enum"
        
        return "text"
    
    def _is_boolean_field(self, values: List[str]) -> bool:
        """Check if values appear to be boolean"""
        if not values:
            return False
        
        # Check if all non-empty values are boolean-like
        boolean_count = 0
        for value in values:
            if value.lower() in self.boolean_values:
                boolean_count += 1
        
        return boolean_count / len(values) >= 0.8
    
    def _is_numeric_field(self, values: List[str]) -> bool:
        """Check if values appear to be numeric"""
        if not values:
            return False
        
        numeric_count = 0
        for value in values:
            if self.number_pattern.match(value.strip()):
                numeric_count += 1
        
        return numeric_count / len(values) >= 0.8
    
    def _is_date_field(self, values: List[str]) -> bool:
        """Check if values appear to be dates"""
        if not values:
            return False
        
        date_count = 0
        for value in values:
            for pattern in self.date_patterns:
                if pattern.search(value):
                    date_count += 1
                    break
        
        return date_count / len(values) >= 0.6
    
    def _calculate_suggested_weight(self, attr_name: str, field_type: str, data_type: str, 
                                  coverage: float, unique_values: int, total_count: int) -> float:
        """Calculate a suggested weight for the attribute"""
        
        base_weight = 0.5  # Start with medium weight
        
        # Boost for high coverage
        base_weight += coverage * 0.3
        
        # Boost for standard fields
        if field_type == "standard":
            if attr_name in ['id', 'title']:
                base_weight += 0.3
            elif attr_name in ['description']:
                base_weight += 0.4
            elif attr_name in ['type', 'priority', 'status']:
                base_weight += 0.2
        
        # Boost for important-sounding attributes
        important_keywords = ['safety', 'critical', 'security', 'risk', 'priority', 
                             'verification', 'validation', 'compliance', 'regulatory']
        attr_lower = attr_name.lower()
        for keyword in important_keywords:
            if keyword in attr_lower:
                base_weight += 0.2
                break
        
        # Adjust based on data type
        if data_type == "enum" and unique_values <= 5:
            base_weight += 0.1  # Enums are often important for categorization
        elif data_type == "boolean":
            base_weight += 0.1  # Boolean flags are often significant
        
        # Reduce weight for very sparse attributes
        if coverage < 0.1:
            base_weight *= 0.5
        
        # Reduce weight for attributes with too many unique values (likely IDs)
        if unique_values > total_count * 0.8:
            base_weight *= 0.3
        
        # Clamp between 0.0 and 1.0
        return max(0.0, min(1.0, base_weight))
    
    def get_recommended_attributes(self, attribute_stats: Dict[str, AttributeStats], 
                                 max_attributes: int = 8) -> List[str]:
        """Get recommended attributes for comparison based on analysis"""
        
        # Sort by suggested weight and coverage
        sorted_attrs = sorted(
            attribute_stats.items(),
            key=lambda x: (x[1].suggested_weight * x[1].coverage),
            reverse=True
        )
        
        # Always include standard fields with good coverage first
        recommended = []
        
        # Add essential standard fields
        for attr_name, stats in sorted_attrs:
            if stats.field_type == "standard" and stats.coverage > 0.5:
                recommended.append(attr_name)
            if len(recommended) >= max_attributes // 2:
                break
        
        # Add best custom attributes
        for attr_name, stats in sorted_attrs:
            if attr_name not in recommended and stats.coverage > 0.3:
                recommended.append(attr_name)
            if len(recommended) >= max_attributes:
                break
        
        return recommended
    
    def generate_profile_suggestions(self, attribute_stats: Dict[str, AttributeStats]) -> List[Dict[str, Any]]:
        """Generate suggested comparison profiles based on analysis"""
        suggestions = []
        
        # Essential fields profile
        essential_attrs = [name for name, stats in attribute_stats.items() 
                          if stats.field_type == "standard" and stats.coverage > 0.8]
        if essential_attrs:
            suggestions.append({
                "name": "Essential Fields Only",
                "description": "Compare only essential requirement fields",
                "attributes": essential_attrs,
                "use_case": "Quick comparison focusing on core requirement data"
            })
        
        # High coverage profile
        high_coverage_attrs = [name for name, stats in attribute_stats.items() 
                              if stats.coverage > 0.7]
        if len(high_coverage_attrs) > len(essential_attrs):
            suggestions.append({
                "name": "High Coverage Fields",
                "description": "Compare fields that are present in most requirements",
                "attributes": high_coverage_attrs,
                "use_case": "Comprehensive comparison of well-populated fields"
            })
        
        # Safety/Critical profile (if applicable)
        safety_attrs = [name for name, stats in attribute_stats.items() 
                       if any(keyword in stats.name.lower() 
                             for keyword in ['safety', 'critical', 'risk', 'hazard'])]
        if safety_attrs:
            # Add some standard fields
            safety_profile_attrs = [name for name, stats in attribute_stats.items() 
                                   if stats.field_type == "standard" and stats.coverage > 0.5]
            safety_profile_attrs.extend(safety_attrs)
            suggestions.append({
                "name": "Safety & Critical Analysis",
                "description": "Focus on safety-critical and risk-related attributes",
                "attributes": list(set(safety_profile_attrs)),
                "use_case": "Safety-critical system requirement analysis"
            })
        
        # Compliance profile (if applicable)
        compliance_attrs = [name for name, stats in attribute_stats.items() 
                           if any(keyword in stats.name.lower() 
                                 for keyword in ['compliance', 'regulatory', 'standard', 
                                               'verification', 'validation', 'trace'])]
        if compliance_attrs:
            compliance_profile_attrs = [name for name, stats in attribute_stats.items() 
                                       if stats.field_type == "standard" and stats.coverage > 0.5]
            compliance_profile_attrs.extend(compliance_attrs)
            suggestions.append({
                "name": "Compliance & Traceability",
                "description": "Focus on compliance and traceability attributes",
                "attributes": list(set(compliance_profile_attrs)),
                "use_case": "Regulatory compliance and audit preparation"
            })
        
        return suggestions
    
    def export_analysis_report(self, attribute_stats: Dict[str, AttributeStats]) -> str:
        """Generate a text report of the attribute analysis"""
        lines = [
            "Attribute Analysis Report",
            "=" * 50,
            "",
            f"Total Attributes Found: {len(attribute_stats)}",
            ""
        ]
        
        # Group by field type
        by_type = defaultdict(list)
        for name, stats in attribute_stats.items():
            by_type[stats.field_type].append((name, stats))
        
        for field_type in ["standard", "attribute", "custom"]:
            if field_type in by_type:
                lines.append(f"{field_type.title()} Fields ({len(by_type[field_type])}):")
                lines.append("-" * 30)
                
                # Sort by coverage
                sorted_attrs = sorted(by_type[field_type], 
                                    key=lambda x: x[1].coverage, reverse=True)
                
                for name, stats in sorted_attrs:
                    lines.append(f"  {stats.display_name}")
                    lines.append(f"    Coverage: {stats.coverage:.1%}")
                    lines.append(f"    Data Type: {stats.data_type}")
                    lines.append(f"    Unique Values: {stats.unique_values}")
                    lines.append(f"    Suggested Weight: {stats.suggested_weight:.2f}")
                    if stats.sample_values:
                        sample_str = ", ".join(stats.sample_values[:3])
                        if len(stats.sample_values) > 3:
                            sample_str += "..."
                        lines.append(f"    Sample Values: {sample_str}")
                    lines.append("")
                
                lines.append("")
        
        # Recommendations
        recommended = self.get_recommended_attributes(attribute_stats)
        lines.append("Recommended Attributes for Comparison:")
        lines.append("-" * 40)
        for attr_name in recommended:
            stats = attribute_stats[attr_name]
            lines.append(f"  • {stats.display_name} (Coverage: {stats.coverage:.1%})")
        
        return "\n".join(lines)
    
    def get_analysis_summary(self, attribute_stats: Dict[str, AttributeStats]) -> Dict[str, Any]:
        """Get a summary of the analysis results"""
        if not attribute_stats:
            return {}
        
        # Count by type
        type_counts = Counter(stats.field_type for stats in attribute_stats.values())
        
        # Coverage statistics
        coverages = [stats.coverage for stats in attribute_stats.values()]
        avg_coverage = statistics.mean(coverages) if coverages else 0.0
        
        # Data type distribution
        data_type_counts = Counter(stats.data_type for stats in attribute_stats.values())
        
        # High-quality attributes (good coverage and weight)
        high_quality = [name for name, stats in attribute_stats.items() 
                       if stats.coverage > 0.5 and stats.suggested_weight > 0.6]
        
        return {
            "total_attributes": len(attribute_stats),
            "by_type": dict(type_counts),
            "by_data_type": dict(data_type_counts),
            "average_coverage": avg_coverage,
            "high_quality_attributes": len(high_quality),
            "recommended_count": len(self.get_recommended_attributes(attribute_stats)),
            "sparsest_attribute": min(attribute_stats.items(), 
                                    key=lambda x: x[1].coverage)[0] if attribute_stats else None,
            "densest_attribute": max(attribute_stats.items(), 
                                   key=lambda x: x[1].coverage)[0] if attribute_stats else None
        }


# Utility functions for integration with existing code
def analyze_requirements_for_profile(requirements1: List[Dict[str, Any]], 
                                   requirements2: List[Dict[str, Any]] = None) -> Dict[str, AttributeStats]:
    """
    Convenience function to analyze requirements for profile creation
    
    Args:
        requirements1: First set of requirements
        requirements2: Optional second set of requirements
        
    Returns:
        Combined attribute analysis from both sets
    """
    analyzer = AttributeAnalyzer()
    
    # Combine requirements if we have two sets
    if requirements2:
        combined_requirements = requirements1 + requirements2
        print(f"Analyzing combined requirements: {len(requirements1)} + {len(requirements2)} = {len(combined_requirements)}")
    else:
        combined_requirements = requirements1
        print(f"Analyzing requirements: {len(requirements1)}")
    
    return analyzer.analyze_requirements(combined_requirements)


def create_profile_from_analysis(attribute_stats: Dict[str, AttributeStats], 
                                profile_name: str = "Auto-Generated Profile") -> 'ComparisonProfile':
    """
    Create a comparison profile based on attribute analysis
    
    Args:
        attribute_stats: Results from analyze_requirements
        profile_name: Name for the new profile
        
    Returns:
        ComparisonProfile configured with analyzed attributes
    """
    from comparison_profile import ComparisonProfile
    
    profile = ComparisonProfile(profile_name)
    profile.description = f"Auto-generated profile based on analysis of {len(attribute_stats)} attributes"
    
    # Clear default attributes and add analyzed ones
    profile.attributes.clear()
    
    for attr_name, stats in attribute_stats.items():
        profile.add_attribute(
            name=attr_name,
            display_name=stats.display_name,
            field_type=stats.field_type,
            data_type=stats.data_type,
            enabled=stats.coverage > 0.3,  # Enable if coverage > 30%
            weight=stats.suggested_weight,
            coverage=stats.coverage
        )
    
    return profile


# Example usage and testing
if __name__ == "__main__":
    print("Attribute Analyzer - Testing")
    
    # Create test requirements
    test_requirements = [
        {
            'id': 'REQ-001',
            'title': 'System shall start',
            'description': 'The system shall start within 5 seconds',
            'type': 'functional',
            'priority': 'high',
            'status': 'approved',
            'attributes': {
                'safety_level': 'SIL-2',
                'verification_method': 'test',
                'source_document': 'SRS-001',
                'creation_date': '2024-01-15'
            }
        },
        {
            'id': 'REQ-002',
            'title': 'System shall stop',
            'description': 'The system shall stop safely',
            'type': 'functional',
            'priority': 'critical',
            'status': 'draft',
            'attributes': {
                'safety_level': 'SIL-3',
                'verification_method': 'inspection',
                'creation_date': '2024-01-16'
            }
        },
        {
            'id': 'REQ-003',
            'title': 'Error handling',
            'description': 'System shall handle errors gracefully',
            'type': 'non-functional',
            'priority': 'medium',
            'status': 'approved',
            'attributes': {
                'safety_level': 'SIL-1',
                'verification_method': 'test',
                'source_document': 'SRS-002'
            }
        }
    ]
    
    # Test analysis
    analyzer = AttributeAnalyzer()
    results = analyzer.analyze_requirements(test_requirements)
    
    print(f"\nFound {len(results)} attributes:")
    for name, stats in results.items():
        print(f"  {stats.display_name}: {stats.coverage:.1%} coverage, weight {stats.suggested_weight:.2f}")
    
    # Test recommendations
    recommended = analyzer.get_recommended_attributes(results)
    print(f"\nRecommended attributes: {recommended}")
    
    # Test profile suggestions
    suggestions = analyzer.generate_profile_suggestions(results)
    print(f"\nProfile suggestions: {len(suggestions)}")
    for suggestion in suggestions:
        print(f"  - {suggestion['name']}: {len(suggestion['attributes'])} attributes")
    
    # Test summary
    summary = analyzer.get_analysis_summary(results)
    print(f"\nAnalysis summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\nAttribute Analyzer testing completed successfully!")