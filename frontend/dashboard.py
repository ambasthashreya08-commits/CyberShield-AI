import streamlit as st
import sqlite3
import requests
import pandas as pd
import plotly.express as px
import math
from html import escape
from pathlib import Path
from datetime import datetime
import streamlit.components.v1 as components

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="CyberShield AI | Security Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "vulnerabilities.db"
REPORT_DIR = BASE_DIR / "reports"

API_URL = "http://127.0.0.1:8000"

# --------------------------------------------------
# GLOBAL STYLING AND ANIMATIONS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&display=swap');

:root {
    --bg: #030d1b;
    --panel: rgba(9,24,42,0.62);
    --panel-strong: rgba(7,19,34,0.86);
    --cyan: #22d3ee;
    --cyan-soft: #67e8f9;
    --blue: #3b82f6;
    --text: #e8f4ff;
    --muted: #93adc6;
    --border: rgba(56,189,248,0.22);
}

html, body {
    background: #030d1b !important;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: transparent !important;
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(3,13,27,0.35) !important;
    backdrop-filter: blur(10px);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

h1, h2, h3 {
    color: #eaf6ff !important;
    font-family: 'Inter', sans-serif !important;
    text-shadow: 0 2px 18px rgba(3,13,27,0.9);
}

[data-testid="stMarkdownContainer"] h2 {
    font-weight: 800;
    letter-spacing: -0.4px;
    padding-left: 14px;
    border-left: 3px solid var(--cyan);
    box-shadow: -8px 0 18px -10px var(--cyan);
}

.stMarkdown, .stMarkdown p, label, [data-testid="stWidgetLabel"] p {
    color: var(--text) !important;
}

[data-testid="stCaptionContainer"], .stCaption {
    color: var(--muted) !important;
}

/* ---------- Streamlit background stage hiding ---------- */

[data-testid="stElementContainer"]:has(.cs-stage),
[data-testid="element-container"]:has(.cs-stage) {
    height: 0 !important;
    min-height: 0 !important;
    margin: -1rem 0 0 0 !important;
    padding: 0 !important;
}

/* ---------- FIXED BACKGROUND STAGE ---------- */

.cs-stage {
    position: fixed;
    inset: 0;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
    background:
        radial-gradient(ellipse at 66% 46%, #08405c 0%, rgba(6,40,66,0.55) 28%, transparent 62%),
        radial-gradient(ellipse at 15% 90%, rgba(12,74,110,0.35), transparent 50%),
        linear-gradient(160deg, #04182b 0%, #030d1b 55%, #020812 100%);
}

.cs-stars {
    position: absolute;
    inset: -90px;
    background-image: radial-gradient(circle, rgba(103,232,249,0.55) 1px, transparent 1.6px);
    background-size: 46px 46px;
    opacity: 0.22;
    animation: csStarDrift 40s linear infinite;
    -webkit-mask-image: radial-gradient(ellipse at 62% 48%, #000 5%, transparent 75%);
    mask-image: radial-gradient(ellipse at 62% 48%, #000 5%, transparent 75%);
}

.cs-grid {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(34,211,238,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34,211,238,0.05) 1px, transparent 1px);
    background-size: 72px 72px;
    -webkit-mask-image: radial-gradient(ellipse at 60% 50%, #000 0%, transparent 68%);
    mask-image: radial-gradient(ellipse at 60% 50%, #000 0%, transparent 68%);
}

.cs-particle {
    position: absolute;
    border-radius: 50%;
    background: #8eeaff;
    box-shadow: 0 0 10px #22d3ee, 0 0 22px rgba(34,211,238,0.5);
    opacity: 0;
    animation-name: csFloat;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
}

.cs-fly {
    position: absolute;
    display: grid;
    place-items: center;
    border-radius: 11px;
    background: rgba(34,211,238,0.10);
    border: 1px solid rgba(103,232,249,0.42);
    box-shadow: 0 0 20px rgba(34,211,238,0.28), inset 0 0 12px rgba(34,211,238,0.12);
    color: #67e8f9;
    animation-name: csBob;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
}

.cs-fly svg {
    width: 56%;
    height: 56%;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.cs-globe {
    position: absolute;
    left: 60%;
    top: 50%;
    width: min(122vh, 92vw);
    aspect-ratio: 1 / 1;
    transform: translate(-50%, -50%);
}

.cs-halo {
    position: absolute;
    inset: -14%;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(34,211,238,0.30) 0%, rgba(14,165,233,0.14) 38%, transparent 66%);
    animation: csPulse 7s ease-in-out infinite;
}

.cs-orbit {
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(56,189,248,0.38);
    box-shadow: 0 0 18px rgba(34,211,238,0.12);
}

.cs-orbit:after {
    content: "";
    position: absolute;
    top: -4px;
    left: 50%;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #8eeaff;
    box-shadow: 0 0 16px #22d3ee, 0 0 34px #22d3ee;
}

.cs-orbit.o1 { inset: 9% -15%; animation: csOrbitA 38s linear infinite; }
.cs-orbit.o2 { inset: 20% -8%; border-style: dashed; border-color: rgba(103,232,249,0.28); animation: csOrbitB 52s linear infinite; }

.cs-sphere {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    overflow: hidden;
    border: 1px solid rgba(103,232,249,0.7);
    box-shadow:
        0 0 50px rgba(14,165,233,0.35),
        0 0 140px rgba(14,165,233,0.2),
        inset 0 0 70px rgba(34,211,238,0.22);
}

.cs-globe-svg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    display: block;
}

.cs-map-scroll {
    animation: csMapSpin 110s linear infinite;
    animation-delay: -60s;
    will-change: transform;
}

.cs-mer {
    fill: none;
    stroke: rgba(56,189,248,0.26);
    stroke-width: 0.28;
    transform-box: fill-box;
    transform-origin: center;
    animation: csMeridian 45s linear infinite;
}

.cs-arc {
    fill: none;
    stroke: #67e8f9;
    stroke-width: 0.38;
    stroke-linecap: round;
    stroke-dasharray: 3 4;
    opacity: 0.85;
    animation: csDash 2.6s linear infinite;
}

.cs-node { fill: #e6fbff; }

.cs-node-halo {
    fill: rgba(34,211,238,0.55);
    transform-box: fill-box;
    transform-origin: center;
    animation: csNodePulse 2.8s ease-out infinite;
}

.cs-shield-wrap {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 33%;
    aspect-ratio: 200 / 240;
    transform: translate(-50%, -50%);
    perspective: 1300px;
    filter: drop-shadow(0 0 22px rgba(34,211,238,0.8)) drop-shadow(0 0 64px rgba(34,211,238,0.4));
}

.cs-shield-aura {
    position: absolute;
    inset: -30%;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(34,211,238,0.35), transparent 62%);
    animation: csPulse 4.5s ease-in-out infinite;
}

.cs-shield3d {
    position: absolute;
    inset: 0;
    transform-style: preserve-3d;
    animation: csShieldSpin 24s linear infinite;
}

.cs-sl {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
}

.cs-sl.mid { backface-visibility: visible; }

.cs-sl svg {
    width: 100%;
    height: 100%;
    display: block;
}

.cs-gloss {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    background:
        radial-gradient(circle at 30% 22%, rgba(255,255,255,0.17), transparent 30%),
        radial-gradient(circle at 50% 50%, transparent 56%, rgba(2,10,22,0.5) 100%);
    box-shadow: inset 0 0 80px rgba(34,211,238,0.3);
}

.cs-scrim {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, rgba(3,13,27,0.86) 0%, rgba(3,13,27,0.55) 38%, rgba(3,13,27,0.08) 78%);
}

.cs-vignette {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 55% 50%, transparent 50%, rgba(2,8,18,0.7) 100%);
}

/* ---------- KEYFRAMES ---------- */

@keyframes csStarDrift { from { transform: translate(0,0); } to { transform: translate(46px,46px); } }
@keyframes csFloat {
    0%   { transform: translate(0,0); opacity: 0; }
    20%  { opacity: 0.95; }
    80%  { opacity: 0.6; }
    100% { transform: translate(18px,-60px); opacity: 0; }
}
@keyframes csBob {
    0%,100% { transform: translateY(0) rotate(-3deg); }
    50%     { transform: translateY(-16px) rotate(3deg); }
}
@keyframes csPulse { 0%,100% { transform: scale(1); opacity: 0.75; } 50% { transform: scale(1.06); opacity: 1; } }
@keyframes csOrbitA { from { transform: rotate(-24deg); } to { transform: rotate(336deg); } }
@keyframes csOrbitB { from { transform: rotate(32deg); } to { transform: rotate(-328deg); } }
@keyframes csMapSpin { from { transform: translateX(0px); } to { transform: translateX(-360px); } }
@keyframes csMeridian { 0% { transform: scaleX(0.02); } 50% { transform: scaleX(1); } 100% { transform: scaleX(0.02); } }
@keyframes csDash { to { stroke-dashoffset: -14; } }
@keyframes csNodePulse { 0% { transform: scale(0.5); opacity: 0.9; } 100% { transform: scale(2.2); opacity: 0; } }
@keyframes csShieldSpin {
    from { transform: rotateX(-8deg) rotateY(0deg); }
    to   { transform: rotateX(-8deg) rotateY(360deg); }
}
@keyframes csFadeUp { from { opacity: 0; transform: translateY(22px); } to { opacity: 1; transform: translateY(0); } }
@keyframes csSheen { 0% { left: -45%; } 55%,100% { left: 130%; } }
@keyframes csShimmer { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
@keyframes csDotPulse { 0%,100% { box-shadow: 0 0 0 0 rgba(45,212,191,0.6); } 50% { box-shadow: 0 0 0 7px rgba(45,212,191,0); } }
@keyframes csLogoFloat { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }

/* ---------- SIDEBAR ---------- */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(6,22,40,0.97), rgba(3,10,20,0.98));
    border-right: 1px solid var(--border);
    box-shadow: 10px 0 44px rgba(0,0,0,0.5);
}

[data-testid="stSidebar"] * {
    color: #d8eaff;
}

.cs-logo {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 6px 0 4px 0;
}

.cs-logo-mark {
    width: 46px;
    height: 54px;
    flex: 0 0 auto;
    filter: drop-shadow(0 0 10px rgba(34,211,238,0.85)) drop-shadow(0 0 24px rgba(34,211,238,0.45));
    animation: csLogoFloat 4s ease-in-out infinite;
}

.cs-logo-mark svg { width: 100%; height: 100%; display: block; }

.brand {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.6px;
    line-height: 1.1;
}

.brand span { color: var(--cyan) !important; }

.sidebar-label {
    color: #6ba9cf !important;
    font-size: 0.62rem;
    letter-spacing: 2.4px;
    font-weight: 700;
    margin-top: 6px;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 6px;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] {
    width: 100%;
    padding: 11px 14px;
    border-radius: 12px;
    border: 1px solid transparent;
    background: rgba(255,255,255,0.015);
    cursor: pointer;
    transition: all .25s ease;
    align-items: center;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] label[data-baseweb="radio"]::before {
    content: "◈";
    display: inline-grid;
    place-items: center;
    width: 30px;
    height: 30px;
    margin-right: 12px;
    border-radius: 9px;
    background: rgba(34,211,238,0.10);
    border: 1px solid rgba(34,211,238,0.28);
    color: #67e8f9;
    font-size: 14px;
    transition: all .25s ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(1)::before { content: "◉"; }
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(2)::before { content: "⌕"; font-size: 17px; }
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(3)::before { content: "✦"; }
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(4)::before { content: "✔"; }
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(5)::before { content: "▤"; }

[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
    background: rgba(34,211,238,0.08);
    border-color: rgba(34,211,238,0.35);
    transform: translateX(5px);
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
    background: linear-gradient(100deg, rgba(8,127,174,0.5), rgba(23,105,187,0.28));
    border-color: rgba(103,232,249,0.65);
    box-shadow: 0 0 22px rgba(34,211,238,0.22), inset 3px 0 0 var(--cyan);
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked)::before {
    background: var(--cyan);
    color: #031425;
    box-shadow: 0 0 14px var(--cyan);
}

[data-testid="stSidebar"] label[data-baseweb="radio"] p {
    font-weight: 600;
    font-size: 0.92rem;
}

.connection {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #5eead4 !important;
    background: rgba(13,148,136,.12);
    border: 1px solid rgba(45,212,191,.35);
    border-radius: 30px;
    padding: 9px 16px;
    font-size: .72rem;
    font-weight: 800;
    letter-spacing: 1px;
}

.connection-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2dd4bf;
    box-shadow: 0 0 12px #2dd4bf;
    animation: csDotPulse 2s ease-out infinite;
}

.connection.offline {
    color: #fca5a5 !important;
    background: rgba(239,68,68,.12);
    border-color: rgba(248,113,113,.4);
}

.connection.offline .connection-dot {
    background: #f87171;
    box-shadow: 0 0 12px #f87171;
}

.sys-rows { margin-top: 14px; }

.sys-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: 6px;
    border-radius: 10px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(56,189,248,0.12);
    font-size: 0.74rem;
}

.sys-row span { color: #7f9db8 !important; letter-spacing: 1px; font-weight: 600; }
.sys-row b { color: #cfe9ff !important; font-weight: 700; }

/* ---------- METRICS ---------- */

div[data-testid="stMetric"] {
    position: relative;
    overflow: hidden;
    background: linear-gradient(145deg, rgba(16,40,65,0.72), rgba(8,22,38,0.62));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px 22px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    transition: transform .3s ease, border-color .3s ease, box-shadow .3s ease;
    animation: csFadeUp .7s ease both;
}

div[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    left: 0; right: 0; top: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    border-color: var(--cyan);
    box-shadow: 0 16px 40px rgba(0,0,0,0.35), 0 0 26px rgba(34,211,238,0.22);
}

[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] { animation-delay: .08s; }
[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] { animation-delay: .16s; }
[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetric"] { animation-delay: .24s; }

div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
    color: #9bb5cd !important;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
    color: #f0f8ff !important;
    font-size: 2.4rem;
    font-weight: 800;
    text-shadow: 0 0 22px rgba(34,211,238,0.35);
}

/* ---------- CONTROLS ---------- */

.stButton > button, .stDownloadButton > button {
    background: linear-gradient(110deg,#087fae,#1769bb);
    color: white;
    border: 1px solid rgba(34,211,238,.45);
    border-radius: 10px;
    font-weight: 700;
    min-height: 42px;
    transition: all .25s ease;
    box-shadow: 0 0 0 rgba(34,211,238,0);
}

.stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(110deg,#0aa6c9,#2786e8);
    border-color: #67e8f9;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(34,211,238,0.28);
    color: white;
}

.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: rgba(9,24,42,0.78) !important;
    color: white !important;
    border-color: var(--border) !important;
    border-radius: 10px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--cyan), 0 0 18px rgba(34,211,238,0.25) !important;
}

.stSelectbox div[data-baseweb="select"] *,
.stMultiSelect div[data-baseweb="select"] * {
    color: #e8f4ff;
}

span[data-baseweb="tag"] {
    background: rgba(34,211,238,0.2) !important;
    color: #e8f4ff !important;
    border-radius: 8px !important;
}

div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li {
    background: #0b1c30 !important;
    color: #e8f4ff !important;
}

div[data-baseweb="popover"] li:hover { background: rgba(34,211,238,0.18) !important; }

[data-testid="stPlotlyChart"] {
    background: var(--panel);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    animation: csFadeUp .8s ease both;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    animation: csFadeUp .8s ease both;
}

[data-testid="stExpander"] {
    background: var(--panel);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 16px;
    animation: csFadeUp .7s ease both;
}

[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: #e8f4ff !important; }

[data-testid="stAlert"] {
    background: rgba(9,24,42,0.72);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 14px;
    animation: csFadeUp .6s ease both;
}

hr {
    border-color: var(--border);
}

.section-caption {
    color: var(--muted);
    font-size: 0.9rem;
    margin-top: -10px;
    margin-bottom: 20px;
}

/* ---------- FINDING CARD ---------- */

.finding-card {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, rgba(16,40,65,0.7), rgba(8,22,38,0.6));
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px 26px;
    margin: 6px 0 14px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.28);
    animation: csFadeUp .7s ease both;
}

.finding-card:before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--cyan), var(--blue));
    box-shadow: 0 0 14px var(--cyan);
}

.finding-title { font-size: 1.15rem; font-weight: 800; color: #f0f8ff; margin-bottom: 12px; }

.finding-meta { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; color: #b5cce0; font-size: 0.86rem; }

.finding-meta .item {
    padding: 6px 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(56,189,248,0.14);
}

.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 30px;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.sev-high { background: rgba(239,68,68,.16); color: #fca5a5; border: 1px solid rgba(248,113,113,.5); }
.sev-med  { background: rgba(245,158,11,.16); color: #fcd34d; border: 1px solid rgba(251,191,36,.5); }
.sev-low  { background: rgba(59,130,246,.18); color: #93c5fd; border: 1px solid rgba(96,165,250,.5); }
.sev-info { background: rgba(148,163,184,.16); color: #cbd5e1; border: 1px solid rgba(148,163,184,.4); }

/* ---------- HERO ---------- */

.hero {
    position: relative;
    overflow: hidden;
    max-width: min(820px, 100%);
    min-height: 360px;
    padding: 54px 58px;
    margin-bottom: 46px;
    border-radius: 26px;
    border: 1px solid rgba(103,232,249,0.3);
    background: linear-gradient(135deg, rgba(14,30,50,0.64), rgba(6,16,30,0.5));
    backdrop-filter: blur(14px) saturate(130%);
    box-shadow: 0 24px 70px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    animation: csFadeUp .9s ease both;
}

.hero:before {
    content: "";
    position: absolute;
    left: 0; right: 0; top: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}

.hero:after {
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    left: -45%;
    width: 30%;
    background: linear-gradient(100deg, transparent, rgba(103,232,249,0.09), transparent);
    animation: csSheen 8s ease-in-out infinite;
}

.hero-content {
    position: relative;
    z-index: 5;
}

.eyebrow {
    color: #22d3ee;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 4px;
    margin-bottom: 23px;
}

.hero h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-size: clamp(2.3rem,4.5vw,4rem);
    font-weight: 800;
    letter-spacing: -1.5px;
    line-height: 1.15;
    background: linear-gradient(90deg,#e5faff,#55d5ff,#3b82f6,#55d5ff,#e5faff);
    background-size: 200% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: csShimmer 8s linear infinite;
    margin: 0 0 22px 0;
    padding: 0;
    text-shadow: none;
}

.hero-description {
    color: #c3d8ea;
    font-size: 1.05rem;
    line-height: 1.85;
    max-width: 620px;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-top: 26px;
    padding: 12px 20px;
    border: 1px solid rgba(34,211,238,.4);
    border-radius: 40px;
    background: rgba(8,145,178,.14);
    color: #8eeaff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

.hero-pill i {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2dd4bf;
    animation: csDotPulse 2s ease-out infinite;
}

.cs-footer {
    text-align: center;
    color: #7894ad;
    padding: 18px;
    font-size: 12px;
    letter-spacing: 1px;
}

/* ---------- RESPONSIVE ---------- */

@media(max-width:900px) {
    .hero { padding: 34px 24px; min-height: 380px; max-width: 100%; }
    .cs-globe { left: 62%; width: 130vh; opacity: .5; }
    .cs-scrim { background: linear-gradient(90deg, rgba(3,13,27,0.85), rgba(3,13,27,0.6)); }
    .cs-fly { display: none; }
    div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * { font-size: 1.9rem; }
}

@media(prefers-reduced-motion: reduce) {
    *, *:before, *:after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
    }
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# UI VISUAL HELPERS (presentation only)
# --------------------------------------------------

def html_block(markup):
    """Collapse markup to a single line so Markdown never shows it as code."""
    return "".join(line.strip() for line in markup.strip().splitlines())


def _rnd(i, k):
    v = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return v - math.floor(v)


def _point_in_polygon(lon, lat, polygon):
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


LAND_POLYGONS = [
    # North America
    [(-168,65),(-164,70),(-156,71.5),(-141,69.5),(-125,70),(-110,68),(-95,71),(-90,68),
     (-82,69),(-82,63),(-93,60),(-94,57),(-88,56),(-82,53),(-79,55),(-78,60),(-72,61),
     (-65,60),(-61,56),(-56,52),(-59,48),(-64,46),(-67,44),(-70,42),(-74,40),(-76,36),
     (-81,31),(-80,26),(-82,27),(-84,30),(-89,30),(-94,29),(-97,26),(-97,21),(-95,18),
     (-91,19),(-90,21),(-87,21),(-88,16),(-84,15),(-83,11),(-80,9),(-77,8),(-79,7.5),
     (-83,8),(-86,11),(-88,13),(-92,15),(-96,16),(-100,17),(-105,20),(-106,23),(-109,26),
     (-112,29),(-114,31),(-117,33),(-121,35),(-124,40),(-124,46),(-125,49),(-130,54),
     (-135,58),(-140,60),(-148,60),(-152,58),(-158,57),(-163,55),(-158,58),(-162,60),
     (-165,62)],
    # Greenland
    [(-52,60),(-44,60),(-40,65),(-22,70),(-20,76),(-18,81),(-35,83),(-60,82),(-72,78),
     (-58,75),(-53,70),(-50,65)],
    # Canadian arctic
    [(-80,63),(-68,63),(-62,67),(-72,71),(-85,72),(-90,70)],
    [(-90,76),(-75,78),(-62,82),(-80,83),(-90,81)],
    # South America
    [(-77,8),(-72,12),(-62,10),(-52,5),(-50,0),(-44,-2),(-35,-5),(-35,-9),(-39,-14),
     (-41,-22),(-48,-26),(-53,-34),(-58,-38),(-62,-40),(-65,-45),(-68,-52),(-70,-55),
     (-74,-52),(-74,-45),(-73,-37),(-71,-30),(-70,-18),(-76,-14),(-81,-5),(-80,0),
     (-78,3)],
    # Eurasia
    [(-5.5,36),(-9,37),(-9,43.5),(-1.5,46),(-4.5,48.5),(1.5,50.5),(4,52),(8,54),(8.5,57),
     (10.5,57.5),(11,54.5),(14,54),(19,54.5),(21,57),(24,59.5),(30,60),(33,66),(40,67),
     (44,68),(60,69),(70,73),(80,73),(100,77),(113,74),(130,72),(142,72),(160,70),
     (170,70),(180,68),(180,65),(170,60),(163,58),(160,53),(156,57),(150,59),(142,59),
     (137,54),(141,52),(140,48),(135,43),(130,42),(129,36),(126,35),(125,39),(122,40),
     (121,37),(119,35),(122,31),(121,28),(117,23),(110,21),(108,21),(106,18),(109,13),
     (105,9),(103,10),(100,13),(99,10),(100,6),(103,1.5),(100,3),(98,8),(98,14),(94,17),
     (92,21),(89,22),(87,21),(85,19),(80,15),(80,10),(77,8),(73,16),(72,21),(69,22),
     (66,25),(61,25),(57,26),(56,27),(52,28),(48,30),(50,26),(52,24),(56,25),(59,22),
     (55,17),(52,16),(45,13),(43,13),(39,21),(35,28),(34,31),(35,33),(36,36),(30,36),
     (27,37),(26,40),(23,40),(22,37),(21,39),(19,42),(16,41),(18,40),(16,38),(15,40),
     (12,42),(10,44),(7,43.5),(3,43),(0,39),(-2,37)],
    # Africa
    [(-5.5,36),(-10,30),(-17,21),(-17,14),(-13,9),(-8,4.5),(-2,5),(5,6),(9,4),(9,-1),
     (12,-6),(13,-12),(12,-18),(15,-27),(18,-34),(21,-35),(27,-34),(33,-27),(35,-22),
     (35,-17),(40,-15),(40,-10),(39,-5),(41,-1),(48,5),(51,11),(43,12),(39,16),(35,24),
     (33,28),(32,31),(25,32),(20,31),(11,33),(10,37),(3,37),(-2,35)],
    # Australia
    [(114,-22),(122,-18),(130,-12),(136,-12),(137,-16),(142,-11),(146,-19),(153,-26),
     (151,-34),(146,-39),(140,-38),(135,-35),(130,-32),(124,-34),(115,-34),(114,-28)],
    # Scandinavia, UK, Ireland, Iceland
    [(5,59),(5,62),(14,68),(20,70),(28,71),(31,70),(30,66),(25,65),(22,63),(21,61),
     (18,60),(17,57),(13,55.5),(11,59),(8,58)],
    [(-5,50),(-3,51),(1,52),(-2,56),(-3,58.5),(-6,58),(-5,55),(-3,54),(-4.5,52)],
    [(-10,52),(-6,52),(-6,55),(-9,54)],
    [(-24,64),(-18,66),(-13,65),(-18,63.5)],
    # Japan
    [(131,34),(135,34),(140,35),(142,39),(141,41),(139,38),(136,37),(132,35)],
    [(140,42),(144,43),(145,44),(142,45.5)],
    # Indonesia, Borneo, Java, New Guinea, NZ, Madagascar
    [(95,5),(98,4),(104,-2),(106,-6),(101,-3),(96,2)],
    [(109,1),(113,3),(117,7),(119,1),(116,-3),(111,-3)],
    [(105,-6),(114,-8),(106,-7)],
    [(131,-1),(138,-2),(147,-6),(150,-10),(142,-9),(138,-8),(132,-4)],
    [(173,-35),(178,-38),(175,-41),(174,-39)],
    [(172,-41),(174,-42),(170,-46),(167,-45)],
    [(44,-25),(47,-25),(50,-15),(49,-12),(44,-17)],
]

CITY_NODES = [
    ("New York", -74.0, 40.7), ("London", -0.1, 51.5), ("Bengaluru", 77.6, 13.0),
    ("Singapore", 103.8, 1.3), ("Tokyo", 139.7, 35.7), ("Sydney", 151.2, -33.9),
    ("Sao Paulo", -46.6, -23.5), ("Cape Town", 18.4, -33.9), ("Dubai", 55.3, 25.2),
    ("San Francisco", -122.4, 37.8), ("Frankfurt", 8.7, 50.1), ("Nairobi", 36.8, -1.3),
]

CITY_LINKS = [(0, 1), (1, 8), (8, 2), (2, 3), (3, 4), (3, 5), (6, 0), (6, 7),
              (7, 11), (11, 8), (9, 0), (1, 10), (10, 8)]

ICON_PATHS = {
    "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "cloud": '<path d="M7 18a4 4 0 0 1-.5-8 5.5 5.5 0 0 1 10.6 1.5A3.3 3.3 0 0 1 17 18z"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "bug": '<rect x="8" y="8" width="8" height="11" rx="4"/><path d="M12 8V5M8 12H4M16 12h4M8 17l-3 2M16 17l3 2M9 5l3-2 3 2"/>',
    "key": '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v4M21 12v3"/>',
    "wifi": '<path d="M3 9a14 14 0 0 1 18 0M6 12.5a9.5 9.5 0 0 1 12 0M9 16a5 5 0 0 1 6 0"/><circle cx="12" cy="19" r="1"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/>',
    "play": '<path d="M8 5l11 7-11 7z"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
}

FLY_ICONS = [
    (63, 6, 40, "chat", 7.5, 2), (88, 14, 36, "cloud", 9.0, 5), (95, 36, 34, "lock", 8.0, 3),
    (86, 56, 40, "play", 10.0, 7), (93, 76, 36, "wifi", 8.5, 1), (72, 88, 34, "bug", 9.5, 4),
    (47, 8, 32, "code", 7.0, 6), (38, 88, 30, "key", 8.8, 2), (56, 92, 34, "shield", 9.2, 8),
    (78, 28, 28, "lock", 7.8, 9), (68, 70, 28, "cloud", 10.5, 3),
]

SHIELD_PATH = "M100 8 L184 40 V112 C184 168 148 208 100 232 C52 208 16 168 16 112 V40 Z"
SHIELD_INNER = "M100 28 L166 52 V112 C166 156 138 188 100 208 C62 188 34 156 34 112 V52 Z"
LOCK_SVG = (
    '<rect x="66" y="104" width="68" height="56" rx="9" fill="#e6fbff" fill-opacity="0.94"/>'
    '<path d="M80 104V90a20 20 0 0 1 40 0v14" fill="none" stroke="#e6fbff" stroke-width="10" stroke-linecap="round"/>'
    '<circle cx="100" cy="128" r="8" fill="#0a3556"/>'
    '<rect x="96.5" y="130" width="7" height="18" rx="3" fill="#0a3556"/>'
)


@st.cache_data(show_spinner=False)
def build_land_path(step=3.6):
    boxes = []
    for poly in LAND_POLYGONS:
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        boxes.append((min(xs), max(xs), min(ys), max(ys)))

    parts = []
    row = 0
    y = step / 2
    while y < 180:
        sin_lat = max(-1.0, min(1.0, (90 - y) / 90.0))
        lat = math.degrees(math.asin(sin_lat))
        x = (step / 2) if row % 2 else 0.0
        while x < 360:
            lon = x - 180
            for poly, (x0, x1, y0, y1) in zip(LAND_POLYGONS, boxes):
                if x0 <= lon <= x1 and y0 <= lat <= y1 and _point_in_polygon(lon, lat, poly):
                    parts.append(f"M{x:.1f} {y:.1f}h0")
                    break
            x += step
        y += step
        row += 1
    return "".join(parts)


def _map_xy(lon, lat):
    return lon + 180, 90 - 90 * math.sin(math.radians(lat))


def _network_group(offset):
    out = [f'<g transform="translate({offset} 0)">']
    for a, b in CITY_LINKS:
        x1, y1 = _map_xy(CITY_NODES[a][1], CITY_NODES[a][2])
        x2, y2 = _map_xy(CITY_NODES[b][1], CITY_NODES[b][2])
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2 - 0.28 * math.hypot(x2 - x1, y2 - y1)
        out.append(f'<path class="cs-arc" d="M{x1:.1f} {y1:.1f}Q{mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}"/>')
    for i, (_, lon, lat) in enumerate(CITY_NODES):
        x, y = _map_xy(lon, lat)
        out.append(
            f'<circle class="cs-node-halo" cx="{x:.1f}" cy="{y:.1f}" r="1.6" '
            f'style="animation-delay:-{(i * 0.37) % 2.8:.2f}s"/>'
            f'<circle class="cs-node" cx="{x:.1f}" cy="{y:.1f}" r="0.7"/>'
        )
    out.append("</g>")
    return "".join(out)


def _shield_layers():
    layers = []
    for z in range(-14, 15, 4):
        if z == 14:
            layers.append(
                f'<div class="cs-sl" style="transform:translateZ({z}px)">'
                '<svg viewBox="0 0 200 240"><defs>'
                '<linearGradient id="csShF" x1="0" y1="0" x2="1" y2="1">'
                '<stop offset="0" stop-color="#4fe3ff" stop-opacity="0.78"/>'
                '<stop offset="1" stop-color="#1769bb" stop-opacity="0.62"/></linearGradient></defs>'
                f'<path d="{SHIELD_PATH}" fill="url(#csShF)" stroke="#9af3ff" stroke-width="3.5" stroke-linejoin="round"/>'
                f'<path d="{SHIELD_INNER}" fill="rgba(3,20,40,0.28)" stroke="#bff8ff" stroke-width="1.6" stroke-opacity="0.8"/>'
                f'{LOCK_SVG}</svg></div>'
            )
        elif z == -14:
            layers.append(
                f'<div class="cs-sl" style="transform:translateZ({z}px) rotateY(180deg)">'
                '<svg viewBox="0 0 200 240"><defs>'
                '<linearGradient id="csShB" x1="0" y1="0" x2="1" y2="1">'
                '<stop offset="0" stop-color="#2cb8e6" stop-opacity="0.78"/>'
                '<stop offset="1" stop-color="#14529a" stop-opacity="0.66"/></linearGradient></defs>'
                f'<path d="{SHIELD_PATH}" fill="url(#csShB)" stroke="#7fe9ff" stroke-width="3.5" stroke-linejoin="round"/>'
                f'<path d="{SHIELD_INNER}" fill="rgba(3,20,40,0.28)" stroke="#bff8ff" stroke-width="1.6" stroke-opacity="0.8"/>'
                f'{LOCK_SVG}</svg></div>'
            )
        else:
            layers.append(
                f'<div class="cs-sl mid" style="transform:translateZ({z}px)">'
                '<svg viewBox="0 0 200 240">'
                f'<path d="{SHIELD_PATH}" fill="rgba(14,116,160,0.38)" stroke="#5ee7ff" stroke-width="2.2" stroke-linejoin="round"/>'
                '</svg></div>'
            )
    return "".join(layers)


@st.cache_data(show_spinner=False)
def build_stage_html():
    dots = build_land_path()
    land = (
        f'<path d="{dots}" fill="none" stroke="#67e8f9" stroke-width="1.15" '
        f'stroke-linecap="round" stroke-opacity="0.92"/>'
    )
    map_group = (
        '<g class="cs-map-scroll">'
        f'<g>{land}{_network_group(0)}</g>'
        f'<g transform="translate(360 0)">{land}{_network_group(0)}</g>'
        '</g>'
    )

    lat_lines = ""
    for lat in (-60, -30, 0, 30, 60):
        yy = 90 - 90 * math.sin(math.radians(lat))
        op = "0.38" if lat == 0 else "0.2"
        lat_lines += (
            f'<line x1="0" x2="180" y1="{yy:.1f}" y2="{yy:.1f}" '
            f'stroke="rgba(56,189,248,{op})" stroke-width="0.28"/>'
        )

    meridians = "".join(
        f'<ellipse class="cs-mer" cx="90" cy="90" rx="90" ry="90" '
        f'style="animation-delay:-{k * 7.5}s"/>'
        for k in range(6)
    )

    globe_svg = (
        '<svg class="cs-globe-svg" viewBox="0 0 180 180" xmlns="http://www.w3.org/2000/svg">'
        '<defs>'
        '<radialGradient id="csSphereFill" cx="38%" cy="32%" r="80%">'
        '<stop offset="0" stop-color="#0f6590"/><stop offset="0.55" stop-color="#0a3556"/>'
        '<stop offset="1" stop-color="#041526"/></radialGradient>'
        '<radialGradient id="csLimb" cx="50%" cy="50%" r="50%">'
        '<stop offset="0.6" stop-color="#030d1b" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#030d1b" stop-opacity="0.82"/></radialGradient>'
        '<clipPath id="csClip"><circle cx="90" cy="90" r="90"/></clipPath>'
        '</defs>'
        '<circle cx="90" cy="90" r="90" fill="url(#csSphereFill)"/>'
        f'<g clip-path="url(#csClip)">{lat_lines}{meridians}{map_group}'
        '<circle cx="90" cy="90" r="90" fill="url(#csLimb)"/></g>'
        '<circle cx="90" cy="90" r="89.6" fill="none" stroke="rgba(103,232,249,0.55)" stroke-width="0.4"/>'
        '</svg>'
    )

    particles = ""
    for i in range(46):
        size = 1.6 + _rnd(i, 3) * 3.6
        particles += (
            f'<span class="cs-particle" style="left:{_rnd(i, 1) * 100:.1f}%;top:{_rnd(i, 2) * 100:.1f}%;'
            f'width:{size:.1f}px;height:{size:.1f}px;animation-duration:{9 + _rnd(i, 4) * 14:.1f}s;'
            f'animation-delay:-{_rnd(i, 5) * 20:.1f}s"></span>'
        )

    fly = ""
    for left, top, size, icon, dur, delay in FLY_ICONS:
        fly += (
            f'<div class="cs-fly" style="left:{left}%;top:{top}%;width:{size}px;height:{size}px;'
            f'animation-duration:{dur}s;animation-delay:-{delay}s">'
            f'<svg viewBox="0 0 24 24">{ICON_PATHS[icon]}</svg></div>'
        )

    return (
        '<div class="cs-stage">'
        '<div class="cs-stars"></div><div class="cs-grid"></div>'
        f'{particles}'
        '<div class="cs-globe">'
        '<div class="cs-halo"></div>'
        '<div class="cs-orbit o1"></div><div class="cs-orbit o2"></div>'
        '<div class="cs-sphere">'
        f'{globe_svg}'
        '<div class="cs-shield-wrap"><div class="cs-shield-aura"></div>'
        f'<div class="cs-shield3d">{_shield_layers()}</div></div>'
        '<div class="cs-gloss"></div>'
        '</div></div>'
        f'{fly}'
        '<div class="cs-scrim"></div><div class="cs-vignette"></div>'
        '</div>'
    )


SIDEBAR_LOGO = """
<div class="cs-logo">
<div class="cs-logo-mark">
<svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="csLogoGrad" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#4fe3ff"/><stop offset="1" stop-color="#1769bb"/></linearGradient></defs>
<path d="M100 8 L184 40 V112 C184 168 148 208 100 232 C52 208 16 168 16 112 V40 Z" fill="url(#csLogoGrad)" stroke="#9af3ff" stroke-width="6" stroke-linejoin="round"/>
<rect x="66" y="104" width="68" height="56" rx="9" fill="#e6fbff"/>
<path d="M80 104V90a20 20 0 0 1 40 0v14" fill="none" stroke="#e6fbff" stroke-width="10" stroke-linecap="round"/>
<circle cx="100" cy="128" r="8" fill="#0a3556"/><rect x="96.5" y="130" width="7" height="18" rx="3" fill="#0a3556"/>
</svg>
</div>
<div>
<div class="brand">CyberShield <span>AI</span></div>
<div class="sidebar-label">APPLICATION SECURITY INTELLIGENCE</div>
</div>
</div>
"""

SEVERITY_COLORS = {
    "Critical": "#dc2626", "High": "#ef4444", "Medium": "#f59e0b",
    "Low": "#3b82f6", "Informational": "#22c55e", "Unknown": "#94a3b8"
}

STATUS_COLORS = {
    "Needs Validation": "#f59e0b", "Confirmed": "#22c55e", "False Positive": "#ef4444"
}


def style_figure(fig, height=340):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cfe6fa"),
        margin=dict(t=20, b=20, l=10, r=10),
        height=height,
        legend_title_text=""
    )
    fig.update_xaxes(gridcolor="rgba(56,189,248,0.10)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(56,189,248,0.10)", zeroline=False)
    return fig


def text_of(value):
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def severity_class(value):
    v = text_of(value).lower()
    if v.startswith("crit") or v.startswith("high"):
        return "sev-high"
    if v.startswith("med"):
        return "sev-med"
    if v.startswith("low"):
        return "sev-low"
    return "sev-info"


def finding_card(finding, show_status=False):
    name = escape(text_of(finding.get("name", "")))
    severity = escape(text_of(finding.get("severity", "")) or "Unknown")
    url = escape(text_of(finding.get("affected_url", "")))
    risk = escape(text_of(finding.get("risk_score", 0)))
    status_chip = ""
    if show_status:
        status_chip = (
            f'<span class="item">Current status: <b>'
            f'{escape(text_of(finding.get("status", "")))}</b></span>'
        )
    st.markdown(
        html_block(f"""
<div class="finding-card">
<div class="finding-title">{name}</div>
<div class="finding-meta">
<span class="badge {severity_class(finding.get("severity", ""))}">{severity}</span>
<span class="item">Risk score: <b>{risk}</b></span>
<span class="item">Affected URL: {url}</span>
{status_chip}
</div>
</div>
"""),
        unsafe_allow_html=True
    )


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_connection():
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_vulnerabilities():
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()

    try:
        df = pd.read_sql_query(
            "SELECT * FROM vulnerabilities ORDER BY risk_score DESC",
            conn
        )
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def safe_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def normalize_status(value):
    if not value:
        return "Needs Validation"
    return str(value)


def api_is_online():
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        try:
            response = requests.get(API_URL, timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False


def section_title(title, subtitle):
    st.markdown(f"## {title}")
    st.markdown(
        f'<p class="section-caption">{subtitle}</p>',
        unsafe_allow_html=True
    )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(html_block(SIDEBAR_LOGO), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Security Overview",
            "Vulnerability Explorer",
            "AI Vulnerability Analysis",
            "Manual Validation",
            "PDF VAPT Report"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### SYSTEM CONNECTIONS")

    online = api_is_online()

    if online:
        st.markdown(
            '<div class="connection"><span class="connection-dot"></span> API CONNECTED</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="connection offline"><span class="connection-dot"></span> API OFFLINE</div>',
            unsafe_allow_html=True
        )

    backend_host = API_URL.split("//")[-1]
    st.markdown(
        html_block(f"""
<div class="sys-rows">
<div class="sys-row"><span>BACKEND</span><b>{escape(backend_host)}</b></div>
<div class="sys-row"><span>STORAGE</span><b>SQLite</b></div>
<div class="sys-row"><span>SCANNER</span><b>OWASP ZAP</b></div>
</div>
"""),
        unsafe_allow_html=True
    )

    st.markdown("")

    if st.button("↻ Refresh workspace", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("CyberShield AI · Security Operations Workspace")
    st.caption("Local assessment environment")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = load_vulnerabilities()

if not df.empty:
    if "risk_score" not in df.columns:
        df["risk_score"] = 0

    if "severity" not in df.columns:
        df["severity"] = "Unknown"

    if "status" not in df.columns:
        df["status"] = "Needs Validation"

    if "analyst_notes" not in df.columns:
        df["analyst_notes"] = ""

    df["risk_score"] = pd.to_numeric(
        df["risk_score"], errors="coerce"
    ).fillna(0)

    df["status"] = df["status"].apply(normalize_status)


# --------------------------------------------------
# BACKGROUND STAGE + HERO
# --------------------------------------------------

st.markdown(build_stage_html(), unsafe_allow_html=True)

st.markdown(
    html_block("""
<div class="hero">
<div class="hero-content">
<div class="eyebrow">APPLICATION SECURITY • THREAT INTELLIGENCE</div>
<h1>CyberShield AI</h1>
<div class="hero-description">Intelligent vulnerability assessment, AI-powered security analysis, risk prioritization and manual validation in one unified security workspace.</div>
<div class="hero-pill"><i></i>SECURITY OPERATIONS CENTER &nbsp;/&nbsp; LOCAL ENVIRONMENT</div>
</div>
</div>
"""),
    unsafe_allow_html=True
)


# --------------------------------------------------
# SECURITY OVERVIEW
# --------------------------------------------------

if page == "Security Overview":

    section_title(
        "Security Overview",
        "Live snapshot of your vulnerability assessment environment."
    )

    if df.empty:
        st.info("No vulnerability findings found. Import a scanner report first.")
    else:
        total = len(df)
        average = df["risk_score"].mean()
        highest = df["risk_score"].max()
        confirmed = int((df["status"] == "Confirmed").sum())

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("TOTAL FINDINGS", total)
        c2.metric("AVERAGE RISK", f"{average:.1f}")
        c3.metric("HIGHEST RISK", f"{highest:.1f}")
        c4.metric("CONFIRMED", confirmed)

        st.markdown("---")

        left, right = st.columns(2)

        with left:
            section_title(
                "Severity Distribution",
                "Breakdown by scanner severity."
            )

            severity_data = (
                df["severity"]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )
            severity_data.columns = ["Severity", "Count"]

            fig = px.pie(
                severity_data,
                names="Severity",
                values="Count",
                hole=0.62,
                color="Severity",
                color_discrete_map=SEVERITY_COLORS,
                color_discrete_sequence=[
                    "#ef4444", "#f59e0b", "#3b82f6",
                    "#22c55e", "#94a3b8"
                ]
            )
            fig.update_traces(
                marker=dict(line=dict(color="#030d1b", width=2)),
                textinfo="percent"
            )
            style_figure(fig)
            fig.add_annotation(
                text=f"<b>{total}</b><br>FINDINGS",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=15, color="#e8f4ff")
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            section_title(
                "Validation Status",
                "Analyst review progress."
            )

            status_data = (
                df["status"]
                .fillna("Needs Validation")
                .value_counts()
                .reset_index()
            )
            status_data.columns = ["Status", "Count"]

            fig = px.bar(
                status_data,
                x="Status",
                y="Count",
                color="Status",
                text="Count",
                color_discrete_map=STATUS_COLORS,
                color_discrete_sequence=[
                    "#f59e0b", "#22c55e", "#ef4444"
                ]
            )
            fig.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False)
            style_figure(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        left2, right2 = st.columns(2)

        with left2:
            section_title(
                "Risk Score Distribution",
                "How findings spread across the custom risk score."
            )

            fig = px.histogram(
                df,
                x="risk_score",
                nbins=10,
                labels={"risk_score": "Risk score"}
            )
            fig.update_traces(
                marker_color="#22d3ee",
                marker_line_color="#030d1b",
                marker_line_width=1.5,
                opacity=0.9
            )
            style_figure(fig)
            fig.update_layout(bargap=0.08, yaxis_title="Findings")
            st.plotly_chart(fig, use_container_width=True)

        with right2:
            section_title(
                "Average Risk by Severity",
                "Mean risk score for each scanner severity level."
            )

            risk_by_severity = (
                df.assign(severity=df["severity"].fillna("Unknown"))
                .groupby("severity", as_index=False)["risk_score"]
                .mean()
            )
            risk_by_severity["risk_score"] = risk_by_severity["risk_score"].round(1)

            fig = px.bar(
                risk_by_severity,
                x="severity",
                y="risk_score",
                color="severity",
                text="risk_score",
                color_discrete_map=SEVERITY_COLORS,
                labels={"severity": "Severity", "risk_score": "Average risk"}
            )
            fig.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False)
            style_figure(fig)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        section_title(
            "Highest Risk Findings",
            "Prioritized findings based on the custom risk score."
        )

        top = df.nlargest(5, "risk_score")

        display_cols = [
            col for col in [
                "id", "name", "severity", "affected_url",
                "risk_score", "status"
            ] if col in top.columns
        ]

        st.dataframe(
            top[display_cols],
            use_container_width=True,
            hide_index=True
        )


# --------------------------------------------------
# VULNERABILITY EXPLORER
# --------------------------------------------------

elif page == "Vulnerability Explorer":

    section_title(
        "Vulnerability Explorer",
        "Search, filter and inspect imported scanner findings."
    )

    if df.empty:
        st.info("No vulnerabilities are available.")
    else:
        f1, f2, f3 = st.columns(3)

        severities = sorted(
            df["severity"].fillna("Unknown").unique().tolist()
        )

        selected_severity = f1.multiselect(
            "Filter by severity",
            severities,
            default=severities
        )

        statuses = sorted(
            df["status"].fillna("Needs Validation").unique().tolist()
        )

        selected_status = f2.multiselect(
            "Filter by validation status",
            statuses,
            default=statuses
        )

        search = f3.text_input(
            "Search findings",
            placeholder="Search name, URL, CWE..."
        )

        filtered = df[
            df["severity"].fillna("Unknown").isin(selected_severity)
            & df["status"].fillna("Needs Validation").isin(selected_status)
        ].copy()

        if search:
            searchable = filtered.astype(str).apply(
                lambda col: col.str.contains(
                    search, case=False, na=False
                )
            ).any(axis=1)
            filtered = filtered[searchable]

        st.caption(f"Showing {len(filtered)} of {len(df)} findings")

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        if not filtered.empty:
            selected_id = st.selectbox(
                "Inspect vulnerability ID",
                filtered["id"].tolist()
            )

            finding = filtered[
                filtered["id"] == selected_id
            ].iloc[0]

            finding_card(finding)

            with st.expander("View complete finding details", expanded=True):
                st.write("**Finding:**", finding.get("name", ""))
                st.write("**Severity:**", finding.get("severity", ""))
                st.write("**Affected URL:**", finding.get("affected_url", ""))
                st.write("**CWE:**", finding.get("cwe_id", "Not mapped"))
                st.write("**Description:**", finding.get("description", ""))
                st.write("**Evidence:**", finding.get("evidence", ""))
                st.write("**Solution:**", finding.get("solution", "Not available"))
                st.write("**Risk Score:**", finding.get("risk_score", 0))


# --------------------------------------------------
# AI VULNERABILITY ANALYSIS
# --------------------------------------------------

elif page == "AI Vulnerability Analysis":

    section_title(
        "AI Vulnerability Analysis",
        "Evidence-grounded explanations and remediation guidance."
    )

    if df.empty:
        st.info("Import vulnerabilities before requesting AI analysis.")
    else:
        selected_id = st.selectbox(
            "Select vulnerability ID",
            df["id"].tolist()
        )

        finding = df[df["id"] == selected_id].iloc[0]

        st.markdown("### Selected Finding")
        finding_card(finding)

        if st.button("✦ Generate AI Security Analysis"):
            if not online:
                st.error("Backend API is offline. Start FastAPI first.")
            else:
                with st.spinner("AI is analyzing the vulnerability..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/vulnerabilities/{selected_id}/analyze",
                            timeout=120
                        )

                        if response.status_code == 200:
                            result = response.json()
                            analysis_data = result.get(
                                "ai_analysis", result
                            )

                            st.session_state[
                                f"ai_result_{selected_id}"
                            ] = analysis_data
                        else:
                            st.error(
                                f"Analysis failed: {response.status_code}"
                            )
                            st.code(response.text)

                    except requests.RequestException as e:
                        st.error(f"Could not contact AI endpoint: {e}")

        result = st.session_state.get(
            f"ai_result_{selected_id}"
        )

        if result:
            st.markdown("---")
            st.markdown("### AI Analysis")

            if isinstance(result, dict):
                st.markdown(
                    result.get("analysis", str(result))
                )
                st.caption(
                    f"Provider: {result.get('provider', 'AI')} · "
                    f"Model: {result.get('model', 'Configured model')}"
                )

                if result.get("automatically_confirmed") is False:
                    st.info(
                        "AI analysis does not automatically confirm a finding. "
                        "Analyst validation is required."
                    )
            else:
                st.write(result)


# --------------------------------------------------
# MANUAL VALIDATION
# --------------------------------------------------

elif page == "Manual Validation":

    section_title(
        "Manual Validation",
        "Review findings and record the security analyst's decision."
    )

    if df.empty:
        st.info("No findings are available for validation.")
    else:
        selected_id = st.selectbox(
            "Select vulnerability ID",
            df["id"].tolist(),
            key="validation_id"
        )

        finding = df[df["id"] == selected_id].iloc[0]

        st.markdown("### Finding Details")
        finding_card(finding, show_status=True)

        st.markdown("---")

        status_options = [
            "Needs Validation",
            "Confirmed",
            "False Positive"
        ]

        current_status = finding.get(
            "status", "Needs Validation"
        )

        default_index = (
            status_options.index(current_status)
            if current_status in status_options else 0
        )

        new_status = st.selectbox(
            "Validation decision",
            status_options,
            index=default_index
        )

        existing_notes = finding.get("analyst_notes", "")
        if pd.isna(existing_notes):
            existing_notes = ""

        analyst_notes = st.text_area(
            "Analyst notes",
            value=str(existing_notes),
            placeholder="Explain the evidence and reason for your decision..."
        )

        if st.button("Save Validation Decision"):
            if not online:
                st.error("Backend API is offline.")
            else:
                try:
                    response = requests.patch(
                        f"{API_URL}/vulnerabilities/{selected_id}/status",
                        json={
                            "status": new_status,
                            "analyst_notes": analyst_notes
                        },
                        timeout=15
                    )

                    if response.status_code == 200:
                        st.success(
                            "Validation decision saved successfully."
                        )
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(
                            f"Could not save decision: {response.status_code}"
                        )
                        st.code(response.text)

                except requests.RequestException as e:
                    st.error(f"Backend connection error: {e}")

        st.caption(
            "Final vulnerability confirmation is a manual analyst decision."
        )


# --------------------------------------------------
# PDF VAPT REPORT
# --------------------------------------------------

elif page == "PDF VAPT Report":

    section_title(
        "PDF VAPT Report",
        "Generate and retrieve your vulnerability assessment report."
    )

    st.markdown("""
    The VAPT report contains vulnerability findings, risk prioritization,
    severity distribution, validation status and remediation information.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Available Findings",
            len(df) if not df.empty else 0
        )

    with col2:
        st.metric(
            "Report Storage",
            "Local /reports"
        )

    st.markdown("---")

    if st.button("Generate and Download Latest PDF Report"):
        if not online:
            st.error("Backend API is offline.")
        else:
            with st.spinner("Generating VAPT report..."):
                try:
                    response = requests.get(
                        f"{API_URL}/reports/pdf",
                        timeout=120
                    )

                    if response.status_code == 200:
                        filename = (
                            f"CyberShield_VAPT_Report_"
                            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        )

                        st.download_button(
                            label="⬇ Download VAPT Report",
                            data=response.content,
                            file_name=filename,
                            mime="application/pdf"
                        )
                        st.success("Report generated successfully.")
                    else:
                        st.error(
                            f"Report generation failed: {response.status_code}"
                        )
                        st.code(response.text)

                except requests.RequestException as e:
                    st.error(f"Report API error: {e}")

    st.markdown("### Previously Generated Reports")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    reports = sorted(
        REPORT_DIR.glob("*.pdf"),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    if not reports:
        st.info("No previously generated PDF reports found.")
    else:
        for report in reports:
            with open(report, "rb") as file:
                report_bytes = file.read()

            st.download_button(
                label=f"⬇ {report.name}",
                data=report_bytes,
                file_name=report.name,
                mime="application/pdf",
                key=f"download_{report.name}"
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <div class="cs-footer">
        🛡️ CYBERSHIELD AI &nbsp; · &nbsp;
        APPLICATION SECURITY INTELLIGENCE
        <br><br>
        AI-assisted vulnerability assessment.
        All findings require appropriate security analyst review.
    </div>
    """,
    unsafe_allow_html=True
)