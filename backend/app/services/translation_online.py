"""
Online translation service wrapper.
Uses googletrans (unofficial) when available to provide full-sentence translations.
Falls back to the offline word-dictionary when googletrans is not available or internet is unreachable.
"""
from typing import Dict
import asyncio

try:
    # googletrans is a third-party package; it's optional
    from googletrans import Translator as _GoogleTranslator
    _GOOGLETRANS_AVAILABLE = True
except Exception:
    _GOOGLETRANS_AVAILABLE = False

from app.services.translation_offline import TranslationService as OfflineTranslationService


class OnlineTranslationService:
    def __init__(self):
        self.translator = None
        self.offline = OfflineTranslationService()
        if _GOOGLETRANS_AVAILABLE:
            try:
                self.translator = _GoogleTranslator()
            except Exception:
                self.translator = None

    async def _has_internet(self) -> bool:
        # Simple internet check using asyncio to avoid blocking.
        def check():
            try:
                import urllib.request
                urllib.request.urlopen('https://www.google.com', timeout=2)
                return True
            except Exception:
                return False
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, check)

    async def translate(self, text: str, target_lang: str, source_lang: str = "en") -> str:
        # Prefer online translator if available and internet is reachable
        if self.translator:
            try:
                has_net = await self._has_internet()
                if has_net:
                    loop = asyncio.get_event_loop()
                    def call_translate():
                        # googletrans uses language codes like 'hi', 'te', etc.
                        res = self.translator.translate(text, src=source_lang, dest=target_lang)
                        return res.text
                    return await loop.run_in_executor(None, call_translate)
            except Exception:
                # fall back to offline
                pass

        # Offline fallback
        return await self.offline.translate(text, target_lang, source_lang)

    async def detect_language(self, text: str) -> str:
        # Try online detection first
        if self.translator:
            try:
                loop = asyncio.get_event_loop()
                def call_detect():
                    res = self.translator.detect(text)
                    return res.lang
                return await loop.run_in_executor(None, call_detect)
            except Exception:
                pass
        return await self.offline.detect_language(text)

    def get_supported_languages(self) -> Dict[str, str]:
        return self.offline.get_supported_languages()

    def translate_common_response(self, response_type: str, language: str) -> str:
        return self.offline.translate_common_response(response_type, language)

