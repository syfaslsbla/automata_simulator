import { apiPost } from './app.js?v=2';
import { initDiagram } from './diagram.js?v=2';

let cyMinOrig = null;
let cyMinMin  = null;

const minTransData = {};

function getMinStates() {
    return document.getElementById('min-states').value
        .split(',').map(s => s.trim()).filter(Boolean);
}

function getMinAlphabet() {
    return document.getElementById('min-alphabet').value
        .split(',').map(s => s.trim()).filter(Boolean);
}

function rebuildMinTransTable() {
    const states    = getMinStates();
    const alpha     = getMinAlphabet();
    const container = document.getElementById('min-trans-table-container');

    if (!states.length || !alpha.length) {
        container.innerHTML = '<p class="trans-hint">Isi States dan Alphabet terlebih dahulu, tabel akan otomatis muncul.</p>';
        return;
    }

    // Seed store
    states.forEach(s => {
        if (!minTransData[s]) minTransData[s] = {};
        alpha.forEach(a => {
            if (minTransData[s][a] === undefined) minTransData[s][a] = '';
        });
    });

    // Build table
    let html = '<div class="trans-table-wrap"><table class="trans-table">';
    html += '<thead><tr><th>δ</th>';
    alpha.forEach(a => { html += `<th>${a}</th>`; });
    html += '</tr></thead><tbody>';

    states.forEach(s => {
        html += `<tr><td class="state-cell">${s}</td>`;
        alpha.forEach(a => {
            const val = minTransData[s]?.[a] ?? '';
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
            if (!minTransData[s]) minTransData[s] = {};
            minTransData[s][a] = inp.value.trim();
        });
    });
}

function serializeMinTransitions() {
    const states = getMinStates();
    const alpha  = getMinAlphabet();
    const lines  = [];
    states.forEach(s => {
        alpha.forEach(a => {
            const dest = (minTransData[s]?.[a] || '').trim();
            if (dest) lines.push(`${s},${a},${dest}`);
        });
    });
    return lines.join('\n');
}

document.getElementById('min-states').addEventListener('input', rebuildMinTransTable);
document.getElementById('min-alphabet').addEventListener('input', rebuildMinTransTable);

document.getElementById('btn-minimize').addEventListener('click', async () => {
    const data = {
        states:       document.getElementById('min-states').value,
        alphabet:     document.getElementById('min-alphabet').value,
        start_state:  document.getElementById('min-start').value,
        accept_states:document.getElementById('min-accept').value,
        transitions:  serializeMinTransitions()
    };

    const res = await apiPost('/api/dfa/minimize', data);
    if (!res) return;

    if (cyMinOrig) cyMinOrig.destroy();
    if (cyMinMin)  cyMinMin.destroy();

    cyMinOrig = initDiagram('cy-min-orig', res.original.graph_elements, false);
    cyMinMin  = initDiagram('cy-min-min',  res.minimized.graph_elements, false);

    document.getElementById('min-explanation-card').style.display = 'block';

    const origStates = res.original.dfa_data.states;
    const minStates  = res.minimized.dfa_data.states;
    const origCount  = origStates.length;
    const minCount   = minStates.length;
    const diff       = origCount - minCount;

    const accent   = '#f0c040';
    const textMuted = '#888';
    const textAcc   = '#f0c040';

    let text = `<div style="color:${accent};font-weight:bold;margin-bottom:0.5rem;">HASIL MINIMASI DFA</div>`;
    text += `  <span style="color:${textMuted};">Jumlah state SEBELUM minimasi :</span> <span style="color:#fff;">${origCount}</span>\n`;
    text += `  <span style="color:${textMuted};">Jumlah state SESUDAH minimasi :</span> <span style="color:#fff;">${minCount}</span>\n`;
    text += `  <span style="color:${textMuted};">Pengurangan state             :</span> <span style="color:${textAcc};font-weight:bold;">${diff}</span>\n\n`;

    text += `<div style="color:${accent};margin-top:1rem;margin-bottom:0.5rem;">Grup State yang Digabungkan</div>`;
    const groups = res.merged_groups;
    let groupCounter = 1;
    groups.forEach(g => {
        const mappedTo = res.state_mapping[g[0]];
        if (g.length > 1) {
            text += `  <span style="color:#fff;">Grup ${groupCounter}: {${g.join(', ')}} → ${mappedTo}</span>  <span style="color:${textAcc};font-weight:bold;">← DIGABUNG</span>\n`;
            groupCounter++;
        } else {
            text += `  <span style="color:${textMuted};">State : ${g[0]} → ${mappedTo}</span>\n`;
        }
    });

    text += `\n<div style="color:${accent};margin-top:1rem;margin-bottom:0.5rem;">Mapping State Lama → Baru</div>`;
    origStates.forEach(s => {
        text += `  <span style="color:#fff;">${s.padEnd(8)} → ${res.state_mapping[s]}</span>\n`;
    });

    text += `\n<div style="color:${accent};margin-top:1rem;margin-bottom:0.5rem;">DFA Hasil Minimasi</div>`;
    const minData   = res.minimized.dfa_data;
    const acceptStr = minData.accept_states.length > 0 ? `{${minData.accept_states.join(', ')}}` : `{}`;
    const alphaStr  = minData.alphabet.length  > 0 ? `{${minData.alphabet.join(', ')}}` : `{}`;
    text += `  <span style="color:${textMuted};">State awal       :</span> <span style="color:#fff;">${minData.start_state}</span>\n`;
    text += `  <span style="color:${textMuted};">Accepting state  :</span> <span style="color:${textAcc};font-weight:bold;">${acceptStr}</span>\n`;
    text += `  <span style="color:${textMuted};">Alphabet         :</span> <span style="color:#fff;">${alphaStr}</span>\n\n`;

    text += `  <span style="color:${accent};">Tabel Transisi:</span>\n`;
    const alphabet = minData.alphabet;
    text += `    <span style="color:${textMuted};">State    ${alphabet.map(a => a.padEnd(6)).join('')}</span>\n`;

    minStates.forEach(s => {
        let prefix = "  ";
        if (s === minData.start_state && minData.accept_states.includes(s)) prefix = "→*";
        else if (s === minData.start_state) prefix = "→ ";
        else if (minData.accept_states.includes(s)) prefix = "* ";

        const isAcc   = minData.accept_states.includes(s);
        const rowColor = isAcc ? textAcc : '#fff';

        let row = `    <span style="color:${accent};">${prefix}</span><span style="color:${rowColor};">${s.padEnd(7)}</span>`;
        alphabet.forEach(a => {
            const key  = `${s},${a}`;
            const dest = minData.transitions[key] || "-";
            row += `<span style="color:#fff;">${dest.padEnd(6)}</span>`;
        });
        text += row.trimEnd() + "  \n";
    });

    document.getElementById('min-explanation-text').innerHTML =
        `<pre style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:var(--text);background:#1a1a1a;padding:1.5rem;border-radius:6px;border:1px solid var(--border);overflow-x:auto;margin:0;line-height:1.6;white-space:pre-wrap;">${text}</pre>`;
});

const defaultMinTrans = [
    ['q0','0','q1'], ['q0','1','q2'],
    ['q1','0','q0'], ['q1','1','q3'],
    ['q2','0','q4'], ['q2','1','q5'],
    ['q3','0','q4'], ['q3','1','q5'],
    ['q4','0','q4'], ['q4','1','q5'],
    ['q5','0','q5'], ['q5','1','q5'],
];
defaultMinTrans.forEach(([s, a, d]) => {
    if (!minTransData[s]) minTransData[s] = {};
    minTransData[s][a] = d;
});

rebuildMinTransTable();