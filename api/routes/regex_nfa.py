from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.nfa import ThompsonConstruction
from utils.graph_builder import nfa_to_cytoscape
from utils.parser import format_nfa_transition_table

router = APIRouter(prefix="/api/regex", tags=["Regex"])

class RegexInput(BaseModel):
    regex: str
    input_string: str = ""

@router.post("/convert")
async def convert_regex(req: RegexInput):
    try:
        builder = ThompsonConstruction()
        nfa = builder.regex_to_nfa(req.regex)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    graph_elements = nfa_to_cytoscape(nfa)
    transition_table = format_nfa_transition_table(nfa)
    
    response = {
        "nfa_data": nfa.to_dict(),
        "graph_elements": graph_elements,
        "transition_table": transition_table,
    }
    
    if req.input_string:
        accepted, steps = nfa.simulate(req.input_string)
        response["simulate"] = {
            "accepted": accepted,
            "steps": steps
        }
        
    return response
