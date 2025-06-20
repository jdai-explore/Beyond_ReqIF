"""
ReqIF Analyzer Module
====================

This module provides comprehensive statistical analysis and metrics
calculation for ReqIF files and requirements data.

Classes:
    ReqIFAnalyzer: Main analysis engine
    AnalysisResult: Container for analysis results
    MetricCalculator: Calculator for various metrics
    TrendAnalyzer: Analyzer for trend detection
    
Functions:
    analyze_requirements: Quick analysis function
    calculate_metrics: Calculate specific metrics
    generate_report: Generate analysis report
"""

import re
import statistics
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Import project modules
from models.requirement import Requirement
from utils.logger import get_logger
from utils.helpers import normalize_text, extract_keywords

logger = get_logger(__name__)


class AnalysisMode(Enum):
    """Analysis mode enumeration"""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class MetricType(Enum):
    """Types of metrics that can be calculated"""
    TEXT_COMPLEXITY = "text_complexity"
    ATTRIBUTE_COMPLETENESS = "attribute_completeness"
    REQUIREMENT_DENSITY = "requirement_density"
    READABILITY = "readability"
    CONSISTENCY = "consistency"
    TRACEABILITY = "traceability"


@dataclass
class AnalysisOptions:
    """Configuration options for analysis"""
    mode: AnalysisMode = AnalysisMode.DETAILED
    include_text_analysis: bool = True
    include_attribute_analysis: bool = True
    include_quality_metrics: bool = True
    include_trends: bool = False
    custom_metrics: List[MetricType] = field(default_factory=list)
    language: str = "en"
    readability_formula: str = "flesch_kincaid"


@dataclass
class RequirementStatistics:
    """Basic requirement statistics"""
    total_count: int = 0
    with_text: int = 0
    with_attributes: int = 0
    empty_requirements: int = 0
    avg_attributes_per_requirement: float = 0.0
    avg_text_length: float = 0.0
    min_text_length: int = 0
    max_text_length: int = 0


@dataclass
class TextStatistics:
    """Text analysis statistics"""
    total_characters: int = 0
    total_words: int = 0
    total_sentences: int = 0
    avg_words_per_requirement: float = 0.0
    avg_sentences_per_requirement: float = 0.0
    avg_word_length: float = 0.0
    avg_readability_score: float = 0.0
    avg_complexity_score: float = 0.0
    word_count_distribution: Dict[str, Any] = field(default_factory=dict)
    readability_distribution: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttributeStatistics:
    """Attribute analysis statistics"""
    total_unique_attributes: int = 0
    attribute_completeness: Dict[str, float] = field(default_factory=dict)
    attribute_distributions: Dict[str, Dict[str, int]] = field(default_factory=dict)
    missing_attributes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    most_common_attributes: Dict[str, int] = field(default_factory=dict)
    avg_completeness: float = 0.0
    min_completeness: float = 0.0
    max_completeness: float = 0.0


@dataclass
class DistributionAnalysis:
    """Distribution analysis results"""
    categories: Dict[str, int] = field(default_factory=dict)
    percentages: Dict[str, float] = field(default_factory=dict)
    total_items: int = 0
    unique_categories: int = 0
    most_common: Tuple[str, int] = ("", 0)


@dataclass
class QualityMetrics:
    """Quality assessment metrics"""
    overall_score: float = 0.0
    readability_score: float = 0.0
    completeness_score: float = 0.0
    consistency_issues: List[Dict[str, str]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    quality_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis results"""
    changes_over_time: Dict[str, List[Any]] = field(default_factory=dict)
    growth_rates: Dict[str, float] = field(default_factory=dict)
    patterns: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    file_path: str
    analysis_timestamp: datetime
    options: AnalysisOptions
    
    # Core statistics
    requirement_stats: RequirementStatistics
    text_stats: TextStatistics
    attribute_stats: AttributeStatistics
    
    # Distribution analysis
    type_distribution: DistributionAnalysis
    status_distribution: DistributionAnalysis
    priority_distribution: DistributionAnalysis
    
    # Quality metrics
    quality_metrics: QualityMetrics
    
    # Optional trend analysis
    trend_analysis: Optional[TrendAnalysis] = None
    
    # Custom metrics
    custom_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Analysis metadata
    processing_time: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class TextAnalyzer:
    """Analyzes text content of requirements"""
    
    def __init__(self, language: str = "en"):
        self.language = language
        
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze a single text for various metrics"""
        if not text:
            return self._empty_analysis()
        
        analysis = {
            'character_count': len(text),
            'word_count': len(text.split()),
            'sentence_count': self._count_sentences(text),
            'paragraph_count': self._count_paragraphs(text),
            'avg_word_length': self._average_word_length(text),
            'avg_sentence_length': self._average_sentence_length(text),
            'complexity_score': self._calculate_complexity(text),
            'readability_score': self._calculate_readability(text),
            'keyword_density': self._calculate_keyword_density(text),
            'special_characters': self._count_special_characters(text),
            'numbers_count': self._count_numbers(text),
            'urls_count': self._count_urls(text),
            'capitalized_words': self._count_capitalized_words(text)
        }
        
        return analysis
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis for null/empty text"""
        return {key: 0 for key in [
            'character_count', 'word_count', 'sentence_count', 'paragraph_count',
            'avg_word_length', 'avg_sentence_length', 'complexity_score',
            'readability_score', 'keyword_density', 'special_characters',
            'numbers_count', 'urls_count', 'capitalized_words'
        ]}
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        sentence_endings = re.findall(r'[.!?]+', text)
        return len(sentence_endings) if sentence_endings else 1
    
    def _count_paragraphs(self, text: str) -> int:
        """Count paragraphs in text"""
        paragraphs = text.split('\n\n')
        return len([p for p in paragraphs if p.strip()])
    
    def _average_word_length(self, text: str) -> float:
        """Calculate average word length"""
        words = text.split()
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    def _average_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words"""
        word_count = len(text.split())
        sentence_count = self._count_sentences(text)
        return word_count / sentence_count if sentence_count > 0 else 0.0
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-100)"""
        words = text.split()
        if not words:
            return 0.0
        
        # Factors contributing to complexity
        avg_word_length = self._average_word_length(text)
        avg_sentence_length = self._average_sentence_length(text)
        special_char_ratio = self._count_special_characters(text) / len(text)
        
        # Weighted complexity score
        complexity = (
            (avg_word_length * 10) +
            (avg_sentence_length * 2) +
            (special_char_ratio * 50)
        )
        
        return min(complexity, 100.0)  # Cap at 100
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score using Flesch-Kincaid formula"""
        words = text.split()
        sentences = self._count_sentences(text)
        
        if not words or sentences == 0:
            return 0.0
        
        # Count syllables (simplified)
        total_syllables = sum(self._count_syllables(word) for word in words)
        
        # Flesch-Kincaid Grade Level
        if sentences > 0 and len(words) > 0:
            score = (
                (0.39 * (len(words) / sentences)) +
                (11.8 * (total_syllables / len(words))) -
                15.59
            )
            return max(0.0, score)
        
        return 0.0
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        vowels = 'aeiouy'
        syllables = 0
        prev_char_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_vowel:
                    syllables += 1
                prev_char_vowel = True
            else:
                prev_char_vowel = False
        
        # Adjust for silent 'e'
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        return max(1, syllables)  # At least 1 syllable per word
    
    def _calculate_keyword_density(self, text: str) -> Dict[str, float]:
        """Calculate keyword density"""
        words = text.lower().split()
        if not words:
            return {}
        
        word_count = Counter(words)
        total_words = len(words)
        
        # Return density for top 10 keywords
        top_keywords = word_count.most_common(10)
        return {word: count / total_words for word, count in top_keywords}
    
    def _count_special_characters(self, text: str) -> int:
        """Count special characters and punctuation"""
        special_chars = re.findall(r'[^a-zA-Z0-9\s]', text)
        return len(special_chars)
    
    def _count_numbers(self, text: str) -> int:
        """Count numeric values in text"""
        numbers = re.findall(r'\b\d+\b', text)
        return len(numbers)
    
    def _count_urls(self, text: str) -> int:
        """Count URLs in text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return len(urls)
    
    def _count_capitalized_words(self, text: str) -> int:
        """Count capitalized words (potential acronyms or proper nouns)"""
        words = text.split()
        capitalized = [word for word in words if word.isupper() and len(word) > 1]
        return len(capitalized)


class AttributeAnalyzer:
    """Analyzes requirement attributes"""
    
    def analyze_attributes(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Analyze attributes across all requirements"""
        if not requirements:
            return self._empty_attribute_analysis()
        
        all_attributes = defaultdict(list)
        attribute_presence = defaultdict(int)
        attribute_types = defaultdict(set)
        
        # Collect all attributes
        for req in requirements.values():
            for attr_name, attr_value in req.attributes.items():
                all_attributes[attr_name].append(attr_value)
                attribute_presence[attr_name] += 1
                attribute_types[attr_name].add(type(attr_value).__name__)
        
        total_requirements = len(requirements)
        
        analysis = {
            'total_unique_attributes': len(all_attributes),
            'attribute_completeness': {},
            'attribute_distributions': {},
            'attribute_types': {},
            'missing_attributes': {},
            'most_common_attributes': [],
            'least_common_attributes': []
        }
        
        # Calculate completeness and distributions
        for attr_name, values in all_attributes.items():
            completeness = attribute_presence[attr_name] / total_requirements
            analysis['attribute_completeness'][attr_name] = completeness
            
            # Value distribution
            value_counts = Counter(values)
            analysis['attribute_distributions'][attr_name] = dict(value_counts.most_common(10))
            
            # Attribute types
            analysis['attribute_types'][attr_name] = list(attribute_types[attr_name])
        
        # Find missing attributes (present in less than 50% of requirements)
        for attr_name, count in attribute_presence.items():
            if count / total_requirements < 0.5:
                analysis['missing_attributes'][attr_name] = {
                    'present_count': count,
                    'missing_count': total_requirements - count,
                    'completeness': count / total_requirements
                }
        
        # Most and least common attributes
        sorted_attrs = sorted(attribute_presence.items(), key=lambda x: x[1], reverse=True)
        analysis['most_common_attributes'] = sorted_attrs[:10]
        analysis['least_common_attributes'] = sorted_attrs[-10:]
        
        return analysis
    
    def _empty_attribute_analysis(self) -> Dict[str, Any]:
        """Return empty analysis for no requirements"""
        return {
            'total_unique_attributes': 0,
            'attribute_completeness': {},
            'attribute_distributions': {},
            'attribute_types': {},
            'missing_attributes': {},
            'most_common_attributes': [],
            'least_common_attributes': []
        }


class QualityAnalyzer:
    """Analyzes quality metrics of requirements"""
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
    
    def analyze_quality(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Analyze quality metrics"""
        if not requirements:
            return self._empty_quality_analysis()
        
        quality_scores = []
        readability_scores = []
        completeness_scores = []
        consistency_issues = []
        
        for req_id, req in requirements.items():
            # Text quality
            text_analysis = self.text_analyzer.analyze_text(req.text)
            quality_score = self._calculate_quality_score(req, text_analysis)
            quality_scores.append(quality_score)
            
            readability_scores.append(text_analysis['readability_score'])
            
            # Completeness
            completeness = self._calculate_completeness(req)
            completeness_scores.append(completeness)
            
            # Consistency checks
            issues = self._check_consistency(req_id, req)
            consistency_issues.extend(issues)
        
        analysis = {
            'overall_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
            'quality_distribution': self._create_distribution(quality_scores),
            'average_readability': statistics.mean(readability_scores) if readability_scores else 0,
            'readability_distribution': self._create_distribution(readability_scores),
            'average_completeness': statistics.mean(completeness_scores) if completeness_scores else 0,
            'completeness_distribution': self._create_distribution(completeness_scores),
            'consistency_issues': consistency_issues,
            'quality_recommendations': self._generate_recommendations(requirements)
        }
        
        return analysis
    
    def _calculate_quality_score(self, req: Requirement, text_analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score for a requirement (0-100)"""
        scores = []
        
        # Text length appropriateness (penalty for too short or too long)
        text_length = text_analysis['character_count']
        if 50 <= text_length <= 500:
            scores.append(100)
        elif text_length < 50:
            scores.append(max(0, text_length * 2))  # Penalty for short text
        else:
            scores.append(max(0, 100 - (text_length - 500) / 10))  # Penalty for long text
        
        # Readability score
        readability = text_analysis['readability_score']
        if 8 <= readability <= 12:  # Ideal grade level
            scores.append(100)
        else:
            scores.append(max(0, 100 - abs(readability - 10) * 5))
        
        # Attribute completeness
        attribute_score = len(req.attributes) * 20  # 20 points per attribute, max 100
        scores.append(min(100, attribute_score))
        
        # Text complexity (prefer moderate complexity)
        complexity = text_analysis['complexity_score']
        if 20 <= complexity <= 60:
            scores.append(100)
        else:
            scores.append(max(0, 100 - abs(complexity - 40)))
        
        return statistics.mean(scores)
    
    def _calculate_completeness(self, req: Requirement) -> float:
        """Calculate completeness score (0-100)"""
        score = 0
        
        # Text presence and quality
        if req.text:
            score += 40
            if len(req.text) >= 50:
                score += 10
        
        # Attribute presence
        essential_attributes = ['TYPE', 'STATUS', 'PRIORITY']
        for attr in essential_attributes:
            if any(attr.lower() in key.lower() for key in req.attributes.keys()):
                score += 15
        
        # Additional attributes
        if len(req.attributes) > 3:
            score += 5
        
        return min(100, score)
    
    def _check_consistency(self, req_id: str, req: Requirement) -> List[Dict[str, str]]:
        """Check for consistency issues"""
        issues = []
        
        # Check ID format consistency
        if not re.match(r'^[A-Z]{2,}-\d+$', req_id):
            issues.append({
                'req_id': req_id,
                'type': 'ID_FORMAT',
                'description': 'Requirement ID does not follow standard format (e.g., REQ-001)'
            })
        
        # Check for empty or very short text
        if not req.text or len(req.text.strip()) < 10:
            issues.append({
                'req_id': req_id,
                'type': 'INSUFFICIENT_TEXT',
                'description': 'Requirement text is too short or empty'
            })
        
        # Check for missing essential attributes
        essential_attrs = ['type', 'status', 'priority']
        req_attr_keys = [key.lower() for key in req.attributes.keys()]
        
        for essential_attr in essential_attrs:
            if not any(essential_attr in key for key in req_attr_keys):
                issues.append({
                    'req_id': req_id,
                    'type': 'MISSING_ATTRIBUTE',
                    'description': f'Missing essential attribute: {essential_attr}'
                })
        
        # Check for potential duplicates (same text)
        text_hash = hash(req.text.strip().lower())
        if hasattr(self, '_seen_text_hashes'):
            if text_hash in self._seen_text_hashes:
                issues.append({
                    'req_id': req_id,
                    'type': 'POTENTIAL_DUPLICATE',
                    'description': 'Requirement text appears to be duplicated'
                })
            else:
                self._seen_text_hashes.add(text_hash)
        else:
            self._seen_text_hashes = {text_hash}
        
        return issues
    
    def _create_distribution(self, values: List[float]) -> Dict[str, int]:
        """Create distribution buckets for values"""
        if not values:
            return {}
        
        buckets = {
            'excellent (90-100)': 0,
            'good (70-89)': 0,
            'fair (50-69)': 0,
            'poor (30-49)': 0,
            'very_poor (0-29)': 0
        }
        
        for value in values:
            if value >= 90:
                buckets['excellent (90-100)'] += 1
            elif value >= 70:
                buckets['good (70-89)'] += 1
            elif value >= 50:
                buckets['fair (50-69)'] += 1
            elif value >= 30:
                buckets['poor (30-49)'] += 1
            else:
                buckets['very_poor (0-29)'] += 1
        
        return buckets
    
    def _generate_recommendations(self, requirements: Dict[str, Requirement]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if not requirements:
            return recommendations
        
        # Analyze text lengths
        text_lengths = [len(req.text) for req in requirements.values()]
        avg_length = statistics.mean(text_lengths)
        
        if avg_length < 50:
            recommendations.append("Consider adding more detail to requirement descriptions")
        elif avg_length > 500:
            recommendations.append("Consider breaking down overly long requirements")
        
        # Analyze attribute completeness
        total_attrs = sum(len(req.attributes) for req in requirements.values())
        avg_attrs = total_attrs / len(requirements)
        
        if avg_attrs < 3:
            recommendations.append("Add more attributes to requirements for better traceability")
        
        # Check for standard attributes
        all_attr_keys = set()
        for req in requirements.values():
            all_attr_keys.update(key.lower() for key in req.attributes.keys())
        
        essential_attrs = ['type', 'status', 'priority']
        missing_essential = [attr for attr in essential_attrs if not any(attr in key for key in all_attr_keys)]
        
        if missing_essential:
            recommendations.append(f"Consider adding essential attributes: {', '.join(missing_essential)}")
        
        return recommendations
    
    def _empty_quality_analysis(self) -> Dict[str, Any]:
        """Return empty quality analysis"""
        return {
            'overall_quality_score': 0,
            'quality_distribution': {},
            'average_readability': 0,
            'readability_distribution': {},
            'average_completeness': 0,
            'completeness_distribution': {},
            'consistency_issues': [],
            'quality_recommendations': []
        }


class ReqIFAnalyzer:
    """
    ReqIF File Analyzer
    
    Provides comprehensive analysis of ReqIF files with support for:
    - Statistical analysis of requirements
    - Text complexity and readability analysis
    - Attribute distribution and completeness
    - Quality metrics and recommendations
    - Trend analysis over time
    """
    
    def __init__(self, options: AnalysisOptions = None):
        """Initialize the analyzer with options"""
        self.options = options or AnalysisOptions()
        self.text_analyzer = TextAnalyzer(self.options.language)
        self.attribute_analyzer = AttributeAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        
        logger.info("ReqIF Analyzer initialized with mode: %s", self.options.mode.value)
    
    def analyze_requirements(self, requirements: Dict[str, Requirement], 
                           file_path: str = None) -> AnalysisResult:
        """
        Analyze a set of requirements
        
        Args:
            requirements: Dictionary of requirements to analyze
            file_path: Optional path to the source file
            
        Returns:
            Complete analysis result
        """
        start_time = datetime.now()
        logger.info("Starting requirement analysis (%d requirements)", len(requirements))
        
        result = AnalysisResult(
            file_path=file_path or "Unknown",
            analysis_timestamp=start_time,
            options=self.options,
            requirement_stats=RequirementStatistics(),
            text_stats=TextStatistics(),
            attribute_stats=AttributeStatistics(),
            type_distribution=DistributionAnalysis(),
            status_distribution=DistributionAnalysis(),
            priority_distribution=DistributionAnalysis(),
            quality_metrics=QualityMetrics()
        )
        
        try:
            # Basic requirement statistics
            result.requirement_stats = self._calculate_requirement_stats(requirements)
            
            # Text analysis
            if self.options.include_text_analysis:
                result.text_stats = self._analyze_text_content(requirements)
            
            # Attribute analysis
            if self.options.include_attribute_analysis:
                result.attribute_stats = self._analyze_attributes(requirements)
                
                # Distribution analysis
                result.type_distribution = self._analyze_type_distribution(requirements)
                result.status_distribution = self._analyze_status_distribution(requirements)
                result.priority_distribution = self._analyze_priority_distribution(requirements)
            
            # Quality metrics
            if self.options.include_quality_metrics:
                result.quality_metrics = self._analyze_quality(requirements)
            
            # Custom metrics
            for metric_type in self.options.custom_metrics:
                result.custom_metrics[metric_type.value] = self._calculate_custom_metric(
                    metric_type, requirements
                )
            
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()
            
            logger.info("Analysis completed in %.2f seconds", result.processing_time)
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        
        return result
    
    def _calculate_requirement_stats(self, requirements: Dict[str, Requirement]) -> RequirementStatistics:
        """Calculate basic requirement statistics"""
        stats = RequirementStatistics()
        
        stats.total_count = len(requirements)
        stats.with_text = sum(1 for req in requirements.values() if req.text)
        stats.with_attributes = sum(1 for req in requirements.values() if req.attributes)
        stats.empty_requirements = sum(1 for req in requirements.values() if not req.text.strip())
        
        # Calculate averages
        if requirements:
            total_attrs = sum(len(req.attributes) for req in requirements.values())
            stats.avg_attributes_per_requirement = total_attrs / len(requirements)
            
            text_lengths = [len(req.text) for req in requirements.values() if req.text]
            if text_lengths:
                stats.avg_text_length = statistics.mean(text_lengths)
                stats.min_text_length = min(text_lengths)
                stats.max_text_length = max(text_lengths)
        
        return stats
    
    def _analyze_text_content(self, requirements: Dict[str, Requirement]) -> TextStatistics:
        """Analyze text content across all requirements"""
        stats = TextStatistics()
        
        all_analyses = []
        for req in requirements.values():
            if req.text:
                analysis = self.text_analyzer.analyze_text(req.text)
                all_analyses.append(analysis)
        
        if all_analyses:
            # Aggregate statistics
            stats.total_characters = sum(a['character_count'] for a in all_analyses)
            stats.total_words = sum(a['word_count'] for a in all_analyses)
            stats.total_sentences = sum(a['sentence_count'] for a in all_analyses)
            
            # Average metrics
            stats.avg_words_per_requirement = statistics.mean([a['word_count'] for a in all_analyses])
            stats.avg_sentences_per_requirement = statistics.mean([a['sentence_count'] for a in all_analyses])
            stats.avg_word_length = statistics.mean([a['avg_word_length'] for a in all_analyses])
            stats.avg_readability_score = statistics.mean([a['readability_score'] for a in all_analyses])
            stats.avg_complexity_score = statistics.mean([a['complexity_score'] for a in all_analyses])
            
            # Distribution analysis
            word_counts = [a['word_count'] for a in all_analyses]
            stats.word_count_distribution = self._create_distribution_stats(word_counts)
            
            readability_scores = [a['readability_score'] for a in all_analyses]
            stats.readability_distribution = self._create_distribution_stats(readability_scores)
        
        return stats
    
    def _analyze_attributes(self, requirements: Dict[str, Requirement]) -> AttributeStatistics:
        """Analyze requirement attributes"""
        analysis = self.attribute_analyzer.analyze_attributes(requirements)
        
        stats = AttributeStatistics()
        stats.total_unique_attributes = analysis['total_unique_attributes']
        stats.attribute_completeness = analysis['attribute_completeness']
        stats.attribute_distributions = analysis['attribute_distributions']
        stats.missing_attributes = analysis['missing_attributes']
        stats.most_common_attributes = dict(analysis['most_common_attributes'])
        
        # Calculate completeness metrics
        if analysis['attribute_completeness']:
            completeness_values = list(analysis['attribute_completeness'].values())
            stats.avg_completeness = statistics.mean(completeness_values)
            stats.min_completeness = min(completeness_values)
            stats.max_completeness = max(completeness_values)
        
        return stats
    
    def _analyze_type_distribution(self, requirements: Dict[str, Requirement]) -> DistributionAnalysis:
        """Analyze requirement type distribution"""
        return self._analyze_attribute_distribution(requirements, 'type')
    
    def _analyze_status_distribution(self, requirements: Dict[str, Requirement]) -> DistributionAnalysis:
        """Analyze requirement status distribution"""
        return self._analyze_attribute_distribution(requirements, 'status')
    
    def _analyze_priority_distribution(self, requirements: Dict[str, Requirement]) -> DistributionAnalysis:
        """Analyze requirement priority distribution"""
        return self._analyze_attribute_distribution(requirements, 'priority')
    
    def _analyze_attribute_distribution(self, requirements: Dict[str, Requirement], 
                                      attr_name: str) -> DistributionAnalysis:
        """Analyze distribution of a specific attribute"""
        values = []
        
        for req in requirements.values():
            # Look for attribute with case-insensitive matching
            attr_value = None
            for key, value in req.attributes.items():
                if attr_name.lower() in key.lower():
                    attr_value = value
                    break
            
            if attr_value:
                values.append(str(attr_value))
            else:
                values.append("Unknown")
        
        distribution = DistributionAnalysis()
        if values:
            value_counts = Counter(values)
            distribution.categories = dict(value_counts)
            distribution.total_items = len(values)
            distribution.unique_categories = len(value_counts)
            distribution.most_common = value_counts.most_common(1)[0] if value_counts else ("", 0)
            
            # Calculate percentages
            distribution.percentages = {
                category: (count / len(values)) * 100
                for category, count in value_counts.items()
            }
        
        return distribution
    
    def _analyze_quality(self, requirements: Dict[str, Requirement]) -> QualityMetrics:
        """Analyze quality metrics"""
        analysis = self.quality_analyzer.analyze_quality(requirements)
        
        metrics = QualityMetrics()
        metrics.overall_score = analysis['overall_quality_score']
        metrics.readability_score = analysis['average_readability']
        metrics.completeness_score = analysis['average_completeness']
        metrics.consistency_issues = analysis['consistency_issues']
        metrics.recommendations = analysis['quality_recommendations']
        metrics.quality_distribution = analysis['quality_distribution']
        
        return metrics
    
    def _calculate_custom_metric(self, metric_type: MetricType, 
                               requirements: Dict[str, Requirement]) -> Any:
        """Calculate custom metrics"""
        if metric_type == MetricType.TEXT_COMPLEXITY:
            return self._calculate_text_complexity_metric(requirements)
        elif metric_type == MetricType.ATTRIBUTE_COMPLETENESS:
            return self._calculate_attribute_completeness_metric(requirements)
        elif metric_type == MetricType.REQUIREMENT_DENSITY:
            return self._calculate_requirement_density_metric(requirements)
        elif metric_type == MetricType.READABILITY:
            return self._calculate_readability_metric(requirements)
        elif metric_type == MetricType.CONSISTENCY:
            return self._calculate_consistency_metric(requirements)
        elif metric_type == MetricType.TRACEABILITY:
            return self._calculate_traceability_metric(requirements)
        else:
            return {}
    
    def _calculate_text_complexity_metric(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Calculate detailed text complexity metrics"""
        complexities = []
        for req in requirements.values():
            if req.text:
                analysis = self.text_analyzer.analyze_text(req.text)
                complexities.append(analysis['complexity_score'])
        
        if not complexities:
            return {}
        
        return {
            'average_complexity': statistics.mean(complexities),
            'complexity_stdev': statistics.stdev(complexities) if len(complexities) > 1 else 0,
            'high_complexity_count': sum(1 for c in complexities if c > 70),
            'low_complexity_count': sum(1 for c in complexities if c < 30),
            'complexity_distribution': self._create_distribution_stats(complexities)
        }
    
    def _calculate_attribute_completeness_metric(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Calculate detailed attribute completeness metrics"""
        attribute_counts = [len(req.attributes) for req in requirements.values()]
        
        if not attribute_counts:
            return {}
        
        return {
            'average_attributes': statistics.mean(attribute_counts),
            'median_attributes': statistics.median(attribute_counts),
            'min_attributes': min(attribute_counts),
            'max_attributes': max(attribute_counts),
            'well_attributed_count': sum(1 for c in attribute_counts if c >= 5),
            'poorly_attributed_count': sum(1 for c in attribute_counts if c < 2)
        }
    
    def _calculate_requirement_density_metric(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Calculate requirement density metrics"""
        if not requirements:
            return {}
        
        total_text_length = sum(len(req.text) for req in requirements.values())
        total_requirements = len(requirements)
        
        return {
            'requirements_per_1000_chars': (total_requirements / total_text_length) * 1000 if total_text_length > 0 else 0,
            'average_requirement_length': total_text_length / total_requirements,
            'content_density_score': total_text_length / total_requirements if total_requirements > 0 else 0
        }
    
    def _calculate_readability_metric(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Calculate detailed readability metrics"""
        readability_scores = []
        for req in requirements.values():
            if req.text:
                analysis = self.text_analyzer.analyze_text(req.text)
                readability_scores.append(analysis['readability_score'])
        
        if not readability_scores:
            return {}
        
        return {
            'average_grade_level': statistics.mean(readability_scores),
            'readability_stdev': statistics.stdev(readability_scores) if len(readability_scores) > 1 else 0,
            'easy_to_read_count': sum(1 for r in readability_scores if r <= 8),
            'difficult_to_read_count': sum(1 for r in readability_scores if r >= 16),
            'optimal_readability_count': sum(1 for r in readability_scores if 8 <= r <= 12)
        }
    
    def _calculate_consistency_metric(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Calculate consistency metrics"""
        # Reset seen text hashes for consistency checking
        if hasattr(self.quality_analyzer, '_seen_text_hashes'):
            delattr(self.quality_analyzer, '_seen_text_hashes')
        
        all_issues = []
        for req_id, req in requirements.items():
            issues = self.quality_analyzer._check_consistency(req_id, req)
            all_issues.extend(issues)
        
        issue_types = Counter(issue['type'] for issue in all_issues)
        
        return {
            'total_issues': len(all_issues),
            'issues_by_type': dict(issue_types),
            'consistency_score': max(0, 100 - (len(all_issues) / len(requirements)) * 100) if requirements else 100,
            'most_common_issue': issue_types.most_common(1)[0][0] if issue_types else None
        }
    
    def _calculate_traceability_metric(self, requirements: Dict[str, Requirement]) -> Dict[str, Any]:
        """Calculate traceability metrics"""
        traced_requirements = 0
        traceability_links = 0
        
        for req in requirements.values():
            has_trace = False
            for attr_name, attr_value in req.attributes.items():
                if any(keyword in attr_name.lower() for keyword in ['trace', 'link', 'parent', 'child']):
                    has_trace = True
                    traceability_links += 1
            
            if has_trace:
                traced_requirements += 1
        
        total_reqs = len(requirements)
        
        return {
            'traced_requirements_count': traced_requirements,
            'traceability_percentage': (traced_requirements / total_reqs) * 100 if total_reqs > 0 else 0,
            'total_traceability_links': traceability_links,
            'average_links_per_requirement': traceability_links / total_reqs if total_reqs > 0 else 0,
            'untraced_requirements_count': total_reqs - traced_requirements
        }
    
    def _create_distribution_stats(self, values: List[float]) -> Dict[str, Any]:
        """Create distribution statistics for a list of values"""
        if not values:
            return {}
        
        return {
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'quartiles': [
                statistics.quantiles(values, n=4)[0] if len(values) >= 4 else min(values),
                statistics.median(values),
                statistics.quantiles(values, n=4)[2] if len(values) >= 4 else max(values)
            ]
        }


def analyze_requirements(requirements: Dict[str, Requirement], 
                       options: AnalysisOptions = None) -> AnalysisResult:
    """
    Quick analysis utility function
    
    Args:
        requirements: Dictionary of requirements to analyze
        options: Analysis options
        
    Returns:
        Complete analysis result
    """
    analyzer = ReqIFAnalyzer(options)
    return analyzer.analyze_requirements(requirements)


def calculate_metrics(requirements: Dict[str, Requirement], 
                     metric_types: List[MetricType]) -> Dict[str, Any]:
    """
    Calculate specific metrics
    
    Args:
        requirements: Dictionary of requirements
        metric_types: List of metrics to calculate
        
    Returns:
        Dictionary of calculated metrics
    """
    options = AnalysisOptions(custom_metrics=metric_types)
    analyzer = ReqIFAnalyzer(options)
    result = analyzer.analyze_requirements(requirements)
    return result.custom_metrics


def generate_report(analysis_result: AnalysisResult) -> str:
    """
    Generate a text report from analysis results
    
    Args:
        analysis_result: Analysis result to report on
        
    Returns:
        Formatted text report
    """
    report_lines = [
        "ReqIF Analysis Report",
        "=" * 50,
        f"File: {analysis_result.file_path}",
        f"Analysis Date: {analysis_result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Processing Time: {analysis_result.processing_time:.2f} seconds",
        "",
        "SUMMARY",
        "-" * 20,
        f"Total Requirements: {analysis_result.requirement_stats.total_count}",
        f"Requirements with Text: {analysis_result.requirement_stats.with_text}",
        f"Requirements with Attributes: {analysis_result.requirement_stats.with_attributes}",
        f"Average Text Length: {analysis_result.requirement_stats.avg_text_length:.1f} characters",
        f"Average Attributes per Requirement: {analysis_result.requirement_stats.avg_attributes_per_requirement:.1f}",
        "",
        "QUALITY METRICS",
        "-" * 20,
        f"Overall Quality Score: {analysis_result.quality_metrics.overall_score:.1f}/100",
        f"Average Readability: {analysis_result.quality_metrics.readability_score:.1f}",
        f"Completeness Score: {analysis_result.quality_metrics.completeness_score:.1f}",
        f"Consistency Issues: {len(analysis_result.quality_metrics.consistency_issues)}",
        ""
    ]
    
    # Add recommendations
    if analysis_result.quality_metrics.recommendations:
        report_lines.extend([
            "RECOMMENDATIONS",
            "-" * 20
        ])
        for i, recommendation in enumerate(analysis_result.quality_metrics.recommendations, 1):
            report_lines.append(f"{i}. {recommendation}")
        report_lines.append("")
    
    # Add distribution analysis
    if analysis_result.type_distribution.categories:
        report_lines.extend([
            "TYPE DISTRIBUTION",
            "-" * 20
        ])
        for category, count in analysis_result.type_distribution.categories.items():
            percentage = analysis_result.type_distribution.percentages.get(category, 0)
            report_lines.append(f"{category}: {count} ({percentage:.1f}%)")
        report_lines.append("")
    
    # Add any errors or warnings
    if analysis_result.errors:
        report_lines.extend([
            "ERRORS",
            "-" * 20
        ])
        for error in analysis_result.errors:
            report_lines.append(f"• {error}")
        report_lines.append("")
    
    if analysis_result.warnings:
        report_lines.extend([
            "WARNINGS", 
            "-" * 20
        ])
        for warning in analysis_result.warnings:
            report_lines.append(f"• {warning}")
        report_lines.append("")
    
    return "\n".join(report_lines)


def compare_analysis_results(result1: AnalysisResult, result2: AnalysisResult) -> Dict[str, Any]:
    """
    Compare two analysis results to identify trends and changes
    
    Args:
        result1: First analysis result (typically older)
        result2: Second analysis result (typically newer)
        
    Returns:
        Comparison analysis with trends and changes
    """
    comparison = {
        'summary': {},
        'text_changes': {},
        'quality_changes': {},
        'distribution_changes': {},
        'trends': []
    }
    
    # Summary comparison
    stats1 = result1.requirement_stats
    stats2 = result2.requirement_stats
    
    comparison['summary'] = {
        'requirement_count_change': stats2.total_count - stats1.total_count,
        'avg_text_length_change': stats2.avg_text_length - stats1.avg_text_length,
        'avg_attributes_change': stats2.avg_attributes_per_requirement - stats1.avg_attributes_per_requirement
    }
    
    # Quality comparison
    quality1 = result1.quality_metrics
    quality2 = result2.quality_metrics
    
    comparison['quality_changes'] = {
        'overall_score_change': quality2.overall_score - quality1.overall_score,
        'readability_change': quality2.readability_score - quality1.readability_score,
        'completeness_change': quality2.completeness_score - quality1.completeness_score,
        'consistency_issues_change': len(quality2.consistency_issues) - len(quality1.consistency_issues)
    }
    
    # Generate trend observations
    trends = []
    
    if comparison['summary']['requirement_count_change'] > 0:
        trends.append(f"Requirements increased by {comparison['summary']['requirement_count_change']}")
    elif comparison['summary']['requirement_count_change'] < 0:
        trends.append(f"Requirements decreased by {abs(comparison['summary']['requirement_count_change'])}")
    
    if comparison['quality_changes']['overall_score_change'] > 5:
        trends.append("Overall quality significantly improved")
    elif comparison['quality_changes']['overall_score_change'] < -5:
        trends.append("Overall quality significantly decreased")
    
    if comparison['quality_changes']['consistency_issues_change'] > 0:
        trends.append("More consistency issues detected")
    elif comparison['quality_changes']['consistency_issues_change'] < 0:
        trends.append("Consistency issues reduced")
    
    comparison['trends'] = trends
    
    return comparison


def export_analysis_to_json(analysis_result: AnalysisResult, file_path: str):
    """
    Export analysis result to JSON file
    
    Args:
        analysis_result: Analysis result to export
        file_path: Output JSON file path
    """
    import json
    from dataclasses import asdict
    
    # Convert dataclass to dictionary
    data = asdict(analysis_result)
    
    # Convert datetime to string
    data['analysis_timestamp'] = analysis_result.analysis_timestamp.isoformat()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info("Analysis exported to JSON: %s", file_path)


def import_analysis_from_json(file_path: str) -> AnalysisResult:
    """
    Import analysis result from JSON file
    
    Args:
        file_path: JSON file path to import
        
    Returns:
        Loaded analysis result
    """
    import json
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert timestamp back to datetime
    data['analysis_timestamp'] = datetime.fromisoformat(data['analysis_timestamp'])
    
    # Reconstruct the analysis result
    # Note: This is a simplified reconstruction - in practice, you might want
    # to properly reconstruct all nested dataclasses
    
    logger.info("Analysis imported from JSON: %s", file_path)
    return data  # Return as dict for now, could be enhanced to return proper AnalysisResult