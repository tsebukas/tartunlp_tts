"""Config flow for TartuNLP Text-to-Speech integration."""
import voluptuous as vol
from urllib.parse import urlparse

from homeassistant import config_entries
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_LANG,
    DEFAULT_VOICE,
    DEFAULT_BASE_URL,
    CONF_VOICE,
    CONF_BASE_URL,
    SUPPORTED_VOICES,
)

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc
    if not domain:  # Handle cases where URL might not have protocol
        domain = parsed.path.split('/')[0]
    return domain

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for TartuNLP TTS."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)
        self.data = dict(config_entry.data)

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        errors = {}

        if user_input is not None:
            updated_data = {
                CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                CONF_VOICE: user_input[CONF_VOICE],
                CONF_BASE_URL: user_input[CONF_BASE_URL],
            }
            # Update the config entry with new title
            domain = get_domain_from_url(user_input[CONF_BASE_URL])
            title = f"{user_input[CONF_VOICE]} ({domain})"
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_data,
                title=title
            )
            return self.async_create_entry(title="", data=updated_data)

        current_voice = self.data.get(CONF_VOICE, DEFAULT_VOICE)
        current_language = self.data.get(CONF_LANGUAGE, DEFAULT_LANG)
        current_base_url = self.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)

        schema = {
            vol.Required(
                CONF_LANGUAGE,
                default=current_language
            ): vol.In(["et"]),
            vol.Required(
                CONF_VOICE,
                default=current_voice
            ): vol.In(SUPPORTED_VOICES),
            vol.Required(
                CONF_BASE_URL,
                default=current_base_url
            ): str,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

class TartuNLPTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TartuNLP TTS."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            domain = get_domain_from_url(user_input[CONF_BASE_URL])
            title = f"{user_input[CONF_VOICE]} ({domain})"
            return self.async_create_entry(
                title=title,
                data={
                    CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                    CONF_VOICE: user_input[CONF_VOICE],
                    CONF_BASE_URL: user_input[CONF_BASE_URL],
                }
            )

        schema = {
            vol.Required(CONF_LANGUAGE, default=DEFAULT_LANG): vol.In(["et"]),
            vol.Required(CONF_VOICE, default=DEFAULT_VOICE): vol.In(SUPPORTED_VOICES),
            vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    async def async_step_import(self, import_info):
        """Handle import from config file."""
        return await self.async_step_user(import_info)
