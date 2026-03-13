import streamlit as st
import av
import threading
import time
import streamlit.components.v1 as components
from textwrap import dedent
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from streamlit_autorefresh import st_autorefresh
from sign_predictor import SignLanguagePredictor

st.set_page_config(page_title="AI Sign Language Detector", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "home"

if "stage_index" not in st.session_state:
    st.session_state.stage_index = 0

if "stage_started" not in st.session_state:
    st.session_state.stage_started = False

if "stage_start_time" not in st.session_state:
    st.session_state.stage_start_time = None

if "stage_status" not in st.session_state:
    st.session_state.stage_status = "idle"

if "stage_feedback" not in st.session_state:
    st.session_state.stage_feedback = ""


def html(block: str):
    st.markdown(dedent(block), unsafe_allow_html=True)


STAGES = [
    {"target": "Hungry", "label": "Hungry"},
    {"target": "Sleepy", "label": "Sleepy"},
    {"target": "Drink", "label": "Drink"},
    {"target": "Yes", "label": "Yes"},
]


st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 20% 20%, rgba(129, 212, 250, 0.25), transparent 25%),
            radial-gradient(circle at 80% 30%, rgba(56, 189, 248, 0.22), transparent 22%),
            radial-gradient(circle at 50% 80%, rgba(125, 211, 252, 0.18), transparent 25%),
            linear-gradient(135deg, #eef9ff 0%, #dff2ff 40%, #caeaff 100%);
        color: #12324a;
        overflow-x: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0rem !important;
    }

    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }

    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }

    .main .block-container {
        max-width: 100% !important;
    }

    section.main > div {
        max-width: 100% !important;
    }

    .nav-wrap {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 4px 18px 4px;
        animation: fadeDown 0.7s ease;
    }

    .nav-logo {
        font-size: 1.15rem;
        font-weight: 800;
        color: #0c4a6e;
        letter-spacing: 0.2px;
    }

    .nav-tag {
        color: #4a7895;
        font-size: 0.92rem;
        font-weight: 600;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(255,255,255,0.65);
        border: 1px solid rgba(160, 220, 255, 0.65);
        border-radius: 999px;
        padding: 10px 16px;
        color: #0b5f8a;
        font-weight: 700;
        margin-bottom: 18px;
        box-shadow: 0 8px 25px rgba(65, 140, 190, 0.10);
    }

    .eyebrow-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #38bdf8;
        animation: pulse 1.5s infinite;
    }

    .hero-title {
        font-size: 4rem;
        line-height: 1.02;
        font-weight: 900;
        color: #093b5b;
        margin-bottom: 16px;
        letter-spacing: -1.3px;
        animation: fadeUp 1s ease;
    }

    .hero-highlight {
        background: linear-gradient(90deg, #0284c7, #38bdf8, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shimmer 4s linear infinite;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        line-height: 1.75;
        color: #416d89;
        max-width: 760px;
        margin-bottom: 26px;
        animation: fadeUp 1.15s ease;
    }

    .features-wrap {
        margin-top: 34px;
        animation: fadeUp 1.45s ease;
    }

    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 22px;
    }

    .feature-card {
        background: rgba(255,255,255,0.68);
        border: 1px solid rgba(160, 220, 255, 0.5);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 12px 30px rgba(44, 111, 161, 0.10);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: fadeUp 0.8s ease;
        min-height: 200px;
    }

    .feature-card:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow: 0 18px 36px rgba(44, 111, 161, 0.16);
    }

    .feature-icon {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        background: linear-gradient(135deg, #d9f3ff, #a7e1ff);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 14px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.65);
    }

    .feature-title {
        font-size: 1.12rem;
        font-weight: 800;
        color: #0f4c75;
        margin-bottom: 8px;
    }

    .feature-text {
        color: #5a8099;
        line-height: 1.75;
        font-size: 0.98rem;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f4c75;
        margin-bottom: 0.8rem;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.62);
        border: 1px solid rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 18px 20px;
        box-shadow: 0 10px 30px rgba(30, 90, 140, 0.12);
        animation: fadeUp 0.6s ease;
    }

    .prediction-main {
        font-size: 2rem;
        font-weight: 800;
        color: #0077b6;
        line-height: 1.1;
        margin-bottom: 0.2rem;
        animation: glowPulse 1.8s ease-in-out infinite;
    }

    .prediction-label {
        color: #4a7895;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
    }

    .mini-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
        margin-top: 10px;
        margin-bottom: 14px;
    }

    .mini-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(238,248,255,0.92));
        border-radius: 18px;
        padding: 16px;
        border: 1px solid rgba(140, 200, 235, 0.45);
        box-shadow: 0 6px 18px rgba(80, 150, 210, 0.10);
    }

    .mini-title {
        color: #5682a1;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }

    .mini-value {
        color: #0b5f8a;
        font-size: 1.2rem;
        font-weight: 700;
    }

    .status-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }

    .pulse-dot {
        width: 12px;
        height: 12px;
        border-radius: 999px;
        background: #38bdf8;
        box-shadow: 0 0 0 rgba(56,189,248, 0.5);
        animation: pulse 1.6s infinite;
    }

    .status-text {
        color: #3d6b88;
        font-weight: 600;
    }

    .top3-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(150, 205, 235, 0.35);
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 10px;
        animation: fadeUp 0.4s ease;
    }

    .top3-name {
        font-weight: 700;
        color: #0f4c75;
    }

    .top3-score {
        color: #0077b6;
        font-weight: 700;
    }

    video {
        width: 100% !important;
        height: auto !important;
        max-height: 360px !important;
        object-fit: contain !important;
        border-radius: 20px !important;
        background: #dcebfa !important;
        box-shadow: 0 10px 30px rgba(30, 90, 140, 0.14) !important;
    }

    div[data-testid="stVideo"] video {
        max-height: 360px !important;
        object-fit: contain !important;
    }

    @keyframes pulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(56,189,248, 0.55);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 14px rgba(56,189,248, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(56,189,248, 0);
        }
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(18px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeDown {
        from {
            opacity: 0;
            transform: translateY(-16px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes glowPulse {
        0% { text-shadow: 0 0 0 rgba(0,119,182,0); }
        50% { text-shadow: 0 0 18px rgba(56,189,248,0.26); }
        100% { text-shadow: 0 0 0 rgba(0,119,182,0); }
    }

    @keyframes shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }

    @media (max-width: 1100px) {
        .hero-title {
            font-size: 3rem;
        }

        .features-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)


class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.predictor = SignLanguagePredictor(confidence_threshold=0.2)
        self.result = {
            "frames_collected": 0,
            "frames_needed": 45,
            "prediction": "Collecting...",
            "confidence": 0.0,
            "top3": []
        }
        self.lock = threading.Lock()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        processed_frame, result = self.predictor.process_frame(img)

        with self.lock:
            self.result = result.copy()

        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")


def go_home():
    st.session_state.page = "home"

def go_demo():
    st.session_state.page = "demo"

def go_stage():
    st.session_state.page = "stage"

def start_stage():
    st.session_state.stage_started = True
    st.session_state.stage_start_time = time.time()
    st.session_state.stage_status = "running"
    st.session_state.stage_feedback = ""

def reset_stage():
    st.session_state.stage_started = False
    st.session_state.stage_start_time = None
    st.session_state.stage_status = "idle"
    st.session_state.stage_feedback = ""

def next_stage():
    if st.session_state.stage_index < len(STAGES) - 1:
        st.session_state.stage_index += 1
    reset_stage()


if st.session_state.page == "home":
    html("""
    <div class="nav-wrap">
        <div class="nav-logo">SignSense AI</div>
        <div class="nav-tag">Smart hand sign recognition demo</div>
    </div>
    """)

    left_col, right_col = st.columns([1.15, 1.0], gap="large")

    with left_col:
        html("""
        <div class="eyebrow">
            <span class="eyebrow-dot"></span>
            Real-time AI accessibility demo
        </div>
        """)

        st.markdown(
            """
            <div class="hero-title">
                Read hand signs<br>
                <span class="hero-highlight">live and instantly</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="hero-subtitle">
                A sleek real-time sign language detection experience powered by MediaPipe landmark tracking
                and an LSTM classification model. Designed to make communication feel faster, smarter,
                and more interactive.
            </div>
            """,
            unsafe_allow_html=True
        )

        btn1, btn2, btn3 = st.columns([0.42, 0.32, 0.18])
        with btn1:
            if st.button("Try Live Demo", use_container_width=True, type="primary"):
                go_demo()
                st.rerun()
        with btn2:
            if st.button("Stage Mode", use_container_width=True):
                go_stage()
                st.rerun()
        with btn3:
            st.button("Info", use_container_width=True)

    with right_col:
        components.html(
            """
            <div style="
                position: relative;
                min-height: 560px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 10px;
            ">
                <div style="
                    position:absolute;
                    width:180px;height:180px;border-radius:999px;
                    background: rgba(56, 189, 248, 0.26);
                    top:30px;right:10px;
                    filter: blur(10px);
                    animation: floatBlob 9s ease-in-out infinite;
                "></div>

                <div style="
                    position:absolute;
                    width:130px;height:130px;border-radius:999px;
                    background: rgba(125, 211, 252, 0.22);
                    bottom:40px;left:10px;
                    filter: blur(10px);
                    animation: floatBlob 9s ease-in-out infinite;
                    animation-delay:1.5s;
                "></div>

                <div style="
                    position: relative;
                    width: 100%;
                    max-width: 560px;
                    background: rgba(255,255,255,0.64);
                    border: 1px solid rgba(255,255,255,0.6);
                    border-radius: 30px;
                    padding: 24px;
                    backdrop-filter: blur(14px);
                    box-shadow: 0 20px 45px rgba(44, 111, 161, 0.18);
                    overflow: hidden;
                ">
                    <div style="
                        background: linear-gradient(180deg, #f8fdff, #e5f5ff);
                        border-radius: 24px;
                        padding: 20px;
                        min-height: 380px;
                        position: relative;
                        overflow: hidden;
                        border: 1px solid rgba(160, 220, 255, 0.45);
                    ">
                        <div style="
                            height: 210px;
                            border-radius: 20px;
                            background:
                                linear-gradient(135deg, rgba(12,74,110,0.08), rgba(56,189,248,0.18)),
                                radial-gradient(circle at 75% 25%, rgba(56,189,248,0.30), transparent 25%),
                                linear-gradient(135deg, #effaff, #d8f0ff);
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            color:#0c4a6e;
                            font-size:1.05rem;
                            font-weight:800;
                            margin-bottom:18px;
                            position:relative;
                            overflow:hidden;
                        ">
                            Live camera + AI prediction preview
                            <div style="
                                position:absolute;
                                width:100%;
                                height:4px;
                                background: linear-gradient(90deg, transparent, rgba(56,189,248,0.95), transparent);
                                top:0;
                                left:0;
                                animation: scanMove 2.5s linear infinite;
                            "></div>
                        </div>

                        <div style="
                            display:grid;
                            grid-template-columns:1fr 1fr;
                            gap:14px;
                            margin-top:12px;
                        ">
                            <div style="background:rgba(255,255,255,0.75);border:1px solid rgba(160,220,255,0.4);border-radius:18px;padding:16px;">
                                <div style="color:#6390ab;font-size:0.82rem;margin-bottom:5px;">Prediction</div>
                                <div style="color:#0077b6;font-size:1.35rem;font-weight:800;">Yes</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.75);border:1px solid rgba(160,220,255,0.4);border-radius:18px;padding:16px;">
                                <div style="color:#6390ab;font-size:0.82rem;margin-bottom:5px;">Confidence</div>
                                <div style="color:#0077b6;font-size:1.35rem;font-weight:800;">0.965</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.75);border:1px solid rgba(160,220,255,0.4);border-radius:18px;padding:16px;">
                                <div style="color:#6390ab;font-size:0.82rem;margin-bottom:5px;">Frames</div>
                                <div style="color:#0077b6;font-size:1.35rem;font-weight:800;">45/45</div>
                            </div>
                            <div style="background:rgba(255,255,255,0.75);border:1px solid rgba(160,220,255,0.4);border-radius:18px;padding:16px;">
                                <div style="color:#6390ab;font-size:0.82rem;margin-bottom:5px;">Status</div>
                                <div style="color:#0077b6;font-size:1.35rem;font-weight:800;">Live</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style>
            @keyframes floatBlob {
                0%   { transform: translateY(0px) translateX(0px); }
                25%  { transform: translateY(-18px) translateX(8px); }
                50%  { transform: translateY(8px) translateX(-10px); }
                75%  { transform: translateY(-10px) translateX(12px); }
                100% { transform: translateY(0px) translateX(0px); }
            }
            @keyframes scanMove {
                0% { top: -5px; }
                100% { top: 100%; }
            }
            </style>
            """,
            height=520,
        )

    html("""
    <div class="features-wrap">
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Real-Time Detection</div>
                <div class="feature-text">
                    Recognizes sign gestures from a live webcam feed with instant predictions and continuous updates.
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🫱</div>
                <div class="feature-title">Landmark Tracking</div>
                <div class="feature-text">
                    Uses pose and hand landmarks to capture motion patterns and body alignment for more reliable classification.
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">AI Sequence Model</div>
                <div class="feature-text">
                    An LSTM-based model reads motion over time instead of a single frame, making the recognition smarter and more context-aware.
                </div>
            </div>
        </div>
    </div>
    """)

elif st.session_state.page == "demo":
    st_autorefresh(interval=2000, key="prediction_refresh")

    back1, back2 = st.columns([0.12, 0.88])
    with back1:
        if st.button("← Back Home", use_container_width=True):
            go_home()
            st.rerun()

    st.markdown(
        '<div class="hero-title" style="font-size:2.8rem; margin-top:10px;">AI Sign Language Detector</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="hero-subtitle" style="margin-bottom:1.4rem;">Live Thai sign recognition with MediaPipe + LSTM</div>',
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">Camera Feed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        ctx = webrtc_streamer(
            key="sign-detection",
            video_processor_factory=VideoProcessor,
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 640},
                    "height": {"ideal": 480},
                    "frameRate": {"ideal": 12},
                },
                "audio": False,
            },
            async_processing=True,
        )

    with right_col:
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">Live Prediction</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if ctx.video_processor:
            with ctx.video_processor.lock:
                result = ctx.video_processor.result.copy()

            current_sign = result["prediction"]
            confidence = result["confidence"]
            frames = f"{result['frames_collected']}/{result['frames_needed']}"

            html("""
            <div class="status-row">
                <div class="pulse-dot"></div>
                <div class="status-text">Model is running live</div>
            </div>
            """)

            st.markdown(f'<div class="prediction-main">{current_sign}</div>', unsafe_allow_html=True)
            st.markdown('<div class="prediction-label">Current detected sign</div>', unsafe_allow_html=True)

            html(f"""
            <div class="mini-grid">
                <div class="mini-card">
                    <div class="mini-title">Confidence</div>
                    <div class="mini-value">{confidence:.3f}</div>
                </div>
                <div class="mini-card">
                    <div class="mini-title">Frames</div>
                    <div class="mini-value">{frames}</div>
                </div>
            </div>
            """)

            st.markdown('<div class="section-title" style="margin-top:4px;">Top 3 Predictions</div>', unsafe_allow_html=True)

            if result["top3"]:
                for item in result["top3"]:
                    html(f"""
                    <div class="top3-item">
                        <span class="top3-name">{item['label']}</span>
                        <span class="top3-score">{item['confidence']:.3f}</span>
                    </div>
                    """)
            else:
                st.info("Waiting for enough frames...")
        else:
            st.info("Start the camera first.")

elif st.session_state.page == "stage":
    st_autorefresh(interval=1000, key="stage_refresh")

    stage = STAGES[st.session_state.stage_index]
    target_sign = stage["target"]
    progress_text = f"Stage {st.session_state.stage_index + 1} / {len(STAGES)}"

    top_left, top_right = st.columns([0.12, 0.88])
    with top_left:
        if st.button("← Back Home", use_container_width=True):
            go_home()
            st.rerun()

    st.subheader("Stage Mode")

    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">Camera</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        ctx = webrtc_streamer(
            key="stage-detection",
            video_processor_factory=VideoProcessor,
            media_stream_constraints={
                "video": {
                    "width": {"ideal": 640},
                    "height": {"ideal": 480},
                    "frameRate": {"ideal": 12},
                },
                "audio": False,
            },
            async_processing=True,
        )

    with right_col:
        st.markdown(
            """
            <div class="glass-card">
                <div class="section-title">Status</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if ctx.video_processor:
            with ctx.video_processor.lock:
                result = ctx.video_processor.result.copy()

            detected_sign = result["prediction"]
            confidence = result["confidence"]

            time_left = 10
            if st.session_state.stage_started and st.session_state.stage_start_time is not None:
                elapsed = time.time() - st.session_state.stage_start_time
                time_left = max(0, 10 - int(elapsed))

                if st.session_state.stage_status == "running":
                    if detected_sign == target_sign and confidence >= 0.70:
                        st.session_state.stage_status = "passed"
                        st.session_state.stage_feedback = f"Correct! You passed {progress_text}."
                        st.rerun()

                    elif elapsed >= 10:
                        st.session_state.stage_status = "failed"
                        st.session_state.stage_feedback = "Time's up. Try again."
                        st.rerun()

            st.markdown(f"**{progress_text}**")
            st.markdown("**TARGET SIGN**")
            st.markdown(
                f"<div style='font-size:3rem; font-weight:900; color:#0077b6; margin-bottom:20px;'>{target_sign}</div>",
                unsafe_allow_html=True
            )

            st.markdown("**TIME LEFT**")
            st.markdown(
                f"<div style='font-size:2.6rem; font-weight:900; color:#0b5f8a; margin-bottom:20px;'>{time_left}s</div>",
                unsafe_allow_html=True
            )

            if st.session_state.stage_status == "idle":
                st.info("Press Start Stage.")
                if st.button("Start Stage", use_container_width=True, type="primary"):
                    start_stage()
                    st.rerun()

            elif st.session_state.stage_status == "running":
                st.warning("Do the sign now.")

            elif st.session_state.stage_status == "passed":
                st.success(st.session_state.stage_feedback)

                if st.session_state.stage_index < len(STAGES) - 1:
                    if st.button("Next Stage", use_container_width=True, type="primary"):
                        next_stage()
                        st.rerun()
                else:
                    st.balloons()
                    st.success("You cleared all stages.")

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Play Again", use_container_width=True):
                            st.session_state.stage_index = 0
                            reset_stage()
                            st.rerun()
                    with col_b:
                        if st.button("Back Home", use_container_width=True):
                            st.session_state.stage_index = 0
                            reset_stage()
                            go_home()
                            st.rerun()

            elif st.session_state.stage_status == "failed":
                st.error(st.session_state.stage_feedback)
                if st.button("Try Again", use_container_width=True, type="primary"):
                    reset_stage()
                    st.rerun()
        else:
            st.info("Start the camera first.")