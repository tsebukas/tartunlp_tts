"""Config flow for TartuNLP Text-to-Speech integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_LANGUAGE

from .const import (
    DOMAIN,
    DEFAULT_LANG,
    DEFAULT_VOICE,
    CONF_VOICE,
    SUPPORTED_VOICES,
)

class TartuNLPTTSOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LANGUAGE,
                        default=self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANG),
                    ): vol.In(["et"]),
                    vol.Required(
                        CONF_VOICE,
                        default=self.config_entry.data.get(CONF_VOICE, DEFAULT_VOICE),
                    ): vol.In(SUPPORTED_VOICES),
                }
            ),
        )