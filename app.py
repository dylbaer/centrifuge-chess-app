import streamlit as st
import numpy as np
import plotly.graph_objects as go
import json
import os
import random

# --- CONFIGURATION ---
HOLES = 24
MAX_IMBALANCE = 2.0  # Safe structural threshold for a 24-hole rotor
LEADERBOARD_FILE = "leaderboard_v2.json"

st.set_page_config(page_title="Centrifuge Chess Pro", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM LAB-BENCH STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stSelectbox label { color: #00ffcc !important; font-weight: bold; }
    .stRadio label { color: #ffffff !important; }
    div[data-testid="stMetricValue"] { color: #ff0055; font-family: 'Courier New', monospace; }
    .status-box { padding: 15px; border-radius: 8px; border: 1px solid #333; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- CORE PHYSICS ENGINE ---
def calculate_imbalance(board):
    """Calculates the center of mass vector magnitude of the rotor."""
    x_sum, y_sum = 0.0, 0.0
    for pos, player in board.items():
        if player != 0:
            angle = np.radians(pos * (360 / HOLES))
            x_sum += np.cos(angle)
            y_sum += np.sin(angle)
    magnitude = np.sqrt(x_sum**2 + y_sum**2)
    return magnitude, x_sum, y_sum

def get_valid_moves(board, player):
    """Returns all legal (from_pos, to_pos) moves that do not instantly exceed MAX_IMBALANCE."""
    valid_moves = []
    my_tubes = [pos for pos, p in board.items() if p == player]
    empty_holes = [pos for pos, p in board.items() if p == 0]
    
    for start in my_tubes:
        for end in empty_holes:
            temp_board = board.copy()
            temp_board[start] = 0
            temp_board[end] = player
            imbalance, _, _ = calculate_imbalance(temp_board)
            if imbalance <= MAX_IMBALANCE:
                valid_moves.append((start, end))
    return valid_moves

# --- SMART LAB-AI BRAIN ---
def get_best_ai_move(board):
    """Evaluates moves to minimize human options (trap strategy) and preserve AI stability."""
    valid_ai_moves = get_valid_moves(board, 2)
    if not valid_ai_moves:
        return None
        
    best_move = None
    min_human_options = 999
    best_stability = 999

    # Look ahead 1 step
    for ai_move in valid_ai_moves:
        start, end = ai_move
        simulated_board = board.copy()
        simulated_board[start] = 0
        simulated_board[end] = 2
        
        # How many legal moves will the human have left?
        human_options = len(get_valid_moves(simulated_board, 1))
        ai_imbalance, _, _ = calculate_imbalance(simulated_board)
        
        # Priority 1: Starve the human of options. Priority 2: Stay perfectly stable.
        if human_options < min_human_options:
            min_human_options = human_options
            best_stability = ai_imbalance
            best_move = ai_move
        elif human_options == min_human_options:
            if ai_imbalance < best_stability:
                best_stability = ai_imbalance
                best_move = ai_move
                
    return best_move if best_move else random.choice(valid_ai_moves)

# --- STATE INITIALIZATION ---
def init_game():
    st.session_state.board = {i: 0 for i in range(HOLES)}
    
    # Player 1 (Red): Perfect balanced hexagon layout
    for pos in [0, 4, 8, 12, 16, 20]:
        st.session_state.board[pos] = 1
        
    # Player 2 (Blue/AI): Perfectly balanced alternating hexagon layout
    for pos in [2, 6, 10, 14, 18, 22]:
        st.session_state.board[pos] = 2
    
    st.session_state.turn = 1
    st.session_state.game_over = False
    st.session_state.status_msg = "🚨 Systems Nominal. Rotor is perfectly balanced. Player 1, break the symmetry."
    st.session_state.moves_survived = 0

if 'board' not in st.session_state:
    init_game()

# --- EPHEMERAL LEADERBOARD ---
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_score(name, score):
    lb = load_leaderboard()
    lb.append({"name": name, "score": score})
    lb = sorted(lb, key=lambda x: x['score'], reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f)

# --- ADVANCED UI GRAPHICS ---
def draw_advanced_rotor():
    board = st.session_state.board
    fig = go.Figure()

    # Outer metal shroud of the centrifuge
    fig.add_shape(type="circle", xref="x", yref="y", x0=-1.4, y0=-1.4, x1=1.4, y1=1.4,
                  line=dict(color="#444", width=3), fillcolor="#1f242d")
    
    # The rotating internal rotor assembly
    fig.add_shape(type="circle", xref="x", yref="y", x0=-1.15, y0=-1.15, x1=1.15, y1=1.15,
                  line=dict(color="#666", width=1), fillcolor="#11141a")

    # DANGER ZONE BOUNDARY RING
    fig.add_shape(type="circle", xref="x", yref="y", 
                  x0=-MAX_IMBALANCE, y0=-MAX_IMBALANCE, x1=MAX_IMBALANCE, y1=MAX_IMBALANCE,
                  line=dict(color="rgba(255, 0, 85, 0.35)", width=2, dash="dash"))

    # Render structural positions and slots
    for pos in range(HOLES):
        angle = np.radians(pos * (360 / HOLES))
        x, y = np.cos(angle), np.sin(angle)
        
        color = "#222733"  # Empty slot
        line_clr = "#444"
        if board[pos] == 1: 
            color = "#ff3366"  # P1 Neon Coral
            line_clr = "#ffffff"
        elif board[pos] == 2: 
            color = "#00ccff"  # P2 Bio-Electric Blue
            line_clr = "#ffffff"
        
        fig.add_shape(type="circle", xref="x", yref="y",
                      x0=x-0.08, y0=y-0.08, x1=x+0.08, y1=y+0.08,
                      line=dict(color=line_clr, width=1.5), fillcolor=color)
        
        # Pinpoint text numbers
        fig.add_annotation(x=x*1.28, y=y*1.28, text=str(pos), showarrow=False, 
                           font=dict(size=10, color="#8892b0", family="Courier New"))

    # Compute Real-time Center of Mass Displacement Vector
    imbalance, x_sum, y_sum = calculate_imbalance(board)
    
    # Vector trail line
    fig.add_trace(go.Scatter(x=[0, x_sum], y=[0, y_sum], mode="lines",
                             line=dict(color="#00ffcc", width=3)))
    # Pulsing vector node
    node_color = "#ff0055" if imbalance > (MAX_IMBALANCE * 0.75) else "#00ffcc"
    fig.add_trace(go.Scatter(x=[x_sum], y=[y_sum], mode="markers",
                             marker=dict(symbol="circle-dot", size=14, color=node_color, line=dict(color="#fff", width=2))))

    fig.update_layout(xaxis=dict(visible=False, range=[-2.2, 2.2]), 
                      yaxis=dict(visible=False, range=[-2.2, 2.2]),
                      width=550, height=550, showlegend=False, 
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=10, r=10, t=10, b=10))
    return fig, imbalance

# --- INTERACTIVE DASHBOARD ENVIRONMENT ---
st.title("⚡ CENTRIFUGE CHESS: ADVANCED ROTOR TACTICS")
st.caption("A physics-based strategic duel for bench scientists.")
st.write("---")

col_left, col_right = st.columns([1.3, 1])

with col_left:
    fig, current_imbalance = draw_advanced_rotor()
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_right:
    st.header("⚙️ Control Panel")
    mode = st.radio("Select Operational Protocol:", ["1v1 Local (Vs Colleague)", "Single Player (Vs Advanced AI)"], on_change=init_game)
    
    if st.button("Emergency System Reset (Restart)"):
        init_game()
        st.rerun()

    # Dynamic status boxes depending on danger state
    box_color = "#1f1f2e"
    if current_imbalance > (MAX_IMBALANCE * 0.75):
        box_color = "#4a1525" # Deep warning crimson
        
    st.markdown(f'<div class="status-box" style="background-color: {box_color};"><h4>{st.session_state.status_msg}</h4></div>', unsafe_allow_html=True)

    # Metric tracking
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="Current G-Force Imbalance Vector", value=f"{current_imbalance:.3f}")
    with c2:
        st.metric(label="Structural Yield Limit", value=f"{MAX_IMBALANCE:.1f}")

    if not st.session_state.game_over:
        current_player = st.session_state.turn
        p_name = "Player 1 (Coral)" if current_player == 1 else "Player 2 (Electric Blue)"
        
        st.subheader(f"Current Authorization: {p_name}")

        my_tubes = [pos for pos, p in st.session_state.board.items() if p == current_player]
        empty_holes = [pos for pos, p in st.session_state.board.items() if p == 0]

        cc1, cc2 = st.columns(2)
        with cc1:
            from_pos = st.selectbox("Extract Tube From Unit:", my_tubes, key="from_p")
        with cc2:
            to_pos = st.selectbox("Insert Tube Into Unit:", empty_holes, key="to_p")

        # Live predictive physics safety calculation
        test_board = st.session_state.board.copy()
        test_board[from_pos] = 0
        test_board[to_pos] = current_player
        pred_imb, _, _ = calculate_imbalance(test_board)
        
        if pred_imb > MAX_IMBALANCE:
            st.warning(f"⚠️ CRITICAL WARNING: This move creates an imbalance of {pred_imb:.2f}! Locking this will trigger immediate catastrophic failure.")
        elif pred_imb < 0.01:
            st.success("✨ HARMONY PREDICTION: This move achieves zero net torque. You will win instantly if locked!")

        if st.button("⚡ EXECUTE DEVIATION (LOCK MOVE)"):
            # Commit Move
            st.session_state.board[from_pos] = 0
            st.session_state.board[to_pos] = current_player
            
            # Re-evaluate system state
            new_imbalance, _, _ = calculate_imbalance(st.session_state.board)
            
            if new_imbalance > MAX_IMBALANCE:
                st.session_state.game_over = True
                st.session_state.status_msg = f"💥 ROTOR EXPLOSION! {p_name} destroyed the equipment. Opponent wins!"
            elif new_imbalance < 0.01:
                st.session_state.game_over = True
                st.session_state.status_msg = f"⚖️ PERFECTION! {p_name} counter-balanced the array flawlessly and won!"
            else:
                # Turn Handshake
                st.session_state.turn = 3 - current_player
                st.session_state.moves_survived += 1
                st.session_state.status_msg = f"Move successful. System torque modified. Handing controls to next operator."
                
                # Checkmate Scan
                if len(get_valid_moves(st.session_state.board, st.session_state.turn)) == 0:
                     st.session_state.game_over = True
                     opp_name = "Player 2" if st.session_state.turn == 1 else "Player 1"
                     st.session_state.status_msg = f"♟️ STRUCTURAL CHECKMATE! {opp_name} has no moves left that don't destroy the chamber. {p_name} wins!"

            st.rerun()

    # --- ENHANCED LOOKAHEAD AI PHASE ---
    if not st.session_state.game_over and mode == "Single Player (vs Advanced AI)" and st.session_state.turn == 2:
        with st.spinner("AI calculating angular trajectories..."):
            ai_move = get_best_ai_move(st.session_state.board)
            
            if not ai_move:
                st.session_state.game_over = True
                st.session_state.status_msg = "♟️ STRUCTURAL CHECKMATE! The AI was out-maneuvered and has no legal vectors left. YOU WIN!"
            else:
                ai_from, ai_to = ai_move
                st.session_state.board[ai_from] = 0
                st.session_state.board[ai_to] = 2
                
                new_imbalance, _, _ = calculate_imbalance(st.session_state.board)
                if new_imbalance < 0.01:
                    st.session_state.game_over = True
                    st.session_state.status_msg = "⚖️ AI reached perfect balance counterweighting. AI wins!"
                else:
                    st.session_state.turn = 1
                    st.session_state.status_msg = f"🤖 AI calculated counter-forces and shifted tube {ai_from} → {ai_to}. Your turn."
                st.rerun()

# --- HIGH SCORE ARCHIVE ---
if mode == "Single Player (vs Advanced AI)" and st.session_state.game_over:
     st.write("---")
     st.subheader("📊 Session Telemetry Record")
     st.info(f"You maintained system integrity for {st.session_state.moves_survived} structural alterations.")
     
     score_name = st.text_input("Enter Initials for Lab Archive:", max_chars=3)
     if st.button("Commit Score to Log"):
         if score_name:
             save_score(score_name.upper(), st.session_state.moves_survived)
             st.success("Data filed successfully!")
             st.rerun()

st.write("---")
st.subheader("🏆 Top Lab Operators (Most Moves Survived)")
lb = load_leaderboard()
if lb:
    # Render sleek technical display table
    st.table(lb)
else:
    st.caption("No archived runs found. Calibrate the machine and set the standard.")
