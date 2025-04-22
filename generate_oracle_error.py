import os
import json
import datetime
import requests

USED_FILE = "used_oracle_errors.json"
POST_DIR = "_posts"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def load_used_errors():
    if not os.path.exists(USED_FILE):
        return []
    with open(USED_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_used_errors(errors):
    with open(USED_FILE, "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)

def get_next_error_article(api_key, used):
    prompt = f"""
次のルールでOracleの実在するエラー番号を1つランダムに選び、以下の構成でブログ記事をMarkdown形式で出力してください。
# 条件
- すでに使用したエラー番号（{', '.join(used[-20:]) if used else 'なし'}）は避ける
- 架空のエラー番号は禁止
- 各セクションは200字以上
- 全体で3000字以上
- 表やコードや外部リンクが使えるなら使う
- コードは黒背景になるようにMarkdownで表現（```sql など）
- 見出し構造を整える
- 実際のエラー番号と内容に沿って書く
- 記事冒頭にタイトル（#）と日付（YYYY-MM-DD）を記載する

# 構成：
1. エラー番号・タイトル（例: ORA-00001: 一意制約に違反）
2. 原因
3. 解決方法（SQLや設定例付き）
4. 類似エラーとの違い
5. 反省と対策
6. 再発防止策
7. 関連リンクや根拠URL（可能な限り）
"""

    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": api_key
    }
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    res = requests.post(API_URL, headers=headers, params=params, json=body)
    if res.status_code != 200:
        raise Exception(f"Gemini API error: {res.status_code} - {res.text}")
    data = res.json()
    content = data['candidates'][0]['content']['parts'][0]['text']
    return content

def extract_error_code(content):
    import re
    match = re.search(r"ORA-\d{5}", content)
    return match.group(0) if match else None

def html = markdown_to_html(content)
    save_post(html, error_code):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{POST_DIR}/{today}-{error_code.lower().replace('-', '')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


import re

def markdown_to_html(md):
    # ## 見出し
    md = re.sub(r'^###### (.+)', r'<h6>\1</h6>', md, flags=re.MULTILINE)
    md = re.sub(r'^##### (.+)', r'<h5>\1</h5>', md, flags=re.MULTILINE)
    md = re.sub(r'^#### (.+)', r'<h4>\1</h4>', md, flags=re.MULTILINE)
    md = re.sub(r'^### (.+)', r'<h3>\1</h3>', md, flags=re.MULTILINE)
    md = re.sub(r'^## (.+)', r'<h2>\1</h2>', md, flags=re.MULTILINE)
    md = re.sub(r'^# (.+)', r'<h1>\1</h1>', md, flags=re.MULTILINE)

    # コードブロック
    md = re.sub(r'```sql\n(.*?)```', r'<pre><code class="sql">\1</code></pre>', md, flags=re.DOTALL)
    md = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', md, flags=re.DOTALL)

    # 太字やリンクは省略または後で追加可能
    return md

def generate_post():
    os.makedirs(POST_DIR, exist_ok=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set")

    used = load_used_errors()
    content = get_next_error_article(api_key, used)
    error_code = extract_error_code(content)
    if error_code and error_code not in used:
        html = markdown_to_html(content)
    save_post(html, error_code)
        used.append(error_code)
        save_used_errors(used)
    else:
        raise Exception("Failed to extract or validate Oracle error code.")

if __name__ == "__main__":
    generate_post()
