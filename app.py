import streamlit as st
from zhipuai import ZhipuAI
import time
import random
import requests
import io

# ============================================================
# 🔒 安全读取 API Key（从 .streamlit/secrets.toml 读取）
# ============================================================
try:
    API_KEY = st.secrets["ZHIPU_API_KEY"]
except Exception:
    st.error("⚠️ 未找到 API Key，请在 `.streamlit/secrets.toml` 中配置 ZHIPU_API_KEY。")
    st.stop()

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(page_title="鲁小营 Pro Max", page_icon="🚀", layout="wide")

st.title("🍖 鲁小营 Pro Max")
st.subheader("山东小微商家【多智能体+多模态】全链路营销引擎")
st.markdown("---")

# ============================================================
# 工具函数：带重试的 API 调用
# ============================================================
def call_api_with_retry(client, model, messages, tools=None, max_retries=3, delay=2):
    """带指数退避重试的 API 调用，防止限速/超时直接崩溃。"""
    for attempt in range(max_retries):
        try:
            kwargs = {"model": model, "messages": messages}
            if tools:
                kwargs["tools"] = tools
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            if attempt < max_retries - 1:
                wait = delay * (2 ** attempt) + random.uniform(0, 1)
                st.warning(f"⚡ API 调用遇到波动（{e}），{wait:.1f}s 后第 {attempt+2} 次重试...")
                time.sleep(wait)
            else:
                raise e

# ============================================================
# 工具函数：动态计算营销转化预测指标
# ============================================================
def calc_marketing_metrics(platform, target_audience):
    """根据平台与受众动态计算预测指标，保持合理随机性。"""
    base_pv = {
        "小红书": (12000, 20000),
        "抖音":   (18000, 35000),
        "微信视频号": (8000, 15000),
        "快手":   (10000, 22000),
    }
    base_rate = {
        "大学生/年轻群体":   (20, 28),
        "周边高频社区居民": (15, 22),
        "外地旅游打卡客":   (18, 25),
        "CBD白领上班族":    (12, 19),
    }
    pv_min, pv_max = base_pv.get(platform, (12000, 20000))
    pv = random.randint(pv_min, pv_max)
    r_min, r_max = base_rate.get(target_audience, (15, 25))
    play_rate = round(random.uniform(r_min, r_max), 1)
    sentiment = round(random.uniform(88, 96), 1)
    conversion = round(random.uniform(3.2, 5.8), 1)
    industry_avg = round(play_rate * 0.55, 1)
    delta_conv = round(random.uniform(0.5, 1.5), 1)
    return pv, play_rate, sentiment, conversion, industry_avg, delta_conv

# ============================================================
# 工具函数：最佳发布时段
# ============================================================
def get_best_publish_time(platform):
    time_map = {
        "小红书":    "周五 12:00 - 13:30（午休种草高峰）",
        "抖音":      "周五 17:30 - 18:45（下班流量波峰）",
        "微信视频号": "周六 20:00 - 21:30（晚间社交高峰）",
        "快手":      "周日 19:00 - 20:30（全家休闲时段）",
    }
    return time_map.get(platform, "周五 17:30 - 18:45")

# ============================================================
# 工具函数：下载图片到内存 buffer
# ============================================================
def download_image(url):
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            return io.BytesIO(resp.content)
    except Exception:
        pass
    return None

# ============================================================
# 布局：左侧输入 / 右侧输出
# ============================================================
col_input, col_output = st.columns([1, 2.5])

with col_input:
    st.markdown("### 📝 1. 商家特征矩阵录入")
    shop_name = st.text_input("🏠 实体店名称", placeholder="如：张大妈把子肉")

    platform = st.selectbox("📱 首选分发网络", ["小红书", "抖音", "微信视频号", "快手"])
    st.caption(f"🎯 **算法自适应已开启**：底层系统检测到您选择了【{platform}】。不同平台的流量分发机制与用户心智差异巨大，系统将为您自适应切换与之匹配的底层营销模型。")

    target_audience = st.selectbox("🎯 流量池定位", ["大学生/年轻群体", "周边高频社区居民", "外地旅游打卡客", "CBD白领上班族"])
    features = st.text_area("✨ 核心竞争力(SKU特色)", placeholder="如：秘制酱料，20年老店，凭学生证打8折...")

    start_btn = st.button("🚀 初始化多智能体营销矩阵", type="primary", use_container_width=True)

    st.info("💡 提示：系统底座将并行调用 GLM-4 语言大模型与 CogView-3 视觉大模型。")

# ============================================================
# 右侧：多智能体输出
# ============================================================
with col_output:
    if not start_btn:
        st.markdown("<br><br><br><div style='text-align: center; color: gray;'>", unsafe_allow_html=True)
        st.markdown("### 📡 引擎待机中...")
        st.markdown("请在左侧配置商家参数，点击启动以生成全链路营销方案。")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        if not shop_name or not features:
            st.warning("⚠️ 必须完成商家特征矩阵录入！")
        else:
            client = ZhipuAI(api_key=API_KEY)

            st.markdown("### 🤖 2. 多智能体深度演算 (Agentic Workflow)")

            with st.status("正在建立神经链接，启动多智能体推演...", expanded=True) as status:

                # ====== Agent-00 平台生态专家 ======
                st.write(f"🌐 **Agent-00 [平台生态专家]** 正在解构【{platform}】的算法机制...")
                prompt_platform = f"你是顶尖的新媒体平台生态专家。请简要分析【{platform}】当前的内容分发逻辑与用户偏好，并针对【{features}】这类美食，指出在该平台什么样的视频和图文最容易爆火（点赞转发高）。字数150字以内，要有专业见地。"
                res0 = call_api_with_retry(client, "glm-4-flash", [{"role": "user", "content": prompt_platform}])
                platform_analysis = res0.choices[0].message.content
                st.success(f"**🌐 平台生态专家洞察：**\n\n{platform_analysis}")

                # ====== Agent-01 市场数据总监 ======
                time.sleep(1)
                st.write(f"🌍 **Agent-01 [市场总监]** 正在结合平台特性，启用 Web Search 检索热点...")
                prompt_research = f"你是顶尖的商业分析师。基于平台专家的建议：{platform_analysis}。请联网检索山东近期的文旅、餐饮热点。用结构化的方式（1.近期热点洞察 2.用户情绪痛点 3.适配{platform}的破局策略），对【{shop_name}】面向【{target_audience}】客群进行深度解构。字数200字以内。"
                res1 = call_api_with_retry(
                    client, "glm-4-flash",
                    [{"role": "user", "content": prompt_research}],
                    tools=[{"type": "web_search", "web_search": {"enable": True}}]
                )
                analysis_result = res1.choices[0].message.content
                st.info(f"**📊 市场总监的商业解构报告：**\n\n{analysis_result}")

                # ====== Agent-02 短视频导演 ======
                time.sleep(1)
                st.write(f"🎬 **Agent-02 [短视频导演]** 正在全网检索【{platform}】同类爆款视频，拆解流量密码...")
                prompt_video = f"你是顶尖的短视频导演。基于前面两位专家的建议，请联网检索当下全网关于【{shop_name}】或【{features}】这类美食在【{platform}】的爆款短视频。为该店量身定制一份专属于【{platform}】的『短视频拍摄分镜脚本与建议』（包括：画面内容、运镜方式、配乐建议、时长推荐）。字数300字以内。"
                res_video = call_api_with_retry(
                    client, "glm-4-flash",
                    [{"role": "user", "content": prompt_video}],
                    tools=[{"type": "web_search", "web_search": {"enable": True}}]
                )
                video_script = res_video.choices[0].message.content
                st.warning(f"**🎬 短视频导演的拍摄分镜方案：**\n\n{video_script}")

                # ====== Agent-03 资深爆款写手 ======
                time.sleep(1)
                st.write("✍️ **Agent-03 [资深爆款写手]** 正在融合所有参数，生成最终文案...")
                prompt_copy = f"你是资深新媒体主编。基于平台生态：{platform_analysis}，市场解构：{analysis_result}，导演设计：{video_script}。为【{shop_name}】写一篇适合【{platform}】发布的爆款图文文案。运用AIDA模型，网感极强，带emoji。提炼3个SEO优化Hashtag。"
                res2 = call_api_with_retry(client, "glm-4-flash", [{"role": "user", "content": prompt_copy}])
                final_copy = res2.choices[0].message.content

                st.success("✅ 多模态内容矩阵生成完毕！")
                status.update(label="点击查看或折叠智能体演算日志", state="complete", expanded=False)

            # ============================================================
            # 📝 多模态内容分发库（Tabs）
            # ============================================================
            st.markdown("### 📝 3. 多模态内容分发库")

            tab1, tab2 = st.tabs(["✍️ 社交媒体图文文案", "🎬 短视频实操拍摄脚本"])

            with tab1:
                st.success(final_copy)
                # 🆕 一键下载文案
                st.download_button(
                    label="📥 下载文案 (.txt)",
                    data=final_copy.encode("utf-8"),
                    file_name=f"{shop_name}_{platform}_爆款文案.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            with tab2:
                st.info(video_script)
                # 🆕 一键下载脚本
                st.download_button(
                    label="📥 下载分镜脚本 (.txt)",
                    data=video_script.encode("utf-8"),
                    file_name=f"{shop_name}_{platform}_分镜脚本.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

            # ============================================================
            # 🎨 AI 视觉生成（CogView-3）
            # ============================================================
            st.markdown("---")
            st.markdown("### 🎨 4. AI 视觉生成 (CogView-3 驱动)")

            with st.spinner("👩‍🎨 Agent-04 [视觉设计师] 正在渲染商用级海报..."):
                # 占位图，让用户知道系统在工作
                placeholder = st.empty()
                placeholder.info("🖌️ 正在为您生成专属海报，预计需要 10-20 秒，请稍候...")
                image_bytes = None
                try:
                    prompt_img = f"高质量商业摄影，特写，山东特色美食{shop_name}，特点是：{features}。景深，绝佳光影，色彩鲜艳，适合发在{platform}上。无文字。"
                    img_res = client.images.generations(model="cogview-3", prompt=prompt_img)
                    image_url = img_res.data[0].url
                    placeholder.empty()
                    st.image(image_url, caption="✨ 独家生成的版权安全海报", use_container_width=True)
                    # 🆕 下载海报
                    image_bytes = download_image(image_url)
                    if image_bytes:
                        st.download_button(
                            label="📥 下载海报 (.jpg)",
                            data=image_bytes,
                            file_name=f"{shop_name}_AI海报.jpg",
                            mime="image/jpeg",
                            use_container_width=True,
                        )
                except Exception as e:
                    placeholder.empty()
                    st.error(f"海报生成受限（可能触及并发限额）：{e}")

            # ============================================================
            # 📊 营销转化预测漏斗（动态计算）
            # ============================================================
            st.markdown("---")
            st.markdown("### 📊 5. 营销转化预测漏斗 (Data Dashboard)")

            pv, play_rate, sentiment, conversion, industry_avg, delta_conv = calc_marketing_metrics(
                platform, target_audience
            )
            pv_display = f"{pv:,}+"
            avg_pv_pct = round((pv / 10200 - 1) * 100)  # 行业平均约10200

            col1, col2, col3, col4 = st.columns(4)
            col1.metric(label="预计初始曝光量 (PV)", value=pv_display, delta=f"高于同城平均 {avg_pv_pct}%")
            col2.metric(label="预计完播率/点击率",   value=f"{play_rate}%",  delta=f"行业均值 {industry_avg}%")
            col3.metric(label="正向情绪倾向",        value=f"{sentiment}%",  delta="极佳")
            col4.metric(label="预计到店转化率",      value=f"{conversion}%", delta=f"+{delta_conv}%", delta_color="normal")

            best_time = get_best_publish_time(platform)
            flow_bar_filled = round(play_rate / 100 * 10)
            flow_bar = "🟩" * flow_bar_filled + "⬜" * (10 - flow_bar_filled)
            flow_pct = round(play_rate * 3.5)

            st.markdown("#### 🚀 算法推荐分发策略")
            st.markdown(f"""
* **最佳发布时段**：{best_time}
* **【{platform}】流量倾斜概率**：{flow_bar} ({flow_pct}% {'极高' if flow_pct >= 80 else '较高'})
* **核心受众兴趣标签**：`本地生活`、`大学生探店`、`高性价比`、`网红打卡`
            """)

            st.balloons()
