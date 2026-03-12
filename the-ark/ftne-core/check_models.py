"""Quick model discovery — list available OpenAI models on this API key."""
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path

# Load .env the same way governor.py does
_env = Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
models = client.models.list()

relevant = [
    m.id for m in sorted(models.data, key=lambda x: x.id)
    if any(p in m.id for p in ["gpt-4", "gpt-3.5", "o1", "o3", "o4"])
]

print("Available models:")
for m in relevant:
    print(f"  {m}")
