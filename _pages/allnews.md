---
title: "BeeryLab • News"
layout: textlay
excerpt: "BeeryLab at MIT."
sitemap: false
permalink: /news
---

# News

{% for article in site.data.news %}
<p><b>{{ article.date }}</b> <br> {% if article.link %}<a href="{{ article.link }}">{{ article.headline }}</a>{% else %}{{ article.headline }}{% endif %}</p>
{% endfor %}
