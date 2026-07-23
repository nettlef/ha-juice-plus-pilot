"""Async client for the unofficial J+ Pilot cloud API."""

from __future__ import annotations

import asyncio
import base64
from collections.abc import Mapping
import json
import logging
from typing import Any

import ssl
from pathlib import Path

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(
    Path(__file__).parent / "certs" / "juice_ca.pem"
)

from aiohttp import ClientError, ClientResponse, ClientSession

from .const import (
    CHARGING_API,
    CLIENT_ID,
    CONTROL_API,
    DEVICE_API,
    TOKEN_URL,
    USER_API,
)

_LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT = 20


class JuiceBoosterApiError(Exception):
    """Base API error."""


class JuiceBoosterAuthError(JuiceBoosterApiError):
    """Authentication failed."""


class JuiceBoosterConnectionError(JuiceBoosterApiError):
    """Communication with the cloud failed."""


class JuiceBoosterApi:
    """J+ Pilot API wrapper."""

    def __init__(
        self,
        session: ClientSession,
        *,
        username: str,
        password: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        self._session = session
        self.username = username
        self.password = password
        self.access_token = access_token
        self.refresh_token = refresh_token

    @staticmethod
    def user_id_from_token(token: str) -> str:
        """Read the subject from a JWT without verifying its signature."""
        try:
            payload_part = token.split(".")[1]
            payload_part += "=" * (-len(payload_part) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_part))
            return str(payload["sub"])
        except (IndexError, KeyError, ValueError, TypeError, json.JSONDecodeError) as err:
            raise JuiceBoosterAuthError("Invalid access token") from err

    async def async_login(self) -> Mapping[str, Any]:
        """Authenticate using the same password grant as the mobile app."""
        tokens = await self._async_token_request(
            {
                "grant_type": "password",
                "client_id": CLIENT_ID,
                "username": self.username,
                "password": self.password,
            }
        )
        self._set_tokens(tokens)
        return tokens

    async def async_refresh_tokens(self) -> Mapping[str, Any]:
        """Refresh the OAuth tokens."""
        if not self.refresh_token:
            return await self.async_login()
        try:
            tokens = await self._async_token_request(
                {
                    "grant_type": "refresh_token",
                    "client_id": CLIENT_ID,
                    "refresh_token": self.refresh_token,
                }
            )
        except JuiceBoosterAuthError:
            tokens = await self.async_login()
        self._set_tokens(tokens)
        return tokens

    async def _async_token_request(self, data: dict[str, str]) -> Mapping[str, Any]:
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.post(TOKEN_URL, data=data)
                payload = await self._json_response(response)
        except (TimeoutError, ClientError) as err:
            raise JuiceBoosterConnectionError("Unable to reach authentication service") from err
        if response.status in (400, 401, 403):
            raise JuiceBoosterAuthError(str(payload.get("error_description", "Authentication failed")))
        if response.status >= 400:
            raise JuiceBoosterConnectionError(f"Authentication service returned HTTP {response.status}")
        if "access_token" not in payload:
            raise JuiceBoosterAuthError("Authentication response did not contain an access token")
        return payload

    def _set_tokens(self, tokens: Mapping[str, Any]) -> None:
        self.access_token = str(tokens["access_token"])
        if tokens.get("refresh_token"):
            self.refresh_token = str(tokens["refresh_token"])

    async def async_get_user(self, user_id: str) -> dict[str, Any]:
        return await self._async_request("GET", USER_API.format(user_id=user_id))

    async def async_get_device(self, device_id: str) -> dict[str, Any]:
        return await self._async_request("GET", DEVICE_API.format(device_id=device_id))

    async def async_get_charging(self, device_id: str) -> dict[str, Any]:
        return await self._async_request("GET", CHARGING_API.format(device_id=device_id))

    async def async_set_current(self, device_id: str, amperes: int) -> None:
        await self._async_request(
            "PUT",
            CONTROL_API.format(device_id=device_id),
            json_data={"amperes": amperes},
        )

    async def _async_request(
        self,
        method: str,
        url: str,
        *,
        json_data: dict[str, Any] | None = None,
        retry_auth: bool = True,
    ) -> dict[str, Any]:
        if not self.access_token:
            await self.async_login()
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.request(
                    method,
                    url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=json_data,
                    ssl=ssl_context,
                )
                if response.status == 401 and retry_auth:
                    await response.read()
                    await self.async_refresh_tokens()
                    return await self._async_request(
                        method, url, json_data=json_data, retry_auth=False
                    )
                payload = await self._json_response(response)
        except JuiceBoosterAuthError:
            raise
        except (TimeoutError, ClientError) as err:
            raise JuiceBoosterConnectionError("Unable to reach J+ Pilot cloud") from err
        if response.status in (401, 403):
            raise JuiceBoosterAuthError("J+ Pilot rejected the credentials")
        if response.status >= 400:
            raise JuiceBoosterApiError(f"J+ Pilot returned HTTP {response.status}: {payload}")
        return dict(payload) if isinstance(payload, Mapping) else {}

    @staticmethod
    async def _json_response(response: ClientResponse) -> Any:
        if response.status == 204:
            return {}
        try:
            return await response.json(content_type=None)
        except (json.JSONDecodeError, ValueError):
            text = await response.text()
            return {"response": text[:500]}
