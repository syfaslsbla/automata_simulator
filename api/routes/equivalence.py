from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from utils.parser import parse_dfa_from_form
from utils.graph_builder import dfa_to_cytoscape
from api.routes.dfa import DFAInput

router = APIRouter(prefix="/api/dfa", tags=["Equivalence"])

class EquivalenceRequest(BaseModel):
    dfa_a: DFAInput
    dfa_b: DFAInput

@router.post("/equivalence")
async def check_equivalence(req: EquivalenceRequest):
    dfa_a, error_a = parse_dfa_from_form(
        req.dfa_a.states, req.dfa_a.alphabet, req.dfa_a.start_state, req.dfa_a.accept_states, req.dfa_a.transitions
    )
    if error_a:
        raise HTTPException(status_code=400, detail=f"DFA A: {error_a}")
        
    dfa_b, error_b = parse_dfa_from_form(
        req.dfa_b.states, req.dfa_b.alphabet, req.dfa_b.start_state, req.dfa_b.accept_states, req.dfa_b.transitions
    )
    if error_b:
        raise HTTPException(status_code=400, detail=f"DFA B: {error_b}")
        
    equivalent, counterexample = dfa_a.is_equivalent_to(dfa_b)
    
    return {
        "equivalent": equivalent,
        "counterexample": counterexample,
        "dfa_a_graph": {"graph_elements": dfa_to_cytoscape(dfa_a)},
        "dfa_b_graph": {"graph_elements": dfa_to_cytoscape(dfa_b)}
    }
