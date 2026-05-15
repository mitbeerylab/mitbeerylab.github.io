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
</style>

<!-- START OF PAGE -->
# Publications

(Last updated {{ site.data.publications_meta.updated }}.
See <a href="https://scholar.google.com/citations?user=Hbr4c10AAAAJ&view_op=list_works&sortby=pubdate">Google Scholar</a> for most up-to-date publications)

<!-- Display all possible research themes as filter buttons -->
<p>
  {% assign themes = site.data.research_themes %}
  {% assign theme_aliases = site.data.research_theme_aliases %}
  **Research Themes:** (select to filter)
  {% for theme in themes %}<span class="badge badge-pill badge-pill-custom filter-button" data-theme="{{ theme.name }}" data-color="{{ theme.color }}" data-darker-color="{{ theme.darker_color }}" style="background-color: {{ theme.color }}">{{ theme.name }}</span>
  {% endfor %}
</p>

---

<!-- Display all publications -->
{% assign themes = site.data.research_themes %}
{% assign theme_aliases = site.data.research_theme_aliases %}
{% for pub in site.data.publications %}
{% assign display_themes = pub.themes %}
{% if display_themes == nil or display_themes == empty %}
  {% assign display_themes = pub.suggested_themes %}
{% endif %}
{% assign normalized_theme_csv = "" %}
{% assign normalized_theme_tokens = "|" %}
{% for theme in display_themes %}
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
<!-- Citations -->
<div class="publication-item" data-themes="{{ normalized_theme_csv }}">
  <p class="hanging-indent">
    {{ pub.authors }}.
    {% if pub.url %} [{{ pub.title }}]({{ pub.url }}). {% else %} {{pub.title}}. {% endif %}*{{ pub.journal }}*{% if pub.volume %} {{ pub.volume }}{% if pub.issue %}({{ pub.issue }}){% endif %},{% endif %}{% if pub.pages %} {{ pub.pages }}{% endif %}. ({{ pub.year }})
    {% if pub.doi %} DOI: {{ pub.doi }} {% elsif pub.preprint %} *preprint: {{ pub.preprint }}*{% endif %}
  </p>
  <!-- Buttons and tags -->
  {% if pub.preprint_url or normalized_theme_csv != "" %}
  <p style="margin-left: 20px; margin-top: -11px">
    {% if pub.preprint_url %}<a href="{{ pub.preprint_url }}" class="btn btn-xs btn-primary">Preprint</a>{% endif %}{% if normalized_theme_csv != "" %}{% assign rendered_theme_tokens = "|" %}{% for theme in display_themes %}{% assign normalized_theme = theme_aliases[theme] | default: theme %}{% assign theme_data = themes | where: "name", normalized_theme | first %}{% assign theme_token = "|" | append: normalized_theme | append: "|" %}{% if theme_data %}{% unless rendered_theme_tokens contains theme_token %} <span class="badge badge-pill badge-pill-custom" style="background-color: {{ theme_data.color }}">{{ normalized_theme }}</span>{% assign rendered_theme_tokens = rendered_theme_tokens | append: normalized_theme | append: "|" %}{% endunless %}{% endif %}{% endfor %}
    {% endif %}
  </p>
  {% endif %}
</div>
{% endfor %}

<!-- JavaScript for filtering publications -->
<script>
  document.addEventListener("DOMContentLoaded", function() {
    const filterButtons = document.querySelectorAll('.filter-button');
    const publicationItems = document.querySelectorAll('.publication-item');

    filterButtons.forEach(button => {
      const originalColor = button.getAttribute('data-color');
      const darkerColor = button.getAttribute('data-darker-color');

      // Log the colors to the console to verify correct retrieval
      console.log('Original Color:', originalColor);
      console.log('Darker Color:', darkerColor);

      button.addEventListener('click', function() {
        this.classList.toggle('active');
        if (this.classList.contains('active')) {
          this.style.backgroundColor = darkerColor;
        } else {
          this.style.backgroundColor = originalColor;
        }
        filterPublications();
      });
    });

    function filterPublications() {
      const activeThemes = Array.from(filterButtons)
                                .filter(btn => btn.classList.contains('active'))
                                .map(btn => btn.getAttribute('data-theme'));

      publicationItems.forEach(item => {
        const itemThemes = item.getAttribute('data-themes').split(',').filter(Boolean);

        if (activeThemes.length === 0 || activeThemes.every(theme => itemThemes.includes(theme))) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
    }
  });
</script>
