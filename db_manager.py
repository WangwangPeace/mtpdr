import os
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import streamlit as st

# 尝试从环境变量或 Streamlit secrets 获取配置
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    # 备用：尝试从环境变量获取（如果 secrets 不存在）
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_client() -> Client:
    """
    获取 Supabase 客户端实例
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ 缺少 Supabase 配置！请在 .streamlit/secrets.toml 中配置 SUPABASE_URL 和 SUPABASE_KEY。")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    """
    Supabase 初始化
    注意：通常建议在 Supabase Dashboard 的 SQL Editor 中运行建表语句。
    这里仅做简单的连接检查。
    """
    client = get_client()
    if client:
        # 可以尝试简单的查询来验证连接
        pass

def login_user(username, password):
    """
    用户登录 (查 users 表)
    """
    with st.spinner("正在登录..."):
        client = get_client()
        try:
            # 查询 users 表
            response = client.table("users").select("*").eq("username", username).eq("password", password).execute()
            data = response.data
            
            if data and len(data) > 0:
                return data[0] # 返回用户信息字典
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None

def create_user(username, password, full_name, department, phone):
    """
    管理员创建新用户
    """
    with st.spinner("正在创建用户..."):
        client = get_client()
        try:
            # 检查用户名是否已存在
            check = client.table("users").select("username").eq("username", username).execute()
            if check.data and len(check.data) > 0:
                return False, "用户名已存在"

            new_user = {
                "username": username,
                "password": password,
                "full_name": full_name,
                "department": department,
                "phone": phone,
                "is_admin": False
            }
            
            client.table("users").insert(new_user).execute()
            return True, "创建成功"
        except Exception as e:
            print(f"Create user error: {e}")
            return False, str(e)

def update_password(username, new_password):
    """
    用户修改密码
    """
    with st.spinner("正在修改密码..."):
        client = get_client()
        try:
            client.table("users").update({"password": new_password}).eq("username", username).execute()
            return True
        except Exception as e:
            print(f"Update password error: {e}")
            return False

def get_all_users():
    """
    获取所有用户信息 (仅管理员)
    """
    client = get_client()
    try:
        # 查询所有用户，按创建时间倒序
        response = client.table("users").select("*").order("created_at", desc=True).execute()
        data = response.data
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Get all users error: {e}")
        return pd.DataFrame()

def admin_reset_password(username, default_password="123456"):
    """
    管理员重置用户密码
    """
    client = get_client()
    try:
        client.table("users").update({"password": default_password}).eq("username", username).execute()
        return True
    except Exception as e:
        print(f"Admin reset password error: {e}")
        return False

def add_report(employee_name, report_date, work_content, next_plan, problems):
    """
    添加一条新的日报记录到 Supabase
    """
    with st.spinner("正在提交日报..."):
        client = get_client()
        if not client:
            return False
            
        try:
            data = {
                "employee_name": employee_name,
                "report_date": report_date,
                "work_content": work_content,
                "next_plan": next_plan,
                "problems": problems,
                # created_at 会由数据库默认值自动生成，也可以手动传
                # "created_at": datetime.now().isoformat()
            }
            
            response = client.table("reports").insert(data).execute()
            # 检查响应（新版 supabase-py 如果出错通常会抛异常，或者返回错误信息）
            return True
        except Exception as e:
            print(f"Error adding report to Supabase: {e}")
            st.error(f"提交失败: {e}")
            return False

def get_previous_plan(employee_name, current_date):
    """
    获取最近一次日报的“明日计划”
    逻辑：查找该员工在 current_date 之前提交的最后一条日报
    """
    client = get_client()
    try:
        # 查找该员工，且日期小于当前日期的记录，按日期倒序排列，取第一条
        response = (
            client.table("reports")
            .select("next_plan, report_date")
            .eq("employee_name", employee_name)
            .lt("report_date", current_date)
            .order("report_date", desc=True)
            .limit(1)
            .execute()
        )
            
        data = response.data
        if data and len(data) > 0:
            return data[0].get('next_plan', ''), data[0].get('report_date', '')
        return None, None
    except Exception as e:
        print(f"Get previous plan error: {e}")
        return None, None

def get_all_reports(username=None, is_admin=False):
    """
    获取日报记录
    - 返回所有记录 (所有人可见)
      
    参数:
    username (str): (已弃用，保留参数兼容)
    is_admin (bool): (已弃用，保留参数兼容)
    """
    with st.spinner("正在加载日报记录..."):
        client = get_client()
        if not client:
            return pd.DataFrame()
            
        try:
            query = client.table("reports").select("*").order("report_date", desc=True).order("created_at", desc=True)
            
            # 以前只有管理员能看所有人，现在所有人都能看所有人，所以不再过滤
            # if not is_admin and username:
            #     query = query.eq("employee_name", username)
                
            response = query.execute()
            
            data = response.data
            if not data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            print(f"Error reading reports from Supabase: {e}")
            st.error(f"读取数据失败: {e}")
            return pd.DataFrame()

def get_latest_previous_report(employee_name, current_date):
    """
    获取指定日期之前的最近一份日报，用于提取“明日计划”
    """
    client = get_client()
    if not client:
        return None
        
    try:
        # 查询日期小于 current_date 的最近一条记录
        response = client.table("reports").select("*")\
            .eq("employee_name", employee_name)\
            .lt("report_date", current_date)\
            .order("report_date", desc=True)\
            .limit(1)\
            .execute()
            
        data = response.data
        if data and len(data) > 0:
            return data[0]
        return None
    except Exception as e:
        print(f"Error getting previous report: {e}")
        return None

def get_unique_names(username=None, is_admin=False):
    """
    获取筛选用的姓名列表
    - 返回所有唯一姓名 (所有人可见)
    """
    # 以前普通用户只能看自己，现在所有人都能看所有人
    # if not is_admin and username:
    #     return [username]

    with st.spinner("正在加载筛选列表..."):
        client = get_client()
        if not client:
            return []
            
        try:
            # 由于 supabase-py 可能不支持直接的 distinct 查询，
            # 我们可以查询所有姓名然后在 Python 端去重，或者使用 rpc (如果写了 SQL function)
            # 这里为了简单，先查询 employee_name 字段
            response = client.table("reports").select("employee_name").execute()
            data = response.data
            
            if not data:
                return []
                
            names = sorted(list(set(item['employee_name'] for item in data)))
            return names
        except Exception as e:
            print(f"Error getting names from Supabase: {e}")
            return []

def get_user_monthly_goal(username, month_str):
    """
    获取用户某月的业绩目标和完成情况
    username: 登录用户名 (非全名，保持唯一性)
    month_str: 'YYYY-MM'
    """
    with st.spinner("正在加载目标数据..."):
        client = get_client()
        try:
            response = client.table("monthly_goals").select("*")\
                .eq("username", username)\
                .eq("month", month_str)\
                .execute()
            
            data = response.data
            if data and len(data) > 0:
                return data[0]
            return None
        except Exception as e:
            print(f"Error getting monthly goal: {e}")
            return None

def get_all_monthly_goals(month_str):
    """
    获取某月所有用户的业绩目标和完成情况
    month_str: 'YYYY-MM'
    """
    with st.spinner("正在加载全员目标..."):
        client = get_client()
        try:
            # 同时关联 users 表获取 full_name 会更好，但 Supabase py 客户端联表查询可能比较麻烦
            # 这里假设 monthly_goals 表里只有 username，我们需要结合 users 表来显示姓名
            # 或者先简单点，直接返回 monthly_goals，在 app.py 里再匹配姓名
            
            response = client.table("monthly_goals").select("*").eq("month", month_str).execute()
            data = response.data
            
            if not data:
                return pd.DataFrame()
                
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting all monthly goals: {e}")
            return pd.DataFrame()

def update_user_monthly_goal(username, month_str, target_amount, completed_amount, revenue_amount, added_completed=0, added_revenue=0):
    """
    更新或创建月度业绩目标，并记录日志
    """
    with st.spinner("正在更新目标..."):
        client = get_client()
        try:
            # 1. 更新 monthly_goals
            data = {
                "username": username,
                "month": month_str,
                "target_amount": target_amount,
                "completed_amount": completed_amount,
                "revenue_amount": revenue_amount,
                "updated_at": datetime.now().isoformat()
            }
            
            # on_conflict 对应 unique 约束的列
            client.table("monthly_goals").upsert(data, on_conflict="username, month").execute()
            
            # 2. 插入 performance_logs (如果增量大于0)
            if added_completed > 0 or added_revenue > 0:
                log_data = {
                    "username": username,
                    "month": month_str,
                    "added_completed": added_completed,
                    "added_revenue": added_revenue,
                    # created_at 由数据库默认生成
                }
                client.table("performance_logs").insert(log_data).execute()
                
            return True, "更新成功"
        except Exception as e:
            print(f"Error updating monthly goal: {e}")
            return False, str(e)

def get_performance_logs(username, month_str):
    """
    获取某月的业绩提交记录
    """
    with st.spinner("正在加载提交记录..."):
        client = get_client()
        try:
            response = client.table("performance_logs").select("*")\
                .eq("username", username)\
                .eq("month", month_str)\
                .order("created_at", desc=True)\
                .execute()
            
            data = response.data
            if not data:
                return pd.DataFrame()
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting performance logs: {e}")
            return pd.DataFrame()

# --- 附录：Supabase 建表 SQL ---
# 请在 Supabase Dashboard -> SQL Editor 中运行以下语句：
"""
-- 1. 启用 RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- 2. 创建允许匿名访问的策略 (适用于当前使用 anon key 的场景)
-- 允许所有操作 (增删改查)
CREATE POLICY "Allow all access for public" ON users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all access for public" ON reports FOR ALL USING (true) WITH CHECK (true);

-- 3. 月度业绩目标表
CREATE TABLE monthly_goals (
  id bigint generated by default as identity primary key,
  username text not null,
  month text not null, -- 格式 YYYY-MM
  target_amount double precision default 0,
  completed_amount double precision default 0,
  revenue_amount double precision default 0,
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  unique(username, month)
);
ALTER TABLE monthly_goals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access for public" ON monthly_goals FOR ALL USING (true) WITH CHECK (true);

-- 4. 业绩提交日志表
CREATE TABLE performance_logs (
  id bigint generated by default as identity primary key,
  username text not null,
  month text not null, -- 格式 YYYY-MM
  added_completed double precision default 0,
  added_revenue double precision default 0,
  created_at timestamp with time zone default timezone('utc'::text, now())
);
ALTER TABLE performance_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all access for public" ON performance_logs FOR ALL USING (true) WITH CHECK (true);
"""
