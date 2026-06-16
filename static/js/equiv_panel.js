import { apiPost } from './app.js?v=2';
import { initDiagram } from './diagram.js?v=2';

let cyEqA = null;
let cyEqB = null;

document.getElementById('btn-check-eq').addEventListener('click', async () => {
    const dfaA = {
        states: document.getElementById('eq-a-states').value,
        alphabet: document.getElementById('eq-a-alphabet').value,
        start_state: document.getElementById('eq-a-start').value,
        accept_states: document.getElementById('eq-a-accept').value,
        transitions: document.getElementById('eq-a-trans').value
    };
    
    const dfaB = {
        states: document.getElementById('eq-b-states').value,
        alphabet: document.getElementById('eq-b-alphabet').value,
        start_state: document.getElementById('eq-b-start').value,
        accept_states: document.getElementById('eq-b-accept').value,
        transitions: document.getElementById('eq-b-trans').value
    };
    
    const res = await apiPost('/api/dfa/equivalence', { dfa_a: dfaA, dfa_b: dfaB });
    if (!res) return;
    
    const resDiv = document.getElementById('eq-result');
    if (res.equivalent) {
        resDiv.innerHTML = `<span class="result r-acc">✓ EQUIVALENT — Kedua DFA menerima bahasa yang persis sama.</span>`;
    } else {
        const ce = res.counterexample === "" ? "ε (string kosong)" : res.counterexample;
        resDiv.innerHTML = `<span class="result r-rej">✗ NOT EQUIVALENT — Counterexample: "${ce}" (Diterima oleh satu DFA tapi ditolak oleh yang lain).</span>`;
    }
    
    if (cyEqA) cyEqA.destroy();
    if (cyEqB) cyEqB.destroy();
    
    cyEqA = initDiagram('cy-eq-a', res.dfa_a_graph.graph_elements, false);
    cyEqB = initDiagram('cy-eq-b', res.dfa_b_graph.graph_elements, false);

});
