---
title: "BeeryLab • Gallery"
layout: textlay
excerpt: "Photos of the BeeryLab team."
sitemap: false
permalink: /gallery
---

<div id="gallery-page" markdown="0">
<style>
  .gallery-grid {
      display: flex;
      flex-wrap: wrap;
      margin: 0 -10px;
  }
  .gallery-item {
      padding: 0 10px;
      margin-bottom: 24px;
  }
  .gallery-thumb {
      display: block;
      width: 100%;
      aspect-ratio: 4 / 3;
      overflow: hidden;
      border-radius: 4px;
      cursor: pointer;
  }
  .gallery-thumb img {
      width: 100%;
      height: 100%;
      margin: 0;
      object-fit: cover;
      transition: transform 0.2s ease;
  }
  .gallery-thumb:hover img {
      transform: scale(1.03);
  }
  #gallery-modal .modal-body img {
      width: 100%;
      margin: 0;
  }
</style>

<h1>Gallery</h1>

<!--<p>Moments from the BeeryLab: fieldwork, conferences, retreats, and time together.</p>-->

<hr>

{% if site.data.gallery and site.data.gallery.size > 0 %}
<div class="gallery-grid">
  {% for photo in site.data.gallery %}
  {% capture src %}{{ site.url }}{{ site.baseurl }}/images/gallerypic/{{ photo.image }}{% endcapture %}
  <div class="gallery-item col-xs-12 col-sm-6 col-md-4">
    <a class="gallery-thumb" href="{{ src }}">
      <img src="{{ src }}" alt="{{ photo.alt | default: 'BeeryLab team photo' | escape }}" loading="lazy">
    </a>
  </div>
  {% endfor %}
</div>
{% else %}
<p><em>Photos coming soon.</em></p>
{% endif %}

<div class="modal fade" id="gallery-modal" tabindex="-1" role="dialog" aria-hidden="true">
  <div class="modal-dialog modal-lg" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
      </div>
      <div class="modal-body"><img src="" alt=""></div>
    </div>
  </div>
</div>

<script>
  document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".gallery-thumb").forEach(function(link) {
      link.addEventListener("click", function(event) {
        event.preventDefault();
        const modal = document.getElementById("gallery-modal");
        const img = modal.querySelector(".modal-body img");
        img.src = this.getAttribute("href");
        img.alt = this.querySelector("img").alt;
        $(modal).modal("show");
      });
    });
  });
</script>
</div>
