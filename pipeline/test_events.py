import json

with open("data/dataset/sample_events.jsonl") as f:
    for i, line in enumerate(f):
        event = json.loads(line)
        print(event)
        if i > 2:
            break
