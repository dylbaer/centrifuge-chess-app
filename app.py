import streamlit as st

st.set_page_config(
    page_title="Centrifuge Chess",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide native Streamlit margins and bars to maximize the arcade cabinet feel
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px; margin: 0px;}
    iframe {display: block; margin: 0 auto; border: none;}
    body {background-color: #04060a;}
    </style>
""", unsafe_allow_html=True)

# --- SELF-CONTAINED ARCADE ENGINE (HTML5 / CANVAS / LOCAL STORAGE) ---
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Centrifuge Chess</title>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #04060a; overflow: hidden; display: flex; justify-content: center; align-items: center; }
        canvas { background: #080c14; box-shadow: 0 0 40px rgba(0, 255, 204, 0.1); border: 2px solid #1e293b; max-width: 100%; max-height: 100%; }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="1000" height="700"></canvas>

<script>
window.onload = function() {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    // ENGINE APPLICATION STATES
    const STATE_HOME = 0;
    const STATE_LAUNCH = 1;
    const STATE_GAME = 2;
    const STATE_EXPLOSION = 3;
    const STATE_GAMEOVER = 4;
    let gameState = STATE_HOME;

    // GAMEPLAY SETTINGS
    const HOLES = 24;
    const MAX_IMBALANCE = 2.2;
    const ROTOR_RADIUS = 145;
    const CENTRIFUGE_CENTER = { x: 500, y: 350 };

    // DYNAMIC VARIABLES
    let board = {};
    let gameMode = "1v1"; 
    let currentTurn = 1;  // 1 = Coral (Player 1), 2 = Blue (Player 2 / AI)
    let selectedSlot = null;
    let hoverSlot = null;
    let scoreCycles = 0;
    
    let mx = 0, my = 0;
    let lidOffset = 0;       
    let launchTimer = 0;
    let stateTimer = 0;
    let nameInputBuffer = "";
    
    let screenShake = { x: 0, y: 0, intensity: 0 };
    let particles = [];
    let backgroundBubbles = [];

    // SEED AMBIENT LAB EQUIPMENT COORDINATES
    for (let i = 0; i < 20; i++) {
        backgroundBubbles.push({
            x: 750 + Math.random() * 80,
            y: 500 + Math.random() * 120,
            r: Math.random() * 3 + 1,
            speed: Math.random() * 30 + 10,
            maxHeight: 460 + Math.random() * 40
        });
    }

    // INITIALIZATION RUNTIME
    animateEngine(0);

    function initRotorDatabase() {
        for (let i = 0; i < HOLES; i++) board[i] = 0;
    }

    // PROCEDURAL RANDOM STARTING GENERATOR
    function generateRandomArray() {
        initRotorDatabase();
        let placedCoral = 0;
        let placedBlue = 0;
        
        // Randomly distribute 6 Coral tubes
        while(placedCoral < 6) {
            let r = Math.floor(Math.random() * HOLES);
            if (board[r] === 0) {
                board[r] = 1;
                placedCoral++;
            }
        }
        // Randomly distribute 6 Blue tubes
        while(placedBlue < 6) {
            let r = Math.floor(Math.random() * HOLES);
            if (board[r] === 0) {
                board[r] = 2;
                placedBlue++;
            }
        }

        // Integrity check: Ensure starting layout doesn't crash instantly and has valid legal moves
        let p = calculatePhysics(board);
        if (p.mag > 1.3 || p.mag < 0.2 || getValidMoves(board, 1).length === 0 || getValidMoves(board, 2).length === 0) {
            generateRandomArray();
        }
    }

    // MAIN CORE RENDER LOOP
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
        // Volumetric liquid animation math
        backgroundBubbles.forEach(b => {
            b.y -= b.speed * dt;
            if (b.y < b.maxHeight) {
                b.y = 600;
                b.x = 750 + Math.random() * 80;
            }
        });

        // Hydraulic lid open sequencer
        if (gameState === STATE_LAUNCH) {
            launchTimer += dt;
            lidOffset = easeOutQuad(Math.min(launchTimer / 1.2, 1.0));
            if (launchTimer >= 1.3) {
                gameState = STATE_GAME;
            }
        }

        // Structural vibration simulation
        if (screenShake.intensity > 0) {
            screenShake.x = (Math.random() - 0.5) * screenShake.intensity;
            screenShake.y = (Math.random() - 0.5) * screenShake.intensity;
            screenShake.intensity -= dt * 35;
        } else {
            screenShake.x = 0;
            screenShake.y = 0;
        }

        // High velocity explosion animation updates
        if (gameState === STATE_EXPLOSION) {
            particles.forEach((p, idx) => {
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                p.vy += 450 * dt; // Gravity pull
                p.alpha -= dt * 0.5;
                p.rot += p.vRot * dt;
                if (p.alpha <= 0) particles.splice(idx, 1);
            });
            stateTimer += dt;
            if (stateTimer > 2.2) {
                gameState = STATE_GAMEOVER;
                stateTimer = 0;
            }
        }
    }

    function renderVisualLayers() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        ctx.save();
        ctx.translate(screenShake.x, screenShake.y);

        // ALWAYS RENDER BASE LAYER (The Lab Bench + Stationary Hardware)
        drawLabBenchBackground();
        drawCentrifugeMachine();

        ctx.restore();

        // RENDER INTERACTIVE INTERFACE MODALS OVER TOP RESIDENTS
        if (gameState === STATE_HOME) drawHomeScreenOverlay();
        if (gameState === STATE_GAMEOVER) drawGameOverScreenOverlay();
    }

    function drawLabBenchBackground() {
        // Slate-gray composite workbench counter surface
        ctx.fillStyle = '#181e29';
        ctx.fillRect(0, 480, canvas.width, 220);
        ctx.strokeStyle = '#2d3748';
        ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(0, 480); ctx.lineTo(canvas.width, 480); ctx.stroke();

        // DECORATIVE EQUIPMENT 1: Test tube rack on left bench
        ctx.fillStyle = '#2d3748';
        ctx.fillRect(80, 450, 100, 45); // Rack base
        for(let i = 0; i < 4; i++) {
            ctx.fillStyle = i % 2 === 0 ? '#ff3366' : '#00ccff';
            ctx.fillRect(95 + (i * 22), 400, 12, 50); // Fluid lines
            ctx.fillStyle = 'rgba(255,255,255,0.2)';
            ctx.fillRect(95 + (i * 22), 400, 3, 50);  // Specular sheen
        }
        ctx.strokeStyle = '#4a5568';
        ctx.strokeRect(80, 400, 100, 95);

        // DECORATIVE EQUIPMENT 2: Volumetric boiling flask on right bench
        ctx.fillStyle = '#0f172a';
        ctx.beginPath(); ctx.arc(790, 560, 45, 0, Math.PI * 2); ctx.fill();
        ctx.fillRect(778, 450, 24, 70); // Neck
        
        // Glowing animated solution chemical
        ctx.fillStyle = 'rgba(168, 85, 247, 0.4)'; // Radioactive purple
        ctx.beginPath(); ctx.arc(790, 560, 42, 0, Math.PI); ctx.fill();
        ctx.fillRect(749, 560, 82, 42);

        // Render ambient bubbles rising inside the boiling flask
        ctx.fillStyle = '#e9d5ff';
        backgroundBubbles.forEach(b => {
            ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2); ctx.fill();
        });

        // Glass reflection line
        ctx.strokeStyle = '#718096';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(790, 560, 45, Math.PI * 0.75, Math.PI * 1.25); ctx.stroke();

        // LAB LOGO TEXT
        ctx.fillStyle = '#4a5568';
        ctx.font = '11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("STATION NO. 4 // CORE PHYSICS", 40, 670);
    }

    function drawCentrifugeMachine() {
        let cx = CENTRIFUGE_CENTER.x;
        let cy = CENTRIFUGE_CENTER.y;

        // Heavy industrial machine chassis casing block
        ctx.fillStyle = '#101520';
        ctx.beginPath(); ctx.arc(cx, cy, 235, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#3b4252';
        ctx.lineWidth = 6;
        ctx.stroke();

        // Dark vacuum core rotor bay
        ctx.fillStyle = '#05070c';
        ctx.beginPath(); ctx.arc(cx, cy, 195, 0, Math.PI*2); ctx.fill();

        if (gameState >= STATE_GAME || gameState === STATE_LAUNCH) {
            // THE INTERNAL ROTOR WHEEL
            ctx.fillStyle = '#141a24';
            ctx.beginPath(); ctx.arc(cx, cy, 172, 0, Math.PI*2); ctx.fill();

            // RED STRUCTURAL MAX DISPLACEMENT BOUNDARY RING
            ctx.strokeStyle = 'rgba(255, 51, 102, 0.35)';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath(); ctx.arc(cx, cy, MAX_IMBALANCE * 35, 0, Math.PI*2); ctx.stroke();
            ctx.setLineDash([]);

            // DRAW ALL 24 HOLE SLOT ANCHORS
            for (let i = 0; i < HOLES; i++) {
                let angle = (i * (360 / HOLES)) * (Math.PI / 180);
                let sx = cx + ROTOR_RADIUS * Math.cos(angle);
                let sy = cy + ROTOR_RADIUS * Math.sin(angle);

                ctx.fillStyle = '#070a0f';
                ctx.beginPath(); ctx.arc(sx, sy, 14, 0, Math.PI*2); ctx.fill();
                ctx.strokeStyle = (hoverSlot === i) ? '#00ffcc' : '#2e3440';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Slot identification tags
                ctx.fillStyle = '#4c566a';
                ctx.font = 'bold 9px monospace';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(i, cx + (ROTOR_RADIUS + 23) * Math.cos(angle), cy + (ROTOR_RADIUS + 23) * Math.sin(angle));

                // DRAW DETAILED BULLETPROOF GLASS TEST TUBES
                if (board[i] !== 0) {
                    let isSelected = (selectedSlot === i);
                    drawArcadeTestTube(sx, sy, board[i], isSelected);
                }
            }

            // VECTOR ENGINE FORCE TELEMETRY GAUGE
            let p = calculatePhysics(board);
            let vx = cx + (p.x * 35);
            let vy = cy + (p.y * 35);

            // Vector center tracking alignment lines
            ctx.strokeStyle = 'rgba(0, 255, 204, 0.3)';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(vx, vy); ctx.stroke();

            // Target vector focal node indicator
            ctx.fillStyle = (p.mag > MAX_IMBALANCE * 0.75) ? '#ff3366' : '#00ffcc';
            ctx.beginPath(); ctx.arc(vx, vy, 6, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // GHOST VECTOR PREDICTIVE PATH ROUTING TRAJECTORIES
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

            // INTERACTIVE DISPLAY GRAPHICAL HUD OVERLAYS
            ctx.fillStyle = '#fff';
            ctx.font = '13px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(`IMBALANCE G-FORCE: ${p.mag.toFixed(3)} / ${MAX_IMBALANCE.toFixed(1)} G`, 40, 45);
            ctx.fillText(`OPERATOR TURN: PLAYER ${currentTurn === 1 ? '1 [CORAL]' : '2 [BLUE]'}`, 40, 65);
            ctx.fillText(`CYCLES MAINTAINED: ${scoreCycles}`, 40, 85);

            // ARCADE DESIGN HEALTH/STABILITY STATUS BAR
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(40, 100, 200, 10);
            let fillPercent = Math.min(p.mag / MAX_IMBALANCE, 1.0);
            ctx.fillStyle = (fillPercent > 0.75) ? '#ff3366' : '#00ffcc';
            ctx.fillRect(40, 100, 200 * fillPercent, 10);
        }

        // CATASTROPHIC VECTOR EXPLOSION FRAGMENT SPARK TRAILS
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

        // PNEUMATIC SECURITY SHUTTER LID HATCH ASSEMBLY
        if (gameState === STATE_HOME || gameState === STATE_LAUNCH) {
            let ly = cy - (lidOffset * 650);
            
            // Clean white/gray enamel mechanical shielding capsule
            ctx.fillStyle = '#e2e8f0';
            ctx.beginPath(); ctx.arc(cx, ly, 230, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#cbd5e1';
            ctx.lineWidth = 4;
            ctx.stroke();

            // Dark circular acrylic tinted viewpoint viewport window glass
            ctx.fillStyle = '#0f172a';
            ctx.beginPath(); ctx.arc(cx, ly, 75, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#94a3b8';
            ctx.lineWidth = 5;
            ctx.stroke();

            // Neon diagnostic readout label text
            ctx.fillStyle = (Math.floor(Date.now() / 500) % 2 === 0) ? '#00ffcc' : '#00aa88';
            ctx.font = 'bold 11px monospace';
            ctx.textAlign = 'center';
            ctx.fillText("READY TO OPEN", cx, ly + 4);
        }
    }

    function drawArcadeTestTube(x, y, player, isSelected) {
        ctx.save();
        ctx.translate(x, y);
        
        if (isSelected) {
            ctx.scale(1.25, 1.25);
            ctx.strokeStyle = '#00ffcc';
            ctx.lineWidth = 2;
            ctx.strokeRect(-11, -21, 22, 42);
        }

        // Clear high density resin casing wall outlines
        ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.beginPath();
        ctx.moveTo(-7, -15); ctx.lineTo(7, -15); ctx.lineTo(7, 8);
        ctx.arc(0, 8, 7, 0, Math.PI, false); ctx.lineTo(-7, -15);
        ctx.fill();

        // Layered internal neon chemical fluids volume blocks
        let fillGradient = ctx.createLinearGradient(-7, 0, 7, 0);
        if (player === 1) {
            fillGradient.addColorStop(0, '#ff3366'); fillGradient.addColorStop(1, '#a30022');
        } else {
            fillGradient.addColorStop(0, '#00ccff'); fillGradient.addColorStop(1, '#004a99');
        }
        ctx.fillStyle = fillGradient;
        ctx.beginPath();
        ctx.moveTo(-6, -3); ctx.lineTo(6, -3); ctx.lineTo(6, 8);
        ctx.arc(0, 8, 6, 0, Math.PI, false); ctx.lineTo(-6, -3);
        ctx.fill();

        // Specular ambient lens glare strip
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.fillRect(-4, -13, 2, 22);

        // Heavy locking plastic friction safety tops
        ctx.fillStyle = (player === 1) ? '#ff8aa8' : '#b3f0ff';
        ctx.fillRect(-8, -19, 16, 5);

        ctx.restore();
    }

    function drawHomeScreenOverlay() {
        // Subtle ambient screen tint shading
        ctx.fillStyle = 'rgba(4, 6, 10, 0.5)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // High contrast central operations dashboard console
        let menu = { x: 50, y: 120, w: 320, h: 320 };
        ctx.fillStyle = '#0b101d';
        ctx.fillRect(menu.x, menu.y, menu.w, menu.h);
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.strokeRect(menu.x, menu.y, menu.w, menu.h);

        // HEADER LABELS
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 26px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("CENTRIFUGE CHESS", menu.x + 20, menu.y + 45);
        
        ctx.fillStyle = '#64748b';
        ctx.font = '11px monospace';
        ctx.fillText("CRASH CODE INITIATIVE PROTOCOL", menu.x + 20, menu.y + 65);

        // BUTTON INTERFACES RENDER CALLS
        drawArcadeMenuButton(menu.x + 20, menu.y + 100, 280, 42, "▶ 1 VS 1 LOCAL PROMPT");
        drawArcadeMenuButton(menu.x + 20, menu.y + 155, 280, 42, "▶ SOLO WORKSTATION (VS AI)");
        
        // REFORMATTED COMPACT HIGH SCORE BILLBOARD READOUTS
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 11px monospace';
        ctx.fillText("--- LAB HIGH RECORD LOG ---", menu.x + 20, menu.y + 230);

        let records = fetchLocalLeaderboardRecords();
        ctx.font = '12px monospace';
        if (records.length > 0) {
            records.forEach((rec, idx) => {
                ctx.fillStyle = '#fff';
                ctx.fillText(`${idx+1}. ${rec.name}`, menu.x + 20, menu.y + 255 + (idx * 18));
                ctx.fillStyle = '#00ffcc';
                ctx.textAlign = 'right';
                ctx.fillText(`${rec.score} CYC`, menu.x + 300, menu.y + 255 + (idx * 18));
                ctx.textAlign = 'left';
            });
        } else {
            ctx.fillStyle = '#475569';
            ctx.fillText("No current telemetry data logged.", menu.x + 20, menu.y + 255);
        }
    }

    function drawArcadeMenuButton(x, y, w, h, text) {
        let isHovered = (mx >= x && mx <= x + w && my >= y && my <= y + h);

        ctx.fillStyle = isHovered ? '#16253b' : '#070c14';
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = isHovered ? '#00ffcc' : '#334155';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x, y, w, h);

        ctx.fillStyle = isHovered ? '#00ffcc' : '#94a3b8';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, x + w/2, y + h/2);
        ctx.textBaseline = 'normal'; // Reset baseline transformations
    }

    function drawGameOverScreenOverlay() {
        ctx.fillStyle = 'rgba(4, 6, 10, 0.92)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // BIG RED VIBRANT RETRO TERMINAL TEXT
        ctx.fillStyle = '#ff3366';
        ctx.font = 'bold 46px monospace';
        ctx.textAlign = 'center';
        ctx.fillText("🚨 CORE DISRUPTION EXPLOSION 🚨", 500, 230);

        ctx.fillStyle = '#94a3b8';
        ctx.font = '15px monospace';
        ctx.fillText(`Rotor balanced yield thresholds shattered. Core safety parameters violated.`, 500, 280);
        
        ctx.fillStyle = '#00ffcc';
        ctx.font = 'bold 18px monospace';
        ctx.fillText(`STABLE RUNTIME MAINTAINED: ${scoreCycles} COMPLETED CYCLES`, 500, 320);

        if (gameMode === "AI") {
            ctx.fillStyle = '#fff';
            ctx.font = '13px monospace';
            ctx.fillText("ARCHIVE WORKSTATION OPERATOR INITIALS (3 CHR):", 500, 375);
            
            ctx.fillStyle = '#0b101d';
            ctx.fillRect(440, 395, 120, 36);
            ctx.strokeStyle = '#334155';
            ctx.strokeRect(440, 395, 120, 36);

            ctx.fillStyle = '#00ffcc';
            ctx.font = 'bold 20px monospace';
            ctx.fillText((nameInputBuffer + "_").substring(0, 4), 500, 421);
            
            ctx.fillStyle = '#4a5568';
            ctx.font = '10px monospace';
            ctx.fillText("[PRESS THE ENTER KEY TO COMMIT METRICS]", 500, 455);
        } else {
            drawArcadeMenuButton(380, 380, 240, 45, "RETURN TO ACCESS TERMINAL");
        }
    }

    // TARGETED INTERACTIVE COORDINATE TRACKERS
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
                if (Math.hypot(mx - sx, my - sy) < 17) {
                    foundHover = i;
                    break;
                }
            }
            hoverSlot = foundHover;
        } else {
            hoverSlot = null;
        }
    });

    window.addEventListener('click', () => {
        if (gameState === STATE_HOME) {
            // Context click intersections
            if (mx >= 70 && mx <= 350) {
                if (my >= 220 && my <= 262) { gameMode = "1v1"; triggerCoreLaunchSequence(); }
                if (my >= 275 && my <= 317) { gameMode = "AI"; triggerCoreLaunchSequence(); }
            }
        }
        else if (gameState === STATE_GAME) {
            if (hoverSlot !== null) {
                handleRotorGridInteraction(hoverSlot);
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
            if (e.key === "Enter" && nameInputBuffer.length > 0) {
                commitLocalLeaderboardScore(nameInputBuffer, scoreCycles);
                gameState = STATE_HOME;
                selectedSlot = null;
                hoverSlot = null;
            } else if (e.key === "Backspace") {
                nameInputBuffer = nameInputBuffer.slice(0, -1);
            } else if (e.key.length === 1 && nameInputBuffer.length < 3 && /[a-zA-Z0-9]/.test(e.key)) {
                nameInputBuffer += e.key.toUpperCase();
            }
        }
    });

    function triggerCoreLaunchSequence() {
        generateRandomArray();
        currentTurn = 1;
        scoreCycles = 0;
        launchTimer = 0;
        lidOffset = 0;
        nameInputBuffer = "";
        gameState = STATE_LAUNCH;
    }

    function handleRotorGridInteraction(index) {
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
                // Execute layout change transformations
                board[index] = currentTurn;
                board[selectedSlot] = 0;
                selectedSlot = null;
                scoreCycles++;

                if (evaluateSystemPhysics()) {
                    currentTurn = 3 - currentTurn;
                    if (gameMode === "AI") {
                        setTimeout(executeAIOptimizerRoutine, 600);
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

    function executeAIOptimizerRoutine() {
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

            // Strategy: Starve human player options or secure highest rotor safety threshold balances
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
            triggerExplosionSequence();
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

    function triggerExplosionSequence() {
        gameState = STATE_EXPLOSION;
        stateTimer = 0;
        screenShake.intensity = 50;
        particles = [];

        // Spawn vector shard cloud
        for (let i = 0; i < 180; i++) {
            let angle = Math.random() * Math.PI * 2;
            let speed = Math.random() * 340 + 90;
            let clr = Math.random() < 0.5 ? '#ff3366' : '#00ccff';
            if (Math.random() < 0.15) clr = '#ffffff';

            particles.push({
                x: CENTRIFUGE_CENTER.x + (Math.random()-0.5)*80,
                y: CENTRIFUGE_CENTER.y + (Math.random()-0.5)*80,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 60,
                size: Math.random() * 5 + 3,
                color: clr,
                alpha: 1.0,
                rot: Math.random() * 6,
                vRot: (Math.random() - 0.5) * 12
            });
        }
    }

    // BROWSER LOCAL STORAGE API CONTROLLERS (CORS SAFE / PERSISTENT)
    function fetchLocalLeaderboardRecords() {
        let raw = localStorage.getItem('centrifuge_scores');
        if (raw) {
            try { return JSON.parse(raw).sort((a,b) => b.score - a.score).slice(0, 3); } catch(e) { return []; }
        }
        return [];
    }

    function commitLocalLeaderboardScore(name, score) {
        let current = fetchLocalLeaderboardRecords();
        current.push({name: name.substring(0,3).upperCase || name, score: score});
        let sorted = current.sort((a,b) => b.score - a.score).slice(0, 3);
        localStorage.setItem('centrifuge_scores', JSON.stringify(sorted));
    }

    function easeOutQuad(x) {
        return 1 - (1 - x) * (1 - x);
    }
};
</script>
</body>
</html>
"""

# Render the self-contained arcade cabinet cleanly inside Streamlit
st.components.v1.html(game_html, height=710, scrolling=False)
