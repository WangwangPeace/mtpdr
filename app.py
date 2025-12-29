import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, timezone
import db_manager
from streamlit_option_menu import option_menu

# --- 时区处理 ---
def get_beijing_today():
    """
    获取北京时间的当前日期
    Streamlit Cloud 服务器是 UTC 时间，需要手动+8小时
    """
    utc_now = datetime.now(timezone.utc)
    beijing_now = utc_now + timedelta(hours=8)
    return beijing_now.date()

# 设置页面配置
st.set_page_config(
    page_title="公司内部日报记录系统",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed" # 默认收起侧边栏，因为我们要隐藏它
)

# --- 自定义 CSS 样式 ---
def load_css():
    st.markdown("""
        <style>
        /* 文字渐变动画 - 呼吸效果 */
        @keyframes text-shimmer {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .gradient-text {
            background: linear-gradient(-45deg, #1e3c72, #2a5298, #ff4b4b, #2575fc);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: text-shimmer 6s ease infinite;
        }

        /* 移动端适配 */
        @media (max-width: 768px) {
            .logo-container {
                justify-content: center !important;
                padding-top: 0 !important;
                margin-bottom: 10px !important;
            }
        }
        
        /* 全局背景色 - 动态多色渐变 */
        @keyframes gradient-animation {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #fad0c4, #a18cd1, #fbc2eb, #8fd3f4, #84fab0, #f6d365);
            background-size: 400% 400%;
            animation: gradient-animation 20s ease infinite;
            background-attachment: fixed;
        }
        
        /* 隐藏侧边栏 */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        /* 隐藏侧边栏折叠按钮 */
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }

        /* 隐藏默认 Header (汉堡菜单等) */
        [data-testid="stHeader"] {
            display: none;
        }
        
        /* 主内容区域调整 */
        div.block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max_width: 1200px;
        }

        /* 通用的 Form 美化 */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid rgba(255,255,255,0.6);
            backdrop-filter: blur(10px);
        }

        /* 登录按钮美化 */
        [data-testid="stFormSubmitButton"] > button {
            width: 100%;
            border-radius: 30px;
            height: 50px;
            font-size: 18px;
            background: linear-gradient(to right, #6a11cb 0%, #2575fc 100%);
            border: none;
            box-shadow: 0 5px 15px rgba(37, 117, 252, 0.3);
            transition: transform 0.2s;
            color: white;
        }

        [data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(37, 117, 252, 0.4);
        }

        /* 输入框样式微调 */
        [data-testid="stTextInput"] input {
            border-radius: 10px;
            padding: 12px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
        }

        [data-testid="stTextInput"] input:focus {
            border-color: #2575fc;
            box-shadow: 0 0 0 2px rgba(37, 117, 252, 0.1);
        }
        
        /* 数据表格美化 */
        [data-testid="stDataFrame"] {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        /* Metric 数值显示 */
        [data-testid="stMetricValue"] {
            font-size: 2.4rem !important;
            font-weight: 900 !important;
            color: #1e3c72 !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }

        /* Metric 标签显示 */
        [data-testid="stMetricLabel"] {
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #555 !important;
        }
        
        /* 顶部导航栏容器样式 */
        .top-nav-container {
            background-color: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            padding: 10px 20px;
            border-radius: 50px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.5);
        }
        
        /* 导航按钮通用样式 */
        div[data-testid="stColumn"] button {
            border-radius: 50px !important;
            border: none !important;
            padding: 5px 20px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }

        /* 导航按钮 - 未选中状态 (白色背景，深蓝字) */
        div[data-testid="stColumn"] button[kind="secondary"] {
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: #1e3c72 !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        }
        div[data-testid="stColumn"] button[kind="secondary"]:hover {
            background-color: #fff !important;
            color: #2575fc !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        }

        /* 导航按钮 - 选中状态 (深蓝背景，白字) */
        div[data-testid="stColumn"] button[kind="primary"] {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
            color: white !important;
            box-shadow: 0 4px 10px rgba(30, 60, 114, 0.3) !important;
        }
        div[data-testid="stColumn"] button[kind="primary"]:hover {
            box-shadow: 0 6px 15px rgba(30, 60, 114, 0.4) !important;
        }

        /* 顶部操作按钮（图标按钮）样式 */
        .st-key-change_pwd_btn, .st-key-logout_btn {
            display: inline-block !important;
            width: auto !important;
            margin-left: 5px !important;
        }
        
        /* 退出按钮 - 圆形图标样式 (仿头像风格) */
        .st-key-logout_btn button {
            width: 32px !important; 
            height: 32px !important; 
            border-radius: 50% !important; 
            background: linear-gradient(135deg, #ff512f 0%, #dd2476 100%) !important; /* 红色渐变 */
            color: white !important; 
            display: flex !important;
            align-items: center !important; 
            justify-content: center !important; 
            font-weight: bold !important;
            font-size: 14px !important;
            box-shadow: 0 2px 6px rgba(221, 36, 118, 0.3) !important;
            border: 2px solid white !important;
            padding: 0 !important;
            min-height: 32px !important;
            line-height: 1 !important;
            transition: all 0.3s ease !important;
        }
        
        .st-key-logout_btn button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 4px 10px rgba(221, 36, 118, 0.5) !important;
            background: linear-gradient(135deg, #ff512f 0%, #dd2476 100%) !important; /* 保持背景不变，仅缩放 */
            color: white !important;
        }
        
        /* 移动端适配 - 用户信息和按钮 */
        @media (max-width: 768px) {
            .user-info-container {
                justify-content: center !important;
            }
            .user-btn-container {
                text-align: center !important;
            }
        }

        /* 表格内容自动换行 */
        .stDataFrame td {
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            max-width: 300px !important;
        }
        
        /* 针对 Streamlit 新版 st.dataframe/st.data_editor 的样式 */
        div[data-testid="stDataFrame"] div[role="grid"] div[role="row"] div[role="gridcell"] {
            white-space: pre-wrap !important;
            overflow-wrap: break-word !important;
        }
        
        /* 隐藏输入框右下角的 "Press Enter to submit form" 提示 */
        [data-testid="InputInstructions"] {
            display: none !important;
        }
        
        /* 兼容旧版或不同结构的提示隐藏 */
        .st-key-instruction {
            display: none !important;
        }
        
        /* 隐藏 Streamlit 顶部的工具栏和状态指示器 */
        [data-testid="stHeaderActionElements"],
        [data-testid="stStatusWidget"],
        .stDeployButton {
            display: none !important;
        }
        
        /* 进一步清理顶部空白，如果需要 */
        /* header[data-testid="stHeader"] {
            display: none !important;
        } */
         </style>
     """, unsafe_allow_html=True)

# 初始化数据库
db_manager.init_db()
load_css()

# Session State 初始化
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

def render_logo(centered=False):
    """
    渲染带渐变效果的 Logo
    """
    import os
    import base64
    from PIL import Image

    # 根据 centered 参数调整对齐方式
    justify_content = "center" if centered else "flex-start"
    
    if os.path.exists("logo.png"):
        # 如果存在 logo，使用 CSS mask 实现渐变效果
        try:
            # 获取图片尺寸以保持比例
            with Image.open("logo.png") as img:
                w, h = img.size
                # 假设高度固定为 40px，计算宽度
                target_h = 40
                target_w = int(w * (target_h / h))
            
            with open("logo.png", "rb") as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
            
            st.markdown(f"""
            <div class="logo-container" style="display: flex; align-items: center; justify-content: {justify_content}; height: 100%; padding-top: 10px; margin-bottom: 10px;">
                <div style="
                    width: {target_w}px;
                    height: {target_h}px;
                    background: linear-gradient(-45deg, #1e3c72, #2a5298, #ff4b4b, #2575fc);
                    background-size: 300% 300%;
                    animation: text-shimmer 6s ease infinite;
                    -webkit-mask-image: url(data:image/png;base64,{encoded});
                    mask-image: url(data:image/png;base64,{encoded});
                    -webkit-mask-size: contain;
                    mask-size: contain;
                    -webkit-mask-repeat: no-repeat;
                    mask-repeat: no-repeat;
                    -webkit-mask-position: center;
                    mask-position: center;
                "></div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            # 如果处理图片出错，降级显示普通图片
            st.image("logo.png")
    else:
        st.markdown(f"""
        <div class="logo-container" style="display: flex; align-items: center; justify-content: {justify_content}; height: 100%; padding-top: 10px; margin-bottom: 10px;">
            <h3 class="gradient-text" style="margin: 0; padding: 0; font-weight: 800;">📝 麦田教育日报</h3>
        </div>
        """, unsafe_allow_html=True)

def login_page():
    """
    渲染登录页面
    """
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        render_logo(centered=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1e3c72;'>公司业绩日报系统</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d; margin-bottom: 2rem;'>请使用管理员分配的账号登录</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("用户名", key="login_user", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", key="login_pass", placeholder="请输入密码")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("登 录", type="primary", use_container_width=True)
            
            if submitted:
                if not username or not password:
                    st.error("请输入用户名和密码")
                else:
                    user = db_manager.login_user(username, password)
                    if user:
                        st.session_state['authenticated'] = True
                        st.session_state['user_info'] = user
                        st.toast(f"欢迎回来，{user['full_name']}！", icon="🎉")
                        st.rerun()
                    else:
                        st.error("登录失败，用户名或密码错误。")
        st.markdown('</div>', unsafe_allow_html=True)

def render_admin_page():
    """
    管理员：用户管理页面
    """
    st.markdown("## 👤 用户管理")
    st.caption("管理员权限面板")
    
    # 1. 用户列表展示
    st.markdown("### 📋 用户列表")
    users_df = db_manager.get_all_users()
    
    if not users_df.empty:
        display_cols = ['full_name', 'username', 'department', 'phone', 'is_admin', 'created_at']
        display_cols = [c for c in display_cols if c in users_df.columns]
        
        column_config = {
            "full_name": "姓名",
            "username": "用户名",
            "department": "部门",
            "phone": "电话",
            "is_admin": "管理员?",
            "created_at": "创建时间"
        }
        
        st.dataframe(
            users_df[display_cols], 
            use_container_width=True, 
            hide_index=True,
            column_config=column_config
        )
    else:
        st.info("暂无用户数据。")

    st.markdown("---")

    # 2. 添加新用户表单
    st.markdown("### ➕ 添加新用户")
    with st.container(border=True):
        with st.form("add_user_form", border=False):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("用户名 (唯一)", placeholder="e.g. zhangsan")
                new_password = st.text_input("登录密码", type="password")
                new_phone = st.text_input("联系电话")
            with col2:
                new_fullname = st.text_input("姓名", placeholder="e.g. 张三")
                new_dept = st.text_input("部门", placeholder="e.g. 市场部")
                
            submitted = st.form_submit_button("创建用户", type="primary")
            
            if submitted:
                if not new_username or not new_password or not new_fullname:
                    st.error("用户名、密码、姓名均为必填项！")
                else:
                    success, msg = db_manager.create_user(
                        new_username, new_password, new_fullname, new_dept, new_phone
                    )
                    if success:
                        st.success(f"用户 {new_fullname} ({new_username}) 创建成功！")
                        st.rerun()
                    else:
                        st.error(f"创建失败: {msg}")

    st.markdown("---")

    # 3. 重置用户密码区域
    st.markdown("### 🔐 重置用户密码")
    if not users_df.empty:
        # 获取所有用户名列表
        all_usernames = users_df['username'].tolist()
        
        col_reset1, col_reset2 = st.columns([3, 1])
        with col_reset1:
            # 选择要重置密码的用户
            user_to_reset = st.selectbox("选择要重置密码的用户", all_usernames)
        
        with col_reset2:
            # 增加一些垂直间距，让按钮对齐
            st.write("")
            st.write("")
            if st.button("重置为 123456"):
                if db_manager.admin_reset_password(user_to_reset):
                    st.success(f"✅ 已将用户 {user_to_reset} 的密码重置为: 123456")
                else:
                    st.error("❌ 重置失败，请稍后重试。")

def render_password_page(user):
    """
    修改密码页面
    """
    st.markdown("## 🔐 修改密码")
    
    with st.container(border=True):
        with st.form("change_password_form", border=False):
            current_password = st.text_input("当前密码", type="password")
            new_password = st.text_input("新密码 (至少6位)", type="password")
            confirm_password = st.text_input("确认新密码", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("确认修改", type="primary")
            
            if submitted:
                if current_password != user['password']:
                    st.error("❌ 当前密码错误！")
                elif len(new_password) < 6:
                    st.error("❌ 新密码长度不能少于 6 位！")
                elif new_password != confirm_password:
                    st.error("❌ 两次输入的新密码不一致！")
                else:
                    if db_manager.update_password(user['username'], new_password):
                        st.success("✅ 密码修改成功！请重新登录。")
                        st.session_state['authenticated'] = False
                        st.session_state['user_info'] = None
                        st.rerun()
                    else:
                        st.error("❌ 修改失败，请稍后重试。")

def render_monthly_goal_page(user):
    """
    渲染本月业绩目标页面
    """
    st.markdown("## 🎯 业绩目标管理")
    
    col_year, col_month, col_empty = st.columns([1, 1, 3])
    
    today = get_beijing_today()
    with col_year:
        start_year = 2024
        end_year = today.year + 2
        year_options = sorted(list(set(range(start_year, end_year + 1))))
        try:
            default_index = year_options.index(today.year)
        except ValueError:
            default_index = 0
        selected_year = st.selectbox("年份", year_options, index=default_index)
        
    with col_month:
        month_options = list(range(1, 13))
        selected_month = st.selectbox("月份", month_options, index=today.month - 1)
    
    current_month = f"{selected_year}-{selected_month:02d}"
    st.caption(f"当前查看月份: {current_month}")
    
    st.markdown("### 🏆 全员目标概览")
    
    all_goals_df = db_manager.get_all_monthly_goals(current_month)
    
    if all_goals_df.empty:
        st.info("暂无本月目标数据。")
    else:
        users_df = db_manager.get_all_users()
        if not users_df.empty:
            merged_df = pd.merge(all_goals_df, users_df[['username', 'full_name', 'department']], on='username', how='left')
            merged_df['full_name'] = merged_df['full_name'].fillna(merged_df['username'])
            merged_df['completion_rate'] = merged_df.apply(
                lambda row: (row['completed_amount'] / row['target_amount'] * 100) if row['target_amount'] > 0 else 0, axis=1
            )
            merged_df = merged_df.sort_values(by='completion_rate', ascending=False)
            
            st.dataframe(
                merged_df[['full_name', 'department', 'target_amount', 'completed_amount', 'revenue_amount', 'completion_rate']],
                column_config={
                    "full_name": "姓名",
                    "department": "部门",
                    "target_amount": st.column_config.NumberColumn("目标业绩", format="¥%d"),
                    "completed_amount": st.column_config.NumberColumn("已完成业绩", format="¥%d"),
                    "revenue_amount": st.column_config.NumberColumn("已完成营收", format="¥%d"),
                    "completion_rate": st.column_config.ProgressColumn("完成率", format="%.1f%%", min_value=0, max_value=100),
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("无法获取用户信息，仅显示用户名。")
            st.dataframe(all_goals_df)

    st.markdown("---")

    st.markdown("### 👤 我的目标")
    
    goal_data = db_manager.get_user_monthly_goal(user['username'], current_month)
    target = goal_data['target_amount'] if goal_data else 0.0
    completed = goal_data['completed_amount'] if goal_data else 0.0
    revenue = goal_data['revenue_amount'] if goal_data else 0.0
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("本月目标业绩", f"¥{target:,.0f}")
        delta_val = completed - target
        col2.metric("已完成业绩", f"¥{completed:,.0f}", delta=f"{delta_val:,.0f}" if target > 0 else None)
        col3.metric("已完成营收", f"¥{revenue:,.0f}")
        
        if target > 0:
            progress = min(completed / target, 1.0)
            st.progress(progress, text=f"业绩完成度: {progress*100:.1f}%")
        else:
            st.info("💡 暂未设定本月目标，请点击下方设置。")

        with st.expander("⚙️ 更新今日业绩数据", expanded=True):
            with st.form("update_goal_form"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if target > 0:
                        st.text_input("本月目标业绩 (已锁定)", value=f"¥{target:,.0f}", disabled=True)
                        new_target = target
                    else:
                        new_target = st.number_input("设定本月目标 (¥)", min_value=0.0, step=1000.0)
                with col_b:
                    added_completed = st.number_input("今日新增业绩 (+)", min_value=0.0, step=500.0, help="输入今天新完成的业绩金额，将累加到总额中")
                with col_c:
                    added_revenue = st.number_input("今日新增营收 (+)", min_value=0.0, step=500.0, help="输入今天新完成的营收金额，将累加到总额中")
                
                submitted = st.form_submit_button("提交更新", type="primary")
                if submitted:
                    final_completed = completed + added_completed
                    final_revenue = revenue + added_revenue
                    
                    if (target == 0 and new_target > 0) or added_completed > 0 or added_revenue > 0:
                        success, msg = db_manager.update_user_monthly_goal(
                            user['username'], current_month, new_target, final_completed, final_revenue,
                            added_completed=added_completed, added_revenue=added_revenue
                        )
                        if success:
                            st.toast(f"✅ 更新成功！业绩 +{added_completed}, 营收 +{added_revenue}", icon="🎉")
                            st.rerun()
                        else:
                            st.error(f"更新失败: {msg}")
                    else:
                        st.warning("⚠️ 没有检测到数据变化（请输入新增金额或设定目标）")

    st.markdown("### 📜 提交记录")
    logs_df = db_manager.get_performance_logs(user['username'], current_month)
    
    if not logs_df.empty:
        cols = ['created_at', 'added_completed', 'added_revenue']
        cols = [c for c in cols if c in logs_df.columns]
        
        st.dataframe(
            logs_df[cols],
            column_config={
                "created_at": st.column_config.DatetimeColumn("提交时间", format="YYYY-MM-DD HH:mm:ss"),
                "added_completed": st.column_config.NumberColumn("新增业绩", format="¥%d"),
                "added_revenue": st.column_config.NumberColumn("新增营收", format="¥%d"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无提交记录")

def render_submission_page(user):
    """
    渲染日报填写页面
    """
    st.markdown("## 📝 填写日报")
    st.caption(f"今天是 {get_beijing_today().strftime('%Y年%m月%d日')}")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("姓名", value=user['full_name'], disabled=True)
        with col2:
            report_date = st.date_input("日期", value=get_beijing_today(), format="YYYY/MM/DD")

        current_date_str = report_date.strftime("%Y-%m-%d")
        last_plan, last_date = db_manager.get_previous_plan(user['full_name'], current_date_str)
        
        if last_plan:
            st.info(f"💡  昨日(**{last_date})制定的计划：**\n\n{last_plan}")
        
        # 检查今天是否已经提交过日报（可选优化，目前先只做提交后的状态切换）
        if 'submission_success' not in st.session_state:
            st.session_state['submission_success'] = False
            
        if st.session_state['submission_success']:
            st.success("✅ 日报已成功提交！")
            st.balloons()
            
            st.markdown("""
            <div style="text-align: center; padding: 20px;">
                <p>您已完成今日日报填写。</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("👀 去查看汇总", use_container_width=True):
                    st.session_state['current_page'] = "查看汇总"
                    st.session_state['submission_success'] = False # 重置状态以便下次填写
                    st.rerun()
            with col_btn2:
                if st.button("✍️ 再写一份", use_container_width=True):
                    st.session_state['submission_success'] = False
                    st.rerun()
        else:
            with st.form("report_form", border=False):
                work_content = st.text_area("今日工作内容 (必填)", height=150, placeholder="请输入今日完成的主要工作...")
                next_plan = st.text_area("明日工作计划 (选填)", height=100, placeholder="请输入明天的计划...")
                problems = st.text_area("遇到的困难/需要的协助 (选填)", height=100, placeholder="如有需要协助的事项请填写...")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("提交日报", type="primary", use_container_width=True)
                
                if submitted:
                    if not work_content.strip():
                        st.error("❌ 今日工作内容不能为空！")
                    else:
                        success = db_manager.add_report(
                            employee_name=user['full_name'], 
                            report_date=report_date.strftime("%Y-%m-%d"),
                            work_content=work_content.strip(),
                            next_plan=next_plan.strip(),
                            problems=problems.strip()
                        )
                        if success:
                            st.session_state['submission_success'] = True
                            st.rerun()
                        else:
                            st.error("❌ 提交失败。")

def render_dashboard_page():
    """
    渲染汇总查看页面
    """
    # 页面标题
    st.markdown("## 📊 日报汇总")
    
    user = st.session_state.get('user_info', {})
    if not user:
        st.error("请先登录")
        return

    is_admin = user.get('is_admin', False)
    current_user_fullname = user.get('full_name')

    df = db_manager.get_all_reports(username=current_user_fullname, is_admin=is_admin)
    
    # 顶部统计指标
    if df.empty:
        total_reports = 0
        today_reports = 0
    else:
        total_reports = len(df)
        # 确保列存在，防止报错
        if 'report_date' in df.columns:
            today_reports = len(df[df['report_date'] == get_beijing_today().strftime("%Y-%m-%d")])
        else:
            today_reports = 0
    
    with st.container(border=True):
        m1, m2 = st.columns(2)
        m1.metric("累计日报总数", total_reports)
        m2.metric("今日新增日报", today_reports)

    if df.empty:
        st.info("暂无数据。请先填写日报。")
        return

    st.markdown("---")

    # 筛选区域 - 使用列布局优化
    st.markdown("### 🔍 筛选查询")
    
    with st.container(border=True):
        col_filter_1, col_filter_2, col_filter_3 = st.columns([1, 1, 1])
        
        filtered_df = df.copy()
        
        with col_filter_1:
            all_names = db_manager.get_unique_names(username=current_user_fullname, is_admin=is_admin)
            if len(all_names) > 1:
                selected_name = st.selectbox("员工姓名", ["全部"] + all_names)
            else:
                selected_name = st.selectbox("员工姓名", all_names, disabled=True)
                
            if selected_name != "全部" and selected_name is not None:
                filtered_df = filtered_df[filtered_df['employee_name'] == selected_name]

        with col_filter_2:
            filter_date = st.date_input("选择日期", value=None, help="不选则显示全部日期")
            if filter_date:
                filtered_df = filtered_df[filtered_df['report_date'] == filter_date.strftime("%Y-%m-%d")]
                
        with col_filter_3:
            # 这里可以放导出按钮或者其他操作
            st.markdown(f"<div style='padding-top: 32px; text-align: right;'><b>当前展示: {len(filtered_df)} 条记录</b></div>", unsafe_allow_html=True)

    # 数据表格展示
    cols_to_show = ['report_date', 'employee_name', 'work_content', 'next_plan', 'problems', 'created_at']
    cols_to_show = [c for c in cols_to_show if c in filtered_df.columns]
    
    column_config = {
        "report_date": st.column_config.DateColumn("汇报日期", format="YYYY-MM-DD", width="small"),
        "employee_name": st.column_config.TextColumn("员工姓名", width="small"),
        "work_content": st.column_config.TextColumn("今日工作内容", width="large"),
        "next_plan": st.column_config.TextColumn("明日工作计划", width="medium"),
        "problems": st.column_config.TextColumn("困难/协助", width="medium"),
        "created_at": st.column_config.DatetimeColumn("提交时间", format="YYYY-MM-DD HH:mm:ss")
    }
    
    st.dataframe(
        filtered_df[cols_to_show], 
        use_container_width=True, 
        hide_index=True,
        column_config=column_config,
        height=600  # 增加高度
    )
    
    # 底部导出按钮
    if not filtered_df.empty:
        export_df = filtered_df[cols_to_show].rename(columns={
            "report_date": "汇报日期",
            "employee_name": "员工姓名",
            "work_content": "今日工作内容",
            "next_plan": "明日工作计划",
            "problems": "遇到的困难/协助",
            "created_at": "提交时间"
        })
        
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
        
        col_export_1, col_export_2 = st.columns([4, 1])
        with col_export_2:
            st.download_button(
                label="📥 导出为 Excel (CSV)",
                data=csv_data,
                file_name=f"daily_reports_{date.today()}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

def main():
    """
    主程序逻辑
    """
    if not st.session_state['authenticated']:
        login_page()
        return

    user = st.session_state['user_info']
    
    # --- 顶部导航栏区域 ---
    # st.markdown('<div class="top-nav-container">', unsafe_allow_html=True)
    
    # 调整列比例，给右侧更多空间
    col_logo, col_menu, col_user = st.columns([2, 4, 3], gap="small")
    
    with col_logo:
        render_logo(centered=False)

        
    with col_menu:
        # 菜单选项
        menu_options = ["本月目标", "填写日报", "查看汇总", "修改密码"]
        
        if user.get('is_admin', False):
            menu_options.append("用户管理")
            
        menu_options.append("退出登录")
            
        # 确定当前选中的菜单项
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = "本月目标"
            
        # 使用原生按钮替代 streamlit-option-menu
        # 计算列数
        num_options = len(menu_options)
        
        # 添加垂直间距，让菜单比 Logo 稍低，增加层次感
        st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)
        
        cols = st.columns(num_options)
        
        for i, option in enumerate(menu_options):
            with cols[i]:
                # 判断是否选中
                is_active = (st.session_state['current_page'] == option)
                # 退出登录按钮使用不同的样式（如 secondary）或者保持一致
                btn_type = "primary" if is_active else "secondary"
                
                # 使用 key 来区分不同按钮
                if st.button(option, key=f"nav_btn_{i}", type=btn_type, use_container_width=True):
                    if option == "退出登录":
                        st.session_state['authenticated'] = False
                        st.session_state['user_info'] = None
                        st.session_state['current_page'] = "本月目标" # 重置页面
                        st.rerun()
                    else:
                        st.session_state['current_page'] = option
                        st.rerun()
        
    with col_user:
        # 用户信息 & 按钮组
        # 使用单个列包含所有内容，方便整体对齐
        # 使用 Flexbox 布局让头像、文字和按钮横向排列
        # justify-content: flex-end 让内容靠右
        avatar = user['full_name'][0] if user['full_name'] else "User"
        
        # 将按钮嵌入到同一个 HTML 结构中有点困难，因为按钮是 Streamlit 组件
        # 我们可以尝试使用列布局，但为了移动端不乱套，我们需要更精细的 CSS 控制
        
        # 方案：使用两列，但调整 CSS 让它们在移动端居中且不换行（如果空间够）或者整体居中换行
        c_content = st.container()
        with c_content:
            # 简化为单列，不再显示退出按钮（已移至菜单）
            st.markdown(f"""
            <div class="user-info-container" style="display: flex; align-items: center; justify-content: flex-end; height: 100%; padding-top: 10px;">
                <div style="
                    width: 32px; 
                    height: 32px; 
                    border-radius: 50%; 
                    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); 
                    color: white; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: bold;
                    font-size: 14px;
                    box-shadow: 0 2px 6px rgba(37, 117, 252, 0.3);
                    border: 2px solid white;
                    margin-right: 8px;
                    flex-shrink: 0;
                ">
                    {avatar}
                </div>
                <div style="font-weight: bold; color: #333; font-size: 14px; margin-right: 8px; white-space: nowrap;">{user['full_name']}</div>
                <div style="font-size: 11px; color: #666; background: rgba(0,0,0,0.05); padding: 2px 8px; border-radius: 10px; display: inline-block; white-space: nowrap;">{user.get('department', '员工')}</div>
            </div>
            """, unsafe_allow_html=True)
            
    # st.markdown('</div>', unsafe_allow_html=True)

    # --- 页面内容渲染 (基于 current_page) ---
    current_page = st.session_state.get('current_page', "本月目标")
    
    if current_page == "本月目标":
        render_monthly_goal_page(user)
    elif current_page == "填写日报":
        render_submission_page(user)
    elif current_page == "查看汇总":
        render_dashboard_page()
    elif current_page == "修改密码":
        render_password_page(user)
    elif current_page == "用户管理":
        render_admin_page()
        
    # --- 底部版权信息 ---
    st.markdown("""
    <div style="
        text-align: center; 
        margin-top: 50px; 
        padding-top: 20px;
        border-top: 1px solid rgba(0,0,0,0.05);
        color: #888; 
        font-size: 12px;
    ">
        © 2025 麦田教育 贵州统招专升本 | 公司内部业绩日报记录系统 | 开发团队：产品视觉部
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
