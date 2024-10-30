"""Support for TartuNLP Text-to-Speech service."""
from __future__ import annotations

import logging
import aiohttp
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA,
    TextToSpeechEntity,
    Voice,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import CONF_LANGUAGE

from .const import (
    DOMAIN,
    DEFAULT_LANG,
    DEFAULT_VOICE,
    DEFAULT_BASE_URL,
    CONF_VOICE,
    CONF_BASE_URL,
    SUPPORTED_VOICES,
)

_LOGGER = logging.getLogger(__name__)

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc
    if not domain:  # Handle cases where URL might not have protocol
        domain = parsed.path.split('/')[0]
    return domain

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(["et"]),
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): vol.In(SUPPORTED_VOICES),
        vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
    }
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TartuNLP TTS from config entry."""
    language = config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANG)
    voice = config_entry.data.get(CONF_VOICE, DEFAULT_VOICE)
    base_url = config_entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)

    # Get the number of existing entries
    entry_num = len([
        entry for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id != config_entry.entry_id
    ]) + 1

    async_add_entities([TartuNLPTTSEntity(hass, config_entry, language, voice, base_url, entry_num)], True)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up TartuNLP TTS platform from YAML."""
    language = config.get(CONF_LANG, DEFAULT_LANG)
    voice = config.get(CONF_VOICE, DEFAULT_VOICE)
    base_url = config.get(CONF_BASE_URL, DEFAULT_BASE_URL)

    # For YAML-based setup, use yaml suffix
    async_add_entities([TartuNLPTTSEntity(hass, None, language, voice, base_url, "yaml")], True)

class TartuNLPTTSEntity(TextToSpeechEntity):
    """The TartuNLP TTS API provider."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        config_entry: ConfigType | None,
        language: str, 
        voice: str,
        base_url: str,
        entry_num: str | int,
    ) -> None:
        """Initialize TartuNLP TTS provider."""
        self.hass = hass
        self._language = language
        self._voice = voice
        self._base_url = base_url
        
        # Set simple entity_id format
        self.entity_id = f"tts.tartunlp_tts_{entry_num}"
        
        # Set unique_id for internal use
        self._attr_unique_id = f"tartunlp_tts_{entry_num}"
        
        # Set descriptive name for display
        domain = get_domain_from_url(base_url)
        self._attr_name = f"TartuNLP TTS - {voice} ({domain})"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return ["et"]

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._language

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [CONF_VOICE]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return a dict with the default options."""
        return {CONF_VOICE: self._voice}

    @property
    def available_voices(self) -> list[Voice] | None:
        """Return a list of available voices."""
        return [Voice(voice_id=voice, name=voice) for voice in SUPPORTED_VOICES]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> tuple[str, bytes]:
        """Load TTS from TartuNLP."""
        options = options or {}
        voice = options.get(CONF_VOICE, self._voice)

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": message,
                    "speaker": voice
                }

                async with session.post(self._base_url, json=payload) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error %d on API call: %s", 
                            response.status, 
                            await response.text()
                        )
                        return None, None

                    data = await response.read()
                    return "wav", data

        except aiohttp.ClientError as error:
            _LOGGER.error("Error occurred for '%s': %s", message, error)
            return None, None
