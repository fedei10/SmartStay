def node_for_agent(agent: str) -> str:
    if agent == "hotel_booking_agent":
        return "hotel_agent"
    if agent == "insurance_management_agent":
        return "insurance_agent"
    if agent == "general_travel_assistant":
        return "general_agent"
    return "package_agent"
