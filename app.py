<<<<<<< HEAD
import base64
import math
import threading
import time
from pathlib import Path

import av
import cv2
import streamlit as st
=======
import time
import av
import threading
from pathlib import Path
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
from streamlit_autorefresh import st_autorefresh
from streamlit_webrtc import (
    RTCConfiguration,
    VideoProcessorBase,
    webrtc_streamer,
)

from sign_predictor import SignLanguagePredictor
import cv2

<<<<<<< HEAD

st.set_page_config(
    page_title="Linguista",
    page_icon="🙌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "logo.png"

RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
        ]
    }
)


@st.cache_resource
def load_predictor():
    return SignLanguagePredictor(confidence_threshold=0.2)


@st.cache_data
def base64_logo():
    if LOGO_PATH.exists():
        return base64.b64encode(LOGO_PATH.read_bytes()).decode()
    return ""


# =========================
# Query-param page sync
# =========================
query_page = st.query_params.get("page", "home")
if query_page not in {"home", "demo", "stage"}:
    query_page = "home"


# =========================
# Session State
# =========================
def init_session_state():
    defaults = {
        "page": query_page,
        "stage_index": 0,
        "stage_started": False,
        "stage_start_time": None,
        "stage_status": "idle",
        "stage_feedback": "",
        "stage_balloons_shown": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()

st.session_state.page = st.query_params.get("page", st.session_state.page)
if st.session_state.page not in {"home", "demo", "stage"}:
    st.session_state.page = "home"


# =========================
# Data
# =========================
STAGES = [
    {
        "target": "Hungry",
        "label": "Hungry",
        "video": BASE_DIR / "assets" / "demo_videos" / "hungry.mp4",
    },
    {
        "target": "Sleepy",
        "label": "Sleepy",
        "video": BASE_DIR / "assets" / "demo_videos" / "sleepy.mp4",
    },
    {
        "target": "Drink",
        "label": "Drink",
        "video": BASE_DIR / "assets" / "demo_videos" / "drink.mp4",
    },
    {
        "target": "Yes",
        "label": "Yes",
        "video": BASE_DIR / "assets" / "demo_videos" / "yes.mp4",
    },
]

SUCCESS_MESSAGES = [
    "Amazing! 🌟",
    "Nice one! 🎉",
    "So good! 💖",
    "You got it! ✨",
]

FAIL_MESSAGES = [
    "Almost there! 🌈",
    "Try again! 💪",
    "One more time! 🫶",
    "Keep going! ✨",
=======
# =========================
# System Config & Paths
# =========================
st.set_page_config(
    page_title="Linguista",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
DEMO_VIDEOS_DIR = BASE_DIR / "assets" / "demo_videos"

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# =========================
# Global ML Resources
# =========================
@st.cache_resource
def load_predictor():
    return SignLanguagePredictor(confidence_threshold=0.2)


# =========================
# Session State Init
# =========================
def init_session_state():
    defaults = {
        "page": "home",  # home, lesson, practice
        "xp": 0,
        "streak": 3,
        "lesson_index": 0,
        "lesson_step": "intro",  # intro, active, feedback
        "lesson_status": None,  # 'correct', 'try_again', None
        "refresh_counter": 0,
        "camera_key_counter": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# =========================
# Content Data
# =========================
LESSONS = [
    {"target": "Hungry", "label": "Lesson 1: Basics", "video": DEMO_VIDEOS_DIR / "hungry.mp4"},
    {"target": "Sleepy", "label": "Lesson 2: Feelings", "video": DEMO_VIDEOS_DIR / "sleepy.mp4"},
    {"target": "Drink", "label": "Lesson 3: Actions", "video": DEMO_VIDEOS_DIR / "drink.mp4"},
    {"target": "Yes", "label": "Lesson 4: Affirmations", "video": DEMO_VIDEOS_DIR / "yes.mp4"},
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
]

# =========================
# Navigation Functions
# =========================
def go_home():
    st.session_state.page = "home"

<<<<<<< HEAD
# =========================
# Navigation helpers
# =========================
def set_page(page_name: str):
    st.session_state.page = page_name
    st.query_params["page"] = page_name


def go_home():
    set_page("home")


def go_demo():
    set_page("demo")


def go_stage():
    set_page("stage")


def start_stage():
    st.session_state.stage_started = True
    st.session_state.stage_start_time = time.time()
    st.session_state.stage_status = "running"
    st.session_state.stage_feedback = ""
    st.session_state.stage_balloons_shown = False


def reset_stage():
    st.session_state.stage_started = False
    st.session_state.stage_start_time = None
    st.session_state.stage_status = "idle"
    st.session_state.stage_feedback = ""
    st.session_state.stage_balloons_shown = False


def next_stage():
    if st.session_state.stage_index < len(STAGES) - 1:
        st.session_state.stage_index += 1
    reset_stage()


# =========================
# Reusable UI helpers
# =========================
def card(title: str, body: str):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-body">{body}</div>
=======
def start_lesson(index):
    st.session_state.lesson_index = index
    st.session_state.lesson_step = "intro"
    st.session_state.lesson_status = None
    st.session_state.page = "lesson"
    st.session_state.camera_key_counter += 1

def start_practice():
    st.session_state.page = "practice"
    st.session_state.camera_key_counter += 1

def advance_lesson_step(step):
    st.session_state.lesson_step = step

def complete_lesson(success):
    st.session_state.lesson_step = "feedback"
    if success:
        st.session_state.lesson_status = "correct"
        st.session_state.xp += 15
    else:
        st.session_state.lesson_status = "try_again"

def next_lesson():
    if st.session_state.lesson_index < len(LESSONS) - 1:
        st.session_state.lesson_index += 1
        st.session_state.lesson_step = "intro"
        st.session_state.camera_key_counter += 1
    else:
        go_home()


# =========================
# CSS Styling (Minimalist Red/Warm)
# =========================
st.markdown(
    """
    <style>
        :root {
            --primary-color: #a96f72;
            --primary-hover: #965f62;
            --bg-color: #fdfaf6;
            --card-bg: #ffffff;
            --text-dark: #523f46;
            --text-light: #9e8e92;
            --accent-peach: #eba793;
            --accent-green: #58cc02;
            --border-color: #e5dbdb;
        }
        
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stToolbar"] {display:none !important;}
        [data-testid="collapsedControl"] {display:none !important;}

        html, body, [class*="css"] {
            font-family: "Nunito", "Segoe UI", sans-serif;
            background-color: var(--bg-color);
            color: var(--text-dark);
        }

        .stApp {
            background-color: var(--bg-color);
        }

        .main .block-container {
            max-width: 480px;
            padding: 2rem 1rem;
            margin: auto;
        }

        /* Top Bar */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0 24px 0;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 24px;
        }

        .stat-item {
            display: flex;
            align-items: center;
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--primary-color);
        }

        .stat-item span.icon {
            margin-right: 6px;
            font-size: 1.2rem;
            color: var(--accent-peach);
        }

        /* Cards */
        .card {
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 0 var(--border-color);
            text-align: center;
        }

        .card-header {
            font-size: 1.2rem;
            font-weight: 800;
            margin-bottom: 8px;
            color: var(--text-dark);
        }

        .card-desc {
            font-size: 0.95rem;
            color: var(--text-light);
            margin-bottom: 16px;
        }

        /* Typography */
        h1, h2, h3 {
            color: var(--text-dark);
            text-align: center;
            font-weight: 800;
        }

        .lesson-title {
            font-size: 1.8rem;
            margin-bottom: 8px;
        }

        .target-word {
            font-size: 2.2rem;
            font-weight: 900;
            color: var(--primary-color);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 16px 0;
            text-align: center;
        }

        /* Progress Bar */
        .progress-container {
            width: 100%;
            background-color: var(--border-color);
            border-radius: 12px;
            height: 16px;
            margin-bottom: 24px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background-color: var(--primary-color);
            transition: width 0.3s ease;
        }

        /* Custom Buttons */
        .stButton > button {
            width: 100%;
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-size: 1.1rem !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            box-shadow: 0 4px 0 var(--primary-hover) !important;
            transition: transform 0.1s, box-shadow 0.1s !important;
            margin-top: 8px;
        }

        .stButton > button:active {
            transform: translateY(4px) !important;
            box-shadow: 0 0 0 var(--primary-hover) !important;
        }

        .btn-secondary > button {
            background-color: var(--bg-color) !important;
            color: var(--text-dark) !important;
            border: 2px solid var(--border-color) !important;
            box-shadow: 0 4px 0 var(--border-color) !important;
        }

        .btn-secondary > button:active {
            box-shadow: 0 0 0 var(--border-color) !important;
        }

        /* Feedback Panels */
        .feedback-panel {
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            font-weight: 800;
            font-size: 1.4rem;
            margin-bottom: 24px;
        }

        .feedback-correct {
            background-color: #d7ffb8;
            color: #2b5900;
            border: 2px solid #58cc02;
        }

        .feedback-incorrect {
            background-color: #ffdfe0;
            color: #a96f72;
            border: 2px solid #a96f72;
        }

        video {
            border-radius: 16px !important;
            width: 100% !important;
            max-width: 320px !important;
            margin: 0 auto;
            display: block;
            border: 2px solid var(--border-color);
        }

        .instruction-text {
            text-align: center;
            font-weight: 700;
            color: var(--text-dark);
            margin-bottom: 16px;
            font-size: 1.1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Video Processor
# =========================
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.predictor = load_predictor()
        self.result = {
            "prediction": "Connecting...",
            "confidence": 0.0,
            "is_confident": False,
        }
        self.lock = threading.Lock()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)

        try:
            processed_frame, result = self.predictor.process_frame(img, draw_landmarks=True)
            with self.lock:
                self.result = result.copy()
        except Exception:
            processed_frame = img

        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")


# =========================
# Component UI Helpers
# =========================
def render_top_bar():
    st.markdown(
        f"""
        <div class="top-bar">
            <div class="stat-item"><span class="icon">🔥</span>{st.session_state.streak}</div>
            <div style="font-weight:900; font-size:1.4rem; color:var(--text-dark); letter-spacing:-0.5px;">Linguista</div>
            <div class="stat-item"><span class="icon">💎</span>{st.session_state.xp}</div>
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
        </div>
        """,
        unsafe_allow_html=True,
    )

<<<<<<< HEAD

def pill(text: str, cls: str = ""):
    st.markdown(
        f"""<div class="pill {cls}">{text}</div>""",
        unsafe_allow_html=True,
    )


def app_link(label: str, page: str, variant: str = ""):
    st.markdown(
        f"""
        <a class="app-link {variant}" href="/?page={page}" target="_self">
            {label}
        </a>
        """,
        unsafe_allow_html=True,
    )


def bottom_nav_item(icon: str, page: str, variant: str = "", active: bool = False):
    active_class = "active" if active else ""
    return (
        f'<a class="bottom-nav-link {variant} {active_class}" '
        f'href="/?page={page}" target="_self" aria-label="{page}">'
        f'<span class="bottom-nav-icon">{icon}</span>'
        f"</a>"
    )


def create_camera_stream(key: str):
    return webrtc_streamer(
        key=key,
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={
            "video": {
                "width": {"ideal": 480},
                "height": {"ideal": 640},
                "frameRate": {"ideal": 12},
                "facingMode": "user",
            },
            "audio": False,
        },
        async_processing=True,
    )


def show_stage_demo(video_path, target_sign: str):
    if video_path and Path(video_path).exists():
        st.markdown(
            f"""
            <div class="card" style="padding:12px 16px;">
                <div class="card-title">Demo Clip</div>
                <div class="card-body">Watch how to sign <b>{target_sign}</b> before starting.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, center, right = st.columns([1, 2, 1])
        with center:
            st.video(str(video_path))
    else:
        card(
            "Demo clip missing 🎬",
            f"Add a video file for {target_sign} in assets/demo_videos.",
        )


# =========================
# Styling
# =========================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&display=swap');

    :root {
        --chocolate-kisses: #45151B;
        --mauvelous: #EA9DAE;
        --royal-orange: #F99256;
        --bittersweet-shimmer: #C74E51;
        --caramel: #FBDE9C;
        --soft-rose: #F8D9E0;
        --text-soft: #6C3C42;
        --text-mid: #7A3340;
        --white-glass: rgba(255,255,255,0.82);
        --nav-dark: rgba(22, 35, 48, 0.96);
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display:none !important;}
    [data-testid="collapsedControl"] {display:none !important;}

    html, body, [class*="css"] {
        font-family: "Avenir Next", "SF Pro Display", "Segoe UI", sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    a {
        text-decoration: none !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(249,146,86,0.15), transparent 30%),
            radial-gradient(circle at top right, rgba(234,157,174,0.18), transparent 28%),
            linear-gradient(180deg, #FBDE9C 0%, #F7CFA8 45%, #EA9DAE 100%);
        color: var(--chocolate-kisses);
    }

    .main .block-container {
        max-width: 430px;
        padding-top: 1rem;
        padding-bottom: 7.6rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .logo-image-wrap {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto 14px auto;
    }

    .logo-image-box {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: #BF4F51;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: logoFloat 2.6s ease-in-out infinite;
    box-shadow:
        0 10px 18px rgba(191,21,27,0.22),
        0 0 0 3px rgba(255,255,255,0.08),
        0 0 16px rgba(191,79,81,0.35)
    }

    .logo-image-box img {
        width: 140%;
        height: 140%;
        object-fit: cover;
        display: block;
        transform: translateY(10px);
        transform: translateX(-1.4px);
    }

    .top-brand {
        background: var(--chocolate-kisses);
        color: var(--mauvelous);
        border-radius: 30px;
        padding: 1.15rem 1.15rem 1.1rem 1.15rem;
        box-shadow: 0 12px 28px rgba(69,21,27,0.18);
        margin-bottom: 12px;
        text-align: center;
    }

    .brand-title {
        font-size: 1.78rem;
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: -0.45px;
        color: var(--mauvelous);
        margin-top: 0.1rem;
    }

    .brand-sub {
        margin-top: 6px;
        color: var(--mauvelous);
        font-size: 0.95rem;
        line-height: 1.4;
    }

    .hero-card {
        background: rgba(255,255,255,0.76);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 28px;
        padding: 18px;
        border: 2px solid rgba(255,255,255,0.4);
        box-shadow: 0 8px 24px rgba(69,21,27,0.10);
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 900;
        color: var(--chocolate-kisses);
        line-height: 1.02;
        margin-bottom: 8px;
    }

    .hero-text {
        color: var(--text-mid);
        font-size: 1rem;
        line-height: 1.5;
    }

    .card {
        background: var(--white-glass);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(69,21,27,0.10);
        border: 1.5px solid rgba(255,255,255,0.45);
        margin-bottom: 12px;
    }

    .card-title {
        font-size: 1rem;
        font-weight: 900;
        color: var(--chocolate-kisses);
        margin-bottom: 8px;
    }

    .card-body {
        color: var(--text-soft);
        line-height: 1.45;
    }

    .pill {
        display: inline-block;
        background: var(--royal-orange);
        color: white;
        border-radius: 999px;
        padding: 8px 12px;
        font-size: 0.82rem;
        font-weight: 900;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(69,21,27,0.08);
    }

    .pill.soft {
        background: var(--mauvelous);
        color: var(--chocolate-kisses);
    }

    .pill.yellow {
        background: var(--caramel);
        color: var(--chocolate-kisses);
    }

    .prediction-card {
        background: linear-gradient(180deg, rgba(69,21,27,0.96), rgba(102,28,38,0.96));
        color: var(--caramel);
        border-radius: 28px;
        padding: 18px;
        box-shadow: 0 12px 28px rgba(69,21,27,0.20);
        margin-bottom: 12px;
    }

    .prediction-label {
        color: var(--soft-rose);
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .prediction-value {
        font-size: 2rem;
        font-weight: 900;
        line-height: 1.05;
        word-break: break-word;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 12px;
    }

    .stat-box {
        background: rgba(255,255,255,0.8);
        border-radius: 22px;
        padding: 14px;
        box-shadow: 0 8px 20px rgba(69,21,27,0.08);
        border: 1px solid rgba(255,255,255,0.35);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }

    .stat-title {
        font-size: 0.82rem;
        color: #A74B5A;
        font-weight: 800;
    }

    .stat-value {
        font-size: 1.25rem;
        color: var(--chocolate-kisses);
        font-weight: 900;
        margin-top: 6px;
    }

    .top-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #F8E4B8;
        border-radius: 20px;
        padding: 12px 14px;
        margin-bottom: 8px;
        border: 1px solid rgba(69,21,27,0.08);
    }

    .top-name {
        font-weight: 900;
        color: var(--chocolate-kisses);
    }

    .top-score {
        font-weight: 900;
        color: var(--bittersweet-shimmer);
    }

    .stage-target {
        background: linear-gradient(180deg, var(--mauvelous), #F7B4C0);
        border-radius: 28px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 10px 24px rgba(199,78,81,0.14);
        margin-bottom: 12px;
    }

    .stage-kicker {
        font-size: 0.9rem;
        font-weight: 800;
        color: var(--text-mid);
        margin-bottom: 8px;
    }

    .stage-word {
        font-size: 2rem;
        font-weight: 900;
        color: var(--chocolate-kisses);
        line-height: 1.05;
    }

    .timer-box {
        background: rgba(255,255,255,0.8);
        border-radius: 24px;
        text-align: center;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 8px 20px rgba(69,21,27,0.08);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }

    .timer-value {
        font-size: 2rem;
        font-weight: 900;
        color: var(--bittersweet-shimmer);
    }

    .feedback-success {
        background: var(--bittersweet-shimmer);
        color: white;
        border-radius: 22px;
        padding: 14px 16px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 12px;
    }

    .feedback-fail {
        background: var(--royal-orange);
        color: white;
        border-radius: 22px;
        padding: 14px 16px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 12px;
    }

    .tiny-note {
        text-align: center;
        color: var(--text-soft);
        font-size: 0.84rem;
        margin-top: 10px;
        margin-bottom: 8px;
    }

    video {
        width: 78% !important;
        max-width: 320px !important;
        height: auto !important;
        margin: 0 auto !important;
        display: block !important;
        border-radius: 24px !important;
        object-fit: cover !important;
        background: var(--chocolate-kisses) !important;
        box-shadow: 0 10px 26px rgba(69,21,27,0.18) !important;
        border: 2px solid rgba(255,255,255,0.22) !important;
    }

    .stButton > button {
        width: 100%;
        border: none !important;
        border-radius: 999px !important;
        height: 58px !important;
        padding: 0.9rem 1rem !important;
        font-size: 1.05rem !important;
        font-weight: 900 !important;
        letter-spacing: 0.3px !important;
        background: var(--chocolate-kisses) !important;
        color: var(--mauvelous) !important;
        box-shadow:
            0 10px 22px rgba(69,21,27,0.18),
            inset 0 -3px 0 rgba(0,0,0,0.16),
            inset 0 1px 0 rgba(255,255,255,0.05) !important;
        transition:
            transform 0.12s ease,
            filter 0.12s ease,
            box-shadow 0.12s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.015);
        filter: brightness(1.04);
    }

    .stButton > button:active {
        transform: translateY(1px) scale(0.985);
    }

    .stButton > button:focus,
    .stButton > button:focus-visible {
        outline: none !important;
        box-shadow:
            0 0 0 3px rgba(255,255,255,0.28),
            0 10px 22px rgba(69,21,27,0.18),
            inset 0 -3px 0 rgba(0,0,0,0.16) !important;
    }

    .app-link {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 58px;
        border-radius: 999px;
        font-size: 1.05rem;
        font-weight: 900;
        letter-spacing: 0.3px;
        text-decoration: none !important;
        box-shadow:
            0 10px 22px rgba(69,21,27,0.18),
            inset 0 -3px 0 rgba(0,0,0,0.16),
            inset 0 1px 0 rgba(255,255,255,0.05);
        transition: transform 0.12s ease, filter 0.12s ease;
        user-select: none;
        -webkit-tap-highlight-color: transparent;
    }

    .app-link:hover {
        transform: translateY(-2px) scale(1.015);
        filter: brightness(1.04);
    }

    .app-link:active {
        transform: translateY(1px) scale(0.985);
    }

    .app-link.freestyle-link {
        background: var(--royal-orange);
        color: var(--chocolate-kisses) !important;
    }

    .app-link.stage-link {
        background: var(--bittersweet-shimmer);
        color: var(--caramel) !important;
    }

    .nav-wrap {
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        bottom: 10px;
        width: min(410px, calc(100vw - 20px));
        background: var(--nav-dark);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border-radius: 28px;
        padding: 14px 16px;
        box-shadow:
            0 18px 36px rgba(0,0,0,0.26),
            inset 0 1px 0 rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.06);
        z-index: 999999;
    }

    .bottom-nav-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 18px;
        align-items: center;
    }

    .bottom-nav-link {
        width: 56px;
        height: 56px;
        margin: 0 auto;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
        background: transparent;
        border: 2px solid transparent;
        transition: all 0.16s ease;
        user-select: none;
        -webkit-tap-highlight-color: transparent;
    }

    .bottom-nav-link:hover {
        background: rgba(255,255,255,0.04);
        transform: translateY(-1px);
    }

    .bottom-nav-link:active {
        transform: scale(0.96);
    }

    .bottom-nav-icon {
        font-size: 1.9rem;
        line-height: 1;
        filter: saturate(1.05);
    }

    .bottom-nav-link.home-link .bottom-nav-icon {
        color: #f4c64f;
    }

    .bottom-nav-link.demo-link .bottom-nav-icon {
        color: #8fc7d8;
    }

    .bottom-nav-link.stage-link-nav .bottom-nav-icon {
        color: #ea8ad0;
    }

    .bottom-nav-link.active {
        background: var(--chocolate-kisses);
        border-color: var(--mauvelous);
        box-shadow:
            0 0 0 1px rgba(234,157,174,0.18),
            0 0 18px rgba(234,157,174,0.20);
    }

    .bottom-nav-link.active .bottom-nav-icon {
        transform: scale(1.03);
    }

    @keyframes logoFloat {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-4px);
        }
    }

    @media (max-width: 480px) {
        .hero-title {
            font-size: 1.8rem;
        }

        .prediction-value,
        .stage-word,
        .timer-value {
            font-size: 1.7rem;
        }

        .main .block-container {
            padding-left: 0.9rem;
            padding-right: 0.9rem;
            padding-bottom: 7.6rem;
        }

        .nav-wrap {
            width: min(410px, calc(100vw - 16px));
            bottom: 8px;
            padding: 12px 14px;
            border-radius: 24px;
        }

        .bottom-nav-grid {
            gap: 12px;
        }

        .bottom-nav-link {
            width: 52px;
            height: 52px;
            border-radius: 16px;
        }

        .bottom-nav-icon {
            font-size: 1.7rem;
        }

        video {
            width: 84% !important;
            max-width: 300px !important;
        }

        .logo-image-box {
            width: 90px;
            height: 90px;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# Video Processor
# =========================
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.predictor = load_predictor()
        self.result = {
            "frames_collected": 0,
            "frames_needed": 45,
            "prediction": "Collecting...",
            "raw_label": None,
            "display_label": None,
            "confidence": 0.0,
            "is_confident": False,
            "top3": [],
        }
        self.lock = threading.Lock()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)

        try:
            processed_frame, result = self.predictor.process_frame(
                img,
                draw_landmarks=True,
            )
            with self.lock:
                self.result = result.copy()
        except Exception:
            processed_frame = img

        return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")


# =========================
# Header
# =========================
if LOGO_PATH.exists():
    st.markdown(
        f"""
        <div class="logo-image-wrap">
            <div class="logo-image-box">
                <img src="data:image/png;base64,{base64_logo()}" alt="Linguista logo">
            </div>
=======
def render_progress_bar(current, total):
    percentage = int((current / total) * 100)
    st.markdown(
        f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {percentage}%;"></div>
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
        </div>
        """,
        unsafe_allow_html=True,
    )

<<<<<<< HEAD
st.markdown(
    """
    <div class="top-brand">
        <div class="brand-title">Linguista 🤲</div>
        <div class="brand-sub">Practice sign language in a playful, mobile-friendly way.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================
# Home
# =========================
if st.session_state.page == "home":
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Learn sign language<br>the fun way ✨</div>
            <div class="hero-text">
                Practice with live AI detection and playful mini challenges.
                It’s friendly, simple, and designed to feel good on your phone.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    card(
        "How it works 🌈",
        "Open Freestyle to explore your sign prediction in real time, or try Stage Mode to complete mini sign challenges one by one.",
    )

    c1, c2 = st.columns(2)

    with c1:
        app_link("Freestyle", "demo", "freestyle-link")

    with c2:
        app_link("Stage Mode", "stage", "stage-link")

    st.markdown(
        '<div class="tiny-note">Tip: try to center yourself for an accurate prediction!</div>',
        unsafe_allow_html=True,
    )


# =========================
# Freestyle
# =========================
elif st.session_state.page == "demo":
    st_autorefresh(interval=1800, key="prediction_refresh")

    pill("Freestyle 🎥")

    back_col, title_col = st.columns([0.28, 0.72])

    with back_col:
        if st.button("← Home", use_container_width=True):
            go_home()
            st.rerun()

    with title_col:
        st.markdown(
            """
            <div class="card" style="padding:12px 16px;">
                <div class="card-title">Freestyle Detection</div>
                <div class="card-body">Show your sign to the camera and let the model guess it ✨</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    ctx = create_camera_stream("sign-detection")

    if ctx.video_processor:
        with ctx.video_processor.lock:
            result = ctx.video_processor.result.copy()

        current_sign = result.get("display_label") or result.get("prediction", "Collecting...")
        confidence = result.get("confidence", 0.0)
        frames = f"{result.get('frames_collected', 0)}/{result.get('frames_needed', 0)}"

        st.markdown(
            f"""
            <div class="prediction-card">
                <div class="prediction-label">Current prediction</div>
                <div class="prediction-value">{current_sign}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-title">Confidence</div>
                    <div class="stat-value">{confidence:.3f}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-title">Frames</div>
                    <div class="stat-value">{frames}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        card("Top 3 guesses 💫", "The model’s favorite guesses right now.")

        if result.get("top3"):
            for item in result["top3"]:
                st.markdown(
                    f"""
                    <div class="top-item">
                        <span class="top-name">{item['label']}</span>
                        <span class="top-score">{item['confidence']:.3f}</span>
=======
# =========================
# Page: Home
# =========================
def render_home():
    render_top_bar()
    
    st.markdown("<h3>Your Course</h3>", unsafe_allow_html=True)

    # Main Lessons Loop
    for idx, lesson in enumerate(LESSONS):
        is_locked = idx > st.session_state.lesson_index

        if is_locked:
            st.markdown(
                f"""
                <div class="card" style="opacity: 0.6; background-color: #f2eded;">
                    <div class="card-header">Locked</div>
                    <div class="card-desc">Complete previous lessons to unlock</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            if idx == st.session_state.lesson_index:
                # Active Lesson
                st.markdown(
                    f"""
                    <div class="card" style="border-color: var(--primary-color);">
                        <div class="card-header">{lesson['label']}</div>
                        <div class="card-desc">Practice signing: {lesson['target']}</div>
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
<<<<<<< HEAD
        else:
            card("Warming up ⏳", "Hold your sign a little longer so the model can collect enough frames.")

    else:
        card("Camera not started yet 📷", "Tap Start above to begin freestyle mode.")


# =========================
# Stage Mode
# =========================
elif st.session_state.page == "stage":
    if st.session_state.stage_status == "running":
        st_autorefresh(interval=1000, key="stage_refresh")

    stage = STAGES[st.session_state.stage_index]
    target_sign = stage["target"]
    demo_video = stage.get("video")
    progress_text = f"Stage {st.session_state.stage_index + 1} / {len(STAGES)}"
    camera_key = f"stage-detection-{st.session_state.stage_index}"

    pill("Stage Mode 🎮", "yellow")

    nav1, nav2 = st.columns([0.28, 0.72])

    with nav1:
        if st.button("← Home", use_container_width=True):
            st.session_state.stage_index = 0
            reset_stage()
=======
                if st.button(f"Start Lesson {idx+1}", key=f"start_{idx}"):
                    start_lesson(idx)
                    st.rerun()
            else:
                # Completed Lesson
                st.markdown(
                    f"""
                    <div class="card" style="border-color: #58cc02; background-color: #f7fff0;">
                        <div class="card-header" style="color: #58cc02;">{lesson['label']} (Completed)</div>
                        <div class="card-desc">Target: {lesson['target']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
                if st.button("Review", key=f"rev_{idx}"):
                    start_lesson(idx)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr style='margin: 32px 0;'>", unsafe_allow_html=True)
    
    st.markdown("<h3>Extra Practice</h3>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="card">
            <div class="card-header">Practice Mode</div>
            <div class="card-desc">Freestyle camera mode to test out your signs.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
    if st.button("Open Practice"):
        start_practice()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Page: Lesson Flow
# =========================
def render_lesson():
    lesson = LESSONS[st.session_state.lesson_index]
    target_sign = lesson["target"]
    video_path = lesson.get("video")

    render_progress_bar(st.session_state.lesson_index, len(LESSONS))

    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.markdown('<div class="btn-secondary" style="margin-bottom:16px;">', unsafe_allow_html=True)
        if st.button("X"):
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
            go_home()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

<<<<<<< HEAD
    with nav2:
        st.markdown(
            f"""
            <div class="card" style="padding:12px 16px;">
                <div class="card-title">{progress_text}</div>
                <div class="card-body">Match the target sign before time runs out 💪</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="stage-target">
            <div class="stage-kicker">Target sign</div>
            <div class="stage-word">{target_sign}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.stage_status == "idle":
        show_stage_demo(demo_video, target_sign)
        card("Ready? 🌟", "Watch the demo clip, then press Start and make the sign before the timer hits zero.")

        if st.button("Start Stage", use_container_width=True):
            start_stage()
            st.rerun()

    elif st.session_state.stage_status == "running":
        ctx = create_camera_stream(camera_key)

=======
    # 1. INTRO STEP
    if st.session_state.lesson_step == "intro":
        st.markdown(f'<div class="instruction-text">New word</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="target-word">{target_sign}</div>', unsafe_allow_html=True)
        
        if video_path and Path(video_path).exists():
            st.video(str(video_path))
        else:
            st.markdown(
                f"""
                <div class="card" style="padding:40px;">
                    <div class="card-desc">Demo clip missing 🎬<br>Add video to assets/demo_videos.</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
        if st.button("Let's Try It"):
            advance_lesson_step("active")
            st.rerun()

    # 2. ACTIVE STEP
    elif st.session_state.lesson_step == "active":
        st_autorefresh(interval=1000, key="lesson_active_refresh")
        
        st.markdown(f'<div class="instruction-text">Sign this word:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="target-word">{target_sign}</div>', unsafe_allow_html=True)

        ctx = webrtc_streamer(
            key=f"lesson_camera_{st.session_state.camera_key_counter}",
            video_processor_factory=VideoProcessor,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={"video": {"facingMode": "user"}, "audio": False},
            async_processing=True,
        )

        detected_sign = "Waiting..."
        confidence = 0.0
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
        if ctx.video_processor:
            with ctx.video_processor.lock:
                result = ctx.video_processor.result.copy()
            detected_sign = result.get("prediction", "Waiting...")
            confidence = result.get("confidence", 0.0)
            is_confident = result.get("is_confident", False)

<<<<<<< HEAD
            detected_sign = result.get("display_label") or result.get("prediction", "Collecting...")
            confidence = result.get("confidence", 0.0)
            is_confident = result.get("is_confident", False)

            elapsed = time.time() - st.session_state.stage_start_time
            time_left = max(0, math.ceil(30 - elapsed))

            if (
                str(detected_sign).strip().lower() == str(target_sign).strip().lower()
                and is_confident
                and confidence >= 0.70
            ):
                st.session_state.stage_status = "passed"
                st.session_state.stage_feedback = SUCCESS_MESSAGES[
                    st.session_state.stage_index % len(SUCCESS_MESSAGES)
                ]
                st.rerun()

            elif elapsed >= 30:
                st.session_state.stage_status = "failed"
                st.session_state.stage_feedback = FAIL_MESSAGES[
                    st.session_state.stage_index % len(FAIL_MESSAGES)
                ]
                st.rerun()

            st.markdown(
                f"""
                <div class="timer-box">
                    <div class="card-title">Time left ⏰</div>
                    <div class="timer-value">{time_left}s</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="prediction-card">
                    <div class="prediction-label">Your current sign</div>
                    <div class="prediction-value">{detected_sign}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-title">Confidence</div>
                        <div class="stat-value">{confidence:.3f}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-title">Target</div>
                        <div class="stat-value">{target_sign}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            pill("Go go go! 💨", "soft")

        else:
            card("Camera not started yet 📷", "Tap Start on the camera box above if your browser asks for permission.")

    elif st.session_state.stage_status == "passed":
        st.markdown(
            """
            <div class="timer-box">
                <div class="card-title">Status ✅</div>
                <div class="timer-value" style="font-size:1.35rem;">Correct hand sign ✅</div>
=======
            # Auto-check logic
            if str(detected_sign).lower() == str(target_sign).lower() and is_confident and confidence >= 0.70:
                complete_lesson(success=True)
                st.rerun()
                
        st.markdown(
            f"""
            <div class="card" style="margin-top: 16px;">
                <div style="font-size: 0.9rem; color: var(--text-light);">Detected</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: var(--text-dark);">{detected_sign}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("I can't do it now"):
            complete_lesson(success=False)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. FEEDBACK STEP
    elif st.session_state.lesson_step == "feedback":
        st.markdown(f'<div class="target-word">{target_sign}</div>', unsafe_allow_html=True)
        
        if st.session_state.lesson_status == "correct":
            st.markdown('<div class="feedback-panel feedback-correct">Correct!</div>', unsafe_allow_html=True)
            if st.button("Continue"):
                next_lesson()
                st.rerun()
        else:
            st.markdown('<div class="feedback-panel feedback-incorrect">Let\'s try again later.</div>', unsafe_allow_html=True)
            if st.button("Got it"):
                go_home()
                st.rerun()

# =========================
# Page: Practice Mode
# =========================
def render_practice():
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.markdown('<div class="btn-secondary" style="margin-bottom:16px;">', unsafe_allow_html=True)
        if st.button("X"):
            go_home()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<h3>Practice Mode</h3>", unsafe_allow_html=True)
    st.markdown('<div class="instruction-text">Show a sign to the camera.</div>', unsafe_allow_html=True)

    st_autorefresh(interval=1500, key="practice_refresh")

    ctx = webrtc_streamer(
        key=f"practice_camera_{st.session_state.camera_key_counter}",
        video_processor_factory=VideoProcessor,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": {"facingMode": "user"}, "audio": False},
        async_processing=True,
    )

    if ctx.video_processor:
        with ctx.video_processor.lock:
            result = ctx.video_processor.result.copy()

        detected_sign = result.get("display_label") or result.get("prediction", "Collecting...")
        confidence = result.get("confidence", 0.0)

        st.markdown(
            f"""
            <div class="card" style="margin-top: 24px;">
                <div class="card-desc">Current Detection</div>
                <div class="target-word" style="margin-top:0;">{detected_sign}</div>
                <div class="card-desc" style="margin-bottom:0;">Confidence: {confidence:.2f}</div>
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
            </div>
            """,
            unsafe_allow_html=True,
        )

<<<<<<< HEAD
        st.markdown(
            f"""<div class="feedback-success">{st.session_state.stage_feedback}</div>""",
            unsafe_allow_html=True,
        )

        if not st.session_state.stage_balloons_shown:
            st.balloons()
            st.session_state.stage_balloons_shown = True

        if st.session_state.stage_index < len(STAGES) - 1:
            if st.button("Next Stage", use_container_width=True):
                next_stage()
                st.rerun()
        else:
            st.markdown(
                """<div class="feedback-success">You cleared all stages! 🎉💖</div>""",
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Play Again", use_container_width=True):
                    st.session_state.stage_index = 0
                    reset_stage()
                    st.rerun()

            with c2:
                if st.button("Home", use_container_width=True):
                    st.session_state.stage_index = 0
                    reset_stage()
                    go_home()
                    st.rerun()

    elif st.session_state.stage_status == "failed":
        show_stage_demo(demo_video, target_sign)

        st.markdown(
            f"""<div class="feedback-fail">{st.session_state.stage_feedback}</div>""",
            unsafe_allow_html=True,
        )

        if st.button("Try Again", use_container_width=True):
            reset_stage()
            st.rerun()


# =========================
# Bottom nav
# =========================
nav_html = f"""
<div class="nav-wrap">
    <div class="bottom-nav-grid">
        {bottom_nav_item("🏠", "home", "home-link", active=(st.session_state.page == "home"))}
        {bottom_nav_item("🎥", "demo", "demo-link", active=(st.session_state.page == "demo"))}
        {bottom_nav_item("🎮", "stage", "stage-link-nav", active=(st.session_state.page == "stage"))}
    </div>
</div>
"""

st.markdown(nav_html, unsafe_allow_html=True)
=======
# =========================
# Router
# =========================
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "lesson":
    render_lesson()
elif st.session_state.page == "practice":
    render_practice()
>>>>>>> 248cea2 (Update codebase with local sharing and FastAPI server)
