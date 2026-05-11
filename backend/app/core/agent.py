from app.agents.booking.dependencies import build_booking_deps
from app.agents.booking.graph import build_booking_graph


def create_booking_graph():
    return build_booking_graph()


def create_booking_deps():
    return build_booking_deps()
