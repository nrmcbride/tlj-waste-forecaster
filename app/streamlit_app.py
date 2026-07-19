import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logger import load_log, calculate_accuracy
from core.data_loader import load_tracker, load_pricing, get_product_list
from core.weather import get_tomorrow_weather
from core.school_calendar import get_school_status

st.set_page_config(
    page_title="TLJ Waste Forecaster",
    page_icon="🥐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@200;300;400;500&display=swap');

/* ── LAYOUT ─────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
    background-color: #EFE0D0 !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    overflow-x: hidden !important;
}

[data-testid="stMain"] {
    flex: 1 !important;
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    background-color: #EFE0D0 !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

.block-container {
    padding-left: 3rem !important;
    padding-right: 3rem !important;
    padding-top: 0 !important;
    padding-bottom: 5rem !important;
    max-width: 100% !important;
    margin: 0 !important;
    box-sizing: border-box !important;
}

/* ── GAP FIX ─────────────────────────────────────────────────────── */
[data-testid="stVerticalBlock"] {
    gap: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stVerticalBlock"] > div:first-child,
[data-testid="stVerticalBlock"] > div:first-child > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

.st-emotion-cache-tn0cau { gap: 0 !important; }

/* ── BACKGROUND ──────────────────────────────────────────────────── */
html, body,
[data-testid="stApp"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background-color: #EFE0D0 !important;
}

[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stToolbar"] {
    display: none !important;
    height: 0 !important;
}

/* ── SIDEBAR ─────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    position: relative !important;
    left: 0 !important;
    top: 0 !important;
    transform: none !important;
    margin: 0 !important;
    background-color: #FFFFFF !important;
    border-right: 2px solid #0B3D2E !important;
    min-width: 240px !important;
    max-width: 240px !important;
    width: 240px !important;
    height: 100vh !important;
    flex-shrink: 0 !important;
    order: -1 !important;
    overflow-y: auto !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 100 !important;
}

section[data-testid="stSidebar"] > div {
    background-color: #FFFFFF !important;
    padding: 1.5rem 1.2rem !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] div {
    color: #0B3D2E !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── SIDEBAR COLLAPSE BUTTON ─────────────────────────────────────── */
[data-testid="stSidebarCollapseButton"] .st-emotion-cache-189uypx,
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
    display: none !important;
}

[data-testid="stSidebarCollapseButton"] button {
    background-color: #F0EBE3 !important;
    border: 1px solid #B08968 !important;
    border-radius: 4px !important;
    width: 32px !important;
    height: 32px !important;
    cursor: pointer !important;
    position: relative !important;
}

[data-testid="stSidebarCollapseButton"] button::after {
    content: '←' !important;
    color: #0B3D2E !important;
    font-size: 1.1rem !important;
    font-family: 'DM Sans', sans-serif !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
}

[data-testid="stSidebarCollapseButton"] button:hover { background-color: #0B3D2E !important; }
[data-testid="stSidebarCollapseButton"] button:hover::after { color: #EFE0D0 !important; }

[data-testid="stSidebarCollapsedControl"] {
    position: fixed !important;
    left: 0 !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    z-index: 99999 !important;
    background: #FFFFFF !important;
    border: 2px solid #0B3D2E !important;
    border-left: none !important;
    border-radius: 0 6px 6px 0 !important;
    width: 28px !important;
    height: 56px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    visibility: visible !important;
    opacity: 1 !important;
}

[data-testid="stSidebarCollapsedControl"] button {
    background: transparent !important;
    border: none !important;
    width: 100% !important;
    height: 100% !important;
    cursor: pointer !important;
    position: relative !important;
}

[data-testid="stSidebarCollapsedControl"] button::after {
    content: '→' !important;
    color: #0B3D2E !important;
    font-size: 1.1rem !important;
    font-family: 'DM Sans', sans-serif !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
}

[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg { display: none !important; }

.sidebar-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.2rem !important;
    color: #0B3D2E !important;
    font-weight: 700 !important;
    display: block !important;
    margin-bottom: 0.15rem !important;
}

.sidebar-subtitle {
    font-size: 0.68rem !important;
    color: #B08968 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 1.6rem !important;
    display: block !important;
}

.nav-section-label {
    font-size: 0.6rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    color: #B08968 !important;
    margin-top: 1.4rem !important;
    margin-bottom: 0.4rem !important;
    display: block !important;
    font-weight: 500 !important;
}

.nav-link {
    display: block !important;
    padding: 0.4rem 0 !important;
    color: #0B3D2E !important;
    text-decoration: none !important;
    font-size: 0.82rem !important;
    font-weight: 300 !important;
    border-bottom: 1px solid rgba(176,137,104,0.18) !important;
    transition: color 0.15s !important;
}

.nav-link:hover { color: #B08968 !important; }

/* ── HERO ────────────────────────────────────────────────────────── */
.hero-section {
    background: linear-gradient(
        180deg,
        #0B3D2E  0%,
        #0B3D2E 10%,
        #124233 20%,
        #234E3F 30%,
        #4E6D5E 42%,
        #96A090 54%,
        #C4C1B1 64%,
        #DED4C4 74%,
        #EBDDCD 84%,
        #EEDFCF 92%,
        #EFE0D0 100%
    );
    width: calc(100% + 6rem);
    margin-left: -3rem;
    margin-right: -3rem;
    margin-top: 0;
    padding: 7rem 3rem 10rem 3rem;
    text-align: center;
    box-sizing: border-box;
    display: block;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    color: #F9F5F1;
    line-height: 1.12;
    margin-bottom: 1.2rem;
    font-weight: 700;
    font-variant: small-caps;
    letter-spacing: 0.04em;
    text-shadow: 0 2px 24px rgba(0,0,0,0.2);
}

.hero-subtitle {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.2rem;
    color: #F9F5F1;
    opacity: 0.78;
}

/* ── NARRATIVE CARDS ─────────────────────────────────────────────── */
.narrative-card {
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(176,137,104,0.32);
    border-radius: 14px;
    padding: 2rem 2.4rem;
    margin: 1.1rem auto;
    max-width: 720px;
    box-sizing: border-box;
    box-shadow: 0 2px 16px rgba(11,61,46,0.05);
}

/* ── TYPOGRAPHY ──────────────────────────────────────────────────── */
body, p, li {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 300 !important;
    color: #3D2008 !important;
    line-height: 1.78 !important;
}

h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    color: #0B3D2E !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
}

h3 { font-size: 1.4rem !important; margin-bottom: 0.6rem !important; }
h4 { font-size: 1.1rem !important; margin-bottom: 0.4rem !important; }
strong { font-weight: 500 !important; color: #0B3D2E !important; }
em {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    color: #B08968 !important;
}

li { margin-bottom: 0.45rem !important; }
ul { padding-left: 1.3rem !important; margin-top: 0.6rem !important; }

/* ── TAG ─────────────────────────────────────────────────────────── */
.tag {
    display: inline-block;
    border: 1px solid #B08968;
    color: #B08968;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.18rem 0.65rem;
    border-radius: 2px;
    margin-bottom: 0.6rem;
}

/* ── DIVIDERS ────────────────────────────────────────────────────── */
.section-divider {
    border: none !important;
    height: 2rem !important;
    margin: 0 auto !important;
    max-width: 720px !important;
    display: block !important;
    background: transparent !important;
}

.wide-divider {
    border: none !important;
    height: 7.25rem !important;
    margin: 0 !important;
    display: block !important;
    background: transparent !important;
}

/* ── ARCHITECTURE BOXES ──────────────────────────────────────────── */
.arch-box {
    background: rgba(255,255,255,0.52);
    border: 1px solid rgba(176,137,104,0.45);
    border-radius: 6px;
    padding: 0.9rem;
    text-align: center;
    margin-bottom: 0.5rem;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.arch-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(11,61,46,0.1);
}

.arch-box-label {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.82rem;
    color: #0B3D2E;
    margin-top: 0.3rem;
}

.arch-box-desc {
    font-size: 0.72rem;
    color: #B08968;
    margin-top: 0.15rem;
    line-height: 1.4;
}

.arch-box-dark {
    background: #0B3D2E;
    border: 1px solid #B08968;
    border-radius: 6px;
    padding: 1.5rem;
    text-align: center;
    color: #EFE0D0;
    min-height: 260px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: transform 0.22s ease;
}

.arch-box-dark:hover { transform: scale(1.02); }

/* ── ARCH BOX INNER ──────────────────────────────────────────────── */
.arch-box-inner {
    background: rgba(11,61,46,0.06);
    border: 1px solid rgba(176,137,104,0.5);
    border-radius: 6px;
    padding: 0.9rem;
    text-align: center;
    margin-bottom: 0.5rem;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.arch-box-inner:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(11,61,46,0.12);
}

/* ── METRIC CARDS ────────────────────────────────────────────────── */
.metric-card {
    background: rgba(255,255,255,0.6);
    border: 1px solid rgba(176,137,104,0.55);
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    margin-bottom: 0.5rem;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* ── SECONDARY METRIC CARDS (Impact Snapshot, folded into Forecasting Engine) ── */
.metric-card-secondary {
    background: rgba(239,224,208,0.55);
    border: 1px solid rgba(176,137,104,0.35);
    border-radius: 6px;
    padding: 0.8rem 1rem;
    text-align: center;
    margin-bottom: 0.5rem;
    overflow: visible;
}

/* Ensure tab panels don't clip their last child */
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    padding-bottom: 1.5rem !important;
    overflow: visible !important;
}

.metric-card-secondary .metric-value-sm {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    color: #6B4C2A;
    line-height: 1.1;
    font-weight: 700;
}

.metric-card-secondary .metric-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.63rem;
    color: #9A7050;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-top: 0.25rem;
    font-weight: 500;
}

.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    color: #0B3D2E;
    line-height: 1.1;
    font-weight: 700;
}

.metric-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    color: #B08968;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.3rem;
    font-weight: 500;
}

.metric-caveat {
    font-size: 0.65rem;
    color: #6B4C2A;
    margin-top: 0.2rem;
    opacity: 0.75;
}

/* ── BUTTONS ─────────────────────────────────────────────────────── */
div[data-testid="stButton"] > button,
div[data-testid="stButton"] > button:not(:active) {
    background-color: #0B3D2E !important;
    color: #EFE0D0 !important;
    border: 1px solid rgba(11,61,46,0.25) !important;
    border-radius: 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.88rem !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    min-height: 44px !important;
    padding: 0 1rem !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
    transition: all 0.18s ease !important;
}

div[data-testid="stButton"] > button * {
    color: #EFE0D0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
}

div[data-testid="stButton"] > button:hover {
    background-color: #124233 !important;
    color: #EFE0D0 !important;
    border-color: #124233 !important;
}

/* ── DEMO CONTROLS — uniform pill ────────────────────────────────── */
div[data-testid="stSelectbox"] > div > div[data-baseweb="select"] > div {
    border-radius: 20px !important;
    border: 1px solid rgba(11,61,46,0.25) !important;
    background: #FFFFFF !important;
    min-height: 44px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #0B3D2E !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    display: flex !important;
    align-items: center !important;
}

/* ── EXPANDER (default — used by Live Demo's "Adjust conditions") ──── */
div[data-testid="stExpander"].stExpander {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    margin-top: 0.5rem !important;
}

div[data-testid="stExpander"] details {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    transition: none !important;
    animation: none !important;
}

div[data-testid="stExpander"] details > summary {
    border: 1px solid rgba(11,61,46,0.25) !important;
    border-radius: 20px !important;
    background: #FFFFFF !important;
    min-height: 44px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #0B3D2E !important;
    padding: 0 1rem !important;
    display: flex !important;
    align-items: center !important;
    list-style: none !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    transition: none !important;
    animation: none !important;
}

div[data-testid="stExpander"] details[open] > summary {
    border-radius: 20px 20px 0 0 !important;
    border-bottom: none !important;
}

div[data-testid="stExpander"] details[open] > summary::after {
    display: none !important;
    content: none !important;
}

div[data-testid="stExpander"] details[open] > [data-testid="stExpanderDetails"] {
    border: 1px solid rgba(11,61,46,0.25) !important;
    border-top: none !important;
    border-radius: 0 0 20px 20px !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0.8rem 1rem 1rem 1rem !important;
    margin-top: 0 !important;
    transition: none !important;
    animation: none !important;
}

div[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"],
div[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p,
div[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] div {
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #0B3D2E !important;
    font-family: 'DM Sans', sans-serif !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
    font-size: 1rem !important;
    color: #0B3D2E !important;
}

/* ── BEHIND THE BUILD — emphasized card-style expanders (JS-applied class) ── */
.tlj-story-expander.stExpander {
    margin-top: 1.1rem !important;
    margin-bottom: 1.1rem !important;
    max-width: 720px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

.tlj-story-expander details {
    border: 1px solid rgba(176,137,104,0.32) !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.62) !important;
    box-shadow: 0 2px 16px rgba(11,61,46,0.05) !important;
    overflow: hidden !important;
}

.tlj-story-expander details > summary {
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    min-height: 60px !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: #0B3D2E !important;
    padding: 1.1rem 1.8rem !important;
}

.tlj-story-expander details[open] > summary {
    border-bottom: 1px solid rgba(176,137,104,0.25) !important;
}

.tlj-story-expander details[open] > [data-testid="stExpanderDetails"] {
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 1.5rem 1.8rem 1.8rem 1.8rem !important;
}

.tlj-story-expander summary [data-testid="stMarkdownContainer"],
.tlj-story-expander summary [data-testid="stMarkdownContainer"] p,
.tlj-story-expander summary [data-testid="stMarkdownContainer"] div {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: #0B3D2E !important;
    font-family: 'Playfair Display', serif !important;
    line-height: 1 !important;
}

.tlj-story-expander summary [data-testid="stIconMaterial"] {
    font-size: 1.3rem !important;
    color: #B08968 !important;
}

/* ── FORECAST RESPONSE ───────────────────────────────────────────── */
.forecast-response {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(176,137,104,0.3);
    border-radius: 12px;
    padding: 1.5rem 1.8rem;
    margin-top: 1.2rem;
}

/* ── KILL BASEWEB SELECTBOX FONT — targets the st-ae class chain ── */
div[data-testid="stSelectbox"] div.st-ae,
div[data-testid="stSelectbox"] div.st-af,
div[data-testid="stSelectbox"] [data-baseweb="select"] div,
div[data-testid="stSelectbox"] [data-baseweb="select"] span,
div[data-testid="stSelectbox"] [data-baseweb="select"] input {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #0B3D2E !important;
}

/* ── KILL EXPANDER TRANSITION — removes white trail ──────────────── */
[data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] * {
    transition: none !important;
    animation: none !important;
}

div[data-testid="stExpander"] details,
div[data-testid="stExpander"] details * {
    transition: none !important;
    animation: none !important;
}

/* Force selectbox pill — highest specificity */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child {
    border-radius: 20px !important;
    border: 1px solid rgba(11,61,46,0.25) !important;
    background: #FFFFFF !important;
    min-height: 44px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #0B3D2E !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    display: flex !important;
    align-items: center !important;
    transition: none !important;
}

/* Kill any inner border BaseWeb adds */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child > div {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #0B3D2E !important;
    border: none !important;
    background: transparent !important;
}

/* ── TABS (Forecasting Engine) ───────────────────────────────────── */
div[data-testid="stTabs"] div[data-testid="stTab"][role="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #0B3D2E !important;
}

div[data-testid="stTabs"] [aria-selected="true"] {
    color: #0B3D2E !important;
    border-bottom-color: #B08968 !important;
}

div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: #B08968 !important;
}

div[data-testid="stTabs"] div[data-testid="stTab"][role="tab"]:nth-child(1) p,
div[data-testid="stTabs"] div[data-testid="stTab"][role="tab"]:nth-child(2) p {
    font-weight: 700 !important;
    color: #0B3D2E !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(176,137,104,0.4) !important;
    border-radius: 6px !important;
}

/* ── MAIN TABLE (Latest Forecast Run) — white, matches sidebar ──────── */
div[data-testid="stTable"]:not(.tlj-secondary-table) table {
    background: #FFFFFF !important;
    border-collapse: collapse !important;
}

div[data-testid="stTable"]:not(.tlj-secondary-table) th {
    background: #FFFFFF !important;
    color: #0B3D2E !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.6rem 0.8rem !important;
    border-bottom: 1px solid rgba(176,137,104,0.4) !important;
}

div[data-testid="stTable"]:not(.tlj-secondary-table) td {
    background: #FFFFFF !important;
    color: #3D2008 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 0.6rem 0.8rem !important;
    border-bottom: 1px solid rgba(176,137,104,0.2) !important;
}

div[data-testid="stTable"]:not(.tlj-secondary-table) {
    background: #FFFFFF !important;
    border: 1px solid rgba(176,137,104,0.4) !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* ── Allow row-highlight colors (Latest Forecast Run) to override base white ── */
div[data-testid="stTable"]:not(.tlj-secondary-table) td[style*="background-color"] {
    background-color: inherit !important;
}

/* ── SECONDARY TABLE (Confidence Breakdown) — matches the 4 de-emphasized boxes ── */
.tlj-secondary-table table {
    background: rgba(239,224,208,0.55) !important;
    border-collapse: collapse !important;
}

.tlj-secondary-table th {
    background: rgba(239,224,208,0.55) !important;
    color: #9A7050 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.6rem 0.8rem !important;
    border-bottom: 1px solid rgba(176,137,104,0.35) !important;
}

.tlj-secondary-table td {
    background: rgba(239,224,208,0.55) !important;
    color: #6B4C2A !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 0.6rem 0.8rem !important;
    border-bottom: 1px solid rgba(176,137,104,0.2) !important;
}

.tlj-secondary-table {
    background: rgba(239,224,208,0.55) !important;
    border: 1px solid rgba(176,137,104,0.35) !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* ── Constrain main content width — prevents shift when sidebar toggles ── */
[data-testid="stMain"] .block-container {
    max-width: 1200px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    position: relative !important;
}

/* ── Let the hero section escape the width constraint and stay full-bleed ── */
.hero-section {
    width: 100vw !important;
    position: relative !important;
    left: 50% !important;
    right: 50% !important;
    margin-left: -50vw !important;
    margin-right: -50vw !important;
}

/* ── Confidence score info icon ─────────────────────────────────── */
.tlj-confidence-info {
    position: absolute;
    bottom: 0.5rem;
    right: 0.6rem;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(11,61,46,0.15);
    color: #0B3D2E;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none !important;
    cursor: pointer;
    transition: background 0.15s ease;
}

.tlj-confidence-info:hover {
    background: rgba(11,61,46,0.3);
    text-decoration: none !important;
}

.tlj-confidence-info:visited {
    color: #0B3D2E;
    text-decoration: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-title">🥐 TLJ Forecaster</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-subtitle">Nolan McBride · UNC-Chapel Hill</span>', unsafe_allow_html=True)
    st.markdown('<span class="nav-section-label">Introduction</span>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link" href="#the-problem">The Problem</a>', unsafe_allow_html=True)
    st.markdown('<span class="nav-section-label">Try It</span>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link" href="#live-forecast-demo">Live Forecast Demo</a>', unsafe_allow_html=True)
    st.markdown('<span class="nav-section-label">Analytics</span>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link" href="#forecasting-engine">Forecasting Engine</a>', unsafe_allow_html=True)
    st.markdown('<span class="nav-section-label">The Project</span>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link" href="#how-it-works">How It Works</a>', unsafe_allow_html=True)
    st.markdown('<a class="nav-link" href="#why-ai">Why AI</a>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HERO — unchanged
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Reducing Bakery Waste<br>with an AI Forecasting Pipeline</div>
    <div class="hero-subtitle">A real operations problem &nbsp;·&nbsp; A real part-time job &nbsp;·&nbsp; Built from scratch</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. THE PROBLEM — hook, keep tight
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<a name="the-problem"></a>
<div class="narrative-card anim-card">
    <div class="tag">Introduction</div>
    <h3>The Problem</h3>
    <p>Every night at closing, the Cary <strong>Tous Les Jours</strong> bakery discards all unsold inventory. And I suppose this is an apt policy, given the English translation of the name is "everyday."</p>
    <p>That said, after my first couple of closing shifts, it became apparent that the amount of discarded pastries was quite significant. Not only that, but it appeared that each shift would produce its own unique culprit: A pastry responsible for the bulk of that night's waste.</p>
    <p>Of course, there were the pastries that persistently piled up at the end. But the unpredictable ones made me curious.</p>
    <p>So as I shoved fistfuls of pastries into trash bags at closing, I began to wonder if there was a pattern to where the waste was coming from - even if I couldn't recognize it immediately.</p>
    <p>Thus, I decided to build a data-driven waste forecasting tool to enable more strategic baking decisions.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 2. LIVE DEMO — moved up, immediately after the problem
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="wide-divider">', unsafe_allow_html=True)
st.markdown('<a name="live-forecast-demo"></a>', unsafe_allow_html=True)

col_intro, col_demo = st.columns([1, 1.6])

with col_intro:
    st.markdown("""
    <div class="narrative-card anim-card" style="max-width:100%;padding:1.6rem 1.8rem">
        <div class="tag">Try It</div>
        <h3>See It In Action</h3>
        <p>Pick any pastry below and the model will read tomorrow's weather, school status, and historical waste patterns to predict how much will be left at closing. This is the same process that runs every night for the top 12 most volatile products.</p>
    </div>
    """, unsafe_allow_html=True)

with col_demo:
    tracker_df = load_tracker(use_synthetic=True)
    pricing_df = load_pricing(use_synthetic=True)
    product_list = get_product_list(tracker_df)

    import datetime
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = "Tomorrow's Forecast — " + tomorrow_date.strftime("%A, %B %-d")

    weather_string = "Forecast for tomorrow -> Open (9:00 AM): 74°F, Clear Sky | Midday (2:00 PM): 79°F, Scattered Clouds | Close (7:30 PM): 82°F, Clear Sky"
    school_status = "Status of Cary High: Outside the 2025-2026 school year (Summer Break)."

    forecast_count   = st.session_state.get('forecast_count', None)
    forecast_product = st.session_state.get('forecast_product', None)
    financial_risk   = st.session_state.get('financial_risk', None)
    strategic_logic  = st.session_state.get('strategic_logic', None)

    if forecast_count:
        big_number = str(forecast_count)
        sub_label  = str(forecast_product)
        sub_sub    = "units predicted at closing"
    else:
        big_number = '<span style="font-size:4.8rem;font-family:Playfair Display,serif;font-weight:700;color:rgba(239,224,208,0.25);line-height:1;letter-spacing:-0.04em">—</span>'
        sub_label  = "awaiting forecast"
        sub_sub    = "select a product below"

    strategic_block = ""
    if strategic_logic:
        reason_parts = [r.strip() for r in str(strategic_logic).split('|') if r.strip()]
        if reason_parts:
            reasons_html = ''.join(
                f'<div style="margin-bottom:0.3rem">{r}</div>' for r in reason_parts
            )
        else:
            reasons_html = str(strategic_logic)
        strategic_block = (
            '<div style="font-family:Playfair Display,serif;font-style:italic;'
            'font-size:0.82rem;color:#0B3D2E;text-align:center;line-height:1.5;'
            'padding:0.8rem 0;border-top:1px solid rgba(11,61,46,0.08);">'
            + reasons_html
            + '</div>'
        )

    financial_block = ""
    if financial_risk:
        financial_block = (
            '<div style="text-align:center;font-size:0.78rem;color:#0B3D2E;'
            'padding:0.6rem 0 0.2rem 0;border-top:1px solid rgba(11,61,46,0.08);">'
            '💸 &nbsp;'
            + str(financial_risk)
            + '</div>'
        )

    card_html = (
        '<div class="tlj-demo-card" style="max-width:420px;margin:0 auto 0 auto;'
        'border-radius:28px 28px 0 0;background:#FFFFFF;'
        'border:1px solid rgba(11,61,46,0.12);border-bottom:none;'
        'padding:1.6rem 1.6rem 1.2rem 1.6rem;font-family:DM Sans,sans-serif;">'

        '<div style="text-align:center;margin-bottom:1.4rem;">'
        '<div style="display:inline-block;border:1px solid rgba(176,137,104,0.5);'
        'color:#9A7050;font-size:0.63rem;font-weight:500;letter-spacing:0.2em;'
        'text-transform:uppercase;padding:0.18rem 0.65rem;border-radius:2px;'
        'margin-bottom:0.7rem;">Try It</div>'
        '<div style="font-family:Playfair Display,serif;font-size:1.4rem;font-weight:700;'
        'color:#0B3D2E;letter-spacing:-0.02em;margin-bottom:0.4rem;">Live Forecast Demo</div>'
        '<div style="font-size:0.82rem;color:#5C3820;line-height:1.6;">'
        "Pick a product. The model reads tomorrow's conditions and predicts closing waste."
        '</div>'
        '</div>'

        '<div style="background:#0B3D2E;border-radius:20px;'
        'padding:2rem 1.5rem 1.8rem 1.5rem;text-align:center;margin-bottom:1.2rem;">'

        '<svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#EFE0D0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:0.8rem;opacity:0.85">'
        '<path d="M10.2 18H4.774a1.5 1.5 0 0 1-1.352-.97 11 11 0 0 1 .132-6.487"/>'
        '<path d="M18 10.2V4.774a1.5 1.5 0 0 0-.97-1.352 11 11 0 0 0-6.486.132"/>'
        '<path d="M18 5a4 3 0 0 1 4 3 2 2 0 0 1-2 2 10 10 0 0 0-5.139 1.42"/>'
        '<path d="M5 18a3 4 0 0 0 3 4 2 2 0 0 0 2-2 10 10 0 0 1 1.42-5.14"/>'
        '<path d="M8.709 2.554a10 10 0 0 0-6.155 6.155 1.5 1.5 0 0 0 .676 1.626l9.807 5.42a2 2 0 0 0 2.718-2.718l-5.42-9.807a1.5 1.5 0 0 0-1.626-.676"/>'
        '</svg>'

        '<div style="font-family:Playfair Display,serif;font-size:4.8rem;font-weight:700;'
        'color:#EFE0D0;line-height:1;letter-spacing:-0.04em;margin-bottom:0.45rem;">'
        + (str(forecast_count) if forecast_count else '<span style="font-size:4.8rem;font-family:Playfair Display,serif;font-weight:700;color:rgba(239,224,208,0.25);line-height:1;letter-spacing:-0.04em">—</span>') +
        '</div>'

        '<div style="font-size:0.85rem;color:rgba(239,224,208,0.7);margin-bottom:0.2rem;">'
        + sub_label +
        '</div>'

        '<div style="font-size:0.65rem;color:rgba(239,224,208,0.38);'
        'letter-spacing:0.08em;text-transform:uppercase;">'
        + sub_sub +
        '</div>'

        '</div>'

        '<div style="font-size:0.68rem;color:#9A7050;letter-spacing:0.06em;'
        'text-transform:uppercase;margin-bottom:0.7rem;font-family:DM Sans,sans-serif;">'
        + tomorrow +
        '</div>'

        '<div style="display:flex;justify-content:space-between;'
        'padding-bottom:1rem;border-bottom:1px solid rgba(11,61,46,0.08);'
        'margin-bottom:0.8rem;">'

        '<div style="text-align:center;flex:1">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0B3D2E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:0.18rem">'
        '<path d="M10 21v-1"/><path d="M10 4V3"/><path d="M10 9a3 3 0 0 0 0 6"/>'
        '<path d="m14 20 1.25-2.5L18 18"/><path d="m14 4 1.25 2.5L18 6"/>'
        '<path d="m17 21-3-6 1.5-3H22"/><path d="m17 3-3 6 1.5 3"/>'
        '<path d="M2 12h1"/><path d="m20 10-1.5 2 1.5 2"/>'
        '<path d="m3.64 18.36.7-.7"/><path d="m4.34 6.34-.7-.7"/>'
        '</svg>'
        '<div style="font-size:0.7rem;color:#0B3D2E;font-weight:500">74°F · Clear</div>'
        '<div style="font-size:0.6rem;color:#9A7050;margin-top:0.08rem">Weather</div>'
        '</div>'

        '<div style="width:1px;background:rgba(11,61,46,0.08);margin:0 0.4rem"></div>'

        '<div style="text-align:center;flex:1">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0B3D2E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:0.18rem">'
        '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/>'
        '<path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>'
        '</svg>'
        '<div style="font-size:0.7rem;color:#0B3D2E;font-weight:500">Summer Break</div>'
        '<div style="font-size:0.6rem;color:#9A7050;margin-top:0.08rem">WCPSS</div>'
        '</div>'

        '<div style="width:1px;background:rgba(11,61,46,0.08);margin:0 0.4rem"></div>'

        '<div style="text-align:center;flex:1">'
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0B3D2E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:0.18rem">'
        '<path d="M12 17v5"/>'
        '<path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"/>'
        '</svg>'
        '<div style="font-size:0.7rem;color:#0B3D2E;font-weight:500">Cary, NC</div>'
        '<div style="font-size:0.6rem;color:#9A7050;margin-top:0.08rem">H Mart</div>'
        '</div>'

        '</div>'

        + strategic_block
        + financial_block

        + '</div>'
    )

    st.markdown(card_html, unsafe_allow_html=True)

    selected_product = st.selectbox(
        "Product",
        options=product_list,
        index=product_list.index('CustardBun') if 'CustardBun' in product_list else 0,
        label_visibility="collapsed"
    )

    with st.expander("Adjust conditions"):
        traffic_density = st.select_slider(
            "Foot traffic",
            options=[1, 2, 3], value=2,
            format_func=lambda x: {1: "Slow", 2: "Moderate", 3: "Busy"}[x]
        )
        bogo_active = st.toggle(f"BOGO active on {selected_product}", value=False)

    st.markdown('<div style="height:0.3rem"></div>', unsafe_allow_html=True)
    run_clicked = st.button("✦  Run Forecast", use_container_width=True)

    if run_clicked:
        AI_KEY = st.secrets.get("AI_KEY", os.getenv("AI_KEY", ""))
        if not AI_KEY:
            st.error("Gemini API key not configured. Add AI_KEY as a secret to enable live forecasting.")
            st.stop()

        from google import genai
        from core.forecast_engine import build_prompt, call_gemini_with_retry
        client = genai.Client(api_key=AI_KEY)

        waste_col = f"{selected_product}_Waste_Count"
        context_cols = [c for c in tracker_df.columns if '_Waste_Count' not in c]
        tracker_extract = (
            tracker_df[context_cols + [waste_col]].to_string(index=False)
            if waste_col in tracker_df.columns
            else tracker_df[context_cols].to_string(index=False)
        )
        tracker_note = (
            f"'{waste_col}' found. {len(tracker_df)} shifts (synthetic demo data)."
            if waste_col in tracker_df.columns else "No column found."
        )
        pricing_dict = dict(zip(pricing_df.columns.tolist(), pricing_df.iloc[0].tolist()))
        unit_price = pricing_dict.get(selected_product, None)

        prompt = build_prompt(
            target_product=selected_product,
            tracker_extract=tracker_extract,
            tracker_note=tracker_note,
            fk_extract="Not available in demo.",
            fk_note="No proxy data in demo mode.",
            weather_string=weather_string,
            school_status=school_status,
            unit_price=unit_price
        )

        with st.spinner(f"Asking Gemini to forecast {selected_product}..."):
            try:
                result = call_gemini_with_retry(client, prompt)
            except RuntimeError:
                st.error("Daily Gemini quota reached. Try again tomorrow.")
                st.stop()
            except Exception as e:
                st.error(f"Forecast failed: {e}")
                st.stop()

        import re
        for line in result.strip().split('\n'):
            if line.startswith("FORECAST:"):
                nums = re.findall(r'\d+', line)
                if nums:
                    st.session_state['forecast_count'] = nums[0]
                    st.session_state['forecast_product'] = selected_product
            elif line.startswith("FINANCIAL RISK:"):
                st.session_state['financial_risk'] = line.replace("FINANCIAL RISK:", "").strip()
            elif line.startswith("STRATEGIC LOGIC:"):
                st.session_state['strategic_logic'] = line.replace("STRATEGIC LOGIC:", "").strip()

        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 3. FORECASTING ENGINE — the product itself: latest run + validation history
#    Impact Snapshot metrics now live here as secondary cards under the 3 main numbers
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="wide-divider">', unsafe_allow_html=True)
st.markdown('<a name="forecasting-engine"></a>', unsafe_allow_html=True)
st.markdown('<div style="text-align:left"><div class="tag">Analytics</div></div>', unsafe_allow_html=True)
st.markdown("### Forecasting Engine")

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
backtest_path = os.path.join(DATA_DIR, 'backtest_results.csv')
if os.path.exists(backtest_path) and os.path.getsize(backtest_path) > 0:
    backtest_df = pd.read_csv(backtest_path)
    has_backtest = not backtest_df.empty
else:
    backtest_df = pd.DataFrame()
    has_backtest = False

log_df = load_log()
accuracy_stats = calculate_accuracy(log_df)

if has_backtest and 'abs_error' in backtest_df.columns and 'unit_price' in backtest_df.columns:
    backtest_df['savings'] = (backtest_df['actual'] - backtest_df['predicted']).clip(lower=0) * backtest_df['unit_price']
    daily_savings = round(backtest_df.groupby('date')['savings'].sum().mean(), 2)
    annual_recovery = round(daily_savings * 365)
    daily_savings_display = f"${daily_savings}/day"
    annual_recovery_display = f"${annual_recovery:,}"
    savings_caveat = "From backtest, in-sample"
else:
    daily_savings_display, annual_recovery_display, savings_caveat = "—", "—", "Populates July 15"

if has_backtest and 'abs_error' in backtest_df.columns:
    within_3_units = (backtest_df['abs_error'] <= 3).sum()
    within_3_pct = round(within_3_units / len(backtest_df) * 100)
    median_error = backtest_df['abs_error'].median()
    accuracy_display = f"{within_3_pct}%"
    accuracy_caveat = f"within 3 units · median error {median_error:.0f} unit(s) · {len(backtest_df)} predictions"
else:
    accuracy_display, accuracy_caveat = "—", "Populates as backtesting continues"

from core.data_loader import get_top_volatile_products
vol_df = get_top_volatile_products(tracker_df, pricing_df, n=12, backtest_path=backtest_path)

tab_latest, tab_insights, tab_volatility, tab_validation, tab_confidence = st.tabs(["Latest Forecast Run", "Insights", "The Shortlist Logic", "Validation History", "Confidence Detail"])

with tab_latest:
    run_date = datetime.date.today().strftime("%B %-d, %Y")
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_label = tomorrow_date.strftime("%A, %B %-d")

    st.markdown(f"""
    <div style="font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:#0B3D2E;margin-bottom:0.3rem">
        Tomorrow's Forecast — {tomorrow_label}
    </div>
    """, unsafe_allow_html=True)

    nightly_forecast_path = os.path.join(DATA_DIR, 'latest_forecast.csv')
    if os.path.exists(nightly_forecast_path) and os.path.getsize(nightly_forecast_path) > 0:
        latest_run_df = pd.read_csv(nightly_forecast_path)
        generated_note = None
        if 'Generated' in latest_run_df.columns and not latest_run_df.empty:
            generated_note = latest_run_df['Generated'].iloc[0]
        latest_run_df = latest_run_df.drop(columns=[c for c in ['Generated', 'Target Date'] if c in latest_run_df.columns])
    else:
        # Fallback demo rows — shown only until the nightly batch job has produced its first run.
        latest_run_df = pd.DataFrame({
            'Product': ['CroissantPlain ($1.50)', 'PainAuChocolat ($1.50)', 'BlueberryMuffin ($1.50)', 'CustardBun ($1.50)', 'KimchiCroquette ($1.50)'],
            'Predicted Waste': [11, 8, 6, 5, 4],
            'Loss': ['$17', '$12', '$9', '$7', '$6'],
            'Explanation': [
                'School\'s out, so fewer walk-in customers | Low traffic on similar past days',
                'Weekends tend to run heavier than expected | No promo running tomorrow',
                'Sunny days usually mean lighter leftovers | Matches a few recent clear days',
                'Weekends are harder to predict here | Wider range of past outcomes',
                'Sells out on comparable days | No unusual conditions expected tomorrow'
            ]
        })
        generated_note = None

    st.markdown('<div style="height:1.25rem"></div>', unsafe_allow_html=True)

    if generated_note:
        st.caption(f"Generated {generated_note} (nightly batch) · {len(latest_run_df)} products evaluated")
    else:
        st.caption(f"Generated {run_date} · demo data — nightly batch has not run yet")

    st.markdown('<div style="height:2.25rem"></div>', unsafe_allow_html=True)

    def render_highlighted_table(df):
        rows_html = ""
        for _, row in df.iterrows():
            bg = "rgba(154,75,62,0.10)" if row['Predicted Waste'] > 0 else "rgba(11,61,46,0.08)"
            rows_html += f'<tr style="background-color:{bg}"><td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4">{row["Product"]}</td><td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4;text-align:right">{row["Predicted Waste"]}</td><td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4">{row["Loss"]}</td><td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4">{row["Explanation"]}</td></tr>'

        table_html = f'<div style="border:none solid rgba(176,137,104,0.4);overflow:hidden"><table style="width:100%;border-collapse:collapse"><thead><tr style="background:#FFFFFF"><th style="padding:0.6rem 0.8rem;text-align:left;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">Product</th><th style="padding:0.6rem 0.8rem;text-align:right;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">Predicted Waste</th><th style="padding:0.6rem 0.8rem;text-align:left;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">Loss</th><th style="padding:0.6rem 0.8rem;text-align:left;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">Explanation</th></tr></thead><tbody>{rows_html}</tbody></table></div>'

        st.markdown(table_html, unsafe_allow_html=True)

    render_highlighted_table(latest_run_df)

    def render_confidence_table(df):
        rows_html = ""
        for _, row in df.iterrows():
            rows_html += f'<tr style="background-color:#FFFFFF"><td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4">{row["Factor"]}</td><td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4">{row["Basis"]}</td><td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4;text-align:right">{row["Score"]}</td></tr>'

        table_html = f'<div style="border:none solid rgba(176,137,104,0.4);overflow:hidden"><table style="width:100%;border-collapse:collapse"><thead><tr style="background:#FFFFFF"><th style="padding:0.6rem 0.8rem;text-align:left;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">Factor</th><th style="padding:0.6rem 0.8rem;text-align:left;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">Basis</th><th style="padding:0.6rem 0.8rem;text-align:right;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">Score</th></tr></thead><tbody>{rows_html}</tbody></table></div>'

        st.markdown(table_html, unsafe_allow_html=True)

    st.markdown('<div style="height:2.75rem"></div>', unsafe_allow_html=True)

    total_waste = latest_run_df['Predicted Waste'].sum()
    total_loss_val = sum(int(x.replace('$', '')) for x in latest_run_df['Loss'])
    top_category = latest_run_df.loc[latest_run_df['Predicted Waste'].idxmax(), 'Product']

    products_expected_to_waste = (latest_run_df['Predicted Waste'] > 0).sum()
    total_products_evaluated = len(latest_run_df)

    from core.data_loader import compute_daily_confidence
    import datetime as _dt
    tomorrow_dow = (_dt.date.today() + _dt.timedelta(days=1)).strftime("%A")
    is_weekend_tomorrow = tomorrow_dow in ["Saturday", "Sunday"]

    confidence_result = compute_daily_confidence(
        tracker_df,
        is_weekend_tomorrow=is_weekend_tomorrow,
        tomorrow_day_name=tomorrow_dow,
        school_status_tomorrow=None
        #TODO: add school_status_tomorrow once WCPSS API is integrated
    )
    score = confidence_result['score']
    if score >= 70:
        conf_bg = "rgba(11,61,46,0.12)"
        conf_border = "rgba(11,61,46,0.4)"
        conf_text = "#0B3D2E"
    elif score >= 40:
        conf_bg = "rgba(176,137,104,0.18)"
        conf_border = "rgba(176,137,104,0.5)"
        conf_text = "#8A5A2E"
    else:
        conf_bg = "rgba(154,75,62,0.14)"
        conf_border = "rgba(154,75,62,0.45)"
        conf_text = "#9A4B3E"

    # ── Main 4 numbers — the headline metrics ──────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="anim-pop-in metric-card"><div class="metric-value">{total_waste}<span style="font-size:0.9rem !important;font-weight:400 !important;font-family:\'DM Sans\',sans-serif !important"></span></div><div class="metric-label">Units of Projected Waste Tomorrow</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="anim-pop-in metric-card" style="transition-delay:0.1s"><div class="metric-value">${total_loss_val}</div><div class="metric-label">of Projected Financial Loss</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="anim-pop-in metric-card" style="transition-delay:0.2s"><div class="metric-value">{products_expected_to_waste}/{total_products_evaluated}</div><div class="metric-label">Products Expected to Waste</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="anim-pop-in metric-card tlj-confidence-card" style="transition-delay:0.3s;background:{conf_bg};border-color:{conf_border};position:relative">
            <div class="metric-value" style="color:{conf_text}">{score}<span style="font-size:1.2rem">/100</span></div>
            <div class="metric-label">Confidence in Today's Prediction</div>
            <a href="#confidence-detail" class="tlj-confidence-info" title="See confidence breakdown">?</a>
        </div>
        """, unsafe_allow_html=True)



    # ── Secondary row — supporting business-impact context, visually de-emphasized ──
    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div style="height:3rem"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card-secondary"><div class="metric-value-sm">{annual_recovery_display}</div><div class="metric-label">Annual Recovery Potential</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="height:3rem"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card-secondary"><div class="metric-value-sm">{daily_savings_display}</div><div class="metric-label">Daily Savings Opportunity</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div style="height:3rem"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card-secondary"><div class="metric-value-sm">{accuracy_display}</div><div class="metric-label">of Predictions Within 3 Units</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div style="height:3rem"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card-secondary"><div class="metric-value-sm">{len(tracker_df)}</div><div class="metric-label">Shifts Logged</div></div>', unsafe_allow_html=True)

with tab_insights:
    from core.data_loader import get_weekday_weekend_waste

    st.markdown("Before any forecasting happens, two patterns in the raw shift data directly shaped how the system is designed — which days it treats with more caution, and which products it prioritizes for prediction.")

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

    # ── Weekend vs weekday waste volatility ──────────────────────────────
    st.markdown('<h4 style="text-align:center">Weekend Waste Is Far Less Predictable</h4>', unsafe_allow_html=True)

    weekday_totals, weekend_totals = get_weekday_weekend_waste(tracker_df)
    weekday_std = weekday_totals.std()
    weekend_std = weekend_totals.std()
    vol_ratio = (weekend_std / weekday_std) if weekday_std else float('nan')

    fig_weekend = go.Figure()
    fig_weekend.add_trace(go.Box(
        y=weekday_totals.tolist(),
        name='Weekday', marker_color='#0B3D2E', line_color='#0B3D2E', boxmean=True
    ))
    fig_weekend.add_trace(go.Box(
        y=weekend_totals.tolist(),
        name='Weekend', marker_color='#B08968', line_color='#B08968', boxmean=True
    ))
    fig_weekend.update_layout(
        plot_bgcolor='rgba(239,224,208,0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#3D2008'),
        yaxis=dict(title='Total Store Waste (units)', gridcolor='rgba(176,137,104,0.3)', color='#3D2008'),
        xaxis=dict(color='#3D2008'),
        margin=dict(l=20, r=20, t=20, b=20),
        height=320
    )
    st.plotly_chart(fig_weekend, use_container_width=True)
    st.caption(f"Weekend waste is {vol_ratio:.1f}× more volatile than weekday waste — not simply higher, but harder to predict. Based on {len(tracker_df)} logged shifts: {len(weekday_totals)} weekday, {len(weekend_totals)} weekend.")

    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)

    # ── Dollar concentration in highest-risk products ────────────────────
    st.markdown('<h4 style="text-align:center">A Small Set of Products Drives Most of the Loss</h4>', unsafe_allow_html=True)

    waste_cols = [c for c in tracker_df.columns if c.endswith('_Waste_Count')]
    pricing_dict = dict(zip(pricing_df.columns.tolist(), pricing_df.iloc[0].tolist()))

    dollar_loss = {}
    for col in waste_cols:
        product = col.replace('_Waste_Count', '')
        unit_price = pricing_dict.get(product, 0)
        total_waste_units = tracker_df[col].sum()
        dollar_loss[product] = total_waste_units * unit_price

    loss_df = pd.Series(dollar_loss).sort_values(ascending=False)
    top_loss_df = loss_df.head(10).sort_values(ascending=True)

    total_dollar_loss = loss_df.sum()
    top10_dollar_loss = loss_df.head(10).sum()
    top10_share = round(top10_dollar_loss / total_dollar_loss * 100) if total_dollar_loss > 0 else 0

    fig_loss = go.Figure(go.Bar(
        x=top_loss_df.values, y=top_loss_df.index,
        orientation='h',
        marker_color='#9A4B3E',
        marker_line_color='#B08968',
        marker_line_width=0.5,
        opacity=0.88
    ))
    fig_loss.update_layout(
        plot_bgcolor='rgba(239,224,208,0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#3D2008'),
        xaxis=dict(title='Total Dollar Loss ($)', gridcolor='rgba(176,137,104,0.3)', color='#3D2008'),
        yaxis=dict(color='#3D2008'),
        margin=dict(l=20, r=20, t=20, b=20),
        height=380
    )
    st.plotly_chart(fig_loss, use_container_width=True)
    st.caption(f"The top 10 highest-loss products account for {top10_share}% of total dollar waste across all 65 SKUs, based on {len(tracker_df)} logged shifts.")

with tab_volatility:
    st.markdown("""
    Every day, the system selects the **12 pastries with the most volatile waste patterns** to forecast — unpredictable pastries are the ones that benefit the most from a predictive tool. That said, selection comes with two caveats:

    - **Dollar floor:** items with negligible financial impact (under $1/shift on average) are excluded, even if their waste count looks erratic. A product that occasionally wastes 1 unit instead of 0 can look "volatile" by the math alone without being worth predicting.
    - **Reliability filter:** items with a demonstrated track record of inaccurate backtested predictions are excluded, even if they'd otherwise rank as volatile enough to qualify. Some pastries swing unpredictably for legitimate reasons while others lack any observable pattern.
    """)


    st.markdown('<div style="height:3rem"></div>', unsafe_allow_html=True)

    st.markdown('<h4 style="text-align:center">The 12 Pastries Worth Predicting (Sorted By Volatility)</h4>', unsafe_allow_html=True)

    fig3 = go.Figure(go.Bar(
        x=vol_df['cv'], y=vol_df['product'],
        orientation='h',
        marker_color='#0B3D2E',
        marker_line_color='#B08968',
        marker_line_width=0.5,
        opacity=0.88
    ))
    fig3.update_layout(
        plot_bgcolor='rgba(239,224,208,0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#3D2008'),
        xaxis=dict(title='Coefficient of Variation', gridcolor='rgba(176,137,104,0.3)', color='#3D2008'),
        yaxis=dict(color='#3D2008'),
        margin=dict(l=20, r=20, t=20, b=20),
        height=420
    )
    st.plotly_chart(fig3, use_container_width=True)

    pricing_dict = dict(zip(pricing_df.columns.tolist(), pricing_df.iloc[0].tolist()))
    vol_df['unit_price'] = vol_df['product'].map(lambda p: pricing_dict.get(p, 0))
    vol_df['avg_nightly_waste'] = vol_df['product'].apply(
        lambda p: tracker_df[f"{p}_Waste_Count"].mean() if f"{p}_Waste_Count" in tracker_df.columns else 0
    )
    vol_df['avg_nightly_loss'] = vol_df['avg_nightly_waste'] * vol_df['unit_price']

    display_vol_df = vol_df[['product', 'unit_price', 'avg_nightly_loss', 'cv']].rename(
        columns={'product': 'Product', 'unit_price': 'Price/Unit', 'avg_nightly_loss': 'Avg Nightly Loss', 'cv': 'Volatility (CV)'}
    ).sort_values('Volatility (CV)', ascending=False)
    display_vol_df['Price/Unit'] = display_vol_df['Price/Unit'].apply(lambda x: f"${x:.2f}")
    display_vol_df['Avg Nightly Loss'] = display_vol_df['Avg Nightly Loss'].apply(lambda x: f"${x:.2f}")
    display_vol_df['Volatility (CV)'] = display_vol_df['Volatility (CV)'].apply(lambda x: f"{x:.2f}")

    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
    st.markdown('<h4 style="text-align:center">Price &amp; Nightly Loss By Product</h4>', unsafe_allow_html=True)

    def render_html_table(headers, rows):
        head_cells = "".join(
            f'<th style="padding:0.6rem 0.8rem;text-align:left;border-bottom:1px solid rgba(176,137,104,0.4);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:500;line-height:1.4">{h}</th>'
            for h in headers
        )
        body_rows = ""
        for row in rows:
            cells = "".join(
                f'<td style="padding:0.6rem 0.8rem;border-bottom:1px solid rgba(176,137,104,0.2);color:#3D2008;font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.4">{val}</td>'
                for val in row
            )
            body_rows += f'<tr style="background-color:#FFFFFF">{cells}</tr>'
        table_html = f'<div style="border:none solid rgba(176,137,104,0.4);overflow:hidden"><table style="width:100%;border-collapse:collapse"><thead><tr style="background:#FFFFFF">{head_cells}</tr></thead><tbody>{body_rows}</tbody></table></div>'
        st.markdown(table_html, unsafe_allow_html=True)

    rows = display_vol_df.values.tolist()
    render_html_table(headers=['Product', 'Price/Unit', 'Avg Nightly Loss', 'Volatility (CV)'], rows=rows)

with tab_validation:
    if has_backtest:
        st.markdown("For each historical shift, the model was shown only prior shifts and asked to predict that day's waste. Predicted vs. actual are plotted below.")

        st.markdown('<div style="height:1.25rem"></div>', unsafe_allow_html=True)

        current_top12 = vol_df['product'].tolist()
        available_products = [p for p in current_top12 if p in backtest_df['product'].unique()]

        if available_products:
            selected_bt = st.selectbox("Select product to view", available_products)
        else:
            st.markdown("No backtest history yet for the current top-12 products.")
            selected_bt = None

        if selected_bt:
            pdf = backtest_df[backtest_df['product'] == selected_bt].sort_values('date')
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pdf['date'], y=pdf['actual'],
                mode='lines+markers', name='Actual',
                line=dict(color='#0B3D2E', width=2),
                marker=dict(color='#0B3D2E', size=7)
            ))
            fig.add_trace(go.Scatter(
                x=pdf['date'], y=pdf['predicted'],
                mode='lines+markers', name='Predicted',
                line=dict(color='#B08968', width=2, dash='dot'),
                marker=dict(color='#B08968', size=7, symbol='diamond')
            ))
            fig.update_layout(
                plot_bgcolor='rgba(239,224,208,0.4)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='DM Sans', color='#3D2008'),
                xaxis=dict(title='Shift Date', gridcolor='rgba(176,137,104,0.3)', color='#3D2008'),
                yaxis=dict(title='Leftover Count', gridcolor='rgba(176,137,104,0.3)', color='#3D2008'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                margin=dict(l=20, r=20, t=40, b=20)
            )

            st.markdown('<div style="height:5rem"></div>', unsafe_allow_html=True)

            st.markdown('<h4 style="text-align:center">How Close Were the Predictions?</h4>', unsafe_allow_html=True)

            st.plotly_chart(fig, use_container_width=True)

        if not log_df.empty and accuracy_stats['n'] > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="anim-pop-in metric-card"><div class="metric-value">{accuracy_stats["n"]}</div><div class="metric-label">Live Observations</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="anim-pop-in metric-card" style="transition-delay:0.1s"><div class="metric-value">{accuracy_stats["mae_pct"]}%</div><div class="metric-label">Live MAE</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="anim-pop-in metric-card" style="transition-delay:0.2s"><div class="metric-value">{accuracy_stats["directional_accuracy"]}%</div><div class="metric-label">Directional Accuracy</div></div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="text-align:center;opacity:0.7;padding:1.5rem 0">
            <p>Validation metrics will populate automatically once sufficient forecast/actual pairs have been collected. Locked for update July 15.</p>
        </div>
        """, unsafe_allow_html=True)

with tab_confidence:
    st.markdown('<a name="confidence-detail"></a>', unsafe_allow_html=True)
    st.markdown("How today's confidence score was calculated — each factor is scored independently based on historical data coverage, then combined into a single 0-100 score.")

    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)

    breakdown_df = pd.DataFrame(confidence_result['breakdown'])
    breakdown_df['Score'] = breakdown_df.apply(lambda r: f"{r['points']:.0f} / {r['max_points']}", axis=1)
    display_df = breakdown_df[['factor', 'detail', 'Score']].rename(columns={'factor': 'Factor', 'detail': 'Basis'})
    render_confidence_table(display_df)

# ══════════════════════════════════════════════════════════════════════════════
# 4. HOW IT WORKS — architecture diagram (unchanged content, just moved down)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="wide-divider tlj-exclude-from-card">', unsafe_allow_html=True)
st.markdown('<a name="how-it-works"></a>', unsafe_allow_html=True)
st.markdown('<div style="text-align:left"><div class="tag">The Project</div></div>', unsafe_allow_html=True)
st.markdown("### How It Works")
st.markdown("Four data streams feed into a single Gemini AI call per product, once per day:")

col1, col2, col3, col4, col5 = st.columns([2, 0.4, 2, 0.4, 2])
with col1:
    st.markdown("""
    <div class="anim-fade-left">
        <div class="arch-box-inner"><div style="font-size:1.3rem">📋</div><div class="arch-box-label">Shift Tracker</div><div class="arch-box-desc">Personal waste logs, foot traffic, weather observations, shift notes</div></div>
    </div>
    <div class="anim-fade-left" style="transition-delay:0.1s">
        <div class="arch-box-inner"><div style="font-size:1.3rem">🌤️</div><div class="arch-box-label">Weather API</div><div class="arch-box-desc">Live 3-point forecast for tomorrow's operating window</div></div>
    </div>
    <div class="anim-fade-left" style="transition-delay:0.2s">
        <div class="arch-box-inner"><div style="font-size:1.3rem">🏫</div><div class="arch-box-label">School Calendar</div><div class="arch-box-desc">WCPSS 2025–27 calendar — school status as a foot traffic signal</div></div>
    </div>
    <div class="anim-fade-left" style="transition-delay:0.3s">
        <div class="arch-box-inner"><div style="font-size:1.3rem">📊</div><div class="arch-box-label">Proxy Dataset</div><div class="arch-box-desc">French-Korean bakery sales data for items with limited personal history</div></div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align:center;font-size:1.4rem;color:#B08968">→</div>', unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="anim-pop-in">
        <div class="arch-box-dark">
            <div style="font-size:1.6rem;margin-bottom:0.6rem">✦</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.05rem;color:#EFE0D0;font-weight:700;margin-bottom:0.6rem">Google Gemini 2.5 Flash</div>
            <div style="font-size:0.76rem;color:#EFE0D0;opacity:0.82;line-height:1.65">Receives all four data streams in a structured prompt. Cross-references tomorrow's conditions against historical shifts to predict leftover count.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown('<div style="text-align:center;font-size:1.4rem;color:#B08968">→</div>', unsafe_allow_html=True)
with col5:
    st.markdown("""
    <div class="anim-fade-left" style="transition-delay:0.1s">
        <div class="arch-box-inner"><div style="font-size:1.3rem">📦</div><div class="arch-box-label">Per-Product Forecast</div><div class="arch-box-desc">Predicted closing leftover count</div></div>
    </div>
    <div class="anim-fade-left" style="transition-delay:0.2s">
        <div class="arch-box-inner"><div style="font-size:1.3rem">💸</div><div class="arch-box-label">Dollar Risk</div><div class="arch-box-desc">Projected waste capital loss</div></div>
    </div>
    <div class="anim-fade-left" style="transition-delay:0.3s">
        <div class="arch-box-inner"><div style="font-size:1.3rem">🧠</div><div class="arch-box-label">Strategic Logic</div><div class="arch-box-desc">One-sentence explanation of what drove the prediction</div></div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 5. WHY AI — tight, 1 card (unchanged content, just moved up ahead of Engineering Journey)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<hr class="wide-divider">
<a name="why-ai"></a>
<div class="narrative-card anim-card">
    <div class="tag">The Project</div>
    <h3>Why AI Over a Regression Model?</h3>
    <p>Why use a large language model instead of a standard regression model?</p>
    <p>Regression models are great for structured numerical data (e.g. temperature, traffic density, day of the week), but they struggle with unstructured text. In this project, the predicted waste counts are largely informed by unstructured shift notes.</p>
    <p>For example, "a customer came in and bought all of the _" or "there was a BOGO deal on _, _, and _."</p>
    <p>These observations contain valuable insights that a standard regression model can't interpret.</p>
    <p>Thus, this isn't AI for the sake of AI. It's AI because the data format demands it.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPONENTS.HTML
# Card animation (.anim-card) slides up as a unit.
# All other animations unchanged from known-good version.
# ══════════════════════════════════════════════════════════════════════════════
import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    var doc = window.parent.document;
    var win = window.parent;
    var sidebarOpen = true;

    function fixSidebar() {
        var sb = doc.querySelector('section[data-testid="stSidebar"]');
        if (!sb) return;
        var container = doc.querySelector('[data-testid="stAppViewContainer"]');
        if (container) {
            container.style.setProperty('display','flex','important');
            container.style.setProperty('flex-direction','row','important');
            container.style.setProperty('align-items','flex-start','important');
        }
        sb.style.setProperty('position','relative','important');
        sb.style.setProperty('left','0','important');
        sb.style.setProperty('top','0','important');
        sb.style.setProperty('transform','none','important');
        sb.style.setProperty('margin-left','0','important');
        sb.style.setProperty('order','-1','important');
        sb.style.setProperty('min-width','240px','important');
        sb.style.setProperty('width','240px','important');
        sb.style.setProperty('background-color','#FFFFFF','important');
        sb.style.setProperty('border-right','2px solid #0B3D2E','important');
        sb.style.setProperty('visibility','visible','important');
        sb.style.setProperty('opacity','1','important');
        sb.style.setProperty('flex-shrink','0','important');
        sb.style.setProperty('height','100vh','important');
        sb.style.setProperty('overflow-y','auto','important');
        sb.style.setProperty('z-index','100','important');
        sb.style.setProperty('transition','width 0.3s ease, min-width 0.3s ease','important');
        var vb = doc.querySelector('[data-testid="stVerticalBlock"]');
        if (vb) {
            vb.style.setProperty('gap','0','important');
            var fc = vb.firstElementChild;
            if (fc) {
                fc.style.setProperty('margin-top','0','important');
                fc.style.setProperty('padding-top','0','important');
            }
        }
    }

    function buildToggle() {
        if (doc.getElementById('tlj-toggle')) return;
        var sb = doc.querySelector('section[data-testid="stSidebar"]');
        if (!sb) return;
        var native = doc.querySelector('[data-testid="stSidebarCollapseButton"]');
        if (native) native.style.cssText = 'display:none!important;';
        var btn = doc.createElement('button');
        btn.id = 'tlj-toggle';
        btn.innerHTML = '&#8592;';
        btn.style.cssText = 'position:fixed;top:50%;left:240px;transform:translateY(-50%);z-index:2147483647;width:26px;height:54px;background:#FFFFFF;border:2px solid #0B3D2E;border-left:none;border-radius:0 6px 6px 0;color:#0B3D2E;font-size:1.1rem;cursor:pointer;box-shadow:2px 0 8px rgba(11,61,46,0.15);transition:left 0.3s ease,background 0.2s,color 0.2s;display:flex;align-items:center;justify-content:center;padding:0;font-family:Georgia,serif;';
        btn.onmouseenter = function() { btn.style.background='#0B3D2E'; btn.style.color='#EFE0D0'; };
        btn.onmouseleave = function() { btn.style.background='#FFFFFF'; btn.style.color='#0B3D2E'; };
        btn.onclick = function() {
            var sb2 = doc.querySelector('section[data-testid="stSidebar"]');
            if (!sb2) return;
            if (sidebarOpen) {
                sb2.style.setProperty('min-width','0px','important');
                sb2.style.setProperty('width','0px','important');
                sb2.style.setProperty('overflow','hidden','important');
                sb2.style.setProperty('border-right','none','important');
                btn.style.left='0px'; btn.innerHTML='&#8594;';
                sidebarOpen = false;
            } else {
                sb2.style.setProperty('min-width','240px','important');
                sb2.style.setProperty('width','240px','important');
                sb2.style.setProperty('overflow-y','auto','important');
                sb2.style.setProperty('border-right','2px solid #0B3D2E','important');
                btn.style.left='240px'; btn.innerHTML='&#8592;';
                sidebarOpen = true;
            }
        };
        doc.body.appendChild(btn);
        var mo = new MutationObserver(function() {
            if (!doc.getElementById('tlj-toggle')) { btn.id = 'tlj-toggle'; doc.body.appendChild(btn); }
        });
        mo.observe(doc.body, { childList: true, subtree: false });
    }

    function buildProgressBar() {
        if (doc.getElementById('tlj-progress')) return;
        var bar = doc.createElement('div');
        bar.id = 'tlj-progress';
        bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;width:0%;background:linear-gradient(90deg,#0B3D2E,#B08968);z-index:2147483647;transition:width 0.08s linear;pointer-events:none;';
        doc.body.appendChild(bar);
        var stMain = doc.querySelector('[data-testid="stMain"]');
        if (!stMain) return;
        stMain.addEventListener('scroll', function() {
            var pct = stMain.scrollHeight - stMain.clientHeight > 0
                ? (stMain.scrollTop / (stMain.scrollHeight - stMain.clientHeight)) * 100 : 0;
            bar.style.width = pct + '%';
        }, { passive: true });
    }

    function initFloatingCards() {
        if (doc.getElementById('tlj-float-style')) return;
        var style = doc.createElement('style');
        style.id = 'tlj-float-style';
        style.innerHTML =
            '@keyframes tljFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}' +
            '@keyframes tljFloatB{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}' +
            '.arch-box-dark{animation:tljFloat 5s ease-in-out infinite;}' +
            '.metric-card{animation:tljFloatB 4s ease-in-out infinite;}';
        doc.head.appendChild(style);
    }

    function initParallax() {
        var stMain = doc.querySelector('[data-testid="stMain"]');
        var heroTitle = doc.querySelector('.hero-title');
        var heroSub = doc.querySelector('.hero-subtitle');
        var heroSection = doc.querySelector('.hero-section');
        if (!stMain || !heroTitle || !heroSection) return;
        stMain.addEventListener('scroll', function() {
            var sy = stMain.scrollTop;
            var hh = heroSection.offsetHeight;
            if (sy > hh) {
                heroTitle.style.transform = ''; heroTitle.style.opacity = '';
                if (heroSub) { heroSub.style.transform = ''; heroSub.style.opacity = ''; }
                return;
            }
            var p = sy / hh;
            var op = Math.max(0, 1 - p * 2);
            heroTitle.style.transform = 'translateY(-' + (sy * 0.3) + 'px)';
            heroTitle.style.opacity = op;
            if (heroSub) {
                heroSub.style.transform = 'translateY(-' + (sy * 0.18) + 'px)';
                heroSub.style.opacity = op;
            }
        }, { passive: true });
    }

    function initAnimations() {
        var stMain = doc.querySelector('[data-testid="stMain"]');
        if (!stMain) return;

        doc.querySelectorAll('.anim-card').forEach(function(el) {
            if (el._tlj_setup) return;
            el._tlj_setup = true;
            el._visible = false;
            el.style.transition = 'opacity 0.65s cubic-bezier(0.22,1,0.36,1), transform 0.65s cubic-bezier(0.22,1,0.36,1)';
            el.style.opacity = '0';
            el.style.transform = 'translateY(28px)';
        });

        doc.querySelectorAll('.arch-box, .anim-fade-left').forEach(function(el) {
            if (el.closest('section[data-testid="stSidebar"]')) return;
            if (el._tlj_setup) return;
            el._tlj_setup = true;
            el._visible = false;
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            el.style.opacity = '0';
            el.style.transform = 'translateX(-20px)';
        });

        doc.querySelectorAll('.anim-pop-in').forEach(function(el) {
            if (el.closest('section[data-testid="stSidebar"]')) return;
            if (el._tlj_setup) return;
            el._tlj_setup = true;
            el._visible = false;
            el.style.transition = 'opacity 0.55s ease, transform 0.55s ease';
            el.style.opacity = '0';
            el.style.transform = 'scale(0.92)';
        });

        doc.querySelectorAll('[data-testid="stPlotlyChart"]').forEach(function(el) {
            if (el._tlj_setup) return;
            el._tlj_setup = true;
            el._visible = false;
            el.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
            el.style.opacity = '0';
            el.style.transform = 'translateY(24px)';
        });

        var STANDARD =
            '.anim-card,' +
            '.arch-box,.anim-fade-left,.anim-pop-in,' +
            '[data-testid="stPlotlyChart"]';

        function reveal() {
            var vh = win.innerHeight;
            doc.querySelectorAll(STANDARD).forEach(function(el) {
                if (!el._tlj_setup) return;
                if (el.closest('section[data-testid="stSidebar"]')) return;
                if (el.closest('.hero-section')) return;

                var rect = el.getBoundingClientRect();
                var inView = rect.top < vh - 30 && rect.bottom > 60;

                if (inView && !el._visible) {
                    el._visible = true;
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                } else if (!inView && el._visible) {
                    el._visible = false;
                    el.style.opacity = '0';
                    if (el.classList.contains('anim-card')) {
                        el.style.transform = 'translateY(28px)';
                    } else if (el.classList.contains('arch-box') || el.classList.contains('anim-fade-left')) {
                        el.style.transform = 'translateX(-20px)';
                    } else if (el.classList.contains('anim-pop-in')) {
                        el.style.transform = 'scale(0.92)';
                    } else if (el.matches('[data-testid="stPlotlyChart"]')) {
                        el.style.transform = 'translateY(24px)';
                    }
                }
            });
        }

        stMain.addEventListener('scroll', reveal, { passive: true });
        reveal();
        setTimeout(reveal, 500);
        setTimeout(reveal, 1200);
    }

    function styleArchColumns() {
        var anchor = doc.querySelector('a[name="how-it-works"]');
        if (!anchor) return;

        var node = anchor, topVB = null;
        while (node && node !== doc.body) {
            if (node.getAttribute && node.getAttribute('data-testid') === 'stVerticalBlock') {
                topVB = node; break;
            }
            node = node.parentElement;
        }
        if (!topVB) return;

        var kids = Array.from(topVB.children);
        var anchorIdx = -1;
        kids.forEach(function(k, i) {
            if (k.contains(anchor)) anchorIdx = i;
        });
        if (anchorIdx === -1) return;

        var hBlock = null;
        for (var i = anchorIdx; i < Math.min(anchorIdx + 8, kids.length); i++) {
            var found = kids[i].querySelector('[data-testid="stHorizontalBlock"]');
            if (found) { hBlock = found; break; }
        }
        if (!hBlock) return;

        hBlock.style.setProperty('align-items', 'center', 'important');
        hBlock.style.setProperty('display', 'flex', 'important');

        var cols = hBlock.querySelectorAll(':scope > [data-testid="stColumn"]');
        cols.forEach(function(col) {
            col.style.setProperty('display', 'flex', 'important');
            col.style.setProperty('flex-direction', 'column', 'important');
            col.style.setProperty('justify-content', 'center', 'important');
        });
    }

    function styleForecastingEngineCard() {
        var anchor = doc.querySelector('a[name="forecasting-engine"]');
        var endEl = doc.querySelector('hr.tlj-exclude-from-card');
        if (!anchor) return;

        var node = anchor, topVB = null;
        while (node && node !== doc.body) {
            if (node.getAttribute && node.getAttribute('data-testid') === 'stVerticalBlock') {
                topVB = node; break;
            }
            node = node.parentElement;
        }
        if (!topVB) return;

        var kids = Array.from(topVB.children);
        var anchorIdx = -1, endIdx = kids.length;
        kids.forEach(function(k, i) {
            if (k.contains(anchor)) anchorIdx = i;
            if (endEl && k.contains(endEl) && endIdx === kids.length) endIdx = i;
        });
        if (anchorIdx === -1) return;

        var sectionEls = kids.slice(anchorIdx, endIdx);
        if (sectionEls.length === 0) return;

        sectionEls.forEach(function(el, i) {
            var isFirst = i === 0;
            var isLast = i === sectionEls.length - 1;
            el.style.backgroundColor = 'rgba(255,255,255,0.62)';
            el.style.borderLeft = '1px solid rgba(176,137,104,0.32)';
            el.style.borderRight = '1px solid rgba(176,137,104,0.32)';
            el.style.paddingLeft = '2rem';
            el.style.paddingRight = '2rem';
            el.style.boxSizing = 'border-box';
            if (isFirst) {
                el.style.borderTop = '1px solid rgba(176,137,104,0.32)';
                el.style.borderRadius = '14px 14px 0 0';
                el.style.paddingTop = '1.5rem';
                el.style.boxShadow = '0 2px 16px rgba(11,61,46,0.05)';
            }
            if (isLast) {
                el.style.borderBottom = '1px solid rgba(176,137,104,0.32)';
                el.style.borderRadius = isFirst ? '14px' : '0 0 14px 14px';
                el.style.paddingBottom = '2rem';
            }
            if (!isFirst && !isLast) {
                el.style.borderTop = 'none';
                el.style.borderBottom = 'none';
            }
        });
    }

    function styleLiveDemoCard() {
        var anchor = doc.querySelector('a[name="live-forecast-demo"]');
        if (!anchor) return;

        var node = anchor, topVB = null;
        while (node && node !== doc.body) {
            if (node.getAttribute && node.getAttribute('data-testid') === 'stVerticalBlock') {
                topVB = node; break;
            }
            node = node.parentElement;
        }
        if (!topVB) return;

        var kids = Array.from(topVB.children);
        var anchorIdx = -1;
        kids.forEach(function(k, i) {
            if (k.contains(anchor)) anchorIdx = i;
        });
        if (anchorIdx === -1) return;

        var hBlock = null;
        for (var i = anchorIdx; i < Math.min(anchorIdx + 4, kids.length); i++) {
            var found = kids[i].querySelector('[data-testid="stHorizontalBlock"]');
            if (found) { hBlock = found; break; }
        }
        if (!hBlock) return;

        var cols = hBlock.querySelectorAll(':scope > [data-testid="stColumn"]');
        if (cols.length < 2) return;
        var demoCol = cols[1];

        var demoColVB = demoCol.querySelector('[data-testid="stVerticalBlock"]');
        if (!demoColVB) return;

        var innerKids = Array.from(demoColVB.children);
        var cardElIdx = -1;
        innerKids.forEach(function(el, i) {
            if (el.querySelector('.tlj-demo-card')) cardElIdx = i;
        });
        if (cardElIdx === -1) return;

        var controlEls = innerKids.slice(cardElIdx + 1);
        controlEls.forEach(function(el, i) {
            var isLast = i === controlEls.length - 1;
            el.style.background = '#FFFFFF';
            el.style.borderLeft = '1px solid rgba(11,61,46,0.12)';
            el.style.borderRight = '1px solid rgba(11,61,46,0.12)';
            el.style.paddingLeft = '1.6rem';
            el.style.paddingRight = '1.6rem';
            el.style.paddingTop = '0';
            el.style.boxSizing = 'border-box';
            el.style.maxWidth = '420px';
            el.style.marginLeft = 'auto';
            el.style.marginRight = 'auto';
            el.style.display = 'block';
            if (isLast) {
                el.style.borderBottom = '1px solid rgba(11,61,46,0.12)';
                el.style.borderRadius = '0 0 28px 28px';
                el.style.paddingBottom = '1.6rem';
            }
        });
    }

    function styleLiveDemoRow() {
        var anchor = doc.querySelector('a[name="live-forecast-demo"]');
        if (!anchor) return;
        var node = anchor, topVB = null;
        while (node && node !== doc.body) {
            if (node.getAttribute && node.getAttribute('data-testid') === 'stVerticalBlock') { topVB = node; break; }
            node = node.parentElement;
        }
        if (!topVB) return;
        var kids = Array.from(topVB.children);
        var anchorIdx = -1;
        kids.forEach(function(k, i) { if (k.contains(anchor)) anchorIdx = i; });
        if (anchorIdx === -1) return;
        var hBlock = null;
        for (var i = anchorIdx; i < Math.min(anchorIdx + 4, kids.length); i++) {
            var found = kids[i].querySelector('[data-testid="stHorizontalBlock"]');
            if (found) { hBlock = found; break; }
        }
        if (!hBlock) return;
        hBlock.style.setProperty('align-items', 'center', 'important');
        hBlock.style.setProperty('justify-content', 'center', 'important');
        hBlock.style.setProperty('max-width', '1000px', 'important');
        hBlock.style.setProperty('margin-left', 'auto', 'important');
        hBlock.style.setProperty('margin-right', 'auto', 'important');
        hBlock.style.setProperty('gap', '1.5rem', 'important');
    }

    function addDemoGlow() {
        if (doc.getElementById('tlj-glow-style')) return;
        var s = doc.createElement('style');
        s.id = 'tlj-glow-style';
        s.textContent = `
            @keyframes tljGlowPulse {
                0%, 100% { box-shadow: 0 2px 20px rgba(11,61,46,0.06); }
                50%       { box-shadow: 0 4px 36px rgba(11,61,46,0.18); }
            }
            .tlj-demo-card {
                animation: tljGlowPulse 3s ease-in-out infinite;
            }
        `;
        doc.head.appendChild(s);
    }

    function initCounters() {
        var stMain = doc.querySelector('[data-testid="stMain"]');
        if (!stMain) return;
        doc.querySelectorAll('.metric-value').forEach(function(el) {
            if (el._tljCounterSetup) return;
            el._tljCounterSetup = true;

            var rawText = el.textContent.trim();

            // Skip anything with a slash — ratios (3/12) and scores-out-of-100 (72/100)
            // don't make sense to "count up" and previously produced garbled output.
            if (rawText.indexOf('/') !== -1) return;

            var match = rawText.match(/^([^\d]*)(\d+(?:\.\d+)?)([^\d]*)$/);
            if (!match) return;

            var prefix = match[1];
            var num = parseFloat(match[2]);
            var suffix = match[3];
            if (isNaN(num) || num === 0) return;

            el._countOriginalHTML = el.innerHTML;
            el._counting = false;

            new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting && !el._counting) {
                        el._counting = true;
                        var t0 = null;
                        function step(ts) {
                            if (!t0) t0 = ts;
                            var p = Math.min((ts - t0) / 1000, 1);
                            var e = 1 - Math.pow(1 - p, 3);
                            el.textContent = prefix + Math.round(num * e) + suffix;
                            if (p < 1) requestAnimationFrame(step);
                            else { el.innerHTML = el._countOriginalHTML; el._counting = false; }
                        }
                        requestAnimationFrame(step);
                    }
                });
            }, { threshold: 0.8, root: stMain }).observe(el);
        });
    }

    function styleTabReveal() {
        if (doc.body._tljTabListenerAttached) return;
        doc.body._tljTabListenerAttached = true;

        doc.addEventListener('click', function(e) {
            var tabBtn = e.target.closest('div[data-testid="stTab"][role="tab"]');
            if (!tabBtn) return;
            setTimeout(function() {
                doc.querySelectorAll('.anim-card, .arch-box, .anim-fade-left, .anim-pop-in, [data-testid="stPlotlyChart"]').forEach(function(el) {
                    if (el.closest('section[data-testid="stSidebar"]')) return;
                    if (el.closest('.hero-section')) return;
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                });
            }, 50);
        }, true);

        doc.addEventListener('click', function(e) {
            var tabBtn = e.target.closest('div[data-testid="stTab"][role="tab"]');
            if (!tabBtn) return;
            setTimeout(function() {
                doc.querySelectorAll('.anim-card, .arch-box, .anim-fade-left, .anim-pop-in, [data-testid="stPlotlyChart"]').forEach(function(el) {
                    if (el.closest('section[data-testid="stSidebar"]')) return;
                    if (el.closest('.hero-section')) return;
                    el.style.opacity = '1';
                    el.style.transform = 'none';
                });
                styleConfidenceBreakdownTable();
                styleForecastingEngineCard();
            }, 60);
        }, true);
    }

    function styleConfidenceBreakdownTable() {
        var labels = doc.querySelectorAll('.metric-label');
        var target = null;
        labels.forEach(function(l) {
            if (l.textContent.trim() === 'Confidence Breakdown') target = l;
        });
        if (!target) return;

        var container = target.closest('[data-testid="stVerticalBlock"]');
        if (!container) return;

        var table = container.querySelector('[data-testid="stTable"]');
        if (table && !table.classList.contains('tlj-secondary-table')) {
            table.classList.add('tlj-secondary-table');
        }
    }

    function styleConfidenceInfoLink() {
        if (doc.body._tljConfidenceLinkAttached) return;
        doc.body._tljConfidenceLinkAttached = true;

        function fireTabPress(el) {
            var rect = el.getBoundingClientRect();
            var cx = rect.left + rect.width / 2;
            var cy = rect.top + rect.height / 2;
            var opts = {
                bubbles: true, cancelable: true, view: win,
                clientX: cx, clientY: cy,
                pointerId: 1, pointerType: 'mouse', isPrimary: true
            };
            ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(function(type) {
                var EventCtor = (type.indexOf('pointer') === 0 && win.PointerEvent) ? win.PointerEvent : win.MouseEvent;
                var evt;
                try {
                    evt = new EventCtor(type, opts);
                } catch (err) {
                    evt = doc.createEvent('MouseEvents');
                    evt.initEvent(type, true, true);
                }
                el.dispatchEvent(evt);
            });
        }

        doc.addEventListener('click', function(e) {
            var link = e.target.closest('.tlj-confidence-info');
            if (!link) return;
            e.preventDefault();

            var tabs = doc.querySelectorAll('div[data-testid="stTab"][role="tab"]');
            var targetTab = null;
            tabs.forEach(function(t) {
                var label = (t.textContent || '').replace(/\s+/g, ' ').trim();
                if (label === 'Confidence Detail') targetTab = t;
            });
            if (!targetTab && tabs.length) targetTab = tabs[tabs.length - 1];

            if (targetTab) {
                fireTabPress(targetTab);
                setTimeout(function() {
                    targetTab.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 150);
            }
        }, true);
    }

    function run() {
        fixSidebar();
        buildToggle();
        buildProgressBar();
        initFloatingCards();
        initParallax();
        initAnimations();
        styleArchColumns();
        styleForecastingEngineCard();
        addDemoGlow();
        styleLiveDemoCard();
        styleLiveDemoRow();
        styleTabReveal();
        styleConfidenceInfoLink();
        initCounters();
    }

    run();
    setTimeout(run, 400);
    setTimeout(run, 1000);
    setTimeout(run, 2000);
})();
</script>
""", height=0)