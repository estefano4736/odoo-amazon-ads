import json

log_path = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3/.system_generated/logs/transcript.jsonl"

with open(log_path, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content", "")
            thinking = data.get("thinking", "")
            if "client_id" in content or "client_secret" in content or "client_id" in thinking or "client_secret" in thinking:
                # print first few steps where they appear
                step = data.get("step_index")
                if step < 500: # only look at early steps
                    print(f"Step {step}:")
                    if thinking:
                        print(f"  Thinking: {thinking[:300]}...")
                    if content:
                        print(f"  Content: {content[:300]}")
        except Exception as e:
            pass
