"""Config flow for TartuNLP Text-to-Speech integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LANGUAGE
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    DEFAULT_LANG,
    DEFAULT_VOICE,
    CONF_VOICE,
    SUPPORTED_VOICES,
)

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
            }
            # Update the config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_data
            )
            return self.async_create_entry(title="", data=updated_data)

        current_voice = self.data.get(CONF_VOICE, DEFAULT_VOICE)
        current_language = self.data.get(CONF_LANGUAGE, DEFAULT_LANG)

        schema = {
            vol.Required(
                CONF_LANGUAGE,
                default=current_language
            ): vol.In(["et"]),
            vol.Required(
                CONF_VOICE,
                default=current_voice
            ): vol.In(SUPPORTED_VOICES),
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
            return self.async_create_entry(
                title="Tartu NLP TTS",
                data={
                    CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                    CONF_VOICE: user_input[CONF_VOICE],
                }
            )

        schema = {
            vol.Required(CONF_LANGUAGE, default=DEFAULT_LANG): vol.In(["et"]),
            vol.Required(CONF_VOICE, default=DEFAULT_VOICE): vol.In(SUPPORTED_VOICES),
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    async def async_step_import(self, import_info):
        """Handle import from config file."""
        return await self.async_step_user(import_info)