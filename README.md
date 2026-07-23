# Juice Booster EV Charger for Home Assistant

Unofficial Home Assistant integration for **JUICE BOOSTER 3 air / J+ Pilot**. It communicates with the J+ Pilot cloud API used by the mobile application.

> This project is not affiliated with or endorsed by JUICE Technology AG. The cloud API is undocumented and may change without notice.

## Features

- UI setup through a Home Assistant config flow
- Charge state, power, energy, phase voltage/current/power sensors
- Start/stop charging switch
- Maximum charging current control (the cloud accepts 0, 6, 8, 10, 13 or 16 A)
- Automatic OAuth token refresh and Home Assistant reauthentication
- English and Czech translations
- Redacted diagnostics

## Installation through HACS

1. In HACS, open **Integrations**.
2. Open the menu and choose **Custom repositories**.
3. Add `https://github.com/nettlef/ha-juice-plus-pilot` as category **Integration**.
4. Download **Juice Booster EV Charger**.
5. Restart Home Assistant.
6. Open **Settings → Devices & services → Add integration**, search for **Juice Booster**, and sign in with your J+ Pilot credentials.

## Important testing note

This is a clean rewrite based on the recovered integration and has not yet been verified against every J+ Pilot API response. Install the first release as a beta and report diagnostics with secrets redacted if an entity is missing or has the wrong unit.

## Current control behavior

- Turning the charging switch off sends `0 A`.
- Turning it on sends `10 A`.
- The current slider rounds to the nearest supported value: `0, 6, 8, 10, 13, 16 A`.

## Privacy and security

The integration stores the J+ Pilot username, password, access token and refresh token in the Home Assistant config entry so it can renew authentication. Protect Home Assistant backups and the `.storage` directory. Credentials are never intentionally written to logs or diagnostics.

## License

MIT
