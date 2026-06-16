from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from utils.parser import parse_dfa_from_form
from utils.graph_builder import dfa_to_cytoscape
from api.routes.dfa import DFAInput

router = APIRouter(prefix="/api/dfa", tags=["Minimize"])

@router.post("/minimize")
async def minimize_dfa(req: DFAInput):
    dfa, error = parse_dfa_from_form(
        req.states, req.alphabet, req.start_state, req.accept_states, req.transitions
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
        
    min_dfa, state_mapping, merged_groups = dfa.minimize()
    
    return {
        "original": {
            "dfa_data": dfa.to_dict(),
            "graph_elements": dfa_to_cytoscape(dfa)
        },
        "minimized": {
            "dfa_data": min_dfa.to_dict(),
            "graph_elements": dfa_to_cytoscape(min_dfa)
        },
        "state_mapping": state_mapping,
        "merged_groups": [list(g) for g in merged_groups]
    }
