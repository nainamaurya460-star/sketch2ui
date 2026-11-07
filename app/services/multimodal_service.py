"""
Phase 2: Hybrid Multimodal Vision-LLM Reasoning Engine
Location: app/services/multimodal_service.py
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

COLOR_MAP = {
    "button": "bg-rose-500",
    "checkbox": "bg-amber-500",
    "heading": "bg-purple-500",
    "image": "bg-emerald-500",
    "image_placeholder": "bg-emerald-500",
    "label": "bg-indigo-500",
    "link": "bg-pink-500",
    "paragraph": "bg-blue-500",
    "radiobutton": "bg-orange-500",
    "select": "bg-teal-500",
    "textbox": "bg-cyan-500",
    "input_field": "bg-cyan-500",
    "card": "bg-amber-500",
    "container": "bg-slate-500",
}

SYSTEM_INSTRUCTION = (
    "You are an expert Frontend Systems Architect. Analyze this hand-drawn UI wireframe.\n"
    "Extract true UI hierarchy: Headings, Text Inputs (with exact labels and placeholders), "
    "Checkboxes, Links, and Primary/Secondary Buttons.\n"
    "Group side-by-side elements (like Checkbox + Forgot Password, or First Name + Last Name) "
    "into horizontal rows.\n"
    "Output strictly valid JSON conforming to the AST Schema. Never guess placeholder dummy buttons."
)

JSON_PROMPT = """Analyze this hand-drawn UI wireframe image and produce a clean, structured UI Abstract Syntax Tree (AST).
You must output ONLY valid, parseable JSON matching the following schema:
{
  "screen_type": "Authentication | Dashboard | Form | Landing Page",
  "theme": "dark_glassmorphic",
  "screen_meta": {
    "title": "Title of the screen",
    "screen_type": "Authentication",
    "theme": "dark_glassmorphic"
  },
  "components": [
    {
      "type": "heading",
      "text": "Heading text",
      "level": 1
    },
    {
      "type": "text_input",
      "label": "Label text (e.g. Email Address, Password, Username)",
      "placeholder": "Placeholder text (e.g. user@example.com, ••••••••)",
      "input_type": "email | password | text | number | tel"
    },
    {
      "type": "row",
      "elements": [
        {
          "type": "checkbox",
          "label": "Remember me",
          "checked": false
        },
        {
          "type": "link",
          "text": "Forgot Password?",
          "href": "#forgot"
        }
      ]
    },
    {
      "type": "button",
      "text": "SIGN IN",
      "variant": "primary"
    }
  ]
}
Do NOT wrap the output in markdown code blocks. Output purely the JSON object."""


class MultimodalVisionService:
    _instance: Optional["MultimodalVisionService"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MultimodalVisionService, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        client: Optional[Any] = None
    ):
        self._explicit_api_key = api_key
        self.model = model or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
        self._client = client
        if self._client is None and self.api_key:
            self._init_client()

    @property
    def api_key(self) -> Optional[str]:
        if self._explicit_api_key:
            return self._explicit_api_key
        return (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("VISION_LLM_API_KEY")
            or os.getenv("MULTIMODAL_API_KEY")
        )

    @api_key.setter
    def api_key(self, value: Optional[str]):
        self._explicit_api_key = value

    def _init_client(self):
        """Initializes Google GenAI client if available."""
        if not self.api_key:
            return
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            logger.info("MultimodalVisionService initialized with Google GenAI client.")
        except Exception as e:
            logger.warning(f"Could not initialize Google GenAI SDK client: {e}. Will use REST HTTP fallback.")
            self._client = None

    def is_available(self) -> bool:
        """Returns True if an API key is configured."""
        return bool(self.api_key and str(self.api_key).strip())

    def _detect_mime_type(self, image_bytes: bytes) -> str:
        """Determines image MIME type from magic headers."""
        if image_bytes.startswith(b"\x89PNG"):
            return "image/png"
        elif image_bytes.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        elif image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:16]:
            return "image/webp"
        return "image/png"

    def analyze_sketch(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Multimodal Vision Analysis:
        Sends hand-drawn sketch to Gemini 2.5 Flash / Claude Vision to parse true UI hierarchy.
        Returns strict AST JSON dict containing 'components' and 'screen_meta'.
        Raises ValueError or RuntimeError on configuration/network failure to trigger graceful fallback.
        """
        # Dynamically refresh API key from environment if changed
        current_key = (
            self.api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("VISION_LLM_API_KEY")
            or os.getenv("MULTIMODAL_API_KEY")
        )
        if not current_key or not str(current_key).strip():
            raise ValueError("No Gemini / Multimodal Vision API key configured in environment.")

        if self._client is None:
            self.api_key = current_key
            self._init_client()

        mime_type = self._detect_mime_type(image_bytes)

        # 1. Primary path: Google GenAI SDK
        if self._client is not None:
            try:
                from google.genai import types
                part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1
                )
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=[part, JSON_PROMPT],
                    config=config
                )
                raw_text = response.text or ""
                return self._parse_and_validate_ast(raw_text)
            except Exception as e:
                logger.warning(f"Google GenAI SDK call failed: {e}. Trying REST API fallback.")

        # 2. Secondary path: Direct Gemini REST HTTP API
        return self._rest_api_call(current_key, image_bytes, mime_type)

    def _rest_api_call(self, api_key: str, image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
        """Direct REST fallback to Google Generative Language API via httpx."""
        import base64
        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": b64_data
                            }
                        },
                        {"text": JSON_PROMPT}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            try:
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as err:
                raise RuntimeError(f"Malformed Gemini response payload: {data}") from err

            return self._parse_and_validate_ast(raw_text)

    def _parse_and_validate_ast(self, raw_text: str) -> Dict[str, Any]:
        """Cleans potential markdown fences and verifies AST schema compliance."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected JSON object AST, got: {type(parsed)}")

        # Ensure required keys exist
        if "components" not in parsed or not isinstance(parsed["components"], list):
            parsed["components"] = []

        if "screen_meta" not in parsed:
            parsed["screen_meta"] = {
                "title": parsed.get("screen_type", "Synthesized Wireframe"),
                "screen_type": parsed.get("screen_type", "Authentication"),
                "theme": parsed.get("theme", "dark_glassmorphic")
            }

        if "screen_type" not in parsed:
            parsed["screen_type"] = parsed["screen_meta"].get("screen_type", "Form")

        if "theme" not in parsed:
            parsed["theme"] = "dark_glassmorphic"

        return parsed

    def ast_to_detected_elements(self, ast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Converts semantic AST components into backend DetectedElement schema contracts
        for response consistency across StudioResultView and ComponentInspector.
        """
        components = ast_data.get("components", [])
        elements: List[Dict[str, Any]] = []

        current_y = 40
        card_x = 40
        card_w = 360

        for comp in components:
            c_type = (comp.get("type") or "textbox").lower()

            # Row cluster with side-by-side elements
            if c_type in ["row", "row_cluster"] or comp.get("elements"):
                children = comp.get("elements", [])
                num_children = max(1, len(children))
                col_w = max(50, (card_w - (num_children - 1) * 16) // num_children)

                for c_idx, child in enumerate(children):
                    child_type = (child.get("type") or "textbox").lower()
                    canonical_name = self._map_canonical_name(child_type)
                    child_x = card_x + c_idx * (col_w + 16)
                    child_h = 35 if child_type in ["checkbox", "link"] else 45

                    el_dict = {
                        "name": canonical_name,
                        "class_name": canonical_name,
                        "conf": "99%",
                        "box": [current_y, child_x, current_y + child_h, child_x + col_w],
                        "x1": child_x,
                        "y1": current_y,
                        "x2": child_x + col_w,
                        "y2": current_y + child_h,
                        "w": col_w,
                        "h": child_h,
                        "color": COLOR_MAP.get(canonical_name.lower(), "bg-cyan-500"),
                        "text": child.get("text") or child.get("label"),
                        "label_above": child.get("label") if child_type in ["text_input", "textbox", "input"] else None,
                        "placeholder": child.get("placeholder") or (child.get("text") if child_type in ["text_input", "textbox", "input"] else None),
                        "type": child.get("input_type") or child.get("type"),
                        "variant": child.get("variant", "primary" if child_type == "button" else None)
                    }
                    elements.append(el_dict)

                current_y += 55

            else:
                canonical_name = self._map_canonical_name(c_type)
                el_h = 40 if c_type in ["heading", "checkbox", "link"] else 50
                el_dict = {
                    "name": canonical_name,
                    "class_name": canonical_name,
                    "conf": "99%",
                    "box": [current_y, card_x, current_y + el_h, card_x + card_w],
                    "x1": card_x,
                    "y1": current_y,
                    "x2": card_x + card_w,
                    "y2": current_y + el_h,
                    "w": card_w,
                    "h": el_h,
                    "color": COLOR_MAP.get(canonical_name.lower(), "bg-cyan-500"),
                    "text": comp.get("text") or comp.get("label"),
                    "label_above": comp.get("label") if c_type in ["text_input", "textbox", "input"] else None,
                    "placeholder": comp.get("placeholder") or (comp.get("text") if c_type in ["text_input", "textbox", "input"] else None),
                    "type": comp.get("input_type") or comp.get("type"),
                    "variant": comp.get("variant", "primary" if c_type == "button" else None)
                }
                elements.append(el_dict)
                current_y += el_h + 16

        return elements

    def _map_canonical_name(self, comp_type: str) -> str:
        """Maps diverse VLM type strings to canonical Sketch2UI component names."""
        ct = comp_type.lower()
        if "head" in ct or "title" in ct:
            return "Heading"
        elif "button" in ct or "btn" in ct or "submit" in ct:
            return "Button"
        elif "check" in ct:
            return "CheckBox"
        elif "link" in ct or "anchor" in ct:
            return "Link"
        elif "radio" in ct:
            return "RadioButton"
        elif "select" in ct or "drop" in ct:
            return "Select"
        elif "img" in ct or "image" in ct or "photo" in ct:
            return "Image"
        elif "desc" in ct or "para" in ct:
            return "Paragraph"
        else:
            return "TextBox"


_GLOBAL_MULTIMODAL_SERVICE = None


def get_multimodal_service() -> MultimodalVisionService:
    """Returns singleton MultimodalVisionService instance."""
    global _GLOBAL_MULTIMODAL_SERVICE
    if _GLOBAL_MULTIMODAL_SERVICE is None:
        _GLOBAL_MULTIMODAL_SERVICE = MultimodalVisionService()
    return _GLOBAL_MULTIMODAL_SERVICE
