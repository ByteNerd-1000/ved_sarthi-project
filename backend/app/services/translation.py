"""
Translation service selector.
If an online translation provider is available and the host has internet connectivity,
use the online translation wrapper. Otherwise fall back to the offline dictionary-based
service (`translation_offline.TranslationService`).
"""

from app.services.translation_offline import TranslationService as OfflineTranslationService
try:
	from app.services.translation_online import OnlineTranslationService
	_ONLINE_AVAILABLE = True
except Exception:
	OnlineTranslationService = None
	_ONLINE_AVAILABLE = False

async def _choose_service():
	# Lazy selection to avoid network checks at import time
	if _ONLINE_AVAILABLE:
		svc = OnlineTranslationService()
		# online service will internally check internet and fall back if needed
		return svc
	return OfflineTranslationService()

class TranslationService:
	"""Facade that delegates to online or offline implementation."""
	def __init__(self):
		# Initialize with offline by default; runtime methods will call online if available
		self._impl = None

	async def _ensure_impl(self):
		if self._impl is None:
			self._impl = await _choose_service()

	async def translate(self, text: str, target_lang: str, source_lang: str = "en") -> str:
		await self._ensure_impl()
		return await self._impl.translate(text, target_lang, source_lang)

	async def detect_language(self, text: str) -> str:
		await self._ensure_impl()
		return await self._impl.detect_language(text)

	def get_supported_languages(self):
		# delegates to offline implementation (list of supported codes)
		return OfflineTranslationService().get_supported_languages()

	def translate_common_response(self, response_type: str, language: str) -> str:
		return OfflineTranslationService().translate_common_response(response_type, language)

__all__ = ["TranslationService"]

