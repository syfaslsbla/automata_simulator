export function initDiagram(containerId, elements = [], isNFA = false) {
    const accent = '#f0c040';
    const accentGlow = 'rgba(240,192,64,0.4)';
    
    return window.cytoscape({
        container: document.getElementById(containerId),
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#141414',
                    'border-color': '#2a2a2a',
                    'border-width': 2,
                    'color': '#888',
                    'font-family': 'JetBrains Mono',
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': 45,
                    'height': 45,
                    'font-size': 14
                }
            },
            {
                selector: 'node[accept]',
                style: {
                    'shape': 'double-ellipse',
                    'border-style': 'double',
                    'border-color': accent,
                    'border-width': 6,
                    'color': accent,
                    'text-shadow-blur': 10,
                    'text-shadow-color': accentGlow
                }
            },
            {
                selector: 'node.dummy-start',
                style: {
                    'width': 1,
                    'height': 1,
                    'label': 'start',
                    'text-valign': 'center',
                    'text-halign': 'left',
                    'font-size': 10,
                    'color': '#666',
                    'background-opacity': 0,
                    'border-width': 0
                }
            },
            {
                selector: 'node.active',
                style: {
                    'background-color': accent,
                    'color': '#000',
                    'border-color': '#fff'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#666',
                    'target-arrow-color': '#666',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-family': 'JetBrains Mono',
                    'font-size': 12,
                    'color': '#aaa',
                    'text-background-color': '#0d0d0d',
                    'text-background-opacity': 1,
                    'text-background-padding': 2,
                    'control-point-step-size': 60,
                    'transition-property': 'line-color, target-arrow-color, width',
                    'transition-duration': '0.3s'
                }
            },
            {
                selector: 'edge.start-edge',
                style: {
                    'label': ''
                }
            },
            {
                selector: 'edge.active',
                style: {
                    'line-color': accent,
                    'target-arrow-color': accent,
                    'width': 3,
                    'color': accent
                }
            },
            {
                selector: 'node.error',
                style: {
                    'background-color': '#ff5252',
                    'color': '#fff',
                    'border-color': '#fff',
                    'border-style': 'double',
                    'border-width': 6

                }
            },
            {
                selector: 'edge.error',
                style: {
                    'line-color': '#ff5252',
                    'target-arrow-color': '#ff5252',
                    'width': 4,
                    'color': '#ff5252'
                }
            }
        ],
        layout: {
            name: 'dagre',
            rankDir: 'LR',
            spacingFactor: 1.2
        },
        userZoomingEnabled: true,
        wheelSensitivity: 0.2,
        minZoom: 0.1,
        maxZoom: 3,
        userPanningEnabled: true,
        boxSelectionEnabled: false
    });
}

export function highlightPath(cy, steps, speed = 800) {
    cy.elements().removeClass('active');
    
    let i = 0;
    function nextStep() {
        if (i >= steps.length) return;
        const step = steps[i];
        
        // Remove previous highlights
        cy.elements().removeClass('active');
        
        // Highlight current node(s)
        if (step.current_state) {
            cy.$(`#${step.current_state}`).addClass('active');
        } else if (step.current_states) {
            step.current_states.forEach(s => cy.$(`#${s}`).addClass('active'));
        }
        
        // Highlight edge
        if (step.symbol && step.next_state && step.next_state !== 'DEAD') {
            // Find edge between current and next
            cy.edges().filter(e => e.source().id() === step.current_state && e.target().id() === step.next_state).addClass('active');
        }
        
        i++;
        setTimeout(nextStep, speed);
    }
    
    nextStep();
}

export function highlightParallelPath(cyA, cyB, proofTable, speed = 1500) {
    if (cyA) cyA.elements().removeClass('active error');
    if (cyB) cyB.elements().removeClass('active error');
    
    if (!proofTable || proofTable.length === 0) return;
    const alphabet = Object.keys(proofTable[0].transitions);
    
    let microSteps = [];
    
    proofTable.forEach((row, rowIndex) => {
        const isLastRow = rowIndex === proofTable.length - 1;
        
        microSteps.push({
            type: 'STATE',
            pair: row.pair,
            status: row.status
        });
        
        alphabet.forEach(sym => {
            const dest = row.transitions[sym];
        
            const isTransitionBroken = dest.keterangan === '(F, non)' || dest.keterangan === '(non, F)';
            const useRedColor = isLastRow && row.status === "NON EKUIVALEN" && isTransitionBroken;
            
            microSteps.push({
                type: 'EDGE',
                pair: row.pair,
                sym: sym,
                destPair: dest.pair,
                isBroken: useRedColor
            });
        });
    });
    
    let stepIdx = 0;
    function runMicroStep() {
        if (stepIdx >= microSteps.length) return;
        const current = microSteps[stepIdx];
        
        if (current.type === 'STATE') {
            if (cyA) cyA.elements().removeClass('active error');
            if (cyB) cyB.elements().removeClass('active error');
            
            const stateClass = (current.status === "NON EKUIVALEN") ? 'error' : 'active';
            
            if (cyA && current.pair[0]) cyA.$(`#${current.pair[0]}`).addClass(stateClass);
            if (cyB && current.pair[1]) cyB.$(`#${current.pair[1]}`).addClass(stateClass);
            
        } else if (current.type === 'EDGE') {
            const stateA = current.pair[0];
            const stateB = current.pair[1];
            const nextA = current.destPair[0];
            const nextB = current.destPair[1];
            const edgeClass = current.isBroken ? 'error' : 'active';
            
            if (cyA && nextA && nextA !== 'DEAD') {
                cyA.edges().filter(e => 
                    e.source().id() === stateA && 
                    e.target().id() === nextA && 
                    String(e.data('label')).split(',').map(s => s.trim()).includes(current.sym)
                ).addClass(edgeClass);
            }
            
            if (cyB && nextB && nextB !== 'DEAD') {
                cyB.edges().filter(e => 
                    e.source().id() === stateB &&  
                    e.target().id() === nextB &&  
                    String(e.data('label')).split(',').map(s => s.trim()).includes(current.sym)
                ).addClass(edgeClass);
            }
        }
        
        stepIdx++;
        setTimeout(runMicroStep, speed);
    }
    
    runMicroStep();
}