import os
from typing import Optional

import requests

AIML_API_KEY = os.getenv("AIML_API_KEY", "")
AIML_BASE_URL = os.getenv("AIML_BASE_URL", "https://api.aimlapi.com")


class AimlClient:
    def __init__(self):
        self.api_key = AIML_API_KEY
        self.base_url = AIML_BASE_URL

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    def ocr_image_to_text(self, image_bytes: bytes) -> Optional[str]:
        if not self.api_key:
            return None

        url = f"{self.base_url}/v1/ocr"
        files = {"file": ("image.png", image_bytes, "image/png")}
        resp = requests.post(url, headers=self._headers(), files=files, timeout=60)

        if resp.status_code != 200:
            return None

        data = resp.json()
        return data.get("text") or data.get("result") or None

    def audio_to_text(self, audio_bytes: bytes) -> Optional[str]:
        if not self.api_key:
            return None

        url = f"{self.base_url}/v1/transcribe"
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        resp = requests.post(url, headers=self._headers(), files=files, timeout=120)

        if resp.status_code != 200:
            return None

        data = resp.json()
        return data.get("text") or data.get("transcript") or None
