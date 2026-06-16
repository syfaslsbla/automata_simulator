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
                    'border-color': accent,
                    'border-width': 3,
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
                    'control-point-step-size': 60
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
