from typing import List, Dict, Any

def dfa_to_cytoscape(dfa) -> List[Dict[str, Any]]:
    elements = []
    
    # Add nodes
    for state in dfa.states:
        node_data = {
            "id": state,
            "label": state
        }
        classes = []
        if state == dfa.start_state:
            classes.append("start")
            # Create a dummy node and edge for the start arrow
            dummy_id = f"dummy_start_{state}"
            elements.append({
                "group": "nodes",
                "data": {"id": dummy_id, "label": "start"},
                "classes": "dummy-start"
            })
            elements.append({
                "group": "edges",
                "data": {
                    "id": f"edge_start_{state}",
                    "source": dummy_id,
                    "target": state
                },
                "classes": "start-edge"
            })
            
        if state in dfa.accept_states:
            classes.append("accept")
            node_data["accept"] = True # For selector
            
        node = {
            "group": "nodes",
            "data": node_data,
        }
        if classes:
            node["classes"] = " ".join(classes)
        elements.append(node)
        
    # Add edges. Group by (source, target) to combine labels.
    edge_map = {}
    for (src, sym), dst in dfa.transitions.items():
        key = (src, dst)
        if key not in edge_map:
            edge_map[key] = []
        edge_map[key].append(sym)
        
    for (src, dst), symbols in edge_map.items():
        label = ", ".join(sorted(symbols))
        elements.append({
            "group": "edges",
            "data": {
                "id": f"e_{src}_{dst}_{label}",
                "source": src,
                "target": dst,
                "label": label
            }
        })
        
    return elements

def nfa_to_cytoscape(nfa) -> List[Dict[str, Any]]:
    elements = []
    
    # Add nodes
    for state in nfa.states:
        node_data = {
            "id": state,
            "label": state
        }
        classes = []
        if state == nfa.start_state:
            classes.append("start")
            dummy_id = f"dummy_start_{state}"
            elements.append({
                "group": "nodes",
                "data": {"id": dummy_id, "label": "start"},
                "classes": "dummy-start"
            })
            elements.append({
                "group": "edges",
                "data": {
                    "id": f"edge_start_{state}",
                    "source": dummy_id,
                    "target": state
                },
                "classes": "start-edge"
            })
            
        if state in nfa.accept_states:
            classes.append("accept")
            node_data["accept"] = True
            
        node = {
            "group": "nodes",
            "data": node_data
        }
        if classes:
            node["classes"] = " ".join(classes)
        elements.append(node)
        
    # Add edges
    edge_map = {}
    for (src, sym), dsts in nfa.transitions.items():
        for dst in dsts:
            key = (src, dst)
            if key not in edge_map:
                edge_map[key] = []
            edge_map[key].append(sym)
            
    for (src, dst), symbols in edge_map.items():
        label = ", ".join(sorted(symbols))
        elements.append({
            "group": "edges",
            "data": {
                "id": f"e_{src}_{dst}_{label}",
                "source": src,
                "target": dst,
                "label": label
            }
        })
        
    return elements
