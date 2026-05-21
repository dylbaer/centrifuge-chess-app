import streamlit as st
import json
import os

LEADERBOARD_FILE = "centrifuge_arcade_scores.json"

st.set_page_config(
    page_title="Centrifuge Overclocked",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LEADERBOARD DATA UTILITY ---
def get_scores():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return sorted(json.load(f), key=lambda x: x['score'], reverse=True)[:5]
        except:
            return []
    return []

if "submit_score" in st.query_params:
    name = st.query_params.get("name", "AAA")
    score = int(st.query_params.get("score", 0))
    scores = get_scores()
    scores.append({"name": name[:3].upper(), "score": score})
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(scores, f)
    st.query_params.clear()
    st.rerun()

# --- THE HIGH-TECH ARCADE UI SIDEBAR ---
st.markdown("""
    <style>
    body { background-color: #030508; color: #e2e8f0; font-family: 'Courier New', monospace; }
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
    <span class="glitch-title">☢️ CENTRIFUGE CHESS: OVERCLOCK</span>
    <p style="color: #64748b; margin-top: 5px;">Maintain angular velocity. Manipulate torque. Do not rupture the core.</p>
</div>
""", unsafe_allow_html=True)

col_game, col_sidebar = st.columns([2.5, 1])

with col_sidebar:
    st.markdown("<div class='leaderboard-card'>", unsafe_allow_html=True)
    st.subheader("🏆 ARCHIVED TOP OPERATORS")
    top_scores = get_scores()
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
        * **Mode Selection:** Choose 1v1 Local or Solo vs AI directly on the center console menu.
        * **Controls:** Click a test tube to select/lift it, then click any empty slot to secure it.
        * **Vector Mechanics:** Keep the glowing center-of-mass reticle out of the dashed **Red Boundary**.
        * **Symmetry Victory:** Bring the center of mass to absolute zero ($0.00$) to secure instant containment success.
        * **Checkmate:** Trap your opponent where any move they make causes a catastrophic rupture.
        """)

# --- THE SELF-CONTAINED CANVAS CORE ENGINE ---
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Centrifuge Chess Engine</title>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #030508; overflow: hidden; display: flex; justify-content: center; align-items: center; }
        canvas { background: #060913; box-shadow: 0 0 50px rgba(0, 255, 204, 0.15); border-radius: 4px; max-width: 100%; max-height: 100%; cursor: default; }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="1000" height="700"></canvas>

<script>
    // 1. ALL ENGINE VARIABLES DECLARED UP FRONT TO PREVENT SCOPING AND REFERENCE ERRORS
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    const STATE_HOME = 0;
    const STATE_LAUNCH = 1;
    const STATE_GAME = 2;
    const STATE_EXPLOSION = 3;
    const STATE_GAMEOVER = 4;
    
    let gameState = STATE_HOME;
    let gameMode = "1v1"; 
    let currentTurn = 1;  
    let selectedSlot = null;
    let hoverSlot = null;
    let scoreCycles = 0;
    
    let mx = 0; 
    let my = 0;
    let lidOffset = 0;       
    let launchTimer = 0;
    let stateTimer = 0;
    let playerInitials = "";
    
    let board = {};
    const HOLES = 24;
    const MAX_IMBALANCE = 2.2;
    const ROTOR_RADIUS = 150;
    const CENTRIFUGE_CENTER = { x: 500, y: 350 };
    
    let screenShake = { x: 0, y: 0, intensity: 0 };
    let particles = [];

    let bubbleBeakers = [
        { x: 120, y: 580, r: 40, h: 90, color: 'rgba(0, 255, 204, 0.4)', liquid: 0.7, bubbles: [] },
        { x: 210, y: 600, r: 25, h: 60, color: 'rgba(255, 51, 102, 0.4)', liquid: 0.5, bubbles: [] },
        { x: 840, y: 570, r: 50, h: 110, color: 'rgba(0, 204, 255, 0.4)', liquid: 0.8, bubbles: [] }
    ];

    // 2. BOOTSTRAP INITIALIZATION PROCEDURES
    initRotorDatabase();
    animateEngine(0);

    function initRotorDatabase() {
        for (let i = 0; i < HOLES; i++) board[i] = 0;
    }

    function generateRandomArray() {
        initRotorDatabase();
        let placed = 0;
        
        while(placed < 6) {
            let r = Math.floor(Math.random() * HOLES);
            if (board[r] === 0) {
                board[r] = 1;
                placed++;
            }
        }
        placed = 0;
        while(placed < 6) {
            let r = Math.floor(Math.random() * HOLES);
            if (board[r] === 0) {
                board[r] = 2;
                placed++;
            }
        }

        let p = calculatePhysics(board);
        if (p.mag > 1.4 || p.mag < 0.1 || getValidMoves(board, 1).length === 0 || getValidMoves(board, 2).length === 0) {
            generateRandomArray();
        }
    }

    let lastTime = 0;
    function animateEngine(timestamp) {
        let dt = (timestamp - lastTime) / 1000;
        if (!dt || dt > 0.1) dt = 0.1;
        lastTime = timestamp;

        updateVisualPhysics(dt);
        renderVisualLayers();

        requestAnimationFrame(animateEngine);
    }

    function updateVisualPhysics(dt) {
        bubbleBeakers.forEach(b => {
            if (Math.random() < 0.05) {
                b.bubbles.push({
                    bx: b.x + (Math.random() - 0.5) * (b.r * 1.4),
                    by: 650,
                    size: Math.random() * 3 + 1,
                    speed: Math.random() * 40 + 20
                });
            }
            b.bubbles.forEach((bubble, idx) => {
                bubble.by -= bubble.speed * dt;
                if (bubble.by < 650 - (b.h * b.liquid)) b.bubbles.splice(idx, 1);
            });
        });

        if (gameState === STATE_LAUNCH) {
            launchTimer += dt;
            lidOffset = easeOutQuad(Math.min(launchTimer / 1.2, 1.0));
            if (launchTimer >= 1.4) {
                gameState = STATE_GAME;
            }
        }

        if (screenShake.intensity > 0) {
            screenShake.x = (Math.random() - 0.5) * screenShake.intensity;
            screenShake.y = (Math.random() - 0.5) * screenShake.intensity;
            screenShake.intensity -= dt * 30;
        } else {
            screenShake.x = 0;
            screenShake.y = 0;
        }

        if (gameState === STATE_EXPLOSION) {
            particles.forEach((p, idx) => {
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                p.vy += 400 * dt; 
                p.alpha -= dt * 0.6;
                p.rot += p.vRot * dt;
                if (p.alpha <= 0) particles.splice(idx, 1);
            });
            stateTimer += dt;
            if (stateTimer > 2.0) {
                gameState = STATE_GAMEOVER;
                stateTimer = 0;
            }
        }
    }

    function renderVisualLayers() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.save();
        ctx.translate(screenShake.x, screenShake.y);

        drawLabEnvironment();
        drawCentrifugeStructure();

        ctx.restore();

        if (gameState === STATE_HOME) drawHomeScreen();
        if (gameState === STATE_GAMEOVER) drawGameOverScreen();
    }

    function drawLabEnvironment() {
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 520, canvas.width, 180);
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 3;
        ctx.beginPath(); ctx.moveTo(0, 520); ctx.lineTo(canvas.width, 520); ctx.stroke();

        bubbleBeakers.forEach(b => {
            ctx.fillStyle = '#0f172a';
            ctx.beginPath();
            ctx.arc(b.x, 650 - b.r, b.r, Math.PI, 0, false);
            ctx.lineTo(b.x + b.r, 650); ctx.lineTo(b.x - b.r, 650);
            ctx.fill();

            ctx.fillStyle = b.color;
            ctx.fillRect(b.x - b.r + 4, 650 - (b.h * b.liquid), (b.r * 2) - 8, (b.h * b.liquid) - 4);

            ctx.fillStyle = '#fff';
            b.bubbles.forEach(bubble => {
                ctx.beginPath(); ctx.arc(bubble.bx, bubble.by, bubble.size, 0, Math.PI*2); ctx.fill();
            });

            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(b.x - b.r, 650 - b.h); ctx.lineTo(b.x - b.r, 650);
            ctx.lineTo(b.x + b.r, 650); ctx.lineTo(b.x + b.r, 650 - b.h);
            ctx.stroke();
        });

        ctx.fillStyle = '#090d16';
        ctx.fillRect(50, 40, 240, 140);
        ctx.strokeStyle = '#1e293b';
        ctx.strokeRect(50, 40, 240, 140);
        
        ctx.fillStyle = 'rgba(0, 255, 204, 0.05)';
        ctx.fillRect(53, 43, 234, 134);

        ctx.strokeStyle = 'rgba(0, 255, 204, 0.1)';
        ctx.lineWidth = 1;
        for (let l = 55; l < 180; l += 15) {
            ctx.beginPath(); ctx.moveTo(60, l); ctx.lineTo(280, l + Math.sin(l)*5); ctx.stroke();
        }
    }

    function drawCentrifugeStructure() {
        let cx = CENTRIFUGE_CENTER.x;
        let cy = CENTRIFUGE_CENTER.y;

        ctx.fillStyle = '#111622';
        ctx.beginPath(); ctx.arc(cx, cy, 240, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 6;
        ctx.stroke();

        ctx.fillStyle = '#070a12';
        ctx.beginPath(); ctx.arc(cx, cy, 200, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.stroke();

        if (gameState >= STATE_GAME || gameState === STATE_LAUNCH) {
            ctx.fillStyle = '#151d2a';
            ctx.beginPath(); ctx.arc(cx, cy, 175, 0, Math.PI*2); ctx.fill();

            ctx.strokeStyle = 'rgba(255, 51, 102, 0.3)';
            ctx.lineWidth = 2;
            ctx.setLineDash([4, 4]);
            ctx.beginPath(); ctx.arc(cx, cy, MAX_IMBALANCE * 35, 0, Math.PI*2); ctx.stroke();
            ctx.setLineDash([]);

            for (let i = 0; i < HOLES; i++) {
                let angle = (i * (360 / HOLES)) * (Math.PI / 180);
                let sx = cx + ROTOR_RADIUS * Math.cos(angle);
                let sy = cy + ROTOR_RADIUS * Math.sin(angle);

                ctx.fillStyle = '#090d14';
                ctx.beginPath(); ctx.arc(sx, sy, 14, 0, Math.PI*2); ctx.fill();
                ctx.strokeStyle = (hoverSlot === i) ? '#00ffcc' : '#334155';
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.fillStyle = '#475569';
                ctx.font = 'bold 10px monospace';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(i, cx + (ROTOR_RADIUS + 24) * Math.cos(angle), cy + (ROTOR_RADIUS + 24) * Math.sin(angle));

                if (board[i] !== 0) {
                    let isSelected = (selectedSlot === i);
                    drawArcadeTestTube(sx, sy, board[i], isSelected);
                }
            }

            let p = calculatePhysics(board);
            let vx = cx + (p.x * 35);
            let vy = cy + (p.y * 35);

            ctx.strokeStyle = 'rgba(255,255,255,0.08)';
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(cx-15, cy); ctx.lineTo(cx+15, cy); ctx.moveTo(cx, cy-15); ctx.lineTo(cx, cy+15); ctx.stroke();

            ctx.strokeStyle = 'rgba(0, 255, 204, 0.4)';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(vx, vy); ctx.stroke();

            ctx.fillStyle = (p.mag > MAX_IMBALANCE * 0.75) ? '#ff3366' : '#00ffcc';
            ctx.beginPath(); ctx.arc(vx, vy, 6, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            if (selectedSlot !== null && hoverSlot !== null && board[hoverSlot] === 0) {
                let ghostBoard = {...board};
                ghostBoard[selectedSlot] = 0;
                ghostBoard[hoverSlot] = board[selectedSlot];
                
                let gp = calculatePhysics(ghostBoard);
                let gvx = cx + (gp.x * 35);
                let gvy = cy + (gp.y * 35);

                ctx.strokeStyle = 'rgba(234, 179, 8, 0.5)';
                ctx.lineWidth = 1.5;
                ctx.setLineDash([3, 3]);
                ctx.beginPath(); ctx.moveTo(vx, vy); ctx.lineTo(gvx, gvy); ctx.stroke();
                
                ctx.fillStyle = 'rgba(234, 179, 8, 0.8)';
                ctx.beginPath(); ctx.arc(gvx, gvy, 5, 0, Math.PI*2); ctx.fill();
                ctx.setLineDash([]);
            }

            ctx.fillStyle = '#fff';
            ctx.font = '14px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(`TORQUE DISPLACEMENT VECTOR: ${p.mag.toFixed(3)} G`, 60, 75);
            ctx.fillText(`OPERATOR AUTHORIZATION: PLAYER ${currentTurn === 1 ? '1 [CORAL]' : '2 [BLUE]'}`, 60, 100);
            ctx.fillText(`SURVIVED PROTOCOL CYCLES: ${scoreCycles}`, 60, 125);
        }

        if (gameState === STATE_EXPLOSION) {
            particles.forEach(p => {
                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.rot);
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.alpha;
                ctx.fillRect(-p.size/2, -p.size/2, p.size, p.size * 2);
                ctx.restore();
            });
            ctx.globalAlpha = 1.0;
        }

        if (gameState === STATE_HOME || gameState === STATE_LAUNCH) {
            let ly = cy - (lidOffset * 650);
            
            ctx.fillStyle = '#273142';
            ctx.beginPath(); ctx.arc(cx, ly, 236, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 4;
            ctx.stroke();

            ctx.fillStyle = '#0f131c';
            ctx.beginPath(); ctx.arc(cx, ly, 80, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 6;
            ctx.stroke();

            ctx.fillStyle = '#00ffcc';
            ctx.font = 'bold 12px monospace';
            ctx.textAlign = 'center';
            ctx.fillText("CHAMBER LOCKED", cx, ly + 5);
        }
    }

    function drawArcadeTestTube(x, y, player, isSelected) {
        ctx.save();
        ctx.translate(x, y);
        
        if (isSelected) {
            ctx.scale(1.25, 1.25);
            ctx.strokeStyle = 'rgba(0, 255, 204, 0.5)';
            ctx.lineWidth = 2;
            ctx.strokeRect(-12, -22, 24, 44);
        }

        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.beginPath();
        ctx.moveTo(-8, -16); ctx.lineTo(8, -16); ctx.lineTo(8, 10);
        ctx.arc(0, 10, 8, 0, Math.PI, false); ctx.lineTo(-8, -16);
        ctx.fill();

        let gradient = ctx.createLinearGradient(-8, 0, 8, 0);
        if (player === 1) {
            gradient.addColorStop(0, '#ff3366'); gradient.addColorStop(1, '#990022');
        } else {
            gradient.addColorStop(0, '#00ccff'); gradient.addColorStop(1, '#004499');
        }
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.moveTo(-7, -4); ctx.lineTo(7, -4); ctx.lineTo(7, 10);
        ctx.arc(0, 10, 7, 0, Math.PI, false); ctx.lineTo(-7, -4);
        ctx.fill();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
        ctx.fillRect(-5, -14, 2, 24);

        ctx.fillStyle = (player === 1) ? '#ff88a8' : '#a5f3ff';
        ctx.fillRect(-9, -20, 18, 5);

        ctx.restore();
    }

    function drawHomeScreen() {
        ctx.fillStyle = 'rgba(3, 5, 8, 0.75)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        let menuBox = { x: 320, y: 180, w: 360, h: 280 };
        ctx.fillStyle = '#0b0f19';
        ctx.fillRect(menuBox.x, menuBox.y, menuBox.w, menuBox.h);
        ctx.strokeStyle = '#00ffcc';
        ctx.lineWidth = 2;
        ctx.strokeRect(menuBox.x, menuBox.y, menuBox.w, menuBox.h);

        ctx.fillStyle = '#fff';
        ctx.font = 'bold 20px monospace';
        ctx.textAlign = 'center';
        ctx.fillText("SELECT OPERATIONS MODE", 500, 230);

        drawMenuButton(360, 270, 280, 45, "1 VS 1 TACTICAL SPLIT");
        drawMenuButton(360, 335, 280, 45, "SOLO PROTOCOL (VS COMP)");
        drawMenuButton(360, 400, 280, 45, "RESET INSTRUMENT UNIT");
    }

    function drawMenuButton(x, y, w, h, text) {
        let isHovered = (mx >= x && mx <= x + w && my >= y && my <= y + h);

        ctx.fillStyle = isHovered ? '#152335' : '#070a12';
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = isHovered ? '#00ffcc' : '#334155';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x, y, w, h);

        ctx.fillStyle = isHovered ? '#00ffcc' : '#94a3b8';
        ctx.font = 'bold 12px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, x + w/2, y + h/2);
    }

    function drawGameOverScreen() {
        ctx.fillStyle = 'rgba(5, 5, 10, 0.9)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#ff3366';
        ctx.font = 'bold 42px monospace';
        ctx.textAlign = 'center';
        ctx.fillText("☢️ CORE EXPLOSION ☢️", 500, 240);

        ctx.fillStyle = '#94a3b8';
        ctx.font = '15px monospace';
        ctx.fillText(`Rotor equilibrium structural yield breached during operations log.`, 500, 290);
        ctx.fillStyle = '#00ffcc';
        ctx.font = 'bold 16px monospace';
        ctx.fillText(`RETAINED RUNTIMELINE: ${scoreCycles} STABLE CYCLES`, 500, 330);

        if (gameMode === "AI") {
            ctx.fillStyle = '#fff';
            ctx.font = '14px monospace';
            ctx.fillText("RECORD IDENTITY TAGS (3 CHR):", 500, 380);
            
            ctx.fillStyle = '#111726';
            ctx.fillRect(440, 400, 120, 35);
            ctx.strokeStyle = '#334155';
            ctx.strokeRect(440, 400, 120, 35);

            ctx.fillStyle = '#00ffcc';
            ctx.font = 'bold 20px monospace';
            ctx.fillText((playerInitials + "_").substring(0, 4), 500, 425);
            
            ctx.fillStyle = '#475569';
            ctx.font = '10px monospace';
            ctx.fillText("[PRESS ENTER TO ARCHIVE SCORE]", 500, 460);
        } else {
            drawMenuButton(380, 380, 240, 45, "RETURN TO MAIN TERMINAL");
        }
    }

    window.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mx = (e.clientX - rect.left) * (canvas.width / rect.width);
        my = (e.clientY - rect.top) * (canvas.height / rect.height);

        if (gameState === STATE_GAME) {
            let foundHover = null;
            for (let i = 0; i < HOLES; i++) {
                let angle = (i * (360 / HOLES)) * (Math.PI / 180);
                let sx = CENTRIFUGE_CENTER.x + ROTOR_RADIUS * Math.cos(angle);
                let sy = CENTRIFUGE_CENTER.y + ROTOR_RADIUS * Math.sin(angle);
                if (Math.hypot(mx - sx, my - sy) < 18) {
                    foundHover = i;
                    break;
                }
            }
            hoverSlot = foundHover;
            canvas.style.cursor = (hoverSlot !== null) ? 'pointer' : 'default';
        } else {
            hoverSlot = null;
            canvas.style.cursor = 'default';
        }
    });

    window.addEventListener('click', () => {
        if (gameState === STATE_HOME) {
            if (mx >= 360 && mx <= 640) {
                if (my >= 270 && my <= 315) { gameMode = "1v1"; triggerCoreLaunch(); }
                if (my >= 335 && my <= 380) { gameMode = "AI"; triggerCoreLaunch(); }
                if (my >= 400 && my <= 445) { location.reload(); }
            }
        }
        else if (gameState === STATE_GAME) {
            if (hoverSlot !== null) {
                handleRotorGridClick(hoverSlot);
            }
        }
        else if (gameState === STATE_GAMEOVER && gameMode !== "AI") {
            if (mx >= 380 && mx <= 620 && my >= 380 && my <= 425) {
                gameState = STATE_HOME;
                selectedSlot = null;
                hoverSlot = null;
            }
        }
    });

    window.addEventListener('keydown', (e) => {
        if (gameState === STATE_GAMEOVER && gameMode === "AI") {
            if (e.key === "Enter" && playerInitials.length > 0) {
                commitScoreData();
            } else if (e.key === "Backspace") {
                playerInitials = playerInitials.slice(0, -1);
            } else if (e.key.length === 1 && playerInitials.length < 3 && /[a-zA-Z0-9]/.test(e.key)) {
                playerInitials += e.key.toUpperCase();
            }
        }
    });

    function triggerCoreLaunch() {
        generateRandomArray();
        currentTurn = 1;
        scoreCycles = 0;
        launchTimer = 0;
        lidOffset = 0;
        gameState = STATE_LAUNCH;
    }

    function handleRotorGridClick(index) {
        if (currentTurn === 2 && gameMode === "AI") return; 

        if (selectedSlot === null) {
            if (board[index] === currentTurn) {
                selectedSlot = index;
            }
        } else {
            if (selectedSlot === index) {
                selectedSlot = null;
                return;
            }

            if (board[index] === 0) {
                board[index] = currentTurn;
                board[selectedSlot] = 0;
                selectedSlot = null;
                scoreCycles++;

                if (evaluateSystemPhysics()) {
                    currentTurn = 3 - currentTurn;
                    if (gameMode === "AI") {
                        setTimeout(executeAIBrainAlgorithms, 600);
                    }
                }
            }
        }
    }

    function calculatePhysics(targetBoard) {
        let xSum = 0, ySum = 0;
        for (let i = 0; i < HOLES; i++) {
            if (targetBoard[i] !== 0) {
                let angle = (i * (360 / HOLES)) * (Math.PI / 180);
                xSum += Math.cos(angle);
                ySum += Math.sin(angle);
            }
        }
        return { mag: Math.sqrt(xSum*xSum + ySum*ySum), x: xSum, y: ySum };
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

    function executeAIBrainAlgorithms() {
        const legalMoves = getValidMoves(board, 2);
        if (legalMoves.length === 0) {
            gameState = STATE_GAMEOVER;
            return;
        }

        let chosenMove = null;
        let minimumHumanAvenues = 999;
        let bestImbalance = 999;

        legalMoves.forEach(m => {
            let sim = {...board};
            sim[m.from] = 0; sim[m.to] = 2;
            let humanOptions = getValidMoves(sim, 1).length;
            let currentImbalance = calculatePhysics(sim).mag;

            if (humanOptions < minimumHumanAvenues) {
                minimumHumanAvenues = humanOptions;
                bestImbalance = currentImbalance;
                chosenMove = m;
            } else if (humanOptions === minimumHumanAvenues) {
                if (currentImbalance < bestImbalance) {
                    bestImbalance = currentImbalance;
                    chosenMove = m;
                }
            }
        });

        if (!chosenMove) chosenMove = legalMoves[Math.floor(Math.random() * legalMoves.length)];

        board[chosenMove.from] = 0;
        board[chosenMove.to] = 2;

        if (evaluateSystemPhysics()) {
            currentTurn = 1;
        }
    }

    function evaluateSystemPhysics() {
        let p = calculatePhysics(board);
        if (p.mag > MAX_IMBALANCE) {
            triggerExplosionSimulation();
            return false;
        }
        if (p.mag < 0.01) {
            gameState = STATE_GAMEOVER;
            return false;
        }
        let nextPlayer = 3 - currentTurn;
        if (getValidMoves(board, nextPlayer).length === 0) {
            gameState = STATE_GAMEOVER;
            return false;
        }
        return true;
    }

    function triggerExplosionSimulation() {
        gameState = STATE_EXPLOSION;
        stateTimer = 0;
        screenShake.intensity = 45;
        particles = [];
        playerInitials = "";

        for (let i = 0; i < 160; i++) {
            let angle = Math.random() * Math.PI * 2;
            let speed = Math.random() * 320 + 80;
            let clr = Math.random() < 0.5 ? '#ff3366' : '#00ccff';
            if (Math.random() < 0.2) clr = '#ffffff';

            particles.push({
                x: CENTRIFUGE_CENTER.x + (Math.random()-0.5)*100,
                y: CENTRIFUGE_CENTER.y + (Math.random()-0.5)*100,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 50,
                size: Math.random() * 6 + 3,
                color: clr,
                alpha: 1.0,
                rot: Math.random() * 5,
                vRot: (Math.random() - 0.5) * 10
            });
        }
    }

    function commitScoreData() {
        window.parent.location.search = `?submit_score=true&name=${playerInitials}&score=${scoreCycles}`;
    }

    function easeOutQuad(x) {
        return 1 - (1 - x) * (1 - x);
    }
</script>
</body>
</html>
"""

st.components.v1.html(game_html, height=715, scrolling=False)
