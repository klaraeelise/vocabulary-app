"""
Base fetcher interface for dictionary scraping.
Provides a consistent interface for fetching word data from different sources.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MeaningEntry:
    """A single meaning/definition with optional examples."""
    description: str
    examples: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"description": self.description}
        if self.examples:
            result["examples"] = self.examples
        return result


@dataclass
class ExpressionEntry:
    """Idiom or fixed expression."""
    phrase: str
    explanation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phrase": self.phrase,
            "explanation": self.explanation
        }


@dataclass
class WordFormEntry:
    """Inflection/conjugation data."""
    label: str
    forms: List[str]
    number: Optional[str] = None
    definiteness: Optional[str] = None
    gender: Optional[str] = None
    degree: Optional[str] = None
    tense: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "label": self.label,
            "forms": self.forms
        }
        if self.number:
            result["number"] = self.number
        if self.definiteness:
            result["definiteness"] = self.definiteness
        if self.gender:
            result["gender"] = self.gender
        if self.degree:
            result["degree"] = self.degree
        if self.tense:
            result["tense"] = self.tense
        return result


@dataclass
class SenseEntry:
    """A single dictionary sense (e.g., one meaning of a multi-sense word)."""
    id: str
    category: str  # noun, verb, adjective, etc.
    meanings: List[MeaningEntry]
    gender: Optional[str] = None
    article: Optional[str] = None
    expressions: Optional[List[ExpressionEntry]] = None
    word_forms: Optional[List[WordFormEntry]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "category": self.category,
            "meanings": [m.to_dict() for m in self.meanings]
        }
        if self.gender:
            result["gender"] = self.gender
        if self.article:
            result["article"] = self.article
        if self.expressions:
            result["expressions"] = [e.to_dict() for e in self.expressions]
        if self.word_forms:
            result["word_forms"] = [w.to_dict() for w in self.word_forms]
        return result


@dataclass
class WordEntry:
    """Top-level word container with multiple senses."""
    word: str
    language: str
    senses: List[SenseEntry]
    source: str  # Source dictionary (e.g., "ordbokene.no", "duden.de")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "language": self.language,
            "source": self.source,
            "senses": [s.to_dict() for s in self.senses]
        }


class BaseFetcher(ABC):
    """
    Abstract base class for dictionary fetchers.
    Each language implementation should inherit from this class.
    """
    
    def __init__(self, language_code: str, source_name: str):
        """
        Initialize the fetcher.
        
        Args:
            language_code: ISO language code (e.g., "no", "en", "de")
            source_name: Name of the dictionary source
        """
        self.language_code = language_code
        self.source_name = source_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def fetch_word(self, word: str) -> Optional[WordEntry]:
        """
        Fetch word data from the dictionary source.
        
        Args:
            word: The word to fetch
            
        Returns:
            WordEntry if successful, None if word not found
            
        Raises:
            Exception: If there's a network or parsing error
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the dictionary source is available.
        
        Returns:
            bool: True if the source is accessible, False otherwise
        """
        pass
    
    def get_language_code(self) -> str:
        """Get the language code for this fetcher."""
        return self.language_code
    
    def get_source_name(self) -> str:
        """Get the source name for this fetcher."""
        return self.source_name


class FetcherRegistry:
    """
    Registry for managing dictionary fetchers.
    Provides easy access to fetchers by language code.
    """
    
    def __init__(self):
        self._fetchers: Dict[str, BaseFetcher] = {}
        self.logger = logging.getLogger(f"{__name__}.FetcherRegistry")
    
    def register(self, fetcher: BaseFetcher) -> None:
        """
        Register a fetcher for a language.
        
        Args:
            fetcher: The fetcher instance to register
        """
        language_code = fetcher.get_language_code()
        self._fetchers[language_code] = fetcher
        self.logger.info(f"Registered fetcher for {language_code}: {fetcher.get_source_name()}")
    
    def get_fetcher(self, language_code: str) -> Optional[BaseFetcher]:
        """
        Get a fetcher for a language.
        
        Args:
            language_code: ISO language code
            
        Returns:
            BaseFetcher instance if registered, None otherwise
        """
        return self._fetchers.get(language_code)
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: ISO language code
            
        Returns:
            bool: True if language has a registered fetcher
        """
        return language_code in self._fetchers
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes.
        
        Returns:
            List of ISO language codes
        """
        return list(self._fetchers.keys())


# Global registry instance
fetcher_registry = FetcherRegistry()
