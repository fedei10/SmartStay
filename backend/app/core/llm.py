from app.core.agent import create_booking_graph


async def get_agent():
    return create_booking_graph()
