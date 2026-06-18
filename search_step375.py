import json

log_path = "/Users/estefanomacedo/.gemini/antigravity/brain/17c3816f-b3a5-4357-9dbd-74deb4dc5ec3/.system_generated/logs/transcript.jsonl"

with open(log_path, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            step = data.get("step_index")
            if 374 <= step <= 388:
                print(f"--- Step {step} ---")
                thinking = data.get("thinking", "")
                content = data.get("content", "")
                tool_calls = data.get("tool_calls", [])
                if thinking:
                    print(f"Thinking:\n{thinking}\n")
                if content:
                    print(f"Content:\n{content[:2000]}\n")
                if tool_calls:
                    print(f"Tool Calls:\n{json.dumps(tool_calls, indent=2)}\n")
        except Exception as e:
            pass
