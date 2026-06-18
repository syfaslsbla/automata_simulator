import { apiPost } from './app.js?v=2';
import { initDiagram, highlightPath } from './diagram.js?v=2';

let cyNfa = null;
let currentNfa = null;

document.getElementById('btn-convert-regex').addEventListener('click', async () => {
    const regex = document.getElementById('regex-input').value.trim();
    if (!regex) return;
    
    const res = await apiPost('/api/regex/convert', { regex: regex });
    if (!res) return;
    
    currentNfa = res.nfa_data;
    if (cyNfa) cyNfa.destroy();
    cyNfa = initDiagram('cy-nfa', res.graph_elements, true);
    
    // Render table
    const tableDiv = document.getElementById('nfa-table-container');
    let html = '<table><thead><tr>';
    
    if (res.transition_table && res.transition_table.length > 0) {
        // Headers
        res.transition_table[0].forEach(h => {
            html += `<th>${h}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        // Rows
        for (let i = 1; i < res.transition_table.length; i++) {
            html += '<tr>';
            res.transition_table[i].forEach(td => {
                html += `<td>${td}</td>`;
            });
            html += '</tr>';
        }
        html += '</tbody></table>';
    }
    
    tableDiv.innerHTML = html;
});

document.getElementById('btn-sim-nfa').addEventListener('click', async () => {

    const regex = document.getElementById('regex-input').value.trim();
    const inputString = document.getElementById('nfa-input-str').value.trim();

    if (!regex) {
        alert('Convert regex terlebih dahulu');
        return;
    }

    const res = await apiPost('/api/regex/convert', {
        regex: regex,
        input_string: inputString
    });

    if (!res || !res.simulate) return;

    const traceDiv = document.getElementById('nfa-trace');
    const resultDiv = document.getElementById('nfa-result');

    traceDiv.innerHTML = '';
    resultDiv.innerHTML = '';

    const steps = res.simulate.steps;
    const acceptStates = res.nfa_data.accept_states;

    let html = '';

    if (steps.length > 0) {

        const startHasAccept =
            steps[0].current_states.some(s =>
                acceptStates.includes(s)
            );

        html += `
            <span class="t-state ${startHasAccept ? 'acc' : ''}">
                {${steps[0].current_states.join(',')}}
            </span>
        `;

        for (let i = 1; i < steps.length - 1; i++) {

            const step = steps[i];

            const hasAccept =
                step.next_states.some(s =>
                    acceptStates.includes(s)
                );

            html += `
                <span class="t-sym">
                    ─${step.symbol}→
                </span>

                <span class="t-state ${hasAccept ? 'acc' : ''}">
                    {${step.next_states.join(',')}}
                </span>
            `;
        }
    }

    traceDiv.innerHTML = html;

    const finalStep = steps[steps.length - 1];
    const finalStates = finalStep.current_states.join(',');

    if (res.simulate.accepted) {
        resultDiv.innerHTML = `
            <span class="result r-acc">
                ✓ ACCEPT — State akhir {${finalStates}}
                mengandung accepting state → DITERIMA
            </span>
        `;

    } else {
        resultDiv.innerHTML = `
            <span class="result r-rej">
                ✗ REJECT — State akhir {${finalStates}}
                tidak mengandung accepting state → DITOLAK
            </span>
        `;
    }
    highlightPath(cyNfa, steps, 1200);
});
