import { apiPost } from './app.js?v=2';
import { initDiagram, highlightParallelPath } from './diagram.js?v=2';

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

    const tableCard = document.getElementById('eq-table-card');
    const tableContainer = document.getElementById('eq-table-container');

    if (res.proof_table && res.proof_table.length > 0) {
        tableCard.style.display = 'block';
        
        const alphabetSymbols = Object.keys(res.proof_table[0].transitions);
        
        let html = `<table class="nfa-table">
                      <thead>
                        <tr>
                          <th>(s, s')</th>`;
                          
        alphabetSymbols.forEach(sym => {
            html += `<th>alfabet '${sym}'</th>`;
        });
        
        html += `         <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>`;
                      
        res.proof_table.forEach(row => {
            html += `<tr>
                       <td>
                       (${row.pair[0]}, ${row.pair[1]})<br>
                       <small style="color: yellow; font-weight: normal;">${row.keterangan}</small>
                       </td>`;
                       
            alphabetSymbols.forEach(sym => {
                const dest = row.transitions[sym];
                html += `<td style="text-align: center;">
                           (${dest.pair[0]}, ${dest.pair[1]})<br>
                           <small style="color: #b0bec5; font-weight: normal;">${dest.keterangan}</small>
                         </td>`;
            });
            
            let statusColor = "#EF4444";
            if (row.status === "PENDING") statusColor = "yellow";
            if (row.status === "EKUIVALEN") statusColor = "lime";
            
            html += `<td style="color: ${statusColor}; font-weight: bold;">${row.status}</td>
                     </tr>`;
        });
        
        html += `</tbody></table>`;
        tableContainer.innerHTML = html;
    } else {
        if (tableCard) tableCard.style.display = 'none';
    }
    
    if (cyEqA) cyEqA.destroy();
    if (cyEqB) cyEqB.destroy();
    
    cyEqA = initDiagram('cy-eq-a', res.dfa_a_graph.graph_elements, false);
    cyEqB = initDiagram('cy-eq-b', res.dfa_b_graph.graph_elements, false);

    if (res.proof_table && res.proof_table.length > 0) {
        highlightParallelPath(cyEqA, cyEqB, res.proof_table, 1500);
    }
});