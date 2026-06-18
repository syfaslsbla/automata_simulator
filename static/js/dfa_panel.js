import { apiPost } from './app.js?v=2';
import { initDiagram, highlightPath } from './diagram.js?v=2';

let cyDfa = null;

const dfaTransData = {};

function getStates() {
    return document.getElementById('dfa-states').value
        .split(',').map(s => s.trim()).filter(Boolean);
}

function getAlphabet() {
    return document.getElementById('dfa-alphabet').value
        .split(',').map(s => s.trim()).filter(Boolean);
}

function rebuildTransTable() {
    const states  = getStates();
    const alpha   = getAlphabet();
    const container = document.getElementById('dfa-trans-table-container');

    if (!states.length || !alpha.length) {
        container.innerHTML = '<p class="trans-hint">Isi States dan Alphabet terlebih dahulu, tabel akan otomatis muncul.</p>';
        return;
    }
    states.forEach(s => {
        if (!dfaTransData[s]) dfaTransData[s] = {};
        alpha.forEach(a => {
            if (dfaTransData[s][a] === undefined) dfaTransData[s][a] = '';
        });
    });

    let html = '<div class="trans-table-wrap"><table class="trans-table">';

    html += '<thead><tr><th>δ</th>';
    alpha.forEach(a => { html += `<th>${a}</th>`; });
    html += '</tr></thead><tbody>';

    states.forEach(s => {
        html += `<tr><td class="state-cell">${s}</td>`;
        alpha.forEach(a => {
            const val = dfaTransData[s]?.[a] ?? '';
            html += `<td><input
                type="text"
                class="trans-input"
                data-state="${s}"
                data-sym="${a}"
                value="${val}"
                placeholder="—"
                autocomplete="off"
            /></td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;

    container.querySelectorAll('.trans-input').forEach(inp => {
        inp.addEventListener('input', () => {
            const s = inp.dataset.state;
            const a = inp.dataset.sym;
            if (!dfaTransData[s]) dfaTransData[s] = {};
            dfaTransData[s][a] = inp.value.trim();
        });
    });
}

function serializeTransitions() {
    const states = getStates();
    const alpha  = getAlphabet();
    const lines  = [];
    states.forEach(s => {
        alpha.forEach(a => {
            const dest = (dfaTransData[s]?.[a] || '').trim();
            if (dest) lines.push(`${s},${a},${dest}`);
        });
    });
    return lines.join('\n');
}

function getDfaInput() {
    return {
        states:       document.getElementById('dfa-states').value,
        alphabet:     document.getElementById('dfa-alphabet').value,
        start_state:  document.getElementById('dfa-start').value,
        accept_states:document.getElementById('dfa-accept').value,
        transitions:  serializeTransitions()
    };
}

document.getElementById('dfa-states').addEventListener('input', rebuildTransTable);
document.getElementById('dfa-alphabet').addEventListener('input', rebuildTransTable);

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

    const traceDiv = document.getElementById('dfa-trace');
    const resDiv   = document.getElementById('dfa-result');
    traceDiv.innerHTML = '';
    resDiv.innerHTML   = '';

    let html = '';
    for (let i = 1; i < res.steps.length; i++) {
        const step = res.steps[i];
        const acceptList = getDfaInput().accept_states.split(',').map(s => s.trim());
        const isAcc = acceptList.includes(step.current_state);

        html += `<span class="t-state ${isAcc ? 'acc' : ''}" id="trace-step-${i}">${step.current_state}</span>`;
        
        if (i < res.steps.length - 1 && step.symbol) {
            html += ` <span class="t-sym">─${step.symbol}→</span> `;
        }

        if (i === res.steps.length - 1) {
            if (res.accepted) {
                resDiv.innerHTML = `<span class="result r-acc">✓ ACCEPT — State akhir '${step.current_state}' adalah accepting state → DITERIMA</span>`;
            } else {
                resDiv.innerHTML = `<span class="result r-rej">✗ REJECT — State akhir '${step.current_state}' bukan accepting state → DITOLAK</span>`;
            }
        }
    }
    traceDiv.innerHTML = html;

    highlightPath(cyDfa, res.steps, 600);
});

const defaultTransitions = [
    ['q0','a','q1'], ['q0','b','q0'],
    ['q1','a','q1'], ['q1','b','q2'],
    ['q2','a','q2'], ['q2','b','q2']
];
defaultTransitions.forEach(([s, a, d]) => {
    if (!dfaTransData[s]) dfaTransData[s] = {};
    dfaTransData[s][a] = d;
});

rebuildTransTable();
setTimeout(() => document.getElementById('btn-draw-dfa').click(), 500);