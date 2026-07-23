"""Constants for the Juice Booster integration."""

from datetime import timedelta

DOMAIN = "juice_booster"
MANUFACTURER = "JUICE Technology"
DEFAULT_NAME = "JUICE BOOSTER 3 air"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_DEVICE_ID = "device_id"
CONF_USER_ID = "user_id"

TOKEN_URL = "https://sso.jplus-pilot.com/auth/realms/juice/protocol/openid-connect/token"
USER_API = "https://profile.juice-pilot.com/api/v2/users/{user_id}"
DEVICE_API = "https://profile.juice-pilot.com/api/v2/devices/{device_id}"
CHARGING_API = "https://profile.juice-pilot.com/api/v2/charging-view/{device_id}"
CONTROL_API = "https://profile.juice-pilot.com/api/v2/devices/{device_id}/charges/maxSupplyCurrent"
CLIENT_ID = "native-webview"
AVAILABLE_AMPERES = (0, 6, 8, 10, 13, 16)
