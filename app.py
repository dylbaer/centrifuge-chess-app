import streamlit as st
import json
import os

LEADERBOARD_FILE = "centrifuge_leaderboard.json"

st.set_page_config(
    page_title="Centrifuge Chess: Overclocked",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- BACKEND LEADERBOARD SYNCHRONIZATION ---
def load_scores():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return sorted(json.load(f), key=lambda x: x['score'], reverse=True)[:5]
        except:
            return []
    return []

# Handle new score submissions from the game engine
if "submit_score" in st.query_params:
    name = st.query_params.get("name", "ANON")
    score = int(st.query_params.get("score", 0))
    scores = load_scores()
    scores.append({"name": name[:3].upper(), "score": score})
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(scores, f)
    st.query_params.clear()
    st.rerun()

# --- HIGH-TECH UI WRAPPER ---
st.markdown("""
    <style>
    body { background-color: #05070a; color: #e2e8f0; font-family: 'Courier New', monospace; }
    .title-container { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #1e293b; padding-bottom: 10px; }
    .glitch-title { font-size: 2.5rem; font-weight: 900; color: #00ffcc; text-shadow: 0 0 10px rgba(0,255,220,0.5); }
    .leaderboard-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
    .lb-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1e293b; font-size: 1.1rem; }
    .lb-rank { color: #ff3366; font-weight: bold; }
    .lb-name { color: #fff; }
    .lb-score { color: #00ffcc; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-container">
    <span class="glitch-title">☢️ CENTRIFUGE CHESS: OVERCLOCK)</span>
    <p style="color: #64748b; margin-top: 5px;">Maintain angular velocity. Manipulate torque. Do not rupture the core.</p>
</div>
""", unsafe_allow_html=True)

col_game, col_sidebar = st.columns([2, 1])

with col_sidebar:
    st.markdown("<div class='leaderboard-card'>", unsafe_allow_html=True)
    st.subheader("🏆 ARCHIVED TOP OPERATORS")
    top_scores = load_scores()
    if top_scores:
        for idx, entry in enumerate(top_scores):
            st.markdown(f"""
            <div class='lb-row'>
                <span><span class='lb-rank'>#{idx+1}</span> <span class='lb-name'>{entry['name']}</span></span>
                <span class='lb-score'>{entry['score']} Cycles</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No telemetry recorded. Set the laboratory baseline.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔬 PROTOCOL MANUAL (HOW TO PLAY)"):
        st.markdown("""
        * **Objective:** Balance the 24-hole structural rotor array. 
        * **Controls:** Click a test tube to extract it. Click an empty node to secure it.
        * **Vector Mechanics:** Every move modifies the center of mass. Keep the glowing reticle out of the outer **Red Boundary**.
        * **Symmetry Victory:** Bring the center of mass to absolute zero ($0.00$) to secure instant containment success.
        * **Checkmate:** Force your opponent into a configuration where every single move they can make causes a catastrophic rupture.
        """)

# --- EMULATION SIMULATOR ENGINE (HTML5/JS Canvas/CSS3) ---
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #05070a; color: #fff; font-family: system-ui, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
        #canvas-container { position: relative; width: 600px; height: 600px; display: flex; justify-content: center; align-items: center; }
        
        /* THE CENTRIFUGE STRUCTURE */
        .centrifuge-body { position: absolute; width: 560px; height: 560px; border-radius: 50%; background: radial-gradient(circle, #1a202c 40%, #0f1319 70%, #2d3748 100%); border: 8px solid #4a5568; box-shadow: 0 0 40px rgba(0,0,0,0.8), inset 0 0 30px rgba(0,0,0,0.9); display: flex; justify-content: center; align-items: center; transition: transform 0.1s; }
        .rotor-plate { position: absolute; width: 440px; height: 440px; border-radius: 50%; background: radial-gradient(circle, #11141a 50%, #1a202c 100%); border: 4px solid #2d3748; box-shadow: inset 0 0 20px #000; }
        
        /* HEAVY HYDRAULIC MECHANICAL LID */
        .centrifuge-lid { position: absolute; width: 576px; height: 576px; border-radius: 50%; background: radial-gradient(circle, #4a5568 20%, #2d3748 60%, #1a202c 100%); border: 4px solid #718096; box-shadow: 0 10px 30px rgba(0,0,0,0.8); z-index: 10; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: all 1.2s cubic-bezier(0.77, 0, 0.175, 1); }
        .lid-glass { width: 180px; height: 180px; border-radius: 50%; background: rgba(0, 255, 200, 0.05); border: 6px solid #1a202c; box-shadow: inset 0 0 20px rgba(0,255,220,0.2); display: flex; justify-content: center; align-items: center; color: #00ffcc; font-weight: bold; letter-spacing: 2px; text-shadow: 0 0 8px #00ffcc; }
        .start-btn { margin-top: 30px; padding: 12px 32px; background: #ff3366; border: none; border-radius: 6px; color: white; font-weight: bold; cursor: pointer; font-size: 1.1rem; box-shadow: 0 0 15px rgba(255,51,102,0.4); transition: 0.2s; }
        .start-btn:hover { background: #ff5588; transform: scale(1.05); }
        
        /* OPEN STATE ANIMATION */
        .lid-open { transform: translateY(-700px) scale(0.9); opacity: 0; pointer-events: none; }
        
        /* PHYSICAL SLOTS AND GLASS TUBES */
        .slot { position: absolute; width: 34px; height: 34px; border-radius: 50%; background: #090d13; border: 2px solid #2d3748; transform: translate(-50%, -50%); cursor: pointer; display: flex; justify-content: center; align-items: center; box-shadow: inset 0 2px 5px rgba(0,0,0,0.8); transition: 0.2s; }
        .slot:hover { border-color: #718096; background: #151b26; }
        .slot-lbl { position: absolute; color: #4a5568; font-size: 9px; font-family: monospace; font-weight: bold; pointer-events: none; }
        
        /* DETAILED TEST TUBE GRAPHICS */
        .test-tube { position: absolute; width: 20px; height: 34px; border-radius: 4px 4px 10px 10px; background: linear-gradient(90deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0) 30%, rgba(0,0,0,0.4) 100%); border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 4px 8px rgba(0,0,0,0.5); pointer-events: none; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; overflow: hidden; transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
        .tube-cap { position: absolute; top: 0; width: 100%; height: 8px; border-radius: 3px 3px 0 0; }
        .tube-liquid { width: 100%; height: 70%; border-radius: 0 0 8px 8px; }
        
        /* PLAYER COLOUR GRADIENTS */
        .p1-gradient { background: linear-gradient(180deg, #ff3366 #cc0044); box-shadow: 0 0 12px rgba(255,51,102,0.6); }
        .p1-cap { background: #ff88a8; border-bottom: 1px solid #cc0044; }
        .p2-gradient { background: linear-gradient(180deg, #00ccff, #0066cc); box-shadow: 0 0 12px rgba(0,204,255,0.6); }
        .p2-cap { background: #88e5ff; border-bottom: 1px solid #0066cc; }
        
        /* TACTILE STATES */
        .slot.selected { border-color: #00ffcc !important; box-shadow: 0 0 15px #00ffcc; }
        .slot.selected .test-tube { transform: scale(1.3) translateY(-5px); z-index: 5; }
        
        /* HUD INTERFACE LAYER */
        .hud-shroud { position: absolute; top: -50px; width: 100%; display: flex; justify-content: space-between; font-family: monospace; font-size: 13px; color: #a0aec0; }
        .hud-metric { background: #0f172a; padding: 6px 12px; border-radius: 4px; border: 1px solid #1e293b; }
        
        /* VECHTOR TARGET RETICLE */
        .center-axis { position: absolute; width: 100px; height: 100px; border: 1px dashed rgba(255,255,255,0.15); border-radius: 50%; pointer-events: none; }
        .danger-ring { position: absolute; width: 80px; height: 80px; border: 2px dashed rgba(255, 51, 102, 0.3); border-radius: 50%; pointer-events: none; }
        .vector-dot { position: absolute; width: 10px; height: 10px; background: #00ffcc; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px #00ffcc; transform: translate(-50%, -50%); transition: all 0.4s ease-out; }
        
        /* HUD SYSTEM MODALS */
        .screen-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(5,7,10,0.9); z-index: 20; display: flex; flex-direction: column; justify-content: center; align-items: center; border-radius: 12px; display: none; }
        .modal-title { font-size: 2rem; font-weight: bold; color: #ff3366; margin-bottom: 15px; text-shadow: 0 0 10px rgba(255,51,102,0.5); }
        .score-input { background: #1a202c; border: 2px solid #2d3748; color: #fff; padding: 10px; font-size: 1.2rem; border-radius: 6px; width: 120px; text-align: center; text-transform: uppercase; margin-bottom: 15px; }
    </style>
</head>
<body>

<div id="canvas-container">
    <div class="hud-shroud">
        <div class="hud-metric" id="turn-display">SYSTEM STATUS: LOADING...</div>
        <div class="hud-metric" id="weight-display">IMBALANCE: 0.00 / 2.00</div>
    </div>

    <div class="centrifuge-body" id="chassis">
        <div class="rotor-plate" id="rotor"></div>
        
        <div class="center-axis"></div>
        <div class="danger-ring"></div>
        <div id="reticle" class="vector-dot" style="left: 50%; top: 50%;"></div>
    </div>

    <div class="centrifuge-lid" id="lid">
        <div class="lid-glass">CORE SEALED</div>
        <button class="start-btn" onclick="openCentrifuge()">INITIALIZE LAUNCH</button>
    </div>

    <div class="screen-overlay" id="end-screen">
        <div class="modal-title" id="end-title">SYSTEM FAILURE</div>
        <p id="end-subtitle" style="color: #a0aec0; margin-bottom: 25px;">Core integrity ruptured.</p>
        <div id="score-section" style="display:none; text-align:center;">
             <input type="text" id="initials" class="score-input" placeholder="XYZ" maxlength="3">
             <br>
             <button class="start-btn" style="margin-top:5px;" onclick="commitScoreData()">ARCHIVE TELEMETRY</button>
        </div>
        <button class="start-btn" id="restart-btn" style="background:#4a5568; box-shadow:none; display:none;" onclick="location.reload()">RECALIBRATE CORE</button>
    </div>
</div>

<script>
    const HOLES = 24;
    const MAX_IMBALANCE = 2.0;
    const RADIUS = 185; // Rotor placement radius
    
    let board = {};
    let selectedSlot = null;
    let currentTurn = 1; 
    let gameMode = "1v1";
    let gameActive = true;
    let survivalMoves = 0;

    // Detect initialization parameters from Streamlit environment
    const parentParams = new URLSearchParams(window.parent.location.search);
    gameMode = window.parent.document.querySelector("input[name='Select Operational Protocol:']:checked")?.value.includes("AI") ? "AI" : "1v1";

    // Initialize physical rotor configuration grid mapping
    const rotor = document.getElementById('rotor');
    for (let i = 0; i < HOLES; i++) {
        const angle = (i * (360 / HOLES)) * (Math.PI / 180);
        const x = 220 + RADIUS * Math.cos(angle);
        const y = 220 + RADIUS * Math.sin(angle);
        
        const slot = document.createElement('div');
        slot.className = 'slot';
        slot.style.left = `${x}px`;
        slot.style.top = `${y}px`;
        slot.setAttribute('data-index', i);
        slot.onclick = () => handleSlotClick(i);
        
        const label = document.createElement('div');
        label.className = 'slot-lbl';
        label.innerText = i;
        label.style.left = `${220 + (RADIUS + 24) * Math.cos(angle)}px`;
        label.style.top = `${220 + (RADIUS + 24) * Math.sin(angle)}px`;
        
        rotor.appendChild(slot);
        document.getElementById('chassis').appendChild(label);
        board[i] = 0;
    }

    // High Symmetry baseline loading array profiles
    const p1Starting = [0, 4, 8, 12, 16, 20];
    const p2Starting = [2, 6, 10, 14, 18, 22];

    p1Starting.forEach(pos => board[pos] = 1);
    p2Starting.forEach(pos => board[pos] = 2);

    function updateRotorVisuals() {
        document.querySelectorAll('.slot').forEach(slot => {
            const idx = slot.getAttribute('data-index');
            slot.innerHTML = '';
            if (board[idx] !== 0) {
                const tube = document.createElement('div');
                tube.className = 'test-tube';
                
                const cap = document.createElement('div');
                cap.className = `tube-cap ${board[idx] === 1 ? 'p1-cap' : 'p2-cap'}`;
                
                const liquid = document.createElement('div');
                liquid.className = `tube-liquid ${board[idx] === 1 ? 'p1-gradient' : 'p2-gradient'}`;
                
                tube.appendChild(cap);
                tube.appendChild(liquid);
                slot.appendChild(tube);
            }
        });

        const physics = calculatePhysics(board);
        document.getElementById('weight-display').innerText = `IMBALANCE: ${physics.mag.toFixed(3)} / ${MAX_IMBALANCE.toFixed(1)}`;
        
        // Map center of mass displacement vector natively to pixel coordinates
        const reticleX = 50 + (physics.x * 20); 
        const reticleY = 50 + (physics.y * 20);
        const reticle = document.getElementById('reticle');
        reticle.style.left = `${reticleX}%`;
        reticle.style.top = `${reticleY}%`;

        if (physics.mag > (MAX_IMBALANCE * 0.75)) {
            document.getElementById('chassis').style.transform = `translate(${(Math.random()-0.5)*4}px, ${(Math.random()-0.5)*4}px)`;
            reticle.style.background = '#ff3366';
        } else {
            document.getElementById('chassis').style.transform = 'none';
            reticle.style.background = '#00ffcc';
        }

        document.getElementById('turn-display').innerText = `OPERATOR SHIFT: PLAYER ${currentTurn === 1 ? '1 (CORAL)' : '2 (BLUE)'}`;
    }

    function openCentrifuge() {
        document.getElementById('lid').classList.add('lid-open');
        setTimeout(() => {
            updateRotorVisuals();
        }, 600);
    }

    function calculatePhysics(targetBoard) {
        let xSum = 0, ySum = 0;
        for (let i = 0; i < HOLES; i++) {
            if (targetBoard[i] !== 0) {
                const angle = (i * (360 / HOLES)) * (Math.PI / 180);
                xSum += Math.cos(angle);
                ySum += Math.sin(angle);
            }
        }
        return { mag: Math.sqrt(xSum*xSum + ySum*ySum), x: xSum, y: ySum };
    }

    function handleSlotClick(index) {
        if (!gameActive || currentTurn === 2 && gameMode === "AI") return;

        const clickedSlotDOM = document.querySelector(`[data-index='${index}']`);

        if (selectedSlot === null) {
            if (board[index] === currentTurn) {
                selectedSlot = index;
                clickedSlotDOM.classList.add('selected');
            }
        } else {
            if (selectedSlot === index) {
                clickedSlotDOM.classList.remove('selected');
                selectedSlot = null;
                return;
            }

            if (board[index] === 0) {
                // Execute spatial translation
                const sourceSlotDOM = document.querySelector(`[data-index='${selectedSlot}']`);
                sourceSlotDOM.classList.remove('selected');
                
                board[index] = currentTurn;
                board[selectedSlot] = 0;
                
                selectedSlot = null;
                survivalMoves++;
                
                if (evaluateSystemState()) {
                    currentTurn = 3 - currentTurn;
                    updateRotorVisuals();
                    
                    if (gameMode === "AI" && gameActive) {
                        setTimeout(executeAIBrain, 800);
                    }
                }
            }
        }
    }

    function getValidMoves(targetBoard, player) {
        let moves = [];
        for (let s = 0; s < HOLES; s++) {
            if (targetBoard[s] === player) {
                for (let e = 0; e < HOLES; e++) {
                    if (targetBoard[e] === 0) {
                        let temp = {...targetBoard};
                        temp[s] = 0;
                        temp[e] = player;
                        if (calculatePhysics(temp).mag <= MAX_IMBALANCE) {
                            moves.push({from: s, to: e});
                        }
                    }
                }
            }
        }
        return moves;
    }

    function executeAIBrain() {
        const legalMoves = getValidMoves(board, 2);
        
        if (legalMoves.length === 0) {
            triggerGameOver("♟️ CONTRTAINMENT CHECKMATE", "AI has no safe trajectories remaining. YOU WIN!");
            return;
        }

        // 1-Step Predictive Trajectory Lookahead Minimax Optimization
        let targetedMove = null;
        let minimumHumanRoutes = 999;
        let optimalStability = 999;

        legalMoves.forEach(move => {
            let simBoard = {...board};
            simBoard[move.from] = 0;
            simBoard[move.to] = 2;

            let humanResponses = getValidMoves(simBoard, 1).length;
            let currentImbalance = calculatePhysics(simBoard).mag;

            if (humanResponses < minimumHumanRoutes) {
                minimumHumanRoutes = humanResponses;
                optimalStability = currentImbalance;
                targetedMove = move;
            } else if (humanResponses === minimumHumanRoutes) {
                if (currentImbalance < optimalStability) {
                    optimalStability = currentImbalance;
                    targetedMove = move;
                }
            }
        });

        if (!targetedMove) targetedMove = legalMoves[Math.floor(Math.random() * legalMoves.length)];

        // Commit AI trajectory modifications
        board[targetedMove.from] = 0;
        board[targetedMove.to] = 2;
        
        if (evaluateSystemState()) {
            currentTurn = 1;
            updateRotorVisuals();
        }
    }

    function evaluateSystemState() {
        const physics = calculatePhysics(board);
        
        if (physics.mag > MAX_IMBALANCE) {
            triggerGameOver("💥 ROTOR EXPLOSION", `System exceeded safe limit. Player ${currentTurn === 1 ? '2' : '1'} wins.`);
            return false;
        }
        if (physics.mag < 0.01) {
            triggerGameOver("⚖️ ISOTROPIC CONTAINMENT", `Player ${currentTurn === 1 ? '1' : '2'} achieved total equilibrium and won instantly!`);
            return false;
        }
        
        const nextPlayer = 3 - currentTurn;
        if (getValidMoves(board, nextPlayer).length === 0) {
            triggerGameOver("♟️ ROTATIONAL CHECKMATE", `Player ${nextPlayer === 1 ? '1' : '2'} has no safe moves remaining. Player ${currentTurn === 1 ? '1' : '2'} wins.`);
            return false;
        }
        return true;
    }

    function triggerGameOver(title, subtitle) {
        gameActive = false;
        document.getElementById('end-title').innerText = title;
        document.getElementById('end-subtitle').innerText = subtitle;
        document.getElementById('end-screen').style.display = 'flex';
        
        if (gameMode === "AI" && currentTurn === 2) {
            document.getElementById('score-section').style.display = 'block';
        } else {
            document.getElementById('restart-btn').style.display = 'block';
        }
    }

    function commitScoreData() {
        const initials = document.getElementById('initials').value || "XYZ";
        // Query param bridge redirection back to Streamlit engine filesystem
        window.parent.location.search = `?submit_score=true&name=${initials}&score=${survivalMoves}`;
    }
</script>
</body>
</html>
"""

# Render the self-contained arcade application viewport cleanly inside Streamlit
st.components.v1.html(game_html, height=670, scrolling=False)
