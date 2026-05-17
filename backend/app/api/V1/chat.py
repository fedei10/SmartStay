from fastapi import APIRouter, HTTPException, Request

from app.core.metrics import agent_requests_total
from app.schemas.base import success_response
from app.schemas.chat import ChatRequest


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("")
async def chat(payload: ChatRequest, request: Request):
    try:
        graph = request.app.state.booking_graph
        deps = request.app.state.booking_deps
        thread_id = f"conversation:{payload.conversation_id}"
        result = await graph.ainvoke(
            {
                "user_message": payload.message,
                "messages": [{"role": "user", "content": payload.message}],
            },
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "conversation_id": payload.conversation_id,
                    "deps": deps,
                }
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Agent request failed: {exc}",
        ) from exc

    await deps.conversation_memory.append_interaction(
        payload.conversation_id,
        user_message=payload.message,
        assistant_message=result.get("response"),
        metadata={
            "intent": result.get("intent"),
            "agent": result.get("agent"),
            "next_action": result.get("next_action"),
            "requested_services": result.get("requested_services", []),
            "city_name": result.get("city_name"),
            "country_code": result.get("country_code"),
            "origin": result.get("origin"),
            "destination": result.get("destination"),
            "departure_date": result.get("departure_date"),
            "return_date": result.get("return_date"),
        },
    )
    if agent_requests_total is not None:
        agent_requests_total.labels(
            agent=result.get("agent") or "unknown",
            intent=result.get("intent") or "unknown",
            next_action=result.get("next_action") or "unknown",
        ).inc()

    return success_response(
        message="chat routed",
        data={
            "conversation_id": payload.conversation_id,
            "intent": result.get("intent"),
            "agent": result.get("agent"),
            "message": result.get("response"),
            "next_action": result.get("next_action"),
            "metadata": {
                "hotels": result.get("hotels", [])
                if result.get("next_action") == "show_hotels"
                else [],
                "error_message": result.get("error_message"),
                "mcp_tools": result.get("mcp_tools", []),
                "retrieval_context": result.get("retrieval_context", []),
                "requested_services": result.get("requested_services", []),
                "flight": {
                    "origin": result.get("origin"),
                    "destination": result.get("destination"),
                    "departure_date": result.get("departure_date"),
                    "return_date": result.get("return_date"),
                }
                if result.get("agent") == "flight_booking_agent"
                else None,
            },
        },
    )
