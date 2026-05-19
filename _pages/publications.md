---
title: "BeeryLab • Publications"
layout: publications
excerpt: "Publications."
sitemap: false
permalink: /publications
---
<!-- Custom CSS -->
<style>
  .hanging-indent {
    margin-left: 20px;
    text-indent: -20px;
  }
  .btn-xs {
    padding: 2px 5px;
    font-size: 9px;
    line-height: 1.5;
    border-radius: 3px;
    border: none;
    box-shadow: none;
    background-color: #0059b3; /* Bootstrap primary color */
    color: white;
  }
  .btn-xs:hover, .btn-xs:focus, .btn-xs:active {
    background-color: #011f4b; /* Darker shade of primary color */
    box-shadow: none;
  }
</style>

<!-- START OF PAGE -->
# Publications

List of publications involving the BeeryLab (Last updated {{ site.data.publications_meta.updated }}.
See <a href="https://scholar.google.com/citations?user=Hbr4c10AAAAJ&view_op=list_works&sortby=pubdate">Google Scholar</a> for most up-to-date publications)

---

<!-- Display all publications -->
{% for pub in site.data.publications %}
<!-- Citations -->
<div class="publication-item">
  <p class="hanging-indent">
    {% if pub.url %} [{{ pub.title }}]({{ pub.url }}). {% else %} {{ pub.title }}. {% endif %}{{ pub.authors }}. *{{ pub.journal }}*{% if pub.volume %} {{ pub.volume }}{% if pub.issue %}({{ pub.issue }}){% endif %},{% endif %}{% if pub.pages %} {{ pub.pages }}{% endif %}. ({{ pub.year }})
    {% if pub.doi %} DOI: {{ pub.doi }} {% elsif pub.preprint %} *preprint: {{ pub.preprint }}*{% endif %}
  </p>
  <!-- Buttons and tags -->
  {% if pub.preprint_url %}
  <p style="margin-left: 20px; margin-top: -11px">
    {% if pub.preprint_url %}<a href="{{ pub.preprint_url }}" class="btn btn-xs btn-primary">Preprint</a>{% endif %}
  </p>
  {% endif %}
</div>
{% endfor %}
