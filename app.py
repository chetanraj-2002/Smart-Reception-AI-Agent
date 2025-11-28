import streamlit as st
import os
import json
from datetime import datetime
import config
from db import init_db, insert_ticket, fetch_recent_tickets, fetch_all_tickets, get_ticket_count
from ai_core import transcribe_audio, analyze_call, validate_analysis
from utils.audio import save_uploaded_file, cleanup_temp_file

# Add this import to reliably render raw HTML
import streamlit.components.v1 as components

# Initialize the database
init_db()

# Page configuration
st.set_page_config(
    page_title="Smart Reception AI Agent",
    page_icon="📞",
    layout="wide"
)

# Custom CSS for glassmorphic design with neon effects
st.markdown("""
<style>
    /* Base styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
        color: #334155;
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }
    
    /* Animated background particles */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        opacity: 0.3;
    }
    
    /* Header / Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        padding: 3rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF, #E0E7FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Glassmorphic card styles */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.25);
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Neon glow effects */
    .neon-purple-glow {
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.5);
    }
    
    .neon-teal-glow {
        box-shadow: 0 0 15px rgba(20, 184, 166, 0.5);
    }
    
    .neon-blue-glow {
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }
    
    /* Audio Upload Card */
    .upload-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(241, 245, 249, 0.6) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
        padding: 2rem;
        margin-bottom: 2rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(139, 92, 246, 0.1), transparent);
        transform: rotate(45deg);
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .upload-card.dragging {
        border: 2px dashed #8B5CF6;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
    }
    
    .upload-card.dragging::before {
        opacity: 1;
    }
    
    .upload-area {
        border: 2px dashed rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        background: rgba(241, 245, 249, 0.5);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #8B5CF6;
        background: rgba(241, 245, 249, 0.8);
    }
    
    .upload-icon {
        font-size: 4rem;
        color: #8B5CF6;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .upload-text {
        color: #64748B;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* Buttons with neon effects */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.85rem 1.75rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px;
    }
    
    .upload-btn {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
    }
    
    .upload-btn:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(139, 92, 246, 0.5) !important;
    }
    
    .process-btn {
        background: linear-gradient(135deg, #14B8A6 0%, #3B82F6 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(20, 184, 166, 0.3) !important;
    }
    
    .process-btn:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(20, 184, 166, 0.5) !important;
    }
    
    /* Progress indicators */
    .progress-container {
        display: flex;
        justify-content: space-between;
        margin-top: 1.5rem;
        padding: 0 1rem;
    }
    
    .progress-step {
        text-align: center;
        flex: 1;
        position: relative;
    }
    
    .progress-step:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 18px;
        right: 0;
        transform: translateX(50%);
        width: calc(100% - 40px);
        height: 3px;
        background: linear-gradient(90deg, #E2E8F0, #CBD5E1);
        z-index: 1;
    }
    
    .step-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #E2E8F0 0%, #F1F5F9 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.75rem;
        position: relative;
        z-index: 2;
        color: #94A3B8;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .step-icon.completed {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%);
        color: white;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
    }
    
    .step-label {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 500;
    }
    
    .step-label.active {
        color: #3B82F6;
        font-weight: 600;
    }
    
    /* Analysis Output Section */
    .analysis-section {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    @media (max-width: 992px) {
        .analysis-section {
            grid-template-columns: 1fr;
        }
    }
    
    /* Transcript Card */
    .transcript-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(139, 92, 246, 0.2);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .transcript-card:hover {
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.2);
        border-color: rgba(139, 92, 246, 0.4);
    }
    
    /* Ticket Insights Card */
    .insights-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(20, 184, 166, 0.2);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .insights-card:hover {
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.2);
        border-color: rgba(20, 184, 166, 0.4);
    }
    
    /* Insights grid */
    .insights-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .insight-item {
        background: rgba(241, 245, 249, 0.7);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(226, 232, 240, 0.5);
    }
    
    .insight-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        background: rgba(241, 245, 249, 0.9);
    }
    
    .insight-label {
        font-size: 0.85rem;
        color: #64748B;
        margin-bottom: 0.75rem;
        font-weight: 500;
    }
    
    .insight-value {
        font-weight: 700;
        font-size: 1.1rem;
        color: #1E293B;
    }
    
    /* Transcript area */
    .transcript-area {
        background: rgba(248, 250, 252, 0.7);
        border-radius: 16px;
        padding: 1.25rem;
        min-height: 250px;
        max-height: 350px;
        overflow-y: auto;
        border: 1px solid rgba(226, 232, 240, 0.5);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Custom scrollbar */
    .transcript-area::-webkit-scrollbar {
        width: 8px;
    }
    
    .transcript-area::-webkit-scrollbar-track {
        background: rgba(226, 232, 240, 0.3);
        border-radius: 4px;
    }
    
    .transcript-area::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #3B82F6, #8B5CF6);
        border-radius: 4px;
    }
    
    .transcript-area::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #2563EB, #7C3AED);
    }
    
    /* Badges with neon colors */
    .badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
    }
    
    .badge-intent {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        color: white;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
    }
    
    .badge-sentiment-positive {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
    }
    
    .badge-sentiment-neutral {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
    }
    
    .badge-sentiment-negative {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
    }
    
    .badge-priority-high {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
    }
    
    .badge-priority-medium {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
        color: white;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
    }
    
    .badge-priority-low {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.3);
    }
    
    .badge-priority-critical {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        color: white;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
    }
    
    .badge-department {
        background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
        color: white;
        box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
    }
    
    /* Summary section */
    .summary-section {
        margin-bottom: 2rem;
    }
    
    .summary-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 1.75rem;
        margin-bottom: 1.25rem;
        transition: all 0.3s ease;
    }
    
    .summary-card:hover {
        box-shadow: 0 10px 25px rgba(31, 38, 135, 0.15);
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    .summary-header {
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    
    .summary-title {
        font-weight: 700;
        color: white;
        margin: 0;
        font-size: 1.25rem;
    }
    
    .short-summary {
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(59, 130, 246, 0.2);
    }
    
    .detailed-summary {
        background: rgba(248, 250, 252, 0.7);
        border-radius: 12px;
        padding: 1.25rem;
        color: #334155;
        line-height: 1.7;
    }
    
    /* Recent Tickets Dashboard */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(226, 232, 240, 0.5);
        padding: 1.75rem;
        transition: all 0.3s ease;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 12px 30px rgba(31, 38, 135, 0.2);
    }
    
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .dashboard-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E293B;
        margin: 0;
    }
    
    .toolbar {
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }
    
    .toolbar select, .toolbar input {
        padding: 0.5rem 1rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
    }
    
    .toolbar button {
        padding: 0.5rem 1rem;
        border-radius: 12px;
        border: none;
        background: #3B82F6;
        color: white;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .toolbar button:hover {
        background: #2563EB;
        transform: translateY(-2px);
    }
    
    /* Recent tickets table */
    .tickets-table-container {
        max-height: 450px;
        overflow-y: auto;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        background-color: white;
    }
    
    .tickets-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.9rem;
        background-color: white;
    }
    
    .tickets-table thead th {
        text-align: center;
        padding: 12px 16px;
        background: #F3F4F6;
        font-weight: 700;
        color: #334155;
        border-bottom: 2px solid #E5E7EB;
        position: sticky;
        top: 0;
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
    }
    
    .tickets-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #E5E7EB;
        vertical-align: middle;
        transition: all 0.2s ease;
        text-align: left;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .tickets-table tr:last-child td {
        border-bottom: none;
    }
    
    .tickets-table tr:nth-child(even) {
        background: #F9FAFB;
    }
    
    .tickets-table tr:hover {
        background: #F3F4F6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Column widths */
    .tickets-table th:nth-child(1),
    .tickets-table td:nth-child(1) { width: 80px; }
    
    .tickets-table th:nth-child(2),
    .tickets-table td:nth-child(2) { width: 170px; }
    
    .tickets-table th:nth-child(3),
    .tickets-table td:nth-child(3) { width: 140px; }
    
    .tickets-table th:nth-child(4),
    .tickets-table td:nth-child(4) { width: 160px; }
    
    .tickets-table th:nth-child(5),
    .tickets-table td:nth-child(5) { width: 120px; text-align: center; }
    
    /* Priority badges in table */
    .priority-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        text-align: center;
        min-width: 80px;
    }
    
    .priority-high {
        background: linear-gradient(135deg, #FECACA 0%, #FCA5A5 100%);
        color: #B91C1C;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);
    }
    
    .priority-medium {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        color: #D97706;
        box-shadow: 0 0 8px rgba(245, 158, 11, 0.3);
    }
    
    .priority-low {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        color: #047857;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.3);
    }
    
    .priority-critical {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        color: #DC2626;
        box-shadow: 0 0 8px rgba(139, 92, 246, 0.3);
    }
    
    /* Scroll anchor */
    .ticket-details-anchor {
        margin-top: -80px;
        padding-top: 80px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.25rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
        }
        
        .analysis-section {
            grid-template-columns: 1fr;
        }
        
        .insights-grid {
            grid-template-columns: 1fr 1fr;
        }
        
        .toolbar {
            flex-direction: column;
            align-items: stretch;
        }
        
        .toolbar select, .toolbar input, .toolbar button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
    }
    
    @media (max-width: 480px) {
        .hero-section {
            padding: 2rem 1rem;
        }
        
        .hero-title {
            font-size: 1.75rem;
        }
        
        .insights-grid {
            grid-template-columns: 1fr;
        }
        
        .progress-step:not(:last-child)::after {
            display: none;
        }
    }
</style>
""", unsafe_allow_html=True)

# Animated background particles
st.markdown("""
<div class="particles">
    <!-- Particles will be added here with JavaScript -->
</div>
<script>
// Simple particle animation
const particlesContainer = document.querySelector('.particles');
if (particlesContainer) {
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = Math.random() * 5 + 2 + 'px';
        particle.style.height = particle.style.width;
        particle.style.backgroundColor = 'rgba(59, 130, 246, 0.3)';
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.opacity = Math.random() * 0.5 + 0.2;
        particle.style.animation = `float${Math.floor(Math.random() * 3) + 1} ${Math.random() * 10 + 10}s infinite ease-in-out`;
        particlesContainer.appendChild(particle);
    }
    
    // Add floating animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float1 {
            0% { transform: translate(0, 0); }
            50% { transform: translate(20px, 20px); }
            100% { transform: translate(0, 0); }
        }
        @keyframes float2 {
            0% { transform: translate(0, 0); }
            50% { transform: translate(-15px, 25px); }
            100% { transform: translate(0, 0); }
        }
        @keyframes float3 {
            0% { transform: translate(0, 0); }
            50% { transform: translate(25px, -15px); }
            100% { transform: translate(0, 0); }
        }
    `;
    document.head.appendChild(style);
}
</script>
""", unsafe_allow_html=True)

# Header / Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Smart Reception AI Agent</h1>
    <p class="hero-subtitle">AI-powered voice transcription & ticket intelligence</p>
</div>
""", unsafe_allow_html=True)

# Check if API key is set
if not config.GOOGLE_GEMINI_API_KEY:
    st.error("❌ Google Gemini API key is not set. Please set the GOOGLE_GEMINI_API_KEY environment variable to use this application.")
    st.stop()

# Add a compatibility wrapper for rerun (works across Streamlit versions)
def safe_rerun():
    """
    Try to trigger a Streamlit rerun in a way that works across Streamlit versions.
    Prefer st.experimental_rerun(), otherwise raise RerunException with a rerun_data
    argument (some Streamlit versions require it). If nothing works, stop execution.
    """
    # Preferred direct call if available
    try:
        rerun_fn = getattr(st, "experimental_rerun", None)
        if callable(rerun_fn):
            rerun_fn()
            return
    except Exception:
        pass

    # Fallback: raise the RerunException with a minimal rerun_data (None)
    for path in (
        "streamlit.runtime.scriptrunner.script_runner",
        "streamlit.runtime.scriptrunner",
    ):
        try:
            mod = __import__(path, fromlist=["RerunException"])
            RerunException = getattr(mod, "RerunException", None)
            if RerunException:
                # Some Streamlit builds require a rerun_data argument; pass None to be safe
                raise RerunException(None)
        except Exception:
            # try next path
            continue

    # Last-resort: stop execution (user will see updated state on next interaction)
    st.stop()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Audio Upload Section
    
    st.markdown('<div class="card-title">📤 Upload Caller Audio</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload a voice message file", 
        type=config.SUPPORTED_AUDIO_FORMATS,
        label_visibility="collapsed",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        st.markdown(f"""
        <div class="upload-area">
            <div class="upload-icon">🎵</div>
            <div class="upload-text">{uploaded_file.name}</div>
            <div class="upload-text">{uploaded_file.size} bytes</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Process button
        if st.button("🔊 Process Audio", type="primary", use_container_width=True):
            # Initialize temp_file_path
            temp_file_path = None
            
            # Show progress steps
            progress_steps = st.empty()
            progress_steps.markdown("""
            <div class="progress-container">
                <div class="progress-step">
                    <div class="step-icon completed">1</div>
                    <div class="step-label active">Upload</div>
                </div>
                <div class="progress-step">
                    <div class="step-icon">2</div>
                    <div class="step-label">Transcribe</div>
                </div>
                <div class="progress-step">
                    <div class="step-icon">3</div>
                    <div class="step-label">Analyze</div>
                </div>
                <div class="progress-step">
                    <div class="step-icon">4</div>
                    <div class="step-label">Ticket</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                # Step 1: Save uploaded file temporarily
                temp_file_path = save_uploaded_file(uploaded_file)
                
                # Update progress
                progress_steps.markdown("""
                <div class="progress-container">
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Upload</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">2</div>
                        <div class="step-label active">Transcribe</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon">3</div>
                        <div class="step-label">Analyze</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon">4</div>
                        <div class="step-label">Ticket</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Step 2: Transcribe audio
                transcript = transcribe_audio(temp_file_path)
                
                # Update progress
                progress_steps.markdown("""
                <div class="progress-container">
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Upload</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Transcribe</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">3</div>
                        <div class="step-label active">Analyze</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon">4</div>
                        <div class="step-label">Ticket</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Step 3: Analyze call
                analysis = analyze_call(transcript)
                
                # Update progress
                progress_steps.markdown("""
                <div class="progress-container">
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Upload</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Transcribe</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Analyze</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon">4</div>
                        <div class="step-label">Ticket</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Step 4: Store in database
                ticket_data = {
                    "transcript": transcript,
                    **analysis
                }
                
                ticket_id = insert_ticket(ticket_data)
                
                # Clean up temporary file
                if temp_file_path:
                    cleanup_temp_file(temp_file_path)
                
                # Complete progress
                progress_steps.markdown("""
                <div class="progress-container">
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Upload</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Transcribe</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Analyze</div>
                    </div>
                    <div class="progress-step">
                        <div class="step-icon completed">✔</div>
                        <div class="step-label active">Ticket</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.success(f"✅ Ticket #{ticket_id} successfully created!")
                
                # Store results in session state for display in other sections
                st.session_state.transcript = transcript
                st.session_state.analysis = analysis
                st.session_state.ticket_id = ticket_id
                
                st.markdown('<div id="ticket-details"></div>', unsafe_allow_html=True)
                st.markdown("""
                <script>
                setTimeout(function() {
                    var element = document.getElementById('ticket-details');
                    if (element) {
                        element.scrollIntoView({behavior: 'smooth'});
                    }
                }, 500);
                </script>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                # Clean up temporary file in case of error
                if temp_file_path:
                    cleanup_temp_file(temp_file_path)
                
                st.error(f"❌ An error occurred: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transcript & Analysis Output
    if 'transcript' in st.session_state:
        
        # Analysis Output Section
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        
        # Transcript Card
        st.markdown('<div class="card-title">📝 Transcription</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="transcript-area">{st.session_state.transcript}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ticket Insights Card
        st.markdown('<div class="card-title">🔍 Ticket Insights</div>', unsafe_allow_html=True)
        
        # Get badge class based on value
        def get_badge_class(category, value):
            if category == "intent":
                return "badge-intent"
            elif category == "sentiment":
                if value == "positive":
                    return "badge-sentiment-positive"
                elif value == "neutral":
                    return "badge-sentiment-neutral"
                elif value == "negative":
                    return "badge-sentiment-negative"
                else:
                    return ""
            elif category == "priority":
                if value == "high":
                    return "badge-priority-high"
                elif value == "medium":
                    return "badge-priority-medium"
                elif value == "low":
                    return "badge-priority-low"
                elif value == "critical":
                    return "badge-priority-critical"
                else:
                    return ""
            elif category == "department":
                return "badge-department"
            else:
                return ""
        
        st.markdown(f"""
        <div class="insights-grid">
            <div class="insight-item">
                <div class="insight-label">Intent</div>
                <div class="insight-value"><span class="badge {get_badge_class('intent', st.session_state.analysis.get('intent_category', ''))}">{st.session_state.analysis.get('intent_category', 'N/A')}</span></div>
            </div>
            <div class="insight-item">
                <div class="insight-label">Sentiment</div>
                <div class="insight-value"><span class="badge {get_badge_class('sentiment', st.session_state.analysis.get('sentiment', ''))}">{st.session_state.analysis.get('sentiment', 'N/A')}</span></div>
            </div>
            <div class="insight-item">
                <div class="insight-label">Priority</div>
                <div class="insight-value"><span class="badge {get_badge_class('priority', st.session_state.analysis.get('priority', ''))}">{st.session_state.analysis.get('priority', 'N/A')}</span></div>
            </div>
            <div class="insight-item">
                <div class="insight-label">Department</div>
                <div class="insight-value"><span class="badge {get_badge_class('department', st.session_state.analysis.get('department', ''))}">{st.session_state.analysis.get('department', 'N/A')}</span></div>
            </div>
            <div class="insight-item">
                <div class="insight-label">Caller Name</div>
                <div class="insight-value">{st.session_state.analysis.get('caller_name', 'Not provided')}</div>
            </div>
            <div class="insight-item">
                <div class="insight-label">Contact</div>
                <div class="insight-value">{st.session_state.analysis.get('caller_contact', 'Not provided')}</div>
            </div>
            <div class="insight-item">
                <div class="insight-label">Ticket ID</div>
                <div class="insight-value">#{st.session_state.ticket_id}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Summary Section
        st.markdown('<div class="summary-section">', unsafe_allow_html=True)
        st.markdown('<div class="summary-header"><h3 class="summary-title">📋 Summary</h3></div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="short-summary">
            {st.session_state.analysis.get('summary_short', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="detailed-summary">
            {st.session_state.analysis.get('summary_full', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Recent Tickets Dashboard
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="dashboard-title">🕒 Recent Tickets</h3>', unsafe_allow_html=True)

    # Replace static toolbar HTML with actual Streamlit controls
    # Build filters from ticket data
    all_tickets_for_filters = fetch_all_tickets()
    departments = sorted({t.get("department") for t in all_tickets_for_filters if t.get("department")})
    dept_options = ["All"] + departments
    priority_options = ["All", "critical", "high", "medium", "low"]

    # Use st.selectbox / text_input so filter changes are reactive
    # Compact filters laid out in columns to save horizontal space and look nicer
    fcol1, fcol2, fcol3 = st.columns([1.2, 1, 2])
    with fcol1:
        dept_filter = st.selectbox("Department", dept_options, key="ra_dept_filter", help="Filter by department")
    with fcol2:
        priority_filter = st.selectbox("Priority", priority_options, key="ra_priority_filter", help="Filter by priority")
    with fcol3:
        search_query = st.text_input("Search tickets...", key="ra_search_query", placeholder="Search caller/intent/department")

    recent_tickets = fetch_recent_tickets(50)  # fetch more then limit client-side

    # simple filter helper
    def apply_filters(tickets, dept, priority, query):
        out = []
        q = (query or "").strip().lower()
        for t in tickets:
            if dept and dept != "All" and (t.get("department") or "") != dept:
                continue
            if priority and priority != "All" and (t.get("priority") or "").lower() != priority.lower():
                continue
            if q:
                combined = " ".join([str(t.get(k,"")) for k in ("caller_name","intent_category","department","transcript")]).lower()
                if q not in combined:
                    continue
            out.append(t)
        return out

    filtered_recent = apply_filters(recent_tickets, dept_filter, priority_filter, search_query)
    # keep original display limit
    display_limit = 5
    display_list = filtered_recent[:display_limit]

    if display_list:
        # Build the entire recent tickets table as one HTML block
        table_html = """
        <div class="tickets-table-container">
        <table class="tickets-table">
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Date & Time</th>
                    <th>Caller</th>
                    <th>Intent</th>
                    <th>Priority</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for ticket in display_list:
            timestamp = ticket.get('created_at', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_datetime = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_datetime = timestamp[:16] if len(timestamp) > 16 else timestamp
            else:
                formatted_datetime = 'N/A'
            
            # nicer priority class (removed avatar/initials)
            priority = (ticket.get('priority') or 'N/A').lower()
            pr_class = "high" if priority == "high" else ("medium" if priority == "medium" else ("critical" if priority == "critical" else "low"))
            caller = ticket.get('caller_name') or "Unknown"
            intent = ticket.get('intent_category') or "N/A"
            # caller cell now only shows name (no avatar)
            table_html += f"""
                <tr class="sr-row">
                    <td class="sr-cell sr-id"><div class="sr-ticket-id">#{ticket.get('id', 'N/A')}</div></td>
                    <td class="sr-cell sr-time">{formatted_datetime}</td>
                    <td class="sr-cell sr-caller"><div class="sr-caller-name">{caller}</div></td>
                    <td class="sr-cell sr-intent">{intent}</td>
                    <td class="sr-cell sr-priority"><span class="sr-priority {pr_class}">{priority.capitalize()}</span></td>
                </tr>
            """

        table_html += """
            </tbody>
        </table>
        </div>
        """
        # Polished scoped CSS (Figma-inspired: avatar removed; caller column simplified)
        table_style = """
        <style>
        /* responsive table wrapper (minimal bottom gap) */
        .sr-table-wrapper{font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#0f172a;padding:6px 6px 4px 6px;box-sizing:border-box;overflow-x:auto;margin-bottom:2px;}
        /* zero bottom margin so controls sit very close to table */
        .sr-card{width:100%;max-width:1200px;margin:0 auto;background:rgba(255,255,255,0.55);backdrop-filter:blur(6px);border-radius:12px;padding:10px;box-shadow:0 6px 20px rgba(12, 20, 60, 0.06);box-sizing:border-box;margin-bottom:0;}
         .sr-table{width:100%;table-layout:fixed;border-collapse:separate;border-spacing:0 10px;min-width:700px;}
         .sr-table thead th{background:transparent;padding:10px 14px 8px 14px;text-align:left;font-weight:700;color:#0b1220;border-bottom:0;}
         .sr-row{background:#ffffff;border-radius:10px;box-shadow:0 6px 16px rgba(12,20,60,0.04);overflow:hidden;}
         .sr-cell{padding:12px 14px;vertical-align:middle;word-break:break-word;white-space:normal;}
         .sr-id{width:80px;flex:0 0 80px;}
         .sr-time{width:160px;color:#64748b;font-size:0.9rem;}
         .sr-caller{display:block;font-weight:600;color:#0f172a;}
         .sr-caller-name{font-weight:600;color:#0f172a;}
         .sr-intent{color:#334155;font-weight:600;}
         .sr-priority{width:120px;text-align:center;}
         .sr-priority .sr-priority{display:inline-block;padding:6px 10px;border-radius:999px;font-weight:700;font-size:0.85rem;white-space:nowrap;}
         .sr-priority .high{background:linear-gradient(135deg,#fee2e2,#fecaca);color:#7f1d1d}
         .sr-priority .medium{background:linear-gradient(135deg,#fffbeb,#fef3c7);color:#92400e}
         .sr-priority .low{background:linear-gradient(135deg,#ecfdf5,#d1fae5);color:#065f46}
         .sr-priority .critical{background:linear-gradient(135deg,#fff1f2,#fee2e2);color:#991b1b}
         /* ensure headers stay readable on small screens */
         @media (max-width:720px){
             .sr-caller-name{font-size:0.9rem;}
             .sr-time{display:none;}
             .sr-card{padding:8px;}
             .sr-table{min-width:600px;}
         }
         </style>
         """
        full_table_html = f"<div class='sr-table-wrapper'><div class='sr-card'>{table_style}{table_html}</div></div>"
        # Recent tickets: slightly reduced iframe height to bring controls closer
        components.html(full_table_html, height=440, scrolling=True)

        # Add View All Tickets button
        if st.button("View All Tickets"):
            st.session_state.view_all_tickets = True
    else:
        st.info("No tickets found in the database.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# View All Tickets Page
if 'view_all_tickets' in st.session_state and st.session_state.view_all_tickets:
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">All Tickets</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Complete history of all processed tickets</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Pagination controls
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    # Add filters for All Tickets page (use same keys so state persists)
    dept_filter_all = st.selectbox("Department", dept_options, key="ra_dept_filter_all")
    priority_filter_all = st.selectbox("Priority", priority_options, key="ra_priority_filter_all")
    search_query_all = st.text_input("Search tickets...", value=st.session_state.get("ra_search_query",""), key="ra_search_query_all")

    # Fetch and filter
    all_tickets = fetch_all_tickets()
    filtered_all = apply_filters(all_tickets, dept_filter_all, priority_filter_all, search_query_all)

    # reset page on filter change
    if 'last_filters' not in st.session_state:
        st.session_state.last_filters = (None, None, None)
    current_filters = (dept_filter_all, priority_filter_all, search_query_all)
    if st.session_state.last_filters != current_filters:
        st.session_state.page = 1
        st.session_state.last_filters = current_filters

    total_tickets = len(filtered_all)
    tickets_per_page = 10
    total_pages = (total_tickets + tickets_per_page - 1) // tickets_per_page if total_tickets > 0 else 1;

    # paginate filtered list
    start_idx = (st.session_state.page - 1) * tickets_per_page
    end_idx = start_idx + tickets_per_page
    page_tickets = filtered_all[start_idx:end_idx]

    if page_tickets:
        # Build full table HTML for all tickets page
        table_html = """
        <div class="tickets-table-container">
        <table class="tickets-table">
            <thead>
                <tr>
                    <th>Ticket ID</th>
                    <th>Date & Time</th>
                    <th>Caller</th>
                    <th>Intent</th>
                    <th>Priority</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for ticket in page_tickets:
            timestamp = ticket.get('created_at', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_datetime = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_datetime = timestamp[:16] if len(timestamp) > 16 else timestamp
            else:
                formatted_datetime = 'N/A'
            
            priority = (ticket.get('priority') or 'N/A').lower()
            pr_class = "high" if priority == "high" else ("medium" if priority == "medium" else ("critical" if priority == "critical" else "low"))
            caller = ticket.get('caller_name') or "Unknown"
            intent = ticket.get('intent_category') or "N/A"
            # caller cell without avatar for all-tickets page
            table_html += f"""
                <tr class="sr-row">
                    <td class="sr-cell sr-id"><div class="sr-ticket-id">#{ticket.get('id', 'N/A')}</div></td>
                    <td class="sr-cell sr-time">{formatted_datetime}</td>
                    <td class="sr-cell sr-caller"><div class="sr-caller-name">{caller}</div></td>
                    <td class="sr-cell sr-intent">{intent}</td>
                    <td class="sr-cell sr-priority"><span class="sr-priority {pr_class}">{priority.capitalize()}</span></td>
                </tr>
            """

        table_html += """
            </tbody>
        </table>
        </div>
        """
        table_style = """
        <style>
        .sr-table-wrapper{font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#0f172a;padding:6px 6px 4px 6px;box-sizing:border-box;overflow-x:auto;margin-bottom:2px;}
        .sr-card{width:100%;max-width:1400px;margin:0 auto;background:rgba(255,255,255,0.55);backdrop-filter:blur(6px);border-radius:12px;padding:12px;box-shadow:0 8px 26px rgba(12, 20, 60, 0.06);box-sizing:border-box;margin-bottom:0;}
          .sr-table{width:100%;table-layout:fixed;border-collapse:separate;border-spacing:0 10px;min-width:720px;}
          .sr-table thead th{background:transparent;padding:10px 14px 8px 14px;text-align:left;font-weight:700;color:#0b1220;border-bottom:0;}
          .sr-row{background:#ffffff;border-radius:10px;box-shadow:0 6px 16px rgba(12,20,60,0.04);overflow:hidden;}
          .sr-cell{padding:12px 14px;vertical-align:middle;word-break:break-word;white-space:normal;}
          .sr-id{width:80px;}
          .sr-time{width:160px;color:#64748b;font-size:0.9rem;}
          .sr-caller{display:block;font-weight:600;color:#0f172a;}
          .sr-caller-name{font-weight:600;color:#0f172a;}
          .sr-intent{color:#334155;font-weight:600;}
          .sr-priority{width:120px;text-align:center;}
          .sr-priority .sr-priority{display:inline-block;padding:6px 10px;border-radius:999px;font-weight:700;font-size:0.85rem;white-space:nowrap;}
          .sr-priority .high{background:linear-gradient(135deg,#fee2e2,#fecaca);color:#7f1d1d}
          .sr-priority .medium{background:linear-gradient(135deg,#fffbeb,#fef3c7);color:#92400e}
          .sr-priority .low{background:linear-gradient(135deg,#ecfdf5,#d1fae5);color:#065f46}
          .sr-priority .critical{background:linear-gradient(135deg,#fff1f2,#fee2e2);color:#991b1b}
          @media (max-width:720px){ .sr-caller-name{font-size:0.9rem} .sr-time{display:none} }
          </style>
          """
        full_table_html = f"<div class='sr-table-wrapper'><div class='sr-card'>{table_style}{table_html}</div></div>"
        # Render with tighter bottom spacing so controls sit closer
        components.html(full_table_html, height=820, scrolling=True)
        
        # Compact pagination: place Previous and Next side-by-side (no large gap)
        p_prev, p_next = st.columns([1,1])
        with p_prev:
            if st.button("← Previous", key="ra_prev") and st.session_state.page > 1:
                st.session_state.page -= 1
                safe_rerun()
        with p_next:
            if st.button("Next →", key="ra_next") and st.session_state.page < total_pages:
                st.session_state.page += 1
                safe_rerun()

        # Back to main page button
        if st.button("Back to Main Page"):
            st.session_state.view_all_tickets = False
            st.session_state.page = 1
            safe_rerun()
    else:
        st.info("No tickets found in the database.")
        if st.button("Back to Main Page"):
            st.session_state.view_all_tickets = False
            st.session_state.page = 1
            safe_rerun()
