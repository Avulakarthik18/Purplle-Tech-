def calculate_abandonment(events, converted_users):
    """
    Users who entered the BILLING zone but did not convert.
    """
    billing_users = set()
    
    for e in events:
        if e.zone_id == "BILLING":
            billing_users.add(e.visitor_id)

    abandoned = billing_users - set(converted_users)

    return len(abandoned)
