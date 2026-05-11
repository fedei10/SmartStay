from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    conversation_id: str = Field(default="default", min_length=1)
    message: str = Field(..., min_length=1)


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

    return {
        "conversation_id": payload.conversation_id,
        "message": result.get("response"),
        "next_action": result.get("next_action"),
        "metadata": {
            "hotels": result.get("hotels", [])
            if result.get("next_action") == "show_hotels"
            else [],
            "error_message": result.get("error_message"),
        },
    }
