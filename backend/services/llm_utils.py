"""
Utility helpers for working with LLM responses.
"""

import json
import re
import logging

logger = logging.getLogger(__name__)

# Matches ```json ... ``` or ``` ... ``` blocks (non-greedy, DOTALL)
_FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)


def parse_llm_json(response: str) -> dict:
    """
    Parse JSON from an LLM response, stripping markdown code fences if present.

    Handles all common LLM output styles:
      • Plain JSON
      • ```json\\n{...}\\n```
      • ```\\n{...}\\n```
      • JSON with leading/trailing prose (falls back to fence extraction)

    Raises ValueError with a descriptive message if parsing fails after all
    stripping attempts, so callers can catch it and apply their own fallback.
    """
    text = response.strip()

    # Try the most common case first: fence-wrapped JSON
    fence_match = _FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Last resort: find the first {...} or [...] block in the raw response
    for start_char, end_char in (("{", "}"), ("[", "]")):
        start = response.find(start_char)
        end   = response.rfind(end_char)
        if start != -1 and end > start:
            try:
                return json.loads(response[start : end + 1])
            except json.JSONDecodeError:
                pass

    raise ValueError(
        f"LLM response could not be parsed as JSON after fence stripping.\n"
        f"Response (first 300 chars): {response[:300]!r}"
    )
