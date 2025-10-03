"""
English dictionary fetcher using Free Dictionary API.
Provides word definitions, phonetics, and examples for English words.
"""
from typing import Optional
import requests
from .base import BaseFetcher, WordEntry, SenseEntry, MeaningEntry


class EnglishFetcher(BaseFetcher):
    """
    Fetcher for English language using Free Dictionary API.
    API: https://dictionaryapi.dev/
    """
    
    def __init__(self):
        """Initialize English fetcher."""
        super().__init__(language_code="en", source_name="Free Dictionary API")
        self.api_url = "https://api.dictionaryapi.dev/api/v2/entries/en"
    
    def fetch_word(self, word: str) -> Optional[WordEntry]:
        """
        Fetch English word data from Free Dictionary API.
        
        Args:
            word: The word to fetch
            
        Returns:
            WordEntry if successful, None if word not found
        """
        try:
            url = f"{self.api_url}/{word}"
            
            self.logger.info(f"Fetching English word '{word}' from {self.source_name}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                self.logger.warning(f"Word '{word}' not found")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            # API returns a list of entries (usually one)
            if not data or not isinstance(data, list):
                return None
            
            return self._parse_response(data, word)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error fetching word '{word}': {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing word '{word}': {e}")
            raise
    
    def _parse_response(self, data: list, word: str) -> WordEntry:
        """
        Parse Free Dictionary API response into WordEntry.
        
        Args:
            data: JSON response from API (list of entries)
            word: The word being fetched
            
        Returns:
            WordEntry object
        """
        senses = []
        
        # Process all entries (usually just one)
        for entry_idx, entry in enumerate(data):
            # Each entry can have multiple meanings
            for meaning_data in entry.get("meanings", []):
                part_of_speech = meaning_data.get("partOfSpeech", "unknown")
                
                # Parse definitions
                meanings = []
                for def_idx, definition_data in enumerate(meaning_data.get("definitions", [])):
                    meaning_text = definition_data.get("definition", "")
                    example = definition_data.get("example")
                    
                    examples = [example] if example else []
                    
                    # Add synonyms as additional context
                    synonyms = definition_data.get("synonyms", [])
                    if synonyms:
                        meaning_text += f" (Synonyms: {', '.join(synonyms[:3])})"
                    
                    meaning = MeaningEntry(
                        description=meaning_text,
                        examples=examples if examples else None
                    )
                    meanings.append(meaning)
                
                if meanings:
                    # Create a sense for this part of speech
                    sense_id = f"{entry_idx}_{part_of_speech}"
                    sense = SenseEntry(
                        id=sense_id,
                        category=part_of_speech,
                        meanings=meanings
                    )
                    senses.append(sense)
        
        return WordEntry(
            word=word,
            language="English",
            senses=senses,
            source=self.source_name
        )
    
    def is_available(self) -> bool:
        """
        Check if Free Dictionary API is available.
        
        Returns:
            bool: True if service is accessible
        """
        try:
            # Test with a common word
            response = requests.get(f"{self.api_url}/hello", timeout=5)
            return response.status_code in [200, 404]  # 404 is ok, means service is up
        except:
            return False
