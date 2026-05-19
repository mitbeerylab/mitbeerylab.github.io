---
title: "BeeryLab • Projects"
layout: textlay
excerpt: "Projects."
sitemap: false
permalink: /projects
---

<!-- Custom CSS -->
<style>
  pubtit {
    font-weight: bold;
    font-size: 1.7rem;
    line-height: 1.5;
  }
  .badge-pill-custom {
      margin-left: 5px;
      border-radius: 10rem;
      padding: 0.18em 0.6em;
      font-size: 13px;
  }
  .filter-button {
      margin-right: 5px;
      cursor: pointer;
  }
  .software-item.deprecated {
      filter: grayscale(100%);
      opacity: 0.7;
  }
  .project-year {
      color: #666;
      font-size: 16px;
      font-weight: 500;
      margin-left: 6px;
  }
  .software-description-toggle {
      margin-bottom: 10px;
  }
</style>

# Projects

Led by students and postdocs in the group with summaries and links to code, data, demos, and papers.
<p>
  {% assign themes = site.data.research_themes %}
  {% assign theme_aliases = site.data.research_theme_aliases %}
  **Research Themes:** (select to filter)
  {% for theme in themes %}<span class="badge badge-pill badge-pill-custom filter-button" data-theme="{{ theme.name }}" data-color="{{ theme.color }}" data-darker-color="{{ theme.darker_color }}" style="background-color: {{ theme.color }}">{{ theme.name }}</span>{% endfor %}
</p>
---

{% assign number_printed = 0 %}
{% for tool in site.data.software %}
{% assign normalized_theme_csv = "" %}
{% assign normalized_theme_tokens = "|" %}
{% for theme in tool.themes %}
  {% assign normalized_theme = theme_aliases[theme] | default: theme %}
  {% assign theme_data = themes | where: "name", normalized_theme | first %}
  {% assign theme_token = "|" | append: normalized_theme | append: "|" %}
  {% if theme_data %}
    {% unless normalized_theme_tokens contains theme_token %}
      {% assign normalized_theme_csv = normalized_theme_csv | append: normalized_theme | append: "," %}
      {% assign normalized_theme_tokens = normalized_theme_tokens | append: normalized_theme | append: "|" %}
    {% endunless %}
  {% endif %}
{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="software-item col-sm-6 clearfix {% if tool.deprecated %}deprecated{% endif %}" data-themes="{{ normalized_theme_csv }}">
 <div class="well">
  {% if tool.image %}{% if tool.image contains '://' %}<img src="{{ tool.image }}" class="software-img" style="float:left;" />{% else %}<img src="{{ site.url }}{{ site.baseurl }}/images/logopic/{{ tool.image }}" class="software-img" style="float:left;" />{% endif %}{% endif %}
  <pubtit>{{ tool.title }}</pubtit>{% if tool.year %}<span class="project-year">({{ tool.year }})</span>{% endif %}
  <div style="clear: both;"></div>
  {% if tool.links -%}{% for l in tool.links -%}<strong>{{ l.label }}:</strong> <a href="{{ l.url }}">{{ l.url }}</a><br/>{%- endfor -%}{% elsif tool.link -%}<a href="{{ tool.link.url }}">{{ tool.link.url }}</a>{%- endif %}
  <hr>
  <details class="software-description" markdown="0">
    <summary class="software-description-toggle">
      <span class="software-description-label-collapsed" style="padding: -2px 0 0 0;">Show description</span>
      <span class="software-description-label-expanded" style="padding: -2px 0 0 0;">Hide description</span>
    </summary>
    <p class="software-description-body">{{ tool.description }}</p>
  </details>
  <p><em>{{ tool.authors }}</em></p>
  <p class="text-danger"><strong> {{ tool.news1 }}</strong></p>
  <p> {{ tool.news2 }}</p>
  {% if normalized_theme_csv != "" %}{% assign rendered_theme_tokens = "|" %}{% for theme in tool.themes %}{% assign normalized_theme = theme_aliases[theme] | default: theme %}{% assign theme_data = themes | where: "name", normalized_theme | first %}{% assign theme_token = "|" | append: normalized_theme | append: "|" %}{% if theme_data %}{% unless rendered_theme_tokens contains theme_token %}<span class="badge badge-pill badge-pill-custom" style="background-color: {{ theme_data.color }}">{{ normalized_theme }}</span>{% assign rendered_theme_tokens = rendered_theme_tokens | append: normalized_theme | append: "|" %}{% endunless %}{% endif %}{% endfor %}
  {% endif %}
 </div>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}

<script>
  document.addEventListener("DOMContentLoaded", function() {
    const filterButtons = document.querySelectorAll('.filter-button');
    const projectItems = document.querySelectorAll('.software-item');

    filterButtons.forEach(button => {
      const originalColor = button.getAttribute('data-color');
      const darkerColor = button.getAttribute('data-darker-color');

      button.addEventListener('click', function() {
        this.classList.toggle('active');
        this.style.backgroundColor = this.classList.contains('active') ? darkerColor : originalColor;
        filterProjects();
      });
    });

    function filterProjects() {
      const activeThemes = Array.from(filterButtons)
        .filter(btn => btn.classList.contains('active'))
        .map(btn => btn.getAttribute('data-theme'));

      projectItems.forEach(item => {
        const itemThemes = item.getAttribute('data-themes').split(',').filter(Boolean);

        if (activeThemes.length === 0 || activeThemes.every(theme => itemThemes.includes(theme))) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });
    }
  });
</script>
