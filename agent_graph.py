from __future__ import annotations
from typing import TypedDict, Dict, Any
import json, re
from langgraph.graph import StateGraph, END

# ---- LLM adapter: Ollama via LangChain ----
try:
    from langchain_ollama import ChatOllama
except Exception:
    from langchain_community.chat_models import ChatOllama  


# -------- JSON Helpers --------
def extract_json(text: str) -> Dict[str, Any]:
    """
    Try to extract a single JSON object from model output.
    1) Prefer ```json ... ``` fenced block
    2) Else use the first {...} block
    3) On failure, return {"_raw": "..."} so the pipeline can continue
    """
    fence = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if brace:
            text = brace.group(0)

    try:
        return json.loads(text)
    except Exception:
        return {"_raw": text.strip()}


def json_safe_state(state: dict) -> dict:
    """Remove/replace non-serializable objects like the LLM adapter."""
    out = {}
    for k, v in state.items():
        if k == "llm":
            out[k] = "<<omitted: non-serializable LLM adapter>>"
        else:
            out[k] = v
    return out


# -----------------------------
# Shared AgentState
# -----------------------------
class AgentState(TypedDict):
    title: str
    content: str
    email: str
    strict: bool
    task: str
    llm: Any
    planner_proposal: Dict[str, Any]
    reviewer_feedback: Dict[str, Any]
    turn_count: int


# -----------------------------
# Agent Nodes
# -----------------------------
def planner_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- NODE: Planner ---")
    llm = state["llm"]
    prompt = (
        "You are the PLANNER.\n"
        "Return ONLY valid minified JSON with fields:\n"
        '{"plan":[{"step":1,"action":"string"}],"assumptions":["string"],"risks":["string"],"complete":false}\n\n'
        f"Given title='{state['title']}', content='{state['content']}', task='{state['task']}', "
        f"email='{state['email']}', propose a plan with 3-5 steps."
    )
    result = llm.invoke(prompt).content.strip()
    proposal = extract_json(result)
    return {"planner_proposal": proposal}


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- NODE: Reviewer ---")
    llm = state["llm"]
    force_issue = state["strict"] and state["turn_count"] < 2  #force loop on first turns

    prompt = (
        "You are the REVIEWER.\n"
        "Return ONLY valid minified JSON with fields:\n"
        '{"has_issues":false,"issues":[{"type":"string","message":"string"}],"comments":"string"}\n\n'
        "Evaluate the following proposal for clarity, completeness, and actionability.\n"
        f"planner_proposal:\n{json.dumps(state.get('planner_proposal', {}))}\n\n"
        + ("Force finding at least one concrete issue." if force_issue else "")
    )
    result = llm.invoke(prompt).content.strip()
    feedback = extract_json(result)
    return {"reviewer_feedback": feedback}


# -----------------------------
# Supervisor & Router
# -----------------------------
MAX_TURNS = 6

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    print("\n--- NODE: Supervisor(State Update) ---")
    new_turn = state.get("turn_count", 0) + 1
    print(f"turn_count -> {new_turn}")
    return {"turn_count": new_turn}


def router_logic(state: AgentState) -> str | object:
    """
    Decide the next hop each cycle:
      - No proposal → planner
      - Proposal, not reviewed → reviewer
      - Reviewed with issues → planner (loop)
      - Reviewed without issues → END
      - Guard on MAX_TURNS
    """
    print("\n--- ROUTER: Deciding Next Step ---")

    if state.get("turn_count", 0) >= MAX_TURNS:
        print("Hit MAX_TURNS, ending.")
        return END

    has_proposal = bool(state.get("planner_proposal"))
    feedback = state.get("reviewer_feedback") or {}
    reviewed = "has_issues" in feedback
    has_issues = bool(feedback.get("has_issues"))

    if not has_proposal:
        print("No proposal yet → planner")
        return "planner"

    if has_proposal and not reviewed:
        print("Proposal present, no review yet → reviewer")
        return "reviewer"

    if has_issues:
        print("Reviewer found issues → planner (loop)")
        return "planner"

    print("No issues → END")
    return END


# -----------------------------
# MAIN: assemble graph + run
# -----------------------------
if __name__ == "__main__":
    # 1) LLM (Ollama)
    llm = ChatOllama(model="llama3.1", temperature=0.0)

    # 2) Initial state
    initial_state: AgentState = {
        "title": "Ethical Challenges in Artificial Intelligence",
        "content": "Covers fairness, bias, transparency, and accountability in AI systems, with emphasis on real-world impacts in hiring, healthcare, and criminal justice.",
        "email": "sarvesh.waghmare@sjsu.edu",
        "strict": True,  # set True to force early correction loops for demo
        "task": "Produce a plan and finalize for email delivery.",
        "llm": llm,
        "planner_proposal": {},
        "reviewer_feedback": {},
        "turn_count": 0,
    }

    # 3) Assemble the graph here (in main)
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("planner", planner_node)
    graph.add_node("reviewer", reviewer_node)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        router_logic,
        {
            "planner": "planner",
            "reviewer": "reviewer",
            END: END,
        },
    )
    graph.add_edge("planner", "supervisor")
    graph.add_edge("reviewer", "supervisor")

    app = graph.compile()

    # 4) Run & test here (in main)
    print("\n===== STREAM START =====")
    for event in app.stream(initial_state):
        print(event)
    print("===== STREAM END =====\n")

    final_state = app.invoke(initial_state)

    print("\nFINAL STATE:")
    print(json.dumps(json_safe_state(final_state), indent=2))
