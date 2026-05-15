---
title: "BeeryLab • Outreach"
layout: textlay
excerpt: "Outreach."
sitemap: false
permalink: /outreach
---

<div id="outreach-page" markdown="0">
<style>
  .badge-pill-custom {
      margin-right: 5px;
      border-radius: 10rem;
      padding: 0.18em 0.6em;
      font-size: 13px;
  }
  .filter-button {
      cursor: pointer;
      color: white;
  }
  .filter-button.active {
      opacity: 1;
  }
  .outreach-item {
      margin-bottom: 18px;
  }
  .outreach-item h4 {
      margin-top: 0;
      margin-bottom: 10px;
  }
  .outreach-item-header {
      margin-bottom: 8px;
  }
  .outreach-meta {
      margin-bottom: 5px;
      color: #555;
  }
  .outreach-date {
      color: #666;
      font-weight: 600;
      margin-left: 4px;
  }
</style>

<h1>Outreach</h1>

<p>We share our work through invited talks, courses, workshops, and community-centered teaching.</p>

<p><strong>Browse:</strong>
<span class="badge badge-pill badge-pill-custom filter-button" data-filter="talk" style="background-color: #457b9d;">Talks</span>
<span class="badge badge-pill badge-pill-custom filter-button" data-filter="teaching" style="background-color: #2a9d8f;">Teaching &amp; Community Building</span>
</p>

<p><em>{{ site.data.outreach.counts.total }} activities listed.</em></p>

<hr>

{% for item in site.data.outreach.items %}
<div class="outreach-item well" data-type="{{ item.type }}">
  <div class="outreach-item-header">
    {% if item.type == "talk" %}
    <span class="badge badge-pill badge-pill-custom" style="background-color: #457b9d;">{{ item.type_label }}</span>
    {% else %}
    <span class="badge badge-pill badge-pill-custom" style="background-color: #2a9d8f;">{{ item.type_label }}</span>
    {% endif %}
    <span class="outreach-date">{{ item.publish_date_display }}</span>
  </div>
  <h4>{% if item.external %}<a href="{{ item.external }}">{{ item.title }}</a>{% else %}{{ item.title }}{% endif %}</h4>
  {% if item.speaker %}<p class="outreach-meta"><strong>{{ item.speaker_label | default: "Speaker" }}:</strong> {{ item.speaker }}</p>{% endif %}
  {% if item.host %}<p class="outreach-meta"><strong>{{ item.host_label | default: "Host" }}:</strong> {{ item.host }}</p>{% endif %}
</div>
{% endfor %}

<script>
  document.addEventListener("DOMContentLoaded", function() {
    const filterButtons = document.querySelectorAll(".filter-button");
    const outreachItems = document.querySelectorAll(".outreach-item");
    const activeColors = {
      talk: "#1f5f8b",
      teaching: "#1f776c"
    };
    const inactiveColors = {
      talk: "#457b9d",
      teaching: "#2a9d8f"
    };

    function applyFilter() {
      const activeFilters = Array.from(filterButtons)
        .filter(button => button.classList.contains("active"))
        .map(button => button.getAttribute("data-filter"));

      outreachItems.forEach(item => {
        const matches = activeFilters.length === 0 || activeFilters.includes(item.getAttribute("data-type"));
        item.style.display = matches ? "block" : "none";
      });
    }

    filterButtons.forEach(button => {
      button.addEventListener("click", function() {
        const filterValue = this.getAttribute("data-filter");
        const isActive = this.classList.toggle("active");
        this.style.backgroundColor = isActive ? activeColors[filterValue] : inactiveColors[filterValue];
        applyFilter();
      });
    });

    applyFilter();
  });
</script>
</div>
