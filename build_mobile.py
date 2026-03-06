import re

md_files = {
    '1-3': None,  # 1-3話はHTMLから抽出
    '4-8': '脚本_第四話〜第八話.md'
}

# 1-3話のデータは既存HTMLから取得するが、MDソースがないので直接定義
# 既存の sendagaya_scripts_tategaki.html を読んでセリフを抽出する
html_file = 'sendagaya_scripts_tategaki.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# MD の 4-8話を読む
with open('脚本_第四話〜第八話.md', 'r', encoding='utf-8') as f:
    md = f.read()

# エピソードのメタデータ
episodes_meta = [
    {
        'num': '第一話',
        'title': '別れ話のプロンプト',
        'theme': 'AIに別れ話を書かせたら、ビジネスメールになった件',
        'location': 'カフェ・テーブル席（昼）',
        'duration': '約2分',
        'cast': [
            ('タク', '29', '吉川 慶'),
            ('カイト', '21', '小久保 宏紀'),
            ('リュウ', '33', '五十嵐 諒'),
        ]
    },
    {
        'num': '第二話',
        'title': '解約ボタンはダンジョンの奥深く',
        'theme': 'サブスク貧乏と「解約忘れ」の罠',
        'location': 'カフェ・テーブル席（昼）',
        'duration': '約2分',
        'cast': [
            ('ソウタ', '27', '中塚 智'),
            ('カナデ', '26', '島田 和奏'),
            ('セトカ', '22', '寺崎 ひな'),
        ]
    },
    {
        'num': '第三話',
        'title': '他人の幸せのパトロン',
        'theme': '結婚式のご祝儀3万円、高すぎ問題',
        'location': 'カフェ・テーブル席（昼）',
        'duration': '約2分',
        'cast': [
            ('タク', '29', '吉川 慶'),
            ('ユイ', '18', '田中 希和'),
            ('リュウ', '33', '五十嵐 諒'),
        ]
    },
    {
        'num': '第四話',
        'title': 'PayPayの功罪',
        'theme': '奢りたいのにPayPayが割り勘ボタン光らせてくる',
        'location': 'バー・テーブル席（夜）',
        'duration': '約2分',
        'cast': [
            ('カイト', '21', '小久保 宏紀'),
            ('タク', '29', '吉川 慶'),
            ('アヤナ', '27', '谷口 彩菜'),
        ]
    },
    {
        'num': '第五話',
        'title': 'メルカリの哲学',
        'theme': '他人の使用済みワイヤレスイヤホン、買える？',
        'location': 'カフェ・テーブル席（昼）',
        'duration': '約2分',
        'cast': [
            ('アヤナ', '27', '谷口 彩菜'),
            ('セトカ', '22', '寺崎 ひな'),
            ('カナデ', '26', '島田 和奏'),
        ]
    },
    {
        'num': '第六話',
        'title': '元カレのストーリーズ',
        'theme': '元カレの新しい彼女のインスタ、なんで見ちゃうんだろう',
        'location': 'カフェ・テーブル席（昼）',
        'duration': '約2分',
        'cast': [
            ('カナデ', '26', '島田 和奏'),
            ('アヤナ', '27', '谷口 彩菜'),
            ('ユイ', '18', '田中 希和'),
        ]
    },
]

# HTMLからセリフを抽出する関数
def extract_lines_from_html(html_content, start_marker, end_marker):
    start = html_content.find(start_marker)
    end = html_content.find(end_marker, start + 1) if end_marker else len(html_content)
    if start == -1:
        return []
    chunk = html_content[start:end]
    
    lines = []
    # serif-block からキャラ名とセリフを抽出
    blocks = re.findall(r'<div class="character-name">(.*?)</div>\s*<div class="serif">(.*?)</div>', chunk, re.DOTALL)
    # ト書きも抽出
    togaki = re.findall(r'<span class="t">(.*?)</span>', chunk)
    
    # 順番を保持するため、位置ベースで再構築
    items = []
    for m in re.finditer(r'<div class="character-name">(.*?)</div>\s*<div class="serif">(.*?)</div>', chunk, re.DOTALL):
        name = m.group(1).strip()
        serif = m.group(2).strip()
        # HTMLタグを除去
        serif = re.sub(r'<[^>]+>', '', serif)
        items.append((m.start(), 'serif', name, serif))
    
    for m in re.finditer(r'<span class="t">(.*?)</span>', chunk):
        text = m.group(1).strip()
        if text.startswith('（') and text.endswith('）'):
            items.append((m.start(), 'togaki', text, ''))
    
    # p class="s" からト書き付きセリフも
    for m in re.finditer(r'<p class="s"><span class="n">(.*?)</span><span\s*class="t">(.*?)</span>(.*?)</p>', chunk, re.DOTALL):
        name = m.group(1).strip()
        togaki_text = m.group(2).strip()
        serif_text = m.group(3).strip()
        serif_text = re.sub(r'<[^>]+>', '', serif_text)
        items.append((m.start(), 'serif_with_togaki', name, togaki_text + serif_text))
    
    items.sort(key=lambda x: x[0])
    return items

# MDからセリフを抽出
def extract_lines_from_md(md_text):
    items = []
    for line in md_text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('（') and line.endswith('）'):
            items.append(('togaki', line, ''))
        elif '「' in line:
            name, rest = line.split('「', 1)
            name = name.strip()
            serif = '「' + rest
            items.append(('serif', name, serif))
    return items

# 1-3話のセリフをHTMLから抽出
ep1_lines = extract_lines_from_html(html, '<!-- ① 台本', '<!-- ② INFO')
ep2_lines = extract_lines_from_html(html, '<!-- ② 台本', '<!-- ③ INFO')
ep3_lines = extract_lines_from_html(html, '<!-- ③ 台本', '<!-- ④ INFO')

# 4-8話のセリフをMDから抽出
md_blocks = re.split(r'## 第([四五六七八])話「(.*?)」', md)
md_blocks = md_blocks[1:]

skip = ['四', '六']
md_episodes = {}
for i in range(0, len(md_blocks), 3):
    kanji = md_blocks[i]
    if kanji in skip:
        continue
    body = md_blocks[i+2].strip()
    parts = body.split('---')
    script = parts[1].strip() if len(parts) > 1 else ''
    md_episodes[kanji] = extract_lines_from_md(script)

# キャラクターの色マップ
char_colors = {
    'タク': '#4A90D9',
    'カイト': '#E67E22',
    'リュウ': '#2ECC71',
    'ソウタ': '#9B59B6',
    'カナデ': '#E74C3C',
    'セトカ': '#1ABC9C',
    'アヤナ': '#F39C12',
    'ユイ': '#FF69B4',
    'サクラ': '#FF8A80',
}

def build_episode_html(meta, lines, ep_idx):
    cast_html = ''
    for role, age, actor in meta['cast']:
        color = char_colors.get(role, '#666')
        cast_html += f'<span class="cast-tag" style="--char-color: {color}"><span class="role-name">{role}</span><span class="actor-name">{actor}（{age}）</span></span>'
    
    lines_html = ''
    for item in lines:
        if item[1] == 'togaki' or (item[0] == 'togaki' if len(item) == 3 else False):
            text = item[1] if len(item) == 3 else item[2]
            if not text:
                text = item[1]
            lines_html += f'<div class="line togaki">{text}</div>\n'
        elif item[1] == 'serif' or (item[0] == 'serif' if len(item) == 3 else False):
            if len(item) == 4:  # from HTML
                name = item[2]
                serif = item[3]
            else:  # from MD
                name = item[1]
                serif = item[2]
            color = char_colors.get(name, '#666')
            lines_html += f'''<div class="line dialogue">
    <span class="char-name" style="color: {color}">{name}</span>
    <span class="dialog-text">{serif}</span>
</div>
'''
        elif len(item) == 4 and item[1] == 'serif_with_togaki':
            name = item[2]
            serif = item[3]
            color = char_colors.get(name, '#666')
            lines_html += f'''<div class="line dialogue">
    <span class="char-name" style="color: {color}">{name}</span>
    <span class="dialog-text">{serif}</span>
</div>
'''
    
    return f'''
<section class="episode" id="ep{ep_idx+1}">
    <div class="ep-header">
        <div class="ep-number">{meta['num']}</div>
        <h2 class="ep-title">{meta['title']}</h2>
        <p class="ep-theme">{meta['theme']}</p>
        <div class="ep-meta">
            <span class="meta-item">📍 {meta['location']}</span>
            <span class="meta-item">⏱ {meta['duration']}</span>
        </div>
        <div class="cast-list">{cast_html}</div>
    </div>
    <div class="script-body">
{lines_html}
    </div>
</section>
'''

all_lines = [ep1_lines, ep2_lines, ep3_lines]

# MD episodes を正しい順に追加
renumber_order = ['五', '七', '八']
for k in renumber_order:
    if k in md_episodes:
        all_lines.append(md_episodes[k])

episodes_html = ''
for i, (meta, lines) in enumerate(zip(episodes_meta, all_lines)):
    episodes_html += build_episode_html(meta, lines, i)

# ナビゲーションボタン
nav_items = ''
for i, meta in enumerate(episodes_meta):
    nav_items += f'<a href="#ep{i+1}" class="nav-item">{meta["num"]}<br><small>{meta["title"]}</small></a>'

full_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>千駄ヶ谷わんてぃく — 脚本</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

:root {{
    --bg: #0a0a0a;
    --surface: #141414;
    --surface-2: #1e1e1e;
    --text: #e8e8e8;
    --text-muted: #888;
    --accent: #ff6b35;
    --accent-dim: rgba(255,107,53,0.15);
    --border: #2a2a2a;
}}

body {{
    font-family: 'Noto Sans JP', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.8;
    -webkit-font-smoothing: antialiased;
}}

/* ヘッダー */
.site-header {{
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(10,10,10,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.site-title {{
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 0.08em;
}}
.site-title span {{
    color: var(--accent);
}}
.site-subtitle {{
    font-size: 11px;
    color: var(--text-muted);
}}

/* ナビ */
.nav-bar {{
    display: flex;
    overflow-x: auto;
    gap: 8px;
    padding: 12px 16px;
    scrollbar-width: none;
    -ms-overflow-style: none;
    border-bottom: 1px solid var(--border);
}}
.nav-bar::-webkit-scrollbar {{ display: none; }}
.nav-item {{
    flex-shrink: 0;
    padding: 8px 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text-muted);
    text-decoration: none;
    font-size: 12px;
    line-height: 1.4;
    transition: all 0.2s;
    text-align: center;
    min-width: 90px;
}}
.nav-item:hover, .nav-item:active {{
    background: var(--accent-dim);
    border-color: var(--accent);
    color: var(--text);
}}
.nav-item small {{
    font-size: 10px;
    display: block;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 80px;
}}

/* エピソード */
.episode {{
    margin: 0;
    padding: 0;
    border-bottom: 1px solid var(--border);
}}
.ep-header {{
    padding: 32px 20px 24px;
    background: linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%);
    border-bottom: 1px solid var(--border);
}}
.ep-number {{
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 6px;
}}
.ep-title {{
    font-size: 22px;
    font-weight: 900;
    line-height: 1.3;
    margin-bottom: 8px;
}}
.ep-theme {{
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 16px;
    padding-left: 12px;
    border-left: 2px solid var(--accent);
}}
.ep-meta {{
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
}}
.meta-item {{
    font-size: 12px;
    color: var(--text-muted);
}}

/* キャスト */
.cast-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}}
.cast-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: var(--surface-2);
    border-radius: 20px;
    border: 1px solid var(--border);
    font-size: 12px;
}}
.role-name {{
    font-weight: 700;
    color: var(--char-color, #fff);
}}
.actor-name {{
    color: var(--text-muted);
    font-size: 11px;
}}

/* 台本本文 */
.script-body {{
    padding: 20px 16px 32px;
}}

.line {{
    margin-bottom: 14px;
}}
.line.togaki {{
    text-align: center;
    color: var(--text-muted);
    font-size: 13px;
    font-style: italic;
    padding: 8px 0;
}}
.line.dialogue {{
    display: flex;
    gap: 10px;
    align-items: flex-start;
}}
.char-name {{
    flex-shrink: 0;
    font-weight: 700;
    font-size: 13px;
    min-width: 56px;
    text-align: right;
    padding-top: 1px;
}}
.dialog-text {{
    font-size: 15px;
    line-height: 1.75;
    flex: 1;
}}

/* フッター */
.site-footer {{
    text-align: center;
    padding: 40px 20px;
    color: var(--text-muted);
    font-size: 11px;
}}

/* スクロール復帰用の余白 */
.episode:target .ep-header {{
    padding-top: 40px;
}}

@media (min-width: 600px) {{
    .script-body {{
        max-width: 640px;
        margin: 0 auto;
        padding: 32px 24px 48px;
    }}
    .ep-header {{
        max-width: 640px;
        margin: 0 auto;
        padding: 40px 24px 28px;
    }}
    .ep-title {{
        font-size: 28px;
    }}
    .dialog-text {{
        font-size: 16px;
    }}
}}
</style>
</head>
<body>
<header class="site-header">
    <div>
        <div class="site-title">千駄ヶ谷<span>わんてぃく</span></div>
        <div class="site-subtitle">脚本 全6話</div>
    </div>
</header>

<nav class="nav-bar">
{nav_items}
</nav>

{episodes_html}

<footer class="site-footer">
    千駄ヶ谷わんてぃく — 脚本案（第一稿）<br>
    © 2026 GATE channel & works
</footer>

<script>
// スムーズスクロール
document.querySelectorAll('.nav-item').forEach(a => {{
    a.addEventListener('click', e => {{
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {{
            const headerH = document.querySelector('.site-header').offsetHeight;
            const y = target.getBoundingClientRect().top + window.pageYOffset - headerH;
            window.scrollTo({{ top: y, behavior: 'smooth' }});
        }}
    }});
}});
</script>
</body>
</html>
'''

out_file = 'sendagaya_scripts_mobile.html'
with open(out_file, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f'Mobile script viewer generated: {out_file}')
