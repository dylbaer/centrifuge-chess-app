import streamlit as st

st.set_page_config(
    page_title="Centrifuge Chess",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enforce clean formatting by removing native Streamlit borders, paddings, and menus
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

# --- BULLETPROOF ARCADE EMBED (HTML5 / SELF-CONTAINED CANVAS PIPELINE) ---
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Centrifuge Chess</title>
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #04060a; overflow: hidden; display: flex; justify-content: center; align-items: center; }
        canvas { background: #070b12; box-shadow: 0 0 40px rgba(0, 255, 170, 0.15); border: 2px solid #1e293b; max-width: 100%; max-height: 100%; }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="1000" height="700"></canvas>

<script>
// Scoped IIFE configuration pattern to execute instantly without timing delays
(function() {
    const canvas = document.getElementById('gameCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // ENGINE CORE APPLICATION STATES
    const STATE_HOME = 0;
    const STATE_LAUNCH = 1;
    const STATE_GAME = 2;
    const STATE_EXPLOSION = 3;
    const STATE_GAMEOVER = 4;
    let gameState = STATE_HOME;

    // PHYSICS CONFIGURATION
    const HOLES = 24;
    const MAX_IMBALANCE = 2.2;
    const ROTOR_RADIUS = 145;
    const CENTRIFUGE_CENTER = { x: 500, y: 350 };

    // GAME STATE TRACKING DATA
    let board = {};
    let gameMode = "1v1"; 
    let currentTurn = 1;  // 1 = Coral Team, 2 = Blue Team / AI Brain
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
    let runtimeMemoryLeaderboard = [
        {name: "DR_R", score: 14},
        {name: "LAB", score: 9},
        {name: "AMP", score: 5}
    ];

    // Seed procedural chemistry bubbles
    for (let i = 0; i < 25; i++) {
        backgroundBubbles.push({
            x: 760 + Math.random() * 65,
            y: 490 + Math.random() * 110,
            r: Math.random() * 2.5 + 1,
            speed: Math.random() * 25 + 12,
            maxHeight: 450 + Math.random() * 30
        });
    }

    // Initialize clean database state array map
    for (let i = 0; i < HOLES; i++) board[i] = 0;

    // KICKSTART ANIMATION FRAME PIPELINE IMMEDIATELY
    requestAnimationFrame(animateEngine);

    // INLINE PROCEDURAL STARTING COMPILER
    function generateRandomInitialArray() {
        for (let i = 0; i < HOLES; i++) board[i] = 0;
        let placedCoral = 0;
        let placedBlue = 0;
        
        while(placedCoral < 6) {
            let r = Math.floor(Math.random() * HOLES);
            if (board[r] === 0) {
                board[r] = 1;
                placedCoral++;
            }
        }
        while(placedBlue < 6) {
            let r = Math.floor(Math.random() * HOLES);
            if (board[r] === 0) {
                board[r] = 2;
                placedBlue++;
            }
        }

        // Validate that generated starting configurations do not trigger instant explosions
        let p = calculatePhysics(board);
        if (p.mag > 1.3 || p.mag < 0.2 || getValidMoves(board, 1).length === 0 || getValidMoves(board, 2).length === 0) {
            generateRandomInitialArray();
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
        // Update chemical beaker fluid physics animations
        backgroundBubbles.forEach(b => {
            b.y -= b.speed * dt;
            if (b.y < b.maxHeight) {
                b.y = 590;
                b.x = 760 + Math.random() * 65;
            }
        });

        // Hydraulic lift opening translation updates
        if (gameState === STATE_LAUNCH) {
            launchTimer += dt;
            lidOffset = easeOutQuad(Math.min(launchTimer / 1.1, 1.0));
            if (launchTimer >= 1.3) {
                gameState = STATE_GAME;
            }
        }

        // Dynamic chassis screen shake decay processing
        if (screenShake.intensity > 0) {
            screenShake.x = (Math.random() - 0.5) * screenShake.intensity;
            screenShake.y = (Math.random() - 0.5) * screenShake.intensity;
            screenShake.intensity -= dt * 32;
        } else {
            screenShake.x = 0;
            screenShake.y = 0;
        }

        // Velocity tracking logic for structural failure shard explosion particles
        if (gameState === STATE_EXPLOSION) {
            particles.forEach((p, idx) => {
                p.x += p.vx * dt;
                p.y += p.vy * dt;
                p.vy += 420 * dt; 
                p.alpha -= dt * 0.55;
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

        // PERSISTENT STRUCTURAL RENDERS (Background Lab Environment)
        drawLabEnvironmentBackdrop();
        drawCentrifugeCoreUnit();

        ctx.restore();

        // RUNTIME VIEWPORT SCREEN INTERFACE OVERLAYS
        if (gameState === STATE_HOME) drawHomeScreenOverlay();
        if (gameState === STATE_GAMEOVER) drawGameOverScreenOverlay();
    }

    function drawLabEnvironmentBackdrop() {
        // Slate workbench platform deck surface
        ctx.fillStyle = '#141923';
        ctx.fillRect(0, 480, canvas.width, 220);
        ctx.strokeStyle = '#242e42';
        ctx.lineWidth = 4;
        ctx.beginPath(); ctx.moveTo(0, 480); ctx.lineTo(canvas.width, 480); ctx.stroke();

        // HARDWARE UNIT 1: Left-aligned modular test tube storage array rack
        ctx.fillStyle = '#242f41';
        ctx.fillRect(70, 445, 110, 45); 
        for(let i = 0; i < 5; i++) {
            ctx.fillStyle = i % 2 === 0 ? '#ff3366' : '#00ccff';
            ctx.fillRect(82 + (i * 20), 395, 10, 50); 
            ctx.fillStyle = 'rgba(255,255,255,0.18)';
            ctx.fillRect(82 + (i * 20), 395, 3, 50);  
        }
        ctx.strokeStyle = '#3b4b66';
        ctx.lineWidth = 2;
        ctx.strokeRect(70, 395, 110, 95);

        // HARDWARE UNIT 2: Procedural boiling flask station with active liquid solutions
        ctx.fillStyle = '#0a0e17';
        ctx.beginPath(); ctx.arc(790, 550, 42, 0, Math.PI * 2); ctx.fill();
        ctx.fillRect(779, 440, 22, 70); 
        
        // Fluid solution render block
        ctx.fillStyle = 'rgba(147, 51, 234, 0.35)'; 
        ctx.beginPath(); ctx.arc(790, 550, 39, 0, Math.PI); ctx.fill();
        ctx.fillRect(751, 550, 78, 40);

        // Bubbles ascending
        ctx.fillStyle = '#f3e8ff';
        backgroundBubbles.forEach(b => {
            ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2); ctx.fill();
        });

        // Specular glass contour lens line pathing
        ctx.strokeStyle = '#5a6982';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(790, 550, 42, Math.PI * 0.7, Math.PI * 1.3); ctx.stroke();

        // Technical station details
        ctx.fillStyle = '#3b4b66';
        ctx.font = '10px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("OPERATIONAL HUB MODULE V-04", 45, 665);
    }

    function drawCentrifugeCoreUnit() {
        let cx = CENTRIFUGE_CENTER.x;
        let cy = CENTRIFUGE_CENTER.y;

        // Main industrial armor casting bulkhead block
        ctx.fillStyle = '#0f131c';
        ctx.beginPath(); ctx.arc(cx, cy, 235, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#2d3748';
        ctx.lineWidth = 6;
        ctx.stroke();

        // Core containment inner dark vacuum bay
        ctx.fillStyle = '#04060a';
        ctx.beginPath(); ctx.arc(cx, cy, 195, 0, Math.PI*2); ctx.fill();

        if (gameState >= STATE_GAME || gameState === STATE_LAUNCH) {
            // THE INTERNAL ROTATIONAL ROTOR WHEEL ASSEMBLY
            ctx.fillStyle = '#121824';
            ctx.beginPath(); ctx.arc(cx, cy, 172, 0, Math.PI*2); ctx.fill();

            // STABILITY CONSTRAINT BOUNDARY (CRITICAL RED THRESHOLD RING)
            ctx.strokeStyle = 'rgba(255, 51, 102, 0.32)';
            ctx.lineWidth = 2;
            ctx.setLineDash([6, 4]);
            ctx.beginPath(); ctx.arc(cx, cy, MAX_IMBALANCE * 35, 0, Math.PI*2); ctx.stroke();
            ctx.setLineDash([]);

            // LOOP MAP ALL 24 POSITION NODES
            for (let i = 0; i < HOLES; i++) {
                let angle = (i * (360 / HOLES)) * (Math.PI / 180);
                let sx = cx + ROTOR_RADIUS * Math.cos(angle);
                let sy = cy + ROTOR_RADIUS * Math.sin(angle);

                ctx.fillStyle = '#06090e';
                ctx.beginPath(); ctx.arc(sx, sy, 14, 0, Math.PI*2); ctx.fill();
                ctx.strokeStyle = (hoverSlot === i) ? '#00ffcc' : '#232d3f';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Slot index label markers
                ctx.fillStyle = '#4a576d';
                ctx.font = 'bold 9px monospace';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(i, cx + (ROTOR_RADIUS + 23) * Math.cos(angle), cy + (ROTOR_RADIUS + 23) * Math.sin(angle));

                // RENDER INDIVIDUAL ARCADE TEST TUBES
                if (board[i] !== 0) {
                    let isSelected = (selectedSlot === i);
                    drawArcadeTestTube(sx, sy, board[i], isSelected);
                }
            }

            // DYNAMIC MOMENTUM DISPLACEMENT VECTOR TRACKING HUD GAUGE
            let p = calculatePhysics(board);
            let vx = cx + (p.x * 35);
            let vy = cy + (p.y * 35);

            ctx.strokeStyle = 'rgba(0, 255, 170, 0.25)';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(vx, vy); ctx.stroke();

            ctx.fillStyle = (p.mag > MAX_IMBALANCE * 0.75) ? '#ff3366' : '#00ffcc';
            ctx.beginPath(); ctx.arc(vx, vy, 6, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // PREDICTIVE GHOST DISPLACEMENT TELEMETRY TRACKER RENDERING ENGINE
            if (selectedSlot !== null && hoverSlot !== null && board[hoverSlot] === 0) {
                let ghostBoard = {...board};
                ghostBoard[selectedSlot] = 0;
                ghostBoard[hoverSlot] = board[selectedSlot];
                
                let gp = calculatePhysics(ghostBoard);
                let gvx = cx + (gp.x * 35);
                let gvy = cy + (gp.y * 35);

                ctx.strokeStyle = 'rgba(234, 179, 8, 0.45)';
                ctx.lineWidth = 1.5;
                ctx.setLineDash([3, 3]);
                ctx.beginPath(); ctx.moveTo(vx, vy); ctx.lineTo(gvx, gvy); ctx.stroke();
                
                ctx.fillStyle = 'rgba(234, 179, 8, 0.8)';
                ctx.beginPath(); ctx.arc(gvx, gvy, 5, 0, Math.PI*2); ctx.fill();
                ctx.setLineDash([]);
            }

            // INTERACTIVE OPERATING READOUT PANELS
            ctx.fillStyle = '#fff';
            ctx.font = '13px monospace';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'normal';
            ctx.fillText(`DISPLACEMENT FORCE: ${p.mag.toFixed(3)} / ${MAX_IMBALANCE.toFixed(1)} G`, 45, 45);
            ctx.fillText(`OPERATOR TURN: PLAYER ${currentTurn === 1 ? '1 [CORAL]' : '2 [BLUE]'}`, 45, 65);
            ctx.fillText(`STABLE CYCLES: ${scoreCycles}`, 45, 85);

            // STABILITY HEALTH BAR
            ctx.fillStyle = '#1a2333';
            ctx.fillRect(45, 100, 180, 8);
            let fillPercent = Math.min(p.mag / MAX_IMBALANCE, 1.0);
            ctx.fillStyle = (fillPercent > 0.75) ? '#ff3366' : '#00ffcc';
            ctx.fillRect(45, 100, 180 * fillPercent, 8);
        }

        // EXPLOSION VELOCITY DISPLACEMENT FX RENDERS
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

        // HEAVY SHIELDING ENAMEL MECHANICAL SEAL COVER LIDS
        if (gameState === STATE_HOME || gameState === STATE_LAUNCH) {
            let ly = cy - (lidOffset * 650);
            
            ctx.fillStyle = '#e2e8f0';
            ctx.beginPath(); ctx.arc(cx, ly, 226, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#cbd5e1';
            ctx.lineWidth = 4;
            ctx.stroke();

            ctx.fillStyle = '#0a0f18';
            ctx.beginPath(); ctx.arc(cx, ly, 75, 0, Math.PI*2); ctx.fill();
            ctx.strokeStyle = '#64748b';
            ctx.lineWidth = 4;
            ctx.stroke();

            ctx.fillStyle = (Math.floor(Date.now() / 400) % 2 === 0) ? '#00ffcc' : '#00bb99';
            ctx.font = 'bold 11px monospace';
            ctx.textAlign = 'center';
            ctx.fillText("READY PROTOCOL", cx, ly + 4);
        }
    }

    function drawArcadeTestTube(x, y, player, isSelected) {
        ctx.save();
        ctx.translate(x, y);
        
        if (isSelected) {
            ctx.scale(1.2, 1.2);
            ctx.strokeStyle = '#00ffcc';
            ctx.lineWidth = 2;
            ctx.strokeRect(-11, -21, 22, 42);
        }

        // Solid glass resin tracking tube frames
        ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.beginPath();
        ctx.moveTo(-7, -15); ctx.lineTo(7, -15); ctx.lineTo(7, 8);
        ctx.arc(0, 8, 7, 0, Math.PI, false); ctx.lineTo(-7, -15);
        ctx.fill();

        // Liquid volume fillings
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

        // Sheen highlight
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.fillRect(-4, -13, 2, 21);

        // Top sealing caps
        ctx.fillStyle = (player === 1) ? '#ff8aa8' : '#b3f0ff';
        ctx.fillRect(-8, -19, 16, 5);

        ctx.restore();
    }

    function drawHomeScreenOverlay() {
        ctx.fillStyle = 'rgba(4, 6, 10, 0.45)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Central Operations Console Terminal Block
        let menu = { x: 50, y: 120, w: 320, h: 320 };
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(menu.x, menu.y, menu.w, menu.h);
        ctx.strokeStyle = '#23314f';
        ctx.lineWidth = 2;
        ctx.strokeRect(menu.x, menu.y, menu.w, menu.h);

        ctx.fillStyle = '#fff';
        ctx.font = 'bold 24px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("CENTRIFUGE CHESS", menu.x + 20, menu.y + 45);
        
        ctx.fillStyle = '#566885';
        ctx.font = '10px monospace';
        ctx.fillText("ANGULAR TORQUE TACTICAL SIMULATOR", menu.x + 20, menu.y + 65);

        // CORE SYSTEM LAUNCH MENU BUTTON LAYERS
        drawArcadeMenuButton(menu.x + 20, menu.y + 100, 280, 42, "▶ INITIALIZE 1 VS 1 MODE");
        drawArcadeMenuButton(menu.x + 20, menu.y + 155, 280, 42, "▶ INITIALIZE VS COMPUTER");
        
        // INTERNALLY MANAGED COMPACT ARCHIVE SYSTEM BOARD
        ctx.fillStyle = '#8f9fb8';
        ctx.font = 'bold 11px monospace';
        ctx.fillText("--- LAB TELEMETRY ARCHIVE ---", menu.x + 20, menu.y + 230);

        let records = fetchSanitizedLeaderboardRecords();
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
            ctx.fillStyle = '#4a576d';
            ctx.fillText("No current telemetry data logged.", menu.x + 20, menu.y + 255);
        }
    }

    function drawArcadeMenuButton(x, y, w, h, text) {
        let isHovered = (mx >= x && mx <= x + w && my >= y && my <= y + h);

        ctx.fillStyle = isHovered ? '#14253d' : '#060a12';
        ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = isHovered ? '#00ffcc' : '#23314f';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x, y, w, h);

        ctx.fillStyle = isHovered ? '#00ffcc' : '#8f9fb8';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(text, x + w/2, y + h/2);
        ctx.textBaseline = 'normal'; 
    }

    function drawGameOverScreenOverlay() {
        ctx.fillStyle = 'rgba(4, 6, 10, 0.93)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#ff3366';
        ctx.font = 'bold 44px monospace';
        ctx.textAlign = 'center';
        ctx.fillText("🚨 CORE DISRUPTION BLOWOUT 🚨", 500, 230);

        ctx.fillStyle = '#8f9fb8';
        ctx.font = '14px monospace';
        ctx.fillText(`Rotor mechanical stability compromised. Containment yield failed.`, 500, 280);
        
        ctx.fillStyle = '#00ffcc';
        ctx.font = 'bold 18px monospace';
        ctx.fillText(`STABLE OPERATION LOGGED: ${scoreCycles} COMPLETED CYCLES`, 500, 320);

        if (gameMode === "AI") {
            ctx.fillStyle = '#fff';
            ctx.font = '13px monospace';
            ctx.fillText("ENTER OPERATOR ID FOR TELEMETRY SYSTEM LOG (3 CHR):", 500, 375);
            
            ctx.fillStyle = '#070b14';
            ctx.fillRect(440, 395, 120, 36);
            ctx.strokeStyle = '#23314f';
            ctx.strokeRect(440, 395, 120, 36);

            ctx.fillStyle = '#00ffcc';
            ctx.font = 'bold 20px monospace';
            ctx.fillText((nameInputBuffer + "_").substring(0, 4), 500, 421);
            
            ctx.fillStyle = '#4a5568';
            ctx.font = '10px monospace';
            ctx.fillText("[PRESS ENTER KEY TO SAVE TO CACHE]", 500, 455);
        } else {
            drawArcadeMenuButton(380, 380, 240, 45, "RETURN TO ACCESS CONSOLE");
        }
    }

    // COORD CAPTURES
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
            if (mx >= 70 && mx <= 350) {
                if (my >= 220 && my <= 262) { gameMode = "1v1"; triggerLaunchSequence(); }
                if (my >= 275 && my <= 317) { gameMode = "AI"; triggerLaunchSequence(); }
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
                commitSanitizedScoreToLeaderboard(nameInputBuffer, scoreCycles);
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

    function triggerLaunchSequence() {
        generateRandomInitialArray();
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

        for (let i = 0; i < 180; i++) {
            let angle = Math.random() * Math.PI * 2;
            let speed = Math.random() * 340 + 90;
            let clr = Math.random() < 0.5 ? '#ff3366' : '#00ccff';
            if (Math.random() < 0.15) clr = '#ffffff';

            particles.push({
                x: CENTRIFUGE_CENTER.x + (Math.random()-0.5)*70,
                y: CENTRIFUGE_CENTER.y + (Math.random()-0.5)*70,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 60,
                size: Math.random() * 5 + 2,
                color: clr,
                alpha: 1.0,
                rot: Math.random() * 6,
                vRot: (Math.random() - 0.5) * 12
            });
        }
    }

    // SHIELDED STORAGE HANDLERS (TRY-CATCH PROTECTED AGAINST SANDBOX TERMINATIONS)
    function fetchSanitizedLeaderboardRecords() {
        try {
            let raw = localStorage.getItem('centrifuge_chess_scores');
            if (raw) {
                return JSON.parse(raw).sort((a,b) => b.score - a.score).slice(0, 3);
            }
        } catch(e) {
            console.warn("Iframe local storage sandboxed. Falling back to runtime tracking state memory storage layout arrays.");
        }
        return runtimeMemoryLeaderboard.sort((a,b) => b.score - a.score).slice(0, 3);
    }

    function commitSanitizedScoreToLeaderboard(name, score) {
        let cleanName = (name || "AAA").substring(0,3).toUpperCase();
        let current = fetchSanitizedLeaderboardRecords();
        current.push({name: cleanName, score: score});
        let sorted = current.sort((a,b) => b.score - a.score).slice(0, 3);
        
        try {
            localStorage.setItem('centrifuge_chess_scores', JSON.stringify(sorted));
        } catch(e) {
            runtimeMemoryLeaderboard = sorted;
        }
    }

    function easeOutQuad(x) {
        return 1 - (1 - x) * (1 - x);
    }
})();
</script>
</body>
</html>
"""

# Render the self-contained arcade workspace window cleanly inside Streamlit
st.components.v1.html(game_html, height=710, scrolling=False)
