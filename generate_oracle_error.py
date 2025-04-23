
import os
import json
import datetime
import requests
import re

USED_FILE = "used_oracle_errors.json"
POST_DIR = "_posts"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
MAX_RETRY = 30

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
必ず次のルールに従ってください。

1. Oracleの実在するエラー番号（ORA-xxxxx 形式）をひとつ明示してください（例: ORA-00001）
2. 記事はそのエラーに対して以下の見出し構成で出力してください（Markdown形式）
3. 最初の1行に「# ORA-xxxxx - エラーの概要」として必ず明記してください

# 条件
- 最近使用されたエラー（{', '.join(used[-20:])}など）や有名なエラー（例: ORA-01722、ORA-00001 など）に偏らないように注意してください。
- バイアスを除去する　頻出のエラーではなくマイナーなエラーなども公平にランダムにエラー番号を選出する事
- 必ず、Oracleのエラーコード（ORA-xxxxx）の中から **毎回異なる実在するエラー番号をランダムに1つだけ**選んでください。
- 頻出ではないが実在するコードも含め、**偏りなく多様なエラーコード**を選定してください。

例：ORA-01403, ORA-02292, ORA-06550, ORA-01843 なども候補としてください。
- 架空のエラー番号は禁止
- 各セクションは200字以上
- 全体で3000字以上
- 表やコードや外部リンクが使えるなら使う
- コードは黒背景になるようにMarkdownで表現（```sql など）
- 見出し構造を整える
- 実際のエラー番号と内容に沿って書く
- 記事冒頭にタイトル（#）と日付（YYYY-MM-DD）を記載する

# 構成：
1. ORA-00001 - 一意制約違反
2. 原因
3. 解決方法
4. 類似エラーとの違い
5. 反省と対策
6. 再発防止策
7. 関連リンクや根拠URL（可能な限り）
"""

    headers = { "Content-Type": "application/json" }
    params = { "key": api_key }
    body = { "contents": [{ "parts": [{"text": prompt }] }] }

    res = requests.post(API_URL, headers=headers, params=params, json=body)
    if res.status_code != 200:
        raise Exception(f"Gemini API error: {res.status_code} - {res.text}")

    data = res.json()
    try:
        parts = data['candidates'][0]['content']['parts']
        content = parts[0]['text'] if parts else ""
        return content.strip()
    except Exception as e:
        print("⚠️ Gemini応答の解析に失敗しました")
        return None

def extract_error_code(content):
    match = re.search(r"ORA-\d{5}", content)
    return match.group(0) if match else None

def save_post(content, error_code):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{POST_DIR}/{today}-{error_code.lower().replace('-', '')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def generate_post():
    print("🚀 Oracle Error Generator 起動")
    os.makedirs(POST_DIR, exist_ok=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set")

    used = load_used_errors()

    for attempt in range(MAX_RETRY):
        content = get_next_error_article(api_key, used)
        print("📦 Gemini応答内容取得完了")
        if not content:
            print(f"⚠️ Gemini応答が空のためリトライ: {attempt + 1}/{MAX_RETRY}")
            continue

        error_code = extract_error_code(content)
        if error_code:
            print(f"🔍 抽出されたエラーコード: {error_code}")
            print(f"📚 使用済みコード一覧（最新20件）: {used[-20:]}")

        if error_code and error_code not in used:
            save_post(content, error_code)
            used.append(error_code)
            save_used_errors(used)
            print(f"✅ 記事生成成功: {error_code}")
            return
        else:
            print(f"⚠️ 未使用ORAコードが取得できずリトライ: {error_code} ({attempt + 1}/{MAX_RETRY})")

    print("❌ 30回試行しても未使用エラーが取得できなかったため終了します。")
    raise Exception("Failed to extract or validate Oracle error code.")

if __name__ == "__main__":
    generate_post()
