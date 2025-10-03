"""
Fetch routes for dictionary word lookups.
Provides endpoints to fetch words from various dictionary sources.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import fetchers
from db_utils import logger

router = APIRouter(prefix="/fetch")


class FetchWordResponse(BaseModel):
    """Response model for word fetch requests."""
    word: str
    language: str
    source: str
    data: dict


@router.get("/languages")
def get_supported_languages():
    """
    Get list of languages that can be fetched.
    
    Returns:
        dict: List of supported language codes and names
    """
    languages = fetchers.get_supported_languages()
    
    # Map codes to full names
    language_map = {
        "no": "Norwegian",
        "en": "English",
        "de": "German"
    }
    
    return {
        "languages": [
            {"code": code, "name": language_map.get(code, code)}
            for code in languages
        ]
    }


@router.get("/word")
def fetch_word(
    word: str = Query(..., description="The word to fetch"),
    language: str = Query(..., description="Language code (e.g., 'en', 'no', 'de')")
):
    """
    Fetch a word from the appropriate dictionary source.
    
    Args:
        word: The word to look up
        language: ISO language code (e.g., "en", "no", "de")
        
    Returns:
        dict: Word data including definitions, examples, and grammatical information
        
    Raises:
        HTTPException: If language not supported or word not found
    """
    # Check if language is supported
    if not fetchers.is_language_supported(language):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{language}' is not supported. Supported languages: {fetchers.get_supported_languages()}"
        )
    
    try:
        logger.info(f"Fetching word '{word}' for language '{language}'")
        
        # Fetch the word
        word_entry = fetchers.fetch_word(word, language)
        
        if not word_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Word '{word}' not found in {language} dictionary"
            )
        
        # Convert to dict for response
        return {
            "word": word_entry.word,
            "language": word_entry.language,
            "source": word_entry.source,
            "data": word_entry.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching word '{word}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch word: {str(e)}"
        )


@router.get("/check-availability")
def check_fetcher_availability():
    """
    Check availability of all dictionary sources.
    
    Returns:
        dict: Status of each language fetcher
    """
    results = {}
    
    for lang_code in fetchers.get_supported_languages():
        fetcher = fetchers.get_fetcher(lang_code)
        if fetcher:
            try:
                available = fetcher.is_available()
                results[lang_code] = {
                    "available": available,
                    "source": fetcher.get_source_name()
                }
            except Exception as e:
                results[lang_code] = {
                    "available": False,
                    "error": str(e),
                    "source": fetcher.get_source_name()
                }
    
    return {"fetchers": results}


@router.get("/preview")
def preview_word(
    word: str = Query(..., description="The word to preview"),
    language: str = Query(..., description="Language code")
):
    """
    Preview a word without saving it to the database.
    Provides a formatted view of the word data.
    
    Args:
        word: The word to look up
        language: ISO language code
        
    Returns:
        dict: Formatted word data ready for display
    """
    # Check if language is supported
    if not fetchers.is_language_supported(language):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{language}' is not supported"
        )
    
    try:
        word_entry = fetchers.fetch_word(word, language)
        
        if not word_entry:
            raise HTTPException(
                status_code=404,
                detail=f"Word '{word}' not found"
            )
        
        # Format for display
        preview = {
            "word": word_entry.word,
            "language": word_entry.language,
            "source": word_entry.source,
            "senses": []
        }
        
        for sense in word_entry.senses:
            sense_preview = {
                "category": sense.category,
                "meanings": [m.description for m in sense.meanings],
                "example_count": sum(len(m.examples or []) for m in sense.meanings)
            }
            
            if sense.gender:
                sense_preview["gender"] = sense.gender
            if sense.expressions:
                sense_preview["expressions_count"] = len(sense.expressions)
            if sense.word_forms:
                sense_preview["word_forms_count"] = len(sense.word_forms)
            
            preview["senses"].append(sense_preview)
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing word '{word}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview word: {str(e)}"
        )
