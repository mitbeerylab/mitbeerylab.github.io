---
title: "BeeryLab • People"
layout: gridlay
excerpt: "BeeryLab: People"
sitemap: false
permalink: /people
---

# People

<!-- TODO: change to album view once we have >1 photo -->
{% for photo in site.data.photos %}
<div class="col-sm-12 clearfix" style="text-align: center; ">
<div style="display: flex; justify-content: center;">
<img class="group-pic" src="{{ site.url }}{{ site.baseurl }}/images/grouppic/{{ photo.name }}" alt="Group photo"/>
</div>
<i>{{ photo.description }}</i>
</div>
{% assign number_printed = forloop.index | modulo: 2 %}
{% if number_printed == 0 %}
</div>
<div class="row">
{% endif %}
{% endfor %}

<!-- Principal Investigator -->
<div class="row" style="margin-bottom: 10px; padding: 15px 0;">
<div class="col-sm-2" style="display: flex; justify-content: center;">
<div class="image-cropper">
<img class="person-pic" src="{{ site.url }}{{ site.baseurl }}/images/teampic/SaraBeery.jpg" alt="Sara Beery photo"/>
</div>
</div>
<div class="col-sm-10" style="display: flex; flex-direction: column;">
<h4 style="margin-top: 0;"><b>Sara Beery</b> <i style="font-size: 0.8em; color: #888;">Assistant Professor</i></h4>
<p style="margin: 1px 0;">Sara is an assistant professor at MIT EECS' Faculty of AI and Decision Making and CSAIL, and was previously a visiting researcher at Google working on Auto Arborist. She has always loved the natural world, and has seen a growing need for technology-based approaches to conservation and sustainability challenges. Her research focuses on building computer vision methods that enable global-scale environmental and biodiversity monitoring across data modalities, tackling real-world challenges including strong spatiotemporal correlations that lead to domain shift, imperfect data quality, fine-grained categories, and long-tailed distributions.</p>
<div style="display: flex; gap: 8px;">
<a href="https://beerys.github.io"><i class="mdi mdi-web"></i></a>
<a href="https://twitter.com/sarameghanbeery"><i class="mdi mdi-twitter"></i></a>
{% comment %} Optional GitHub icon slot for Sara. {% endcomment %}
<a href="https://scholar.google.com/citations?user=Hbr4c10AAAAJ"><i class="mdi mdi-school"></i></a>
</div>
</div>
</div>

<!-- Post-docs -->
{% for member in site.data.postdocs %}
<div class="row" style="margin-bottom: 10px; padding: 15px 0;">
<div class="col-sm-2" style="display: flex; justify-content: center;">
<div class="image-cropper">
<img class="person-pic" src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" alt="{{ member.name }} photo"/>
</div>
</div>
<div class="col-sm-10" style="display: flex; flex-direction: column;">
<h4 style="margin-top: 0;"><b>{{ member.name }}</b> <i style="font-size: 0.8em; color: #888;">{{ member.info }}</i></h4> 
<p style="margin: 1px 0;">{{ member.description }}</p>
<div style="display: flex; gap: 8px;">
{% if member.website %}<a href="{{ member.website }}"><i class="mdi mdi-web"></i></a>{% endif %}
{% if member.twitter %}<a href="{{ member.twitter }}"><i class="mdi mdi-twitter"></i></a>{% endif %}
{% if member.linkedin %}<a href="{{ member.linkedin }}"><i class="mdi mdi-linkedin"></i></a>{% endif %}
{% if member.github %}<a href="{{ member.github }}"><i class="mdi mdi-github"></i></a>{% endif %}
{% if member.google_scholar %}<a href="{{ member.google_scholar }}"><i class="mdi mdi-school"></i></a>{% endif %}
{% if member.youtube %}<a href="{{ member.youtube }}"><i class="mdi mdi-youtube"></i></a>{% endif %}
{% if member.instagram %}<a href="{{ member.instagram }}"><i class="mdi mdi-instagram"></i></a>{% endif %}
</div>
</div>
</div>
{% endfor %}

<!-- Grad students -->
{% for member in site.data.grad_students %}
<div class="row" style="margin-bottom: 10px; padding: 15px 0;">
<div class="col-sm-2" style="display: flex; justify-content: center;">
<div class="image-cropper">
<img class="person-pic" src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" alt="{{ member.name }} photo"/>
</div>
</div>
<div class="col-sm-10" style="display: flex; flex-direction: column;">
<h4 style="margin-top: 0;"><b>{{ member.name }}</b> <i style="font-size: 0.8em; color: #888;">{{ member.info }}</i></h4> 
<p style="margin: 1px 0;">{{ member.description }}</p>
<div style="display: flex; gap: 8px;">
{% if member.website %}<a href="{{ member.website }}"><i class="mdi mdi-web"></i></a>{% endif %}
{% if member.twitter %}<a href="{{ member.twitter }}"><i class="mdi mdi-twitter"></i></a>{% endif %}
{% if member.linkedin %}<a href="{{ member.linkedin }}"><i class="mdi mdi-linkedin"></i></a>{% endif %}
{% if member.github %}<a href="{{ member.github }}"><i class="mdi mdi-github"></i></a>{% endif %}
{% if member.google_scholar %}<a href="{{ member.google_scholar }}"><i class="mdi mdi-school"></i></a>{% endif %}
{% if member.youtube %}<a href="{{ member.youtube }}"><i class="mdi mdi-youtube"></i></a>{% endif %}
{% if member.instagram %}<a href="{{ member.instagram }}"><i class="mdi mdi-instagram"></i></a>{% endif %}
</div>
</div>
</div>
{% endfor %}

---
<h2 style="padding: 20px 0 10px">Masters & Visiting Students</h2>
<ul class="space-y-2" style="list-style: none; padding: 0;">
{% for member in site.data.msvisit %}
  <li style="margin-bottom: 8px;">
    <span style="font-size: 1.1em;">{{ member.name }}</span>
    {% if member.info %}<br><span style="color: #666; font-size: 0.9em;">{{ member.info }}</span>{% endif %}
  </li>
{% endfor %}
</ul>

---
<h2 style="padding: 20px 0 10px">Undergraduates</h2>
<ul style="list-style: none; padding: 0;">
{% for member in site.data.undergrads %}
  <li style="margin-bottom: 8px;">
    <span style="font-size: 1.1em;">{{ member.name }}</span>
    {% if member.info %}<br><span style="color: #666; font-size: 0.9em;">{{ member.info }}</span>{% endif %}
  </li>
{% endfor %}
</ul>

---
<h2 style="padding: 20px 0 10px">Lab Alumni</h2>
<ul style="list-style: none; padding: 0;">
{% for member in site.data.alumni %}
  <li style="margin-bottom: 8px;">
    {% if member.link %}
      <a href="{{ member.link }}" style="font-size: 1.1em;">{{ member.name }}</a>
    {% else %}
      <span style="font-size: 1.1em;">{{ member.name }}</span>
    {% endif %}
    <span style="color: #666; font-size: 0.9em;">({{ member.previous }}){% if member.current %} &rarr; {{ member.current }}{% endif %}</span>
  </li>
{% endfor %}
</ul>
