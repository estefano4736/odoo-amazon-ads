import json

log_path = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3/.system_generated/logs/transcript.jsonl"

with open(log_path, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content", "")
            thinking = data.get("thinking", "")
            step = data.get("step_index")
            # Look for command output of get_refresh_token.py
            if "get_refresh_token.py" in content or "get_refresh_token.py" in thinking or "Atzr|" in content:
                print(f"--- Step {step} ---")
                if thinking:
                    print(f"Thinking:\n{thinking[:300]}\n")
                if content:
                    print(f"Content:\n{content[:1500]}\n")
        except Exception as e:
            pass
