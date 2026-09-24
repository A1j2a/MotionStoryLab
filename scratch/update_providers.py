import re

providers_path = "/Users/dd-mac-04/Desktop/MotionStoryLab/ai/providers.py"
with open(providers_path, "r") as f:
    lines = f.readlines()

content = "".join(lines)

if "from ai.json_utils import extract_and_repair_json" not in content:
    content = "from ai.json_utils import extract_and_repair_json\n" + content

# In OpenRouterProvider
content = re.sub(
    r"def generate_json\(self, prompt: str, system_prompt: str = \"\", max_tokens: Optional\[int\] = None\) -> Optional\[Dict\[str, Any\]\]:\n.*?return None",
    """def generate_json(self, prompt: str, system_prompt: str = "", max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        raw = self._call_api(prompt, system_prompt, max_tokens=max_tokens)
        if not raw:
            return None
        parsed = extract_and_repair_json(raw)
        if parsed is None:
            self.last_error = f"LLM response could not be parsed into JSON (length: {len(raw)})"
        return parsed""",
    content,
    count=1,
    flags=re.DOTALL
)

with open(providers_path, "w") as f:
    f.write(content)

print("Updated providers.py with extract_and_repair_json successfully")
