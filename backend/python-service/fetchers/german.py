"""
German dictionary fetcher using Wiktionary API.
Provides German word definitions and basic grammatical information.

Note: For production use, consider implementing duden.de scraping for more comprehensive data.
This implementation uses Wiktionary as a starting point since it has a public API.
"""
from typing import Optional
import requests
from .base import BaseFetcher, WordEntry, SenseEntry, MeaningEntry


class GermanFetcher(BaseFetcher):
    """
    Fetcher for German language using Wiktionary API.
    
    TODO: Implement duden.de scraping for more comprehensive German dictionary data.
    Duden provides:
    - More detailed definitions
    - Usage examples
    - Etymology
    - Compound word analysis
    - Grammatical tables
    
    For now, uses Wiktionary as it has a public API.
    """
    
    def __init__(self):
        """Initialize German fetcher."""
        super().__init__(language_code="de", source_name="Wiktionary (German)")
        self.api_url = "https://de.wiktionary.org/api/rest_v1/page/definition"
    
    def fetch_word(self, word: str) -> Optional[WordEntry]:
        """
        Fetch German word data from Wiktionary.
        
        Args:
            word: The word to fetch
            
        Returns:
            WordEntry if successful, None if word not found
        """
        try:
            # Wiktionary API endpoint for definitions
            url = f"{self.api_url}/{word}"
            
            self.logger.info(f"Fetching German word '{word}' from {self.source_name}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                self.logger.warning(f"Word '{word}' not found")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            return self._parse_response(data, word)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error fetching word '{word}': {e}")
            # Return basic entry if API fails
            return self._create_fallback_entry(word)
        except Exception as e:
            self.logger.error(f"Error parsing word '{word}': {e}")
            return self._create_fallback_entry(word)
    
    def _parse_response(self, data: dict, word: str) -> WordEntry:
        """
        Parse Wiktionary API response into WordEntry.
        
        Args:
            data: JSON response from Wiktionary API
            word: The word being fetched
            
        Returns:
            WordEntry object
        """
        senses = []
        
        # Wiktionary groups definitions by language
        for lang_key, lang_data in data.items():
            # Only process German entries
            if not isinstance(lang_data, list):
                continue
            
            for sense_idx, sense_data in enumerate(lang_data):
                part_of_speech = sense_data.get("partOfSpeech", "unknown")
                
                # Parse definitions
                meanings = []
                for definition_item in sense_data.get("definitions", []):
                    definition_text = definition_item.get("definition", "")
                    
                    # Clean HTML tags from definition
                    import re
                    definition_text = re.sub(r'<[^>]+>', '', definition_text)
                    
                    # Extract examples if present
                    examples = []
                    if "examples" in definition_item:
                        examples = definition_item["examples"]
                    
                    meaning = MeaningEntry(
                        description=definition_text,
                        examples=examples if examples else None
                    )
                    meanings.append(meaning)
                
                if meanings:
                    sense = SenseEntry(
                        id=f"{sense_idx}_{part_of_speech}",
                        category=part_of_speech,
                        meanings=meanings
                    )
                    senses.append(sense)
        
        if not senses:
            # Fallback if no senses found
            return self._create_fallback_entry(word)
        
        return WordEntry(
            word=word,
            language="German",
            senses=senses,
            source=self.source_name
        )
    
    def _create_fallback_entry(self, word: str) -> WordEntry:
        """
        Create a basic fallback entry when API fails or returns no data.
        
        Args:
            word: The word
            
        Returns:
            Basic WordEntry
        """
        sense = SenseEntry(
            id="fallback",
            category="unknown",
            meanings=[
                MeaningEntry(
                    description=f"Dictionary data for '{word}' could not be retrieved. Please add manually.",
                    examples=None
                )
            ]
        )
        
        return WordEntry(
            word=word,
            language="German",
            senses=[sense],
            source="fallback"
        )
    
    def is_available(self) -> bool:
        """
        Check if Wiktionary API is available.
        
        Returns:
            bool: True if service is accessible
        """
        try:
            # Test with a common word
            response = requests.get(f"{self.api_url}/Haus", timeout=5)
            return response.status_code in [200, 404]
        except:
            return False


# TODO: Implement Duden.de scraper
# class DudenFetcher(BaseFetcher):
#     """
#     Future implementation for duden.de scraping.
#     Will provide more comprehensive German dictionary data.
#     """
#     pass
