
import streamlit as st
from bs4 import BeautifulSoup
import requests
import openai

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key


# アプリのタイトル
st.title('求人詳細ページから質問作成')
st.image("疑問.jpg")

# ユーザーからURLを入力してもらう
url = st.text_input('転職サイト リジョブの求人詳細ページのURLを入力してください:')

# 作成して欲しい質問数を設定（10個まで）
num_questions = st.number_input('作成して欲しい質問数を設定してください（最大10）:', min_value=1, max_value=10, value=3)

# URLが入力されたら処理を開始
if url:
    # 指定されたURLから情報を取得
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 各セクションから情報を取得（仕事内容、必要経験、求める人物像）
    sections_to_scrape = ['仕事内容', '必要経験', '求める人物像']
    scraped_data = {}

    for heading in sections_to_scrape:
        detail_heading = soup.find(lambda tag: tag.name in ['h3', 'h2'] and tag.text.strip() == heading.strip())
        detail_section = detail_heading.find_parent('section') if detail_heading else None
        scraped_data[heading] = detail_section.text.strip() if detail_section else "情報が見つかりませんでした。"

    # インプットした情報から面接で聞ける質問を作成
    prompt = f"以下の情報は求人が採用したい人材の条件です。以下の情報を理解した上で人事が求職者に対して面接で聞く質問を{num_questions}個作成してください。またアウトプットした質問の冒頭には質問番号(例えば、1,①,質問1など)は入れないようにしてください。質問は、scraped_dataにリストされている項目をバランスよく使って作成するようにしてください。また質問する際は、求職者がこれまで経験してきたことが、求人のニーズとマッチしているか？という観点を持って質問を作成するようにしてください。そして求職者が求人にマッチするかどうかを判断するために、直接的な質問だけでなく、洞察を深めるための質問を考えるようにしてください。\n"
    for key, value in scraped_data.items():
        prompt += f"\n{key}:\n{value}\n"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=700,
        n=1
    )

    # 生成された質問を抽出し、設定した数だけ表示
    generated_questions = response.choices[0].text.strip().split('\n')
    generated_questions = [q.strip() for q in generated_questions if q.strip()]  # 空白行を除去
    generated_questions = [q.lstrip('0123456789. ') for q in generated_questions]  # 既存のナンバリングを取り除く
    generated_questions = generated_questions[:num_questions]  # 設定した数だけ取得

    st.write('生成された面接質問:')
    for idx, question in enumerate(generated_questions):
        st.write(f"{idx+1}. {question}")
