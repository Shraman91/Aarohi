"""
AMERICAN WEDDING - A Romantic CTF in Streamlit
"""

import os
import time
import streamlit as st

from challenges import CHALLENGES
from renderer import render_ring_animation

# ------------------------------------------------------------------ Page Config
st.set_page_config(
    page_title="AMERICAN WEDDING",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------ Terminal CSS (Blush & Rose Theme)
CUSTOM_CSS = """
<style>
/* Reset and white background with pink undertones */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #fff5f7 !important;
    color: #4c0519 !important;
    font-family: 'Fira Code', 'Courier New', Courier, monospace !important;
}

/* Expand block container for full visual spread */
.block-container {
    max-width: 1300px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
}

/* Hide Streamlit default chrome */
#MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {
    visibility: hidden;
    display: none;
}

/* Monospace headings with soft rose glow */
h1, h2, h3, h4, h5, h6 {
    color: #881337 !important;
    font-family: 'Fira Code', 'Courier New', Courier, monospace !important;
    text-shadow: 0 0 12px rgba(244, 63, 94, 0.25);
    letter-spacing: 1px;
}

/* Card styling */
.terminal-card {
    background-color: #ffffff;
    border: 1px solid #fecdd3;
    border-radius: 8px;
    padding: 18px 22px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(244, 114, 182, 0.12);
}

.terminal-card:hover {
    border-color: #f43f5e;
    box-shadow: 0 6px 25px rgba(244, 63, 94, 0.2);
}

/* Badges */
.badge-pwn {
    background: #ffe4e6;
    color: #9f1239;
    border: 1px solid #fda4af;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

.badge-crypto {
    background: #fdf2f8;
    color: #86198f;
    border: 1px solid #f0abfc;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

.badge-osint {
    background: #fff1f2;
    color: #be123c;
    border: 1px solid #fecdd3;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

.badge-sanity {
    background: #fdf4ff;
    color: #a21caf;
    border: 1px solid #f0abfc;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

.badge-stego, .badge-insanity {
    background: #fff1f2;
    color: #e11d48;
    border: 1px solid #fb7185;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

.badge-status-done {
    background: #fce7f3;
    color: #9d174d;
    border: 1px solid #f472b6;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

.badge-status-pending {
    background: #f8fafc;
    color: #64748b;
    border: 1px solid #cbd5e1;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
}

/* Button overrides */
.stButton > button, .stDownloadButton > button {
    background-color: #ffffff !important;
    color: #be123c !important;
    border: 1.5px solid #f43f5e !important;
    border-radius: 4px !important;
    font-family: 'Fira Code', 'Courier New', Courier, monospace !important;
    font-weight: bold !important;
    transition: all 0.2s ease-in-out !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    background-color: #f43f5e !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(244, 63, 94, 0.35) !important;
}

/* Big YES button */
.yes-button > div > button {
    background: linear-gradient(135deg, #f43f5e 0%, #ec4899 50%, #e11d48 100%) !important;
    color: #ffffff !important;
    font-size: 26px !important;
    padding: 16px 50px !important;
    font-weight: 900 !important;
    border: 2px solid #fda4af !important;
    box-shadow: 0 0 35px rgba(244, 63, 94, 0.45) !important;
    letter-spacing: 3px;
    border-radius: 8px !important;
}

.yes-button > div > button:hover {
    background: linear-gradient(135deg, #fb7185 0%, #f43f5e 50%, #e11d48 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 0 50px rgba(244, 63, 94, 0.7) !important;
    transform: scale(1.05);
}

/* Text inputs */
.stTextInput > div > div > input {
    background-color: #ffffff !important;
    color: #4c0519 !important;
    border: 1.5px solid #fda4af !important;
    font-family: 'Fira Code', 'Courier New', Courier, monospace !important;
    border-radius: 4px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #e11d48 !important;
    box-shadow: 0 0 10px rgba(225, 29, 72, 0.25) !important;
}

/* Code blocks & pre */
[data-testid="stCodeBlock"] {
    border: 1px solid #fecdd3 !important;
    border-radius: 6px !important;
    background-color: #fff1f2 !important;
}

[data-testid="stCodeBlock"] pre {
    background-color: #fff1f2 !important;
    color: #9f1239 !important;
    font-family: 'Fira Code', 'Courier New', Courier, monospace !important;
}

[data-testid="stCodeBlock"] code {
    color: #881337 !important;
}

/* Progress bar */
div[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #f43f5e, #ec4899) !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #fecdd3 !important;
    border-radius: 6px !important;
}

[data-testid="stExpander"] summary {
    color: #9f1239 !important;
    font-weight: bold !important;
}

/* Alert boxes */
.terminal-alert-success {
    background-color: #fff1f2;
    border: 1px solid #f43f5e;
    color: #9f1239;
    padding: 12px 16px;
    border-radius: 4px;
    margin: 12px 0;
    font-weight: bold;
}

.terminal-alert-error {
    background-color: #fef2f2;
    border: 1px solid #ef4444;
    color: #991b1b;
    padding: 12px 16px;
    border-radius: 4px;
    margin: 12px 0;
    font-weight: bold;
}

.terminal-easter-egg {
    color: #831843;
    font-style: italic;
    padding: 10px 14px;
    border-left: 3px solid #db2777;
    background: #fdf2f8;
    margin-top: 10px;
    border-radius: 0 4px 4px 0;
}

/* System override box */
.override-container {
    background: #ffffff;
    border: 2px solid #f43f5e;
    border-radius: 8px;
    padding: 30px;
    text-align: center;
    box-shadow: 0 6px 30px rgba(244, 63, 94, 0.2);
    margin: 25px 0;
}

/* Ring Video Player */
div[data-testid="stVideo"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 10px auto 25px auto !important;
}

div[data-testid="stVideo"] > video {
    border-radius: 12px !important;
    border: 2px solid #fda4af !important;
    box-shadow: 0 8px 35px rgba(244, 63, 94, 0.25) !important;
    background-color: #040605 !important;
    max-height: 72vh !important;
    max-width: 100% !important;
    width: auto !important;
    margin: 0 auto !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------ Session State
if "completed" not in st.session_state:
    st.session_state.completed = set()

if "active_challenge" not in st.session_state:
    st.session_state.active_challenge = None

if "reveal" not in st.session_state:
    st.session_state.reveal = False

if "ring_animation_played" not in st.session_state:
    st.session_state.ring_animation_played = False

if "accepted" not in st.session_state:
    st.session_state.accepted = False

if "loading_done" not in st.session_state:
    st.session_state.loading_done = False

# Developer Switch for quick testing (DEV_SKIP=1 or ?dev=1 query parameter)
query_params = st.query_params
dev_mode = (
    os.getenv("DEV_SKIP", "0") == "1"
    or query_params.get("dev", ["0"])[0] == "1"
    or query_params.get("dev", "") == "1"
)

if dev_mode and not st.session_state.reveal:
    st.session_state.completed = set(CHALLENGES.keys())
    st.session_state.reveal = True

# Check if all challenges solved
if len(st.session_state.completed) == len(CHALLENGES):
    st.session_state.reveal = True

# ------------------------------------------------------------------ Top Banner
def render_header():
    banner = r"""
 █████╗ ███╗   ███╗███████╗██████╗ ██╗ ██████╗ █████╗ ███╗   ██╗    ██╗    ██╗███████╗██████╗ ██████╗ ██╗███╗   ██╗ ██████╗ 
██╔══██╗████╗ ████║██╔════╝██╔══██╗██║██╔════╝██╔══██╗████╗  ██║    ██║    ██║██╔════╝██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ 
███████║██╔████╔██║█████╗  ██████╔╝██║██║     ███████║██╔██╗ ██║    ██║ █╗ ██║█████╗  ██║  ██║██║  ██║██║██╔██╗ ██║██║  ██╗
██╔══██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║██║     ██╔══██║██║╚██╗██║    ██║███╗██║██╔══╝  ██║  ██║██║  ██║██║██║╚██╗██║██║   ██║
██║  ██║██║ ╚═╝ ██║███████╗██║  ██║██║╚██████╗██║  ██║██║ ╚████║    ╚███╔███╔╝███████╗██████╔╝██████╔╝██║██║ ╚████║╚██████╔╝
╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝     ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
    """
    st.code(banner, language=None)

# ------------------------------------------------------------------ Final Reveal
def render_reveal():
    container = st.container()
    with container:
        # Step 1: Fake Terminal Loading Sequence (runs once per session)
        if not st.session_state.loading_done:
            status_box = st.empty()
            progress_bar = st.progress(0)
            log_lines = []

            boot_sequence = [
                ("Validating master cryptographic hashes...", 0.20),
                (f"All {len(CHALLENGES)} security protocols cleared.", 0.40),
                ("Compiling feelings...", 0.60),
                ("Decrypting intentions...", 0.80),
                ("Initialising Heart.exe...", 1.00),
            ]

            for msg, frac in boot_sequence:
                log_lines.append(f"> {msg}")
                status_box.markdown(
                    f"<div class='terminal-card' style='font-size: 15px; color: #be123c; font-weight: bold;'>"
                    + "<br>".join(log_lines)
                    + "</div>",
                    unsafe_allow_html=True,
                )
                progress_bar.progress(frac)
                time.sleep(0.6)

            time.sleep(0.4)
            status_box.empty()
            progress_bar.empty()
            st.session_state.loading_done = True

        # Pre-allocate containers so override prompt and YES button are interactive immediately
        ring_placeholder = st.empty()
        override_placeholder = st.empty()
        yes_placeholder = st.empty()
        status_placeholder = st.empty()

        # Step 2: Proposal Message
        override_placeholder.markdown(
            """
            <div class="override-container">
                <div style="color: #e11d48; font-size: 24px; font-weight: bold; letter-spacing: 1px; margin-bottom: 14px;">
                    So proud of you for solving the questions my love!!!
                </div>
                <div style="color: #881337; font-size: 19px; margin: 10px 0; font-style: italic;">
                    U da real CTF heh.
                </div>
                <div style="color: #4c0519; font-size: 22px; font-weight: 900; margin-top: 18px;">
                    So whats your answer ^^
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Step 3: The Proposal Buttons (yes and YESS!!!!)
        if not st.session_state.accepted:
            col1, col2, col3, col4 = yes_placeholder.columns([1, 2, 2, 1])
            with col2:
                st.markdown('<div class="yes-button">', unsafe_allow_html=True)
                if st.button("yes", use_container_width=True, key="proposal_yes"):
                    st.session_state.accepted = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="yes-button">', unsafe_allow_html=True)
                if st.button("YESS!!!!", use_container_width=True, key="proposal_yess"):
                    st.session_state.accepted = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            yes_placeholder.empty()

        # Step 4: Post-Acceptance Celebration
        if st.session_state.accepted:
            status_placeholder.markdown(
                """
                <div class="terminal-card" style="border: 2px solid #f43f5e; text-align: center; padding: 35px 25px; box-shadow: 0 4px 35px rgba(244, 63, 94, 0.25);">
                    <h1 style="color: #be123c !important; font-size: 26px; line-height: 1.5; margin: 15px 0; font-weight: bold;">
                        Heh, knew you'd say yes, you're all mine now (you dont have a choice)
                    </h1>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Step 5: Infinite Live 3D ASCII Animation
        render_ring_animation(ring_placeholder, mono=False, infinite=True)

# ------------------------------------------------------------------ Challenge Page
def render_challenge_view(c_id: str):
    c_cls = CHALLENGES[c_id]
    is_done = c_id in st.session_state.completed

    # Navigation header
    col_nav, col_status = st.columns([3, 1])
    with col_nav:
        if st.button("<- RETURN TO CHALLENGES", key=f"back_{c_id}"):
            st.session_state.active_challenge = None
            st.rerun()
    with col_status:
        status_html = (
            '<span class="badge-status-done">SOLVED [OK]</span>'
            if is_done
            else '<span class="badge-status-pending">PENDING [ ]</span>'
        )
        st.markdown(f"<div style='text-align: right; padding-top: 5px;'>{status_html}</div>", unsafe_allow_html=True)

    # Challenge Title & Category
    badge_class = f"badge-{c_cls.category.lower()}"
    st.markdown(
        f"<h2>{c_cls.title} "
        f"<span class='{badge_class}'>{c_cls.category}</span> "
        f"<span style='color: #9f1239; font-size: 14px;'>[{c_cls.difficulty}]</span></h2>",
        unsafe_allow_html=True,
    )

    # Scenario
    st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
    st.markdown(c_cls.scenario)

    # Challenge-specific content
    if c_id == "binary":
        src = c_cls.get_source_code()
        if src:
            st.markdown("#### Vulnerable Source (`vuln.c`)")
            st.code(src, language="c")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.download_button(
                    label="DOWNLOAD vuln.c",
                    data=src,
                    file_name="vuln.c",
                    mime="text/plain",
                    use_container_width=True,
                )
            with col_b2:
                bin_data = c_cls.get_binary_bytes()
                if bin_data:
                    st.download_button(
                        label="DOWNLOAD Compiled vuln (ELF)",
                        data=bin_data,
                        file_name="vuln",
                        mime="application/octet-stream",
                        use_container_width=True,
                    )
                else:
                    st.button("[!] Binary Available via Dockerfile", disabled=True, use_container_width=True)

    elif c_id == "crypto":
        st.markdown("#### Classified Intercepted Ciphertext")
        st.code(c_cls.CIPHERTEXT, language=None)

    elif c_id == "insanity":
        st.markdown("#### Intercepted Terminal Stream")
        st.markdown(c_cls.get_html_payload(), unsafe_allow_html=True)

    elif c_id in ["sanity", "osint"]:
        pass

    st.markdown('</div>', unsafe_allow_html=True)

    # Hints Expander
    with st.expander("[+] INTEL DECRYPT HINTS"):
        for i, hint in enumerate(c_cls.hints, start=1):
            st.markdown(f"**Hint {i}:** {hint}")

    # Flag Submission Form
    st.markdown("### SUBMIT PROTOCOL FLAG")
    flag_input = st.text_input(
        "Enter Flag (e.g. CTF{...})",
        key=f"input_{c_id}",
        placeholder="CTF{...}",
        disabled=is_done,
    )

    if not is_done:
        if st.button("SUBMIT FLAG", key=f"btn_{c_id}", use_container_width=True):
            if c_cls.check_flag(flag_input):
                st.session_state.completed.add(c_id)
                st.markdown(
                    f'<div class="terminal-alert-success">'
                    f'<strong>[ ACCESS GRANTED ]</strong> Correct flag verified! Challenge marked complete.'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="terminal-easter-egg">{c_cls.EASTER_EGG}</div>',
                    unsafe_allow_html=True,
                )
                time.sleep(1.2)
                st.rerun()
            else:
                st.markdown(
                    '<div class="terminal-alert-error">'
                    '[ ACCESS DENIED ] Invalid key. Hash mismatch detected.'
                    '</div>',
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            '<div class="terminal-alert-success">'
            '<strong>[ COMPLETED ]</strong> You have already captured this flag.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="terminal-easter-egg">{c_cls.EASTER_EGG}</div>',
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------------ Mission Control Landing
def render_mission_control():
    render_header()

    completed_count = len(st.session_state.completed)
    total_challenges = len(CHALLENGES)

    # Progress Bar & Tracker
    st.markdown(f"### {total_challenges} CHALLENGES")
    st.progress(completed_count / total_challenges)
    st.markdown(
        f"<div style='color: #be123c; margin-bottom: 25px; font-weight: bold;'>"
        f"PROGRESS: [{completed_count}/{total_challenges}] NODES LIBERATED "
        f"({'READY FOR OVERRIDE' if completed_count == total_challenges else 'IN PROGRESS'})"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Challenge Cards
    for c_id, c_cls in CHALLENGES.items():
        is_done = c_id in st.session_state.completed
        badge_class = f"badge-{c_cls.category.lower()}"
        status_badge = (
            '<span class="badge-status-done">SOLVED [OK]</span>'
            if is_done
            else '<span class="badge-status-pending">PENDING [ ]</span>'
        )

        with st.container():
            st.markdown(
                f"""
                <div class="terminal-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 18px; font-weight: bold; color: #4c0519;">{c_cls.title}</span>
                        <div>
                            <span class="{badge_class}">{c_cls.category}</span>
                            <span style="color: #9f1239; font-size: 12px; margin-left: 6px;">[{c_cls.difficulty}]</span>
                            <span style="margin-left: 10px;">{status_badge}</span>
                        </div>
                    </div>
                    <div style="color: #881337; font-size: 13px; line-height: 1.5; margin-bottom: 15px;">
                        {c_cls.scenario.strip().splitlines()[0]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_btn, _ = st.columns([1, 3])
            with col_btn:
                btn_label = f"REVIEW NODE [ {c_cls.category} ]" if is_done else f"ACCESS NODE [ {c_cls.category} ]"
                if st.button(btn_label, key=f"card_{c_id}", use_container_width=True):
                    st.session_state.active_challenge = c_id
                    st.rerun()

    # Reset / Dev footer helper
    st.markdown("<hr style='border: 1px solid #fecdd3; margin-top: 40px;'>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns([3, 1])
    with col_f2:
        if st.button("RESET PROTOCOL SESSION", key="reset_session"):
            st.session_state.completed = set()
            st.session_state.active_challenge = None
            st.session_state.reveal = False
            st.session_state.ring_animation_played = False
            st.session_state.ring_intro_played = False
            st.session_state.accepted = False
            st.session_state.loading_done = False
            st.rerun()

# ------------------------------------------------------------------ Main Router
def main():
    if st.session_state.reveal:
        render_reveal()
    elif st.session_state.active_challenge:
        render_challenge_view(st.session_state.active_challenge)
    else:
        render_mission_control()

if __name__ == "__main__":
    main()

