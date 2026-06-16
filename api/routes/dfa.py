from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from utils.graph_builder import dfa_to_cytoscape
from utils.parser import parse_dfa_from_form

router = APIRouter(prefix="/api/dfa", tags=["DFA"])

class DFAInput(BaseModel):
    states: str
    alphabet: str
    start_state: str
    accept_states: str
    transitions: str

class SimulateRequest(BaseModel):
    dfa: DFAInput
    input_string: str

@router.post("/simulate")
async def simulate_dfa(req: SimulateRequest):
    dfa, error = parse_dfa_from_form(
        req.dfa.states,
        req.dfa.alphabet,
        req.dfa.start_state,
        req.dfa.accept_states,
        req.dfa.transitions
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    accepted, steps = dfa.simulate(req.input_string)
    graph_elements = dfa_to_cytoscape(dfa)
    
    return {
        "accepted": accepted,
        "steps": steps,
        "graph_elements": graph_elements
    }

@router.post("/graph")
async def get_dfa_graph(req: DFAInput):
    dfa, error = parse_dfa_from_form(
        req.states,
        req.alphabet,
        req.start_state,
        req.accept_states,
        req.transitions
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    graph_elements = dfa_to_cytoscape(dfa)
    return {"graph_elements": graph_elements}
