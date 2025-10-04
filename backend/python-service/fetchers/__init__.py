"""
Dictionary fetchers module.
Provides unified interface for fetching words from multiple dictionary sources.

Supported languages:
- Norwegian (no): ordbokene.no via Go service proxy (no local fetcher)
- English (en): Free Dictionary API
- German (de): Wiktionary API (TODO: upgrade to duden.de)

Usage:
    from fetchers import get_fetcher, is_language_supported
    
    # Get a fetcher for a language
    fetcher = get_fetcher("en")
    if fetcher:
        word_entry = fetcher.fetch_word("hello")
    
    # Check if language is supported
    if is_language_supported("de"):
        print("German is supported")
"""
from .base import (
    BaseFetcher, 
    FetcherRegistry, 
    WordEntry, 
    SenseEntry, 
    MeaningEntry, 
    ExpressionEntry, 
    WordFormEntry,
    fetcher_registry,
    GoServiceProxyFetcher
)
from .english import EnglishFetcher
from .german import GermanFetcher
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Initialize fetchers and register them
def initialize_fetchers():
    """
    Initialize and register all available fetchers.
    Call this once on application startup.
    
    Norwegian is proxied directly to the Go service without a local fetcher class.
    """
    try:
        # Register Norwegian proxy to Go service
        norwegian_proxy = GoServiceProxyFetcher()
        fetcher_registry.register(norwegian_proxy)
        
        # Register English fetcher
        english = EnglishFetcher()
        fetcher_registry.register(english)
        
        # Register German fetcher
        german = GermanFetcher()
        fetcher_registry.register(german)
        
        logger.info(f"Initialized fetchers for languages: {fetcher_registry.get_supported_languages()}")
        
    except Exception as e:
        logger.error(f"Error initializing fetchers: {e}")


# Convenience functions for direct access
def get_fetcher(language_code: str) -> Optional[BaseFetcher]:
    """
    Get a fetcher for a specific language.
    
    Args:
        language_code: ISO language code (e.g., "en", "no", "de")
        
    Returns:
        BaseFetcher instance or None if language not supported
    """
    return fetcher_registry.get_fetcher(language_code)


def is_language_supported(language_code: str) -> bool:
    """
    Check if a language is supported.
    
    Args:
        language_code: ISO language code
        
    Returns:
        bool: True if language has a registered fetcher
    """
    return fetcher_registry.is_language_supported(language_code)


def get_supported_languages() -> List[str]:
    """
    Get list of supported language codes.
    
    Returns:
        List of ISO language codes
    """
    return fetcher_registry.get_supported_languages()


def fetch_word(word: str, language_code: str) -> Optional[WordEntry]:
    """
    Convenience function to fetch a word.
    
    Args:
        word: The word to fetch
        language_code: ISO language code
        
    Returns:
        WordEntry or None if word not found or language not supported
    """
    fetcher = get_fetcher(language_code)
    if not fetcher:
        logger.warning(f"No fetcher available for language: {language_code}")
        return None
    
    return fetcher.fetch_word(word)


# Export all public APIs
__all__ = [
    'BaseFetcher',
    'FetcherRegistry',
    'WordEntry',
    'SenseEntry',
    'MeaningEntry',
    'ExpressionEntry',
    'WordFormEntry',
    'GoServiceProxyFetcher',
    'EnglishFetcher',
    'GermanFetcher',
    'get_fetcher',
    'is_language_supported',
    'get_supported_languages',
    'fetch_word',
    'initialize_fetchers',
    'fetcher_registry'
]
