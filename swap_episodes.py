import codecs
import re

file_path = r"c:\Users\togawa_takayuki\.gemini\antigravity\GATEチャンネル＆ワークス\sendagaya_scripts_tategaki.html"

with codecs.open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# === 1. 居酒屋→カフェ（第一話のみ、18歳の田中がいるため） ===
# INFO部分: 場所：居酒屋・テーブル席（夜）→ 場所：カフェ（昼）
text = text.replace(
    '場所：居酒屋・テーブル席（夜）</div>\r\n        <div class="ep-detail">尺：約<span class="tcy">2</span>分</div>\r\n        <div class="ep-cast">\r\n            <div><span class="cast-role">タク</span>',
    '場所：カフェ（昼）</div>\r\n        <div class="ep-detail">尺：約<span class="tcy">2</span>分</div>\r\n        <div class="ep-cast">\r\n            <div><span class="cast-role">タク</span>'
)
# hashira部分: ○居酒屋・テーブル席（夜）→ ○カフェ（昼）
text = text.replace(
    '○居酒屋・テーブル席（夜）</div>\r\n        <div class="serif-block">\r\n            <div class="character-name">タク</div>\r\n            <div class="serif">「……リュウさん',
    '○カフェ（昼）</div>\r\n        <div class="serif-block">\r\n            <div class="character-name">タク</div>\r\n            <div class="serif">「……リュウさん'
)

# === 2. 第一話と第三話の入れ替え ===
# 構造:
# 第一話: <!-- ① INFO --> ... <!-- ① 台本 1/2 --> ... <!-- ① 台本 2/2 --> ...
# 第三話: <!-- ③ INFO --> ... <!-- ③ 台本 1/2 --> ... <!-- ③ 台本 2/2 --> ...

# a. 第一話のコンテンツブロック（INFO + 台本 x 2）を抽出
ep1_start_marker = '<!-- ① INFO -->'
ep1_end_marker = '<!-- ② INFO -->'  # 第二話の開始が第一話の終了
ep2_start_marker = '<!-- ② INFO -->'
ep2_end_marker = '<!-- ③ INFO -->'  # 第三話の開始が第二話の終了
ep3_start_marker = '<!-- ③ INFO -->'
ep3_end_marker = '</body>'

ep1_start = text.find(ep1_start_marker)
ep1_end = text.find(ep1_end_marker)
ep2_start = text.find(ep2_start_marker)
ep2_end = text.find(ep2_end_marker)
ep3_start = text.find(ep3_start_marker)
ep3_end = text.find(ep3_end_marker)

if all(x != -1 for x in [ep1_start, ep1_end, ep2_start, ep2_end, ep3_start, ep3_end]):
    # 各エピソードのコンテンツを抽出（コメントマーカーは含まない）
    ep1_content = text[ep1_start:ep1_end]  # ① INFO ~ ② INFOの直前まで
    ep2_content = text[ep2_start:ep2_end]  # ② INFO ~ ③ INFOの直前まで
    ep3_content = text[ep3_start:ep3_end]  # ③ INFO ~ </body>の直前まで
    
    # エピソード番号のラベルを入れ替え
    # ep1のラベルを③→①にし、ep3のラベルを①→③にする
    # ただし内容そのものを入れ替えるので:
    # 旧第三話 → 新第一話（番号を①に、「第三話」→「第一話」に）
    # 旧第一話 → 新第三話（番号を③に、「第一話」→「第三話」に）
    
    new_ep1 = ep3_content  # 旧第三話を第一話の位置に
    new_ep3 = ep1_content  # 旧第一話を第三話の位置に
    
    # 新第一話（旧第三話）のラベル修正
    new_ep1 = new_ep1.replace('<!-- ③ INFO -->', '<!-- ① INFO -->')
    new_ep1 = new_ep1.replace('<!-- ③ 台本 1/2 -->', '<!-- ① 台本 1/2 -->')
    new_ep1 = new_ep1.replace('<!-- ③ 台本 2/2 -->', '<!-- ① 台本 2/2 -->')
    new_ep1 = new_ep1.replace('>第三話<', '>第一話<')
    # フッターの番号 ③ → ①
    new_ep1 = new_ep1.replace('<span class="tcy">③</span>', '<span class="tcy">①</span>')
    
    # 新第三話（旧第一話）のラベル修正
    new_ep3 = new_ep3.replace('<!-- ① INFO -->', '<!-- ③ INFO -->')
    new_ep3 = new_ep3.replace('<!-- ① 台本 1/2 -->', '<!-- ③ 台本 1/2 -->')
    new_ep3 = new_ep3.replace('<!-- ① 台本 2/2 -->', '<!-- ③ 台本 2/2 -->')
    new_ep3 = new_ep3.replace('>第一話<', '>第三話<')
    # フッターの番号 ① → ③
    new_ep3 = new_ep3.replace('<span class="tcy">①</span>', '<span class="tcy">③</span>')
    # フッターのタイトルも修正
    new_ep1 = new_ep1.replace('別れ話のプロンプト', '別れ話のプロンプト')  # タイトルは変わらない
    new_ep3 = new_ep3.replace('他人の幸せのパトロン', '他人の幸せのパトロン')  # タイトルは変わらない
    
    # 再構築
    before = text[:ep1_start]
    after = text[ep3_end:]
    
    text = before + new_ep1 + ep2_content + new_ep3 + after
    
    print("Episode swap completed successfully!")
else:
    print(f"ERROR: Could not find all markers!")
    print(f"  ep1_start={ep1_start}, ep1_end={ep1_end}")
    print(f"  ep2_start={ep2_start}, ep2_end={ep2_end}")
    print(f"  ep3_start={ep3_start}, ep3_end={ep3_end}")

with codecs.open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("All changes saved.")
