import { apiPost } from './app.js?v=2';
import { initDiagram, highlightPath } from './diagram.js?v=2';

let cyDfa = null;

function getDfaInput() {
    return {
        states: document.getElementById('dfa-states').value,
        alphabet: document.getElementById('dfa-alphabet').value,
        start_state: document.getElementById('dfa-start').value,
        accept_states: document.getElementById('dfa-accept').value,
        transitions: document.getElementById('dfa-transitions').value
    };
}

document.getElementById('btn-draw-dfa').addEventListener('click', async () => {
    const data = getDfaInput();
    const res = await apiPost('/api/dfa/graph', data);
    if (res && res.graph_elements) {
        if (cyDfa) cyDfa.destroy();
        cyDfa = initDiagram('cy-dfa', res.graph_elements, false);
    }
});

document.getElementById('btn-sim-dfa').addEventListener('click', async () => {
    const input_string = document.getElementById('dfa-input-str').value.trim();
    const data = {
        dfa: getDfaInput(),
        input_string: input_string
    };
    
    const res = await apiPost('/api/dfa/simulate', data);
    if (!res) return;
    
    if (cyDfa) cyDfa.destroy();
    cyDfa = initDiagram('cy-dfa', res.graph_elements, false);
    
    // Render trace
    const traceDiv = document.getElementById('dfa-trace');
    const resDiv = document.getElementById('dfa-result');
    
    traceDiv.innerHTML = '';
    resDiv.innerHTML = '';
    
    let html = '';
    for (let i = 0; i < res.steps.length; i++) {
        const step = res.steps[i];
        if (i === res.steps.length - 1) {
            // Last step (result)
            if (res.accepted) {
                resDiv.innerHTML = `<span class="result r-acc">✓ ACCEPT — ${step.description}</span>`;
            } else {
                resDiv.innerHTML = `<span class="result r-rej">✗ REJECT — ${step.description}</span>`;
            }
        } else {
            // Trace
            const isAcc = getDfaInput().accept_states.split(',').map(s=>s.trim()).includes(step.current_state);
            html += `<span class="t-state ${isAcc ? 'acc' : ''}" id="trace-step-${i}">${step.current_state}</span>`;
            if (step.symbol) {
                html += ` <span class="t-sym">─${step.symbol}→</span> `;
            }
        }
    }
    traceDiv.innerHTML = html;
    
    highlightPath(cyDfa, res.steps, 600);
});

// Init on load
setTimeout(() => document.getElementById('btn-draw-dfa').click(), 500);
