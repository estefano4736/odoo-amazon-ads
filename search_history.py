import json

log_path = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3/.system_generated/logs/transcript.jsonl"

with open(log_path, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content", "")
            thinking = data.get("thinking", "")
            if "SUCCESS" in content or "SUCCESS" in thinking or "success" in content or "success" in thinking:
                step = data.get("step_index")
                print(f"Step {step}:")
                if thinking:
                    print(f"  Thinking: {thinking[:200]}...")
                if content:
                    print(f"  Content: {content[:300]}")
        except Exception as e:
            pass
