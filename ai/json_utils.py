import json
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("studio.ai.json_utils")


def extract_and_repair_json(raw: str) -> Optional[Dict[str, Any]]:
    """
    Robust multi-strategy JSON parser designed for LLM outputs.
    Handles:
    - Reasoning model tags (<think>...</think>)
    - Markdown code fences (```json ... ```)
    - Unescaped newlines/tabs inside strings (strict=False)
    - Trailing commas before closing brackets ({"a": 1,})
    - Single-line comments (// ...)
    - Truncated responses with stack-based nesting balance
    """
    if not raw or not isinstance(raw, str):
        return None

    # Step 1: Remove reasoning tags (<think>...</think>)
    clean = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Step 2: Strip markdown code fences
    clean = re.sub(r"^```(?:json)?\s*", "", clean, flags=re.MULTILINE)
    clean = re.sub(r"```$", "", clean, flags=re.MULTILINE).strip()

    # Step 3: Locate outermost JSON structure
    first_brace = clean.find("{")
    last_brace = clean.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean = clean[first_brace : last_brace + 1]

    # Attempt 1: Direct parse with non-strict mode (allows literal newlines/control chars inside strings)
    try:
        return json.loads(clean, strict=False)
    except Exception:
        pass

    # Attempt 2: Strip comments and trailing commas
    repaired = clean
    repaired = re.sub(r"//.*$", "", repaired, flags=re.MULTILINE)
    repaired = re.sub(r",\s*([\]}])", r"\1", repaired)

    try:
        return json.loads(repaired, strict=False)
    except Exception:
        pass

    # Attempt 3: Stack-based truncated JSON repair
    try:
        working = repaired

        # Balance quotes: count unescaped quotes
        in_string = False
        escape = False
        stack = []

        for char in working:
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if not in_string:
                if char in ("{", "["):
                    stack.append(char)
                elif char == "}":
                    if stack and stack[-1] == "{":
                        stack.pop()
                elif char == "]":
                    if stack and stack[-1] == "[":
                        stack.pop()

        # If ended inside string, close it
        if in_string:
            working += '"'

        # Strip any trailing comma before closing
        working = re.sub(r",\s*$", "", working.rstrip())

        # Close all remaining open brackets in reverse order (LIFO)
        while stack:
            open_bracket = stack.pop()
            if open_bracket == "{":
                working += "}"
            elif open_bracket == "[":
                working += "]"

        working = re.sub(r",\s*([\]}])", r"\1", working)
        return json.loads(working, strict=False)
    except Exception as e:
        logger.debug(f"JSON repair attempt 3 failed: {e}")

    # Attempt 4: Array-level wrapper fallback
    try:
        first_sq = clean.find("[")
        last_sq = clean.rfind("]")
        if first_sq != -1 and last_sq != -1 and last_sq > first_sq:
            array_str = clean[first_sq : last_sq + 1]
            array_str = re.sub(r",\s*([\]}])", r"\1", array_str)
            parsed_list = json.loads(array_str, strict=False)
            if isinstance(parsed_list, list):
                return {"items": parsed_list, "topics": parsed_list, "scenes": parsed_list}
    except Exception:
        pass

    return None
