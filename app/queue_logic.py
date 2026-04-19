def calculate_queue_depth(events):
    queue_depth = 0
    max_depth = 0

    # Sort events by timestamp to ensure correct state tracking
    sorted_events = sorted(events, key=lambda x: x.timestamp)

    for e in sorted_events:
        if e.zone_id == "BILLING" and e.event_type == "ZONE_ENTER":
            queue_depth += 1
        elif e.zone_id == "BILLING" and e.event_type == "ZONE_EXIT":
            queue_depth -= 1

        # Safety: depth can't be negative
        queue_depth = max(0, queue_depth)
        max_depth = max(max_depth, queue_depth)

    return max_depth
