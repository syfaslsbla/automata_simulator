import { apiPost } from './app.js?v=2';
import { initDiagram } from './diagram.js?v=2';

let cyNfa = null;

document.getElementById('btn-convert-regex').addEventListener('click', async () => {
    const regex = document.getElementById('regex-input').value.trim();
    if (!regex) return;
    
    const res = await apiPost('/api/regex/convert', { regex: regex });
    if (!res) return;
    
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
