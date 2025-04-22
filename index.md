---
layout: default
title: ORACLE エラー解決ブログ
---

<h1>☕ ORACLEエラー図解解説ブログ</h1>
<p>実在するOracleエラー番号に基づき、原因・解決策・再発防止策までを図表・コード付きでわかりやすく紹介します。</p>

<div class="posts">
  {% for post in paginator.posts %}
    <article style="margin-bottom: 2em; padding: 1em; border: 1px solid #ccc; border-radius: 10px;">
      <h2><a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a></h2>
      <p><small>{{ post.date | date: "%Y年%m月%d日" }}</small></p>
      <p>{{ post.description }}</p>
    </article>
  {% endfor %}
</div>

<div class="pagination">
  {% if paginator.previous_page %}
    <a href="{{ paginator.previous_page_path }}" class="previous">← 前のページ</a>
  {% endif %}
  {% if paginator.next_page %}
    <a href="{{ paginator.next_page_path }}" class="next">次のページ →</a>
  {% endif %}
</div>
