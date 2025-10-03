"""
Norwegian dictionary fetcher using ordbokene.no via Go service.
Delegates to the existing Go scraper for Norwegian words.
"""
from typing import Optional
import requests
from .base import BaseFetcher, WordEntry, SenseEntry, MeaningEntry, ExpressionEntry, WordFormEntry


class NorwegianFetcher(BaseFetcher):
    """
    Fetcher for Norwegian language using ordbokene.no dictionary.
    Uses the existing Go service for scraping.
    """
    
    def __init__(self, go_service_url: str = "http://localhost:8080"):
        """
        Initialize Norwegian fetcher.
        
        Args:
            go_service_url: Base URL of the Go scraper service
        """
        super().__init__(language_code="no", source_name="ordbokene.no")
        self.go_service_url = go_service_url
    
    def fetch_word(self, word: str) -> Optional[WordEntry]:
        """
        Fetch Norwegian word data via Go service.
        
        Args:
            word: The word to fetch
            
        Returns:
            WordEntry if successful, None if word not found
        """
        try:
            url = f"{self.go_service_url}/api/scrape"
            params = {"word": word}
            
            self.logger.info(f"Fetching Norwegian word '{word}' from {self.source_name}")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 404:
                self.logger.warning(f"Word '{word}' not found")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            # Convert Go service response to our data model
            return self._parse_response(data, word)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error fetching word '{word}': {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing word '{word}': {e}")
            raise
    
    def _parse_response(self, data: dict, word: str) -> WordEntry:
        """
        Parse Go service response into WordEntry.
        
        Args:
            data: JSON response from Go service
            word: The word being fetched
            
        Returns:
            WordEntry object
        """
        senses = []
        
        for sense_data in data.get("senses", []):
            # Parse meanings
            meanings = []
            for meaning_data in sense_data.get("meanings", []):
                meaning = MeaningEntry(
                    description=meaning_data.get("description", ""),
                    examples=meaning_data.get("examples", [])
                )
                meanings.append(meaning)
            
            # Parse expressions
            expressions = []
            for expr_data in sense_data.get("expressions", []):
                expression = ExpressionEntry(
                    phrase=expr_data.get("phrase", ""),
                    explanation=expr_data.get("explanation", "")
                )
                expressions.append(expression)
            
            # Parse word forms
            word_forms = []
            for form_data in sense_data.get("word_forms", []):
                word_form = WordFormEntry(
                    label=form_data.get("label", ""),
                    forms=form_data.get("forms", []),
                    number=form_data.get("number"),
                    definiteness=form_data.get("definiteness"),
                    gender=form_data.get("gender"),
                    degree=form_data.get("degree"),
                    tense=form_data.get("tense")
                )
                word_forms.append(word_form)
            
            # Create sense entry
            sense = SenseEntry(
                id=sense_data.get("id", ""),
                category=sense_data.get("category", ""),
                meanings=meanings,
                gender=sense_data.get("gender"),
                article=sense_data.get("article"),
                expressions=expressions if expressions else None,
                word_forms=word_forms if word_forms else None
            )
            senses.append(sense)
        
        return WordEntry(
            word=word,
            language="Norwegian",
            senses=senses,
            source=self.source_name
        )
    
    def is_available(self) -> bool:
        """
        Check if Go service is available.
        
        Returns:
            bool: True if service is accessible
        """
        try:
            response = requests.get(f"{self.go_service_url}/api/scrape", timeout=5)
            # Even 400 means service is up (just missing word param)
            return response.status_code in [200, 400]
        except:
            return False
