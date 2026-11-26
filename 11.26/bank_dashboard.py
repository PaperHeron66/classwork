"""银行理财产品销售看板 —— Power BI 案例的 Python 迁移版。

原报告（案例结果.pbix）包含 1 个页面、6 个视觉对象：
  1. KPI 卡：MTD 销售额 + MTD 销售目标达成率（DAX: SUM(购买金额)/25000000）
  2. 分解树：按 家庭年收入 → 年龄 → 学历 → 性别 拆解销售额占比
  3. 簇状柱形图：不同理财品类的销售占比（品类 × 风险等级）
  4. 柱线组合图：各品类客单价（平均购买金额）与期限均值
  5. 词云：选择本行的原因
  6. 词云：购买目的（原报告标题写作“选择产品原因”，数据来源为“购买目的”）

本脚本用 pandas 重建数据模型与度量，用 Plotly 重建全部视觉对象，
输出一个不依赖网络、可直接双击打开的交互式 HTML 看板。

用法：
    python bank_dashboard.py
    python bank_dashboard.py --excel "路径/银行案例数据 - 学员用.xlsx" --output "路径/看板.html"
"""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import get_plotlyjs
from plotly.subplots import make_subplots
from wordcloud import WordCloud

# ---------------------------------------------------------------------------
# 业务参数（来自“业务描述”表与 DAX 度量）
# ---------------------------------------------------------------------------
TARGET_AMOUNT = 25_000_000  # 本月销售目标：2500 万元
CURRENT_DAY = 29            # 数据截止当月第 29 天
DAYS_IN_MONTH = 31          # 假设当月 31 天

ROOT = Path(__file__).resolve().parent
_EXCEL_NAME = "银行案例数据 - 学员用.xlsx"
# 源 Excel 放在上一级项目目录；若与脚本同目录也能找到
DEFAULT_EXCEL = ROOT / _EXCEL_NAME if (ROOT / _EXCEL_NAME).exists() else ROOT.parent / _EXCEL_NAME
DEFAULT_OUTPUT = ROOT / "银行销售看板.html"

INCOME_ORDER = ["5万以下", "5万-10万", "10万-20万", "20万-50万", "50万-100万", "100万以上"]
AGE_ORDER = ["18-30岁", "31-40岁", "41-50岁", "50-60岁", "61岁以上"]
EDU_ORDER = ["初中及初中以下", "高中", "大学专科", "大学本科", "硕士", "博士及以上"]
RISK_CODE_ORDER = ["S1", "S2", "S3"]

# Solar 主题（原报告主题）的暖色系
C_GOLD = "#FFAC00"
C_ORANGE = "#E87200"
C_RED = "#D3004C"
C_PINK = "#EF008C"
C_INK = "#3B2418"
C_MUTED = "#8A7365"
FONT_FAMILY = "Microsoft YaHei, SimHei, PingFang SC, sans-serif"

DECOMP_OPTIONS = {
    "收入 → 年龄 → 学历 → 性别（原报告）": ["家庭年收入", "年龄", "学历名称", "性别"],
    "年龄 → 收入 → 学历 → 性别": ["年龄", "家庭年收入", "学历名称", "性别"],
    "学历 → 收入 → 年龄 → 性别": ["学历名称", "家庭年收入", "年龄", "性别"],
    "风险偏好 → 收入 → 品类": ["风险说明", "家庭年收入", "品类名称"],
}


def find_font() -> str | None:
    """优先使用微软雅黑，保证词云里的中文正常显示。"""
    for candidate in (
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ):
        if Path(candidate).exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# 数据模型：读取星型模型并完成三张码表的关联
# ---------------------------------------------------------------------------
def load_model(excel_path: Path) -> tuple[pd.DataFrame, dict[str, str], list[str]]:
    sales = pd.read_excel(excel_path, sheet_name="销售数据")
    risk = pd.read_excel(excel_path, sheet_name="风险偏好说明表")
    category = pd.read_excel(excel_path, sheet_name="品类说明表")
    education = pd.read_excel(excel_path, sheet_name="学历说明表")

    df = (
        sales.merge(risk, on="风险编号", how="left")
        .merge(category, on="品类编号", how="left")
        .merge(education, on="学历编号", how="left")
    )

    risk_labels = risk.set_index("风险编号").loc[RISK_CODE_ORDER, "风险说明"].to_dict()
    category_order = category.sort_values("品类编号")["品类名称"].tolist()

    # 有序分类：让图表顺序遵循业务含义，而不是中文拼音排序
    df["家庭年收入"] = pd.Categorical(df["家庭年收入"], categories=INCOME_ORDER, ordered=True)
    df["年龄"] = pd.Categorical(df["年龄"], categories=AGE_ORDER, ordered=True)
    df["学历名称"] = pd.Categorical(df["学历名称"], categories=EDU_ORDER, ordered=True)
    df["风险说明"] = pd.Categorical(
        df["风险说明"], categories=[risk_labels[c] for c in RISK_CODE_ORDER], ordered=True
    )
    df["品类名称"] = pd.Categorical(df["品类名称"], categories=category_order, ordered=True)
    df["收益率"] = df["收益"] / df["购买金额"]

    return df, risk_labels, category_order


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    total = int(df["购买金额"].sum())
    gap = max(TARGET_AMOUNT - total, 0)
    return {
        "total": total,
        "target": TARGET_AMOUNT,
        "achievement": total / TARGET_AMOUNT,
        "gap": gap,
        "current_daily": total / CURRENT_DAY,
        "required_daily": gap / (DAYS_IN_MONTH - CURRENT_DAY),
        "orders": len(df),
    }


def fmt_money(value: float) -> str:
    return f"¥{value:,.0f}"


# ---------------------------------------------------------------------------
# 视觉对象 2：分解树的 Plotly 等价实现（交互式 Sunburst）
# ---------------------------------------------------------------------------
def build_sunburst(df: pd.DataFrame, levels: list[str]) -> dict:
    total = int(df["购买金额"].sum())
    ids = ["root"]
    labels = ["全部客群"]
    parents = [""]
    values = [total]
    texts = [f"全部客群<br>销售额：{fmt_money(total)}<br>占总额：100.0%"]

    for depth in range(1, len(levels) + 1):
        series = df.groupby(levels[:depth], observed=True)["购买金额"].sum()
        for key, value in series.items():
            parts = key if isinstance(key, tuple) else (key,)
            path = " / ".join(str(part) for part in parts)
            parent = "root" if depth == 1 else " / ".join(str(part) for part in parts[:-1])
            ids.append(path)
            labels.append(str(parts[-1]))
            parents.append(parent)
            values.append(int(value))
            texts.append(
                f"{path}<br>销售额：{fmt_money(value)}<br>占总额：{value / total * 100:.1f}%"
            )

    palette = [C_GOLD, C_ORANGE, C_RED, C_PINK, "#9B0065", "#7D0033"]
    colors = [C_GOLD]
    for item_id in ids[1:]:
        depth = item_id.count(" / ") + 1
        colors.append(palette[(depth - 1) % len(palette)])

    return {"ids": ids, "labels": labels, "parents": parents, "values": values,
            "text": texts, "colors": colors}


def build_decomp_data(df: pd.DataFrame) -> dict[str, dict]:
    return {name: build_sunburst(df, levels) for name, levels in DECOMP_OPTIONS.items()}


# ---------------------------------------------------------------------------
# 视觉对象 3：不同理财品类的销售占比（品类 × 风险）
# ---------------------------------------------------------------------------
def chart_category_risk(df: pd.DataFrame, risk_labels: dict[str, str],
                        category_order: list[str], total: int) -> go.Figure:
    pivot = df.pivot_table(
        index="品类名称", columns="风险说明", values="购买金额",
        aggfunc="sum", observed=True, fill_value=0,
    ).reindex(category_order)

    share = pivot.sum(axis=1) / total * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for code, color in zip(RISK_CODE_ORDER, [C_GOLD, C_ORANGE, C_RED]):
        label = risk_labels[code]
        if label not in pivot.columns:
            continue
        fig.add_bar(
            x=list(pivot.index), y=pivot[label].tolist(), name=label,
            marker_color=color,
            hovertemplate="%{x}<br>" + label + "：¥%{y:,.0f}<extra></extra>",
        )
    fig.add_scatter(
        x=list(pivot.index), y=share.round(2).tolist(), name="品类占总额比例",
        mode="lines+markers", line=dict(color=C_INK, width=2, dash="dot"),
        marker=dict(size=6, color=C_INK), yaxis="y2",
        hovertemplate="%{x}<br>总计占比：%{y:.1f}%<extra></extra>",
    )
    fig.update_layout(
        barmode="group", height=250, margin=dict(t=30, r=10, b=10, l=10),
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
        font=dict(family=FONT_FAMILY, size=11, color=C_INK),
    )
    fig.update_yaxes(title_text="销售额（元）", secondary_y=False,
                     gridcolor="#F0EAE5", zeroline=False)
    fig.update_yaxes(title_text="占比（%）", secondary_y=True, showgrid=False,
                     range=[0, float(share.max() * 1.35)], zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# 视觉对象 4：客单及期限均值分布
# ---------------------------------------------------------------------------
def chart_combo(df: pd.DataFrame, category_order: list[str]) -> go.Figure:
    grouped = df.groupby("品类名称", observed=True).agg(
        客单=("购买金额", "mean"), 期限均值=("期限", "mean")
    ).reindex(category_order)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(
        x=list(grouped.index), y=grouped["客单"].round(0).tolist(), name="客单价（平均购买金额）",
        marker_color=C_ORANGE,
        hovertemplate="%{x}<br>客单价：¥%{y:,.0f}<extra></extra>",
    )
    fig.add_scatter(
        x=list(grouped.index), y=grouped["期限均值"].round(2).tolist(), name="期限均值（年）",
        mode="lines+markers", line=dict(color=C_RED, width=3),
        marker=dict(size=8, color=C_RED), yaxis="y2",
        hovertemplate="%{x}<br>期限均值：%{y:.2f} 年<extra></extra>",
    )
    fig.update_layout(
        height=250, margin=dict(t=30, r=10, b=10, l=10),
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
        font=dict(family=FONT_FAMILY, size=11, color=C_INK),
    )
    fig.update_yaxes(title_text="客单价（元）", secondary_y=False,
                     gridcolor="#F0EAE5", zeroline=False)
    fig.update_yaxes(title_text="期限（年）", secondary_y=True, showgrid=False,
                     range=[0, 6], zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# 视觉对象 5 / 6：词云
# ---------------------------------------------------------------------------
def wordcloud_data_uri(frequencies: pd.Series, colormap: str) -> str:
    wc = WordCloud(
        font_path=find_font(), width=760, height=300,
        background_color=None, mode="RGBA", colormap=colormap,
        prefer_horizontal=0.88, relative_scaling=0.55,
        max_words=30, margin=5, random_state=11,
    )
    wc.generate_from_frequencies({str(k): int(v) for k, v in frequencies.items()})
    buffer = io.BytesIO()
    wc.to_image().save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------
# 生成自包含 HTML 看板
# ---------------------------------------------------------------------------
def render_dashboard(
    df: pd.DataFrame,
    kpi: dict[str, float],
    risk_labels: dict[str, str],
    category_order: list[str],
    output: Path,
) -> None:
    decomp_data = build_decomp_data(df)
    default_key = next(iter(decomp_data))
    decomp_layout = dict(
        height=248, margin=dict(t=4, b=4, l=4, r=4),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, size=11, color=C_INK),
        uniformtext=dict(minsize=9, mode="hide"), showlegend=False,
    )
    chart_config = {"displayModeBar": False, "responsive": True}
    chart_html = {
        "chart_category": pio.to_html(
            chart_category_risk(df, risk_labels, category_order, kpi["total"]),
            full_html=False, include_plotlyjs=False,
            div_id="chart_category", config=chart_config,
        ),
        "chart_combo": pio.to_html(
            chart_combo(df, category_order),
            full_html=False, include_plotlyjs=False,
            div_id="chart_combo", config=chart_config,
        ),
    }

    reason_freq = df["选择本行的原因"].value_counts()
    purpose_freq = df["购买目的"].value_counts()
    reason_wc = wordcloud_data_uri(reason_freq, "autumn")
    purpose_wc = wordcloud_data_uri(purpose_freq, "magma")

    achievement_pct = kpi["achievement"] * 100
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>银行理财产品销售看板 · Python 迁移版</title>
<script>{get_plotlyjs()}</script>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #F7F4F1; color: {C_INK}; font-family: {FONT_FAMILY}; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; padding: 14px 16px 26px; }}
  header {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
            padding: 4px 4px 14px; }}
  header h1 {{ margin: 0; font-size: 21px; letter-spacing: .5px; }}
  header h1 span {{ color: {C_ORANGE}; }}
  .tags {{ display: flex; gap: 8px; flex-wrap: wrap; font-size: 12px; color: {C_MUTED}; }}
  .tag {{ background: #fff; border: 1px solid #EFE4DC; border-radius: 999px; padding: 5px 11px; }}
  .card {{ background: #fff; border: 1px solid #F0E7E0; border-radius: 12px;
           box-shadow: 0 2px 12px rgba(90, 45, 10, .06); padding: 10px 12px; }}
  .card h3 {{ margin: 2px 2px 6px; font-size: 14px; font-weight: 600; }}
  .card h3::before {{ content: ''; display: inline-block; width: 4px; height: 14px;
                      background: {C_ORANGE}; border-radius: 2px; margin-right: 8px;
                      vertical-align: -2px; }}
  .top {{ display: grid; grid-template-columns: 384px 1fr; gap: 10px; }}
  .kpi-panel {{ display: flex; flex-direction: column; gap: 10px; }}
  .kpi {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }}
  .kpi .label {{ font-size: 12px; color: {C_MUTED}; }}
  .kpi .value {{ font-size: 27px; font-weight: 700; color: {C_ORANGE}; margin: 2px 0; }}
  .kpi .value.red {{ color: {C_RED}; }}
  .kpi .sub {{ font-size: 11px; color: {C_MUTED}; }}
  .progress {{ height: 7px; background: #F5EBE4; border-radius: 4px; overflow: hidden; margin-top: 5px; }}
  .progress i {{ display: block; height: 100%; width: {achievement_pct:.2f}%;
                 background: linear-gradient(90deg, {C_GOLD}, {C_RED}); }}
  .decomp-head {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; }}
  select {{ font-family: {FONT_FAMILY}; font-size: 11px; color: {C_INK}; background: #FFF8F2;
            border: 1px solid #EFD8C8; border-radius: 6px; padding: 4px 7px; }}
  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }}
  .wc {{ text-align: center; }}
  .wc img {{ width: 100%; max-height: 318px; object-fit: contain; display: block; }}
  footer {{ margin-top: 14px; font-size: 11px; color: {C_MUTED}; text-align: right; }}
  @media (max-width: 900px) {{
    .top, .grid2 {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>银行理财产品<span>销售看板</span> · Python 迁移版</h1>
    <div class="tags">
      <div class="tag">月度目标 {fmt_money(kpi['target'])}</div>
      <div class="tag">数据截止：当月第 {CURRENT_DAY} / {DAYS_IN_MONTH} 天</div>
      <div class="tag">{kpi['orders']} 笔销售记录</div>
    </div>
  </header>

  <section class="top">
    <div class="kpi-panel">
      <div class="card kpi">
        <div class="label">MTD 销售额（SUM 购买金额）</div>
        <div class="value">{fmt_money(kpi['total'])}</div>
        <div class="sub">约 {kpi['total'] / 10000:,.1f} 万元 · 当前日均 {fmt_money(kpi['current_daily'])}</div>
      </div>
      <div class="card kpi">
        <div class="label">MTD 销售目标达成率（原 DAX 度量）</div>
        <div class="value red">{achievement_pct:.2f}%</div>
        <div class="progress"><i></i></div>
        <div class="sub">SUM(购买金额) / 25,000,000</div>
      </div>
      <div class="card kpi">
        <div class="label">目标缺口与追赶节奏</div>
        <div class="value">{fmt_money(kpi['gap'])}</div>
        <div class="sub">剩余 {DAYS_IN_MONTH - CURRENT_DAY} 天，日均需完成 {fmt_money(kpi['required_daily'])}</div>
      </div>
    </div>
    <div class="card">
      <div class="decomp-head">
        <h3>客群销售额分解树（占总计比例）</h3>
        <select id="decompSelect">
          {''.join(f'<option value="{name}">{name}</option>' for name in decomp_data)}
        </select>
      </div>
      <div id="decomp"></div>
    </div>
  </section>

  <section class="grid2">
    <div class="card"><h3>不同理财品类的销售占比</h3>{chart_html['chart_category']}</div>
    <div class="card"><h3>客单及期限均值分布</h3>{chart_html['chart_combo']}</div>
  </section>

  <section class="grid2">
    <div class="card wc"><h3>选择本行的原因</h3><img src="{reason_wc}" alt="选择本行的原因词云"></div>
    <div class="card wc"><h3>选择产品原因（购买目的）</h3><img src="{purpose_wc}" alt="购买目的词云"></div>
  </section>

  <footer>数据来源：银行案例数据 - 学员用.xlsx ｜ 由 bank_dashboard.py 生成（pandas + Plotly + WordCloud）</footer>
</div>

<script>
const DECOMP = {json.dumps(decomp_data, ensure_ascii=False)};
const DECOMP_LAYOUT = {json.dumps(decomp_layout, ensure_ascii=False)};
function renderDecomp(key) {{
  const d = DECOMP[key];
  Plotly.react('decomp', [{{
    type: 'sunburst', ids: d.ids, labels: d.labels, parents: d.parents,
    values: d.values, text: d.text, branchvalues: 'total',
    textinfo: 'label+percent root', insidetextorientation: 'radial',
    hovertemplate: '%{{text}}<extra></extra>',
    marker: {{ colors: d.colors, line: {{ color: '#ffffff', width: 1 }} }}
  }}], DECOMP_LAYOUT, {{ displayModeBar: false, responsive: true }});
}}
document.getElementById('decompSelect').addEventListener('change', function(e) {{
  renderDecomp(e.target.value);
}});
renderDecomp({json.dumps(default_key, ensure_ascii=False)});
</script>
</body>
</html>"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="把银行案例 Power BI 看板迁移为 Python 实现")
    parser.add_argument("--excel", type=Path, default=DEFAULT_EXCEL, help="源 Excel 路径")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="输出 HTML 路径")
    args = parser.parse_args()

    if not args.excel.exists():
        parser.error(f"找不到源文件：{args.excel}")

    df, risk_labels, category_order = load_model(args.excel)
    kpi = compute_kpis(df)
    render_dashboard(df, kpi, risk_labels, category_order, args.output)

    print("=" * 52)
    print("银行理财产品销售看板 · Python 迁移版")
    print("=" * 52)
    print(f"销售笔数        : {kpi['orders']:,}")
    print(f"MTD 销售额      : {fmt_money(kpi['total'])}（{kpi['total'] / 10000:,.1f} 万元）")
    print(f"月度目标        : {fmt_money(kpi['target'])}")
    print(f"MTD 目标达成率  : {kpi['achievement'] * 100:.2f}%")
    print(f"目标缺口        : {fmt_money(kpi['gap'])}")
    print(f"当前日均        : {fmt_money(kpi['current_daily'])}")
    print(f"剩余日均需完成  : {fmt_money(kpi['required_daily'])}")
    by_category = df.groupby("品类名称", observed=True)["购买金额"].sum().sort_values(ascending=False)
    print("品类 TOP3       : " + "、".join(
        f"{name} {fmt_money(value)}" for name, value in by_category.head(3).items()
    ))
    print(f"看板已生成      : {args.output.resolve()}")
    print("=" * 52)


if __name__ == "__main__":
    main()
