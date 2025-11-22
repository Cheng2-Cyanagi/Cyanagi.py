import streamlit as st
import pandas as pd
import json
import os
import uuid
import time
import random
from datetime import datetime, timedelta
from streamlit_calendar import calendar

# --- Constants & Configuration ---
DATA_FILE = "qing_journey_data.json"
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/9815/9815474.png"

# Color Palette
C_LIGHT = '#C5FFF8'
C_CYAN = '#96EFFF'
C_SKY = '#5FBDFF'
C_PURPLE = '#7B66FF'

# Categories
CATEGORIES = {
    'Critical': {'label': '🔥 超級必要 (無法延後)', 'color': '#EF4444', 'bg': '#FEF2F2'},
    'Daily': {'label': '✅ 每日必做 (00:00 重置)', 'color': '#7B66FF', 'bg': '#F3F0FF'},
    'Todo': {'label': '📝 待辦事項 (To-Do)', 'color': '#5FBDFF', 'bg': '#F0F9FF'},
    'Costume': {'label': '🛠️ 服裝製作 (CCF前完成)', 'color': '#10B981', 'bg': '#ECFDF5'},
    'A': {'label': '📅 A. 半天以上行程', 'color': '#7B66FF', 'bg': '#F3F0FF'},
    'B': {'label': '⏳ B. 3-4 小時短程', 'color': '#5FBDFF', 'bg': '#F0F9FF'},
    'C': {'label': '💤 C. 放鬆/低消耗', 'color': '#14B8A6', 'bg': '#F0FDFA'},
    'D': {'label': '🆓 D. 填補空檔', 'color': '#6B7280', 'bg': '#F9FAFB'},
    'Inventory': {'label': '🎒 必備物品/購物', 'color': '#14B8A6', 'bg': '#F0FDFA'},
    'Food': {'label': '🍜 必吃美食', 'color': '#EC4899', 'bg': '#FDF2F8'},
    'Meetup': {'label': '🤝 必約對象', 'color': '#6366F1', 'bg': '#EEF2FF'},
    'Uncertain': {'label': '❓ 待確認行程', 'color': '#64748B', 'bg': '#F1F5F9'}
}

# Initial Data (Mirrored from your React code)
INITIAL_DATA = [
    {"id": str(uuid.uuid4()), "title": "印製認親卡/名片", "category": "Critical", "desc": "務必於 4/5 前完成設計與送印。", "date": "2026-04-04", "isCompleted": False},
    {"id": str(uuid.uuid4()), "title": "季雪專場", "category": "Critical", "desc": "16:00 - 22:00。需提前確認交通。", "date": "2026-04-05", "time": "16:00", "isCompleted": False},
    {"id": str(uuid.uuid4()), "title": "CCF", "category": "Critical", "desc": "全天活動。服裝務必完成。", "date": "2026-04-26", "time": "09:00", "isCompleted": False},
    {"id": str(uuid.uuid4()), "title": "打音遊", "category": "Daily", "desc": "維持手感習慣。", "isCompleted": False},
    {"id": str(uuid.uuid4()), "title": "綠色帽外套", "category": "Costume", "desc": "尋找版型。", "progress": 25, "isCompleted": False},
    {"id": str(uuid.uuid4()), "title": "黑色工裝褲", "category": "Costume", "desc": "需有多口袋設計。", "progress": 50, "isCompleted": False},
    {"id": str(uuid.uuid4()), "title": "三創十二樓", "category": "B", "desc": "3C愛好者必逛。", "isCompleted": False},
    {"id": str(uuid.uuid4()), "title": "公館雪腐冰", "category": "Food", "desc": "第一週必吃。", "isCompleted": False},
]

# --- Helper Functions ---

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return INITIAL_DATA

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_category_style(cat):
    return CATEGORIES.get(cat, CATEGORIES['D'])

# --- Setup Page ---
st.set_page_config(
    page_title="靑凪旅程紀錄版",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Aesthetics ---
st.markdown(f"""
<style>
    /* Global Background */
    .stApp {{
        background-color: {C_LIGHT};
        background-image: radial-gradient({C_CYAN} 1px, transparent 1px);
        background-size: 20px 20px;
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: {C_SKY}; border-radius: 4px; }}
    
    /* Card Styling */
    .item-card {{
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }}
    .item-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(150, 239, 255, 0.3);
    }}
    
    /* Typography */
    h1, h2, h3 {{ color: #333; font-family: 'Segoe UI', sans-serif; }}
    .stButton button {{
        border-radius: 20px;
        font-weight: bold;
    }}
    
    /* Progress Bar Customization */
    .stProgress > div > div > div > div {{
        background-image: linear-gradient(to right, {C_SKY}, {C_PURPLE});
    }}
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if 'random_result' not in st.session_state:
    st.session_state.random_result = None

# --- Sidebar (Logo & Actions) ---
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown("### 靑凪旅程")
    
    if st.button("➕ 新增行程", use_container_width=True):
        st.session_state.editing_item = None # New item mode
        st.session_state.show_edit_modal = True
    
    if st.button("🔄 重置資料", use_container_width=True):
        st.session_state.data = INITIAL_DATA
        save_data(INITIAL_DATA)
        st.rerun()

# --- Header ---
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.markdown(f"<h2 style='color:{C_PURPLE}'>{datetime.now().strftime('%H:%M')}</h2>", unsafe_allow_html=True)
    st.caption(datetime.now().strftime('%Y-%m-%d %A'))
with col2:
    st.title("2026 靑凪旅程紀錄")
    # Search Bar
    search_query = st.text_input("🔍", placeholder="搜尋行程...", label_visibility="collapsed")

# --- Main Logic Functions ---

def render_item_card(item, key_suffix):
    """Renders a single todo item card."""
    cat_style = get_category_style(item['category'])
    border_color = cat_style['color']
    
    # Checkbox for completion
    is_done = item.get('isCompleted', False)
    
    # Container with custom styling
    with st.container():
        cols = st.columns([0.5, 4, 1, 1])
        
        # Checkbox
        with cols[0]:
            new_status = st.checkbox("", value=is_done, key=f"check_{item['id']}_{key_suffix}")
            if new_status != is_done:
                item['isCompleted'] = new_status
                save_data(st.session_state.data)
                st.rerun()

        # Content
        with cols[1]:
            title_style = "text-decoration: line-through; color: gray;" if is_done else "font-weight: bold;"
            st.markdown(f"<div style='{title_style}'>{item['title']}</div>", unsafe_allow_html=True)
            
            # Tags: Date & Category
            tags_html = f"""
            <span style='background:{cat_style['bg']}; color:{cat_style['color']}; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:bold; border:1px solid {cat_style['color']}30'>
                {CATEGORIES[item['category']]['label'].split(' ')[0]}
            </span>
            """
            if item.get('date'):
                tags_html += f" <span style='background:#f0f9ff; color:#666; padding:2px 8px; border-radius:10px; font-size:10px; border:1px solid #ddd'>📅 {item['date']} {item.get('time', '')}</span>"
            
            if item.get('location'):
                map_url = f"https://www.google.com/maps/search/?api=1&query={item['location']}"
                tags_html += f" <a href='{map_url}' target='_blank' style='text-decoration:none; background:#e0f2fe; color:#0284c7; padding:2px 8px; border-radius:10px; font-size:10px;'>📍 {item['location']}</a>"

            st.markdown(tags_html, unsafe_allow_html=True)
            
            if item.get('desc'):
                st.caption(item['desc'])
            
            # Progress Bar for Costume
            if item['category'] == 'Costume' and not is_done:
                progress = item.get('progress', 0)
                st.progress(progress / 100)
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("25%", key=f"p25_{item['id']}"): update_progress(item['id'], 25)
                if c2.button("50%", key=f"p50_{item['id']}"): update_progress(item['id'], 50)
                if c3.button("75%", key=f"p75_{item['id']}"): update_progress(item['id'], 75)
                if c4.button("100%", key=f"p100_{item['id']}"): update_progress(item['id'], 100)

        # Actions (Edit/Delete)
        with cols[3]:
            if st.button("✏️", key=f"edit_{item['id']}_{key_suffix}"):
                st.session_state.editing_item = item
                st.session_state.show_edit_modal = True
                st.rerun()
            if st.button("🗑️", key=f"del_{item['id']}_{key_suffix}"):
                st.session_state.data = [i for i in st.session_state.data if i['id'] != item['id']]
                save_data(st.session_state.data)
                st.rerun()
        
        st.markdown("---")

def update_progress(item_id, val):
    for i in st.session_state.data:
        if i['id'] == item_id:
            i['progress'] = val
            if val == 100: i['isCompleted'] = True
    save_data(st.session_state.data)
    st.rerun()

def pick_random(category=None):
    candidates = [i for i in st.session_state.data if not i['isCompleted']]
    if category:
        candidates = [i for i in candidates if i['category'] == category]
    
    if candidates:
        winner = random.choice(candidates)
        st.toast(f"✨ 命運決定：{winner['title']}", icon="🎲")
    else:
        st.toast("沒有可選的行程！", icon="⚠️")

# --- Edit Modal (Form) ---
if st.session_state.get("show_edit_modal", False):
    with st.form("edit_form"):
        st.subheader("編輯/新增 行程")
        item = st.session_state.get("editing_item", {})
        
        new_title = st.text_input("行程名稱", value=item.get("title", ""))
        
        cat_options = list(CATEGORIES.keys())
        current_cat_idx = cat_options.index(item.get("category", "D")) if item.get("category") in cat_options else 7
        new_category = st.selectbox("分類", cat_options, index=current_cat_idx, format_func=lambda x: CATEGORIES[x]['label'])
        
        col_d, col_t = st.columns(2)
        with col_d:
            d_val = datetime.strptime(item.get("date"), "%Y-%m-%d").date() if item.get("date") else None
            new_date = st.date_input("日期", value=d_val)
        with col_t:
            new_time = st.text_input("時間 (HH:MM)", value=item.get("time", ""))
            
        new_loc = st.text_input("地點 (用於導航)", value=item.get("location", ""))
        new_desc = st.text_area("詳細說明 / 備註", value=item.get("desc", ""))
        
        # AI Suggestion Simulation
        if st.form_submit_button("✨ AI 寫內容"):
             new_desc = f"關於 {new_title} 的建議：記得確認營業時間，如果是戶外行程請帶傘！ ({new_category} 分類建議)"
             st.info("已生成建議，請點擊下方儲存")

        col_save, col_cancel = st.columns(2)
        with col_save:
            submitted = st.form_submit_button("💾 儲存")
        with col_cancel:
            cancelled = st.form_submit_button("❌ 取消")

        if submitted:
            new_item = {
                "id": item.get("id", str(uuid.uuid4())),
                "title": new_title,
                "category": new_category,
                "date": str(new_date) if new_date else None,
                "time": new_time,
                "location": new_loc,
                "desc": new_desc,
                "isCompleted": item.get("isCompleted", False),
                "progress": item.get("progress", 0)
            }
            
            if item: # Update existing
                st.session_state.data = [new_item if i['id'] == item['id'] else i for i in st.session_state.data]
            else: # Add new
                st.session_state.data.append(new_item)
            
            save_data(st.session_state.data)
            st.session_state.show_edit_modal = False
            st.rerun()
            
        if cancelled:
            st.session_state.show_edit_modal = False
            st.rerun()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 總覽 (Dashboard)", "📅 日曆 (Calendar)", "🎒 清單 (Lists)"])

# === TAB 1: DASHBOARD ===
with tab1:
    # Progress Stats
    completed_count = len([i for i in st.session_state.data if i['isCompleted']])
    total_count = len(st.session_state.data)
    progress_pct = int((completed_count / total_count) * 100) if total_count > 0 else 0
    
    st.markdown(f"""
    <div style="background:linear-gradient(45deg, {C_PURPLE}, {C_SKY}); padding:20px; border-radius:20px; color:white; margin-bottom:20px;">
        <h3>旅程進度</h3>
        <h1 style="color:white">{progress_pct}%</h1>
        <p>已完成 {completed_count} / {total_count} 個項目</p>
    </div>
    """, unsafe_allow_html=True)

    # Randomizer
    st.subheader("🎲 隨機決策")
    r_cols = st.columns(6)
    buttons = [('A', '長時'), ('B', '短程'), ('C', '放鬆'), ('D', '填補'), ('Food', '食'), ('Todo', '待辦')]
    for idx, (cat, label) in enumerate(buttons):
        with r_cols[idx]:
            if st.button(label, key=f"rand_{cat}"):
                pick_random(cat)

    # Sections
    sections = [
        ('Daily', 'Daily'),
        ('Todo', 'Todo'),
        ('Critical', 'Critical'),
        ('Costume', 'Costume')
    ]
    
    # Filter items
    display_items = st.session_state.data
    if search_query:
        display_items = [i for i in display_items if search_query.lower() in i['title'].lower()]

    for cat_key, title in sections:
        filtered = [i for i in display_items if i['category'] == cat_key]
        if filtered:
            st.subheader(CATEGORIES[cat_key]['label'])
            for item in filtered:
                render_item_card(item, "dash")

    # A/B/C/D Groups
    st.subheader("📂 分類行程")
    c1, c2 = st.columns(2)
    with c1:
        for cat in ['A', 'C']:
            filtered = [i for i in display_items if i['category'] == cat]
            if filtered:
                st.markdown(f"#### {CATEGORIES[cat]['label']}")
                for item in filtered:
                    render_item_card(item, "dash_grp1")
    with c2:
        for cat in ['B', 'D', 'Uncertain']:
            filtered = [i for i in display_items if i['category'] == cat]
            if filtered:
                st.markdown(f"#### {CATEGORIES[cat]['label']}")
                for item in filtered:
                    render_item_card(item, "dash_grp2")

# === TAB 2: CALENDAR ===
with tab2:
    st.subheader("行程日曆")
    events = []
    for item in st.session_state.data:
        if item.get('date'):
            color = CATEGORIES[item['category']]['color']
            events.append({
                "title": item['title'],
                "start": item['date'],
                "backgroundColor": color,
                "borderColor": color
            })
    
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,listMonth"
        },
        "initialDate": "2026-04-01",
    }
    calendar(events=events, options=calendar_options)

# === TAB 3: LISTS (Inventory & Food) ===
with tab3:
    col_inv, col_food = st.columns(2)
    
    with col_inv:
        st.subheader("🎒 必備物品 & 購物")
        inv_items = [i for i in st.session_state.data if i['category'] == 'Inventory']
        for item in inv_items:
            render_item_card(item, "inv")
            
    with col_food:
        st.subheader("🍜 美食 & 必約")
        food_meet_items = [i for i in st.session_state.data if i['category'] in ['Food', 'Meetup']]
        for item in food_meet_items:
            render_item_card(item, "food")

# Footer
st.markdown("---")
st.caption("Made with ❤️ for 靑凪旅程 2026")
