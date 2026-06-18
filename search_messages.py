import json

log_path = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3/.system_generated/logs/transcript.jsonl"

with open(log_path, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            type_ = data.get("type")
            if type_ == "USER_INPUT":
                step = data.get("step_index")
                content = data.get("content", "")
                created_at = data.get("created_at", "")
                print(f"--- Step {step} [{created_at}] ---")
                print(content)
        except Exception as e:
            pass
