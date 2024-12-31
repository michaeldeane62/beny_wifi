"""Coordinator."""
import asyncio
from datetime import timedelta
import logging
import socket
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import utcnow

from .communication import build_message, read_message
from .const import CLIENT_MESSAGE, DOMAIN, REQUEST_TYPE
from .conversions import get_hex

_LOGGER = logging.getLogger(__name__)

class BenyWifiUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Beny Wifi update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        ip_address,
        port,
        scan_interval
    ) -> None:
        """Initialize Beny Wifi update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

        self.ip_address = ip_address
        self.port = port

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data asynchronously."""
        return await self._fetch_data()

    async def _fetch_data(self):
        """Send UDP request and fetch data asynchronously."""
        try:
            # Build the request message
            request = build_message(
                CLIENT_MESSAGE.REQUEST_DATA,
                {"request_type": get_hex(REQUEST_TYPE.VALUES.value)}
            ).encode('ascii')

            # Send UDP request asynchronously
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._send_udp_request, request)

            # Decode and parse the response
            response = response.decode('ascii')
            data = read_message(response)

            # Convert timer values to timestamps
            now = utcnow()
            start = now.replace(
                hour=data['timer_start_h'], minute=data['timer_start_min'], second=0, microsecond=0
            )
            end = now.replace(
                hour=data['timer_end_h'], minute=data['timer_end_min'], second=0, microsecond=0
            )

            # Adjust for logic:
            # If start is before current time, move it to the next day
            if start < now:
                start += timedelta(days=1)

            # If end is before current time, move it to the next day
            if end < now:
                end += timedelta(days=1)

            # If end is before start, move end to the next day of start
            if end <= start:
                end += timedelta(days=1)

            data['state'] = data['state'].lower()

            data['power'] = float(data['power']) / 10
            data['timer_start'] = start
            data['timer_end'] = end

            return data  # noqa: TRY300
        except Exception as err:  # noqa: BLE001
            _LOGGER.error(f"Failed to fetch data: {err}")  # noqa: G004
            raise UpdateFailed(f"Error fetching data: {err}")  # noqa: B904

    def _send_udp_request(self, request):
        """Send UDP request synchronously in a separate thread."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)  # 5 seconds timeout
            sock.sendto(request, (self.ip_address, self.port))

            # Receive response
            response, addr = sock.recvfrom(1024)
            sock.close()
            return response  # noqa: TRY300
        except Exception as err:  # noqa: BLE001
            _LOGGER.error(f"UDP request failed: {err}")  # noqa: G004
            raise UpdateFailed(f"Error sending UDP request: {err}")  # noqa: B904
