import json

log_path = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3/.system_generated/logs/transcript.jsonl"

with open(log_path, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            step = data.get("step_index")
            if 795 <= step <= 830:
                print(f"--- Step {step} ---")
                thinking = data.get("thinking", "")
                content = data.get("content", "")
                if thinking:
                    print(f"Thinking:\n{thinking}\n")
                if content:
                    print(f"Content:\n{content[:500]}\n")
        except Exception as e:
            pass
