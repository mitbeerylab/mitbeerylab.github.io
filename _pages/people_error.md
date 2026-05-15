---
title: "BeeryLab  People"
layout: gridlay
excerpt: "BeeryLab: People"
sitemap: false
permalink: /people_errors
---

# People

<!-- TODO: change to album view once we have >1 photo -->
<div class="row">
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
</div>

---
<div class="row">
	{% assign counter = 1 %}
	<div class="col-sm-4 clearfix" style="text-align: center; ">
		<div style="display: flex; justify-content: center;">
			<div class="image-cropper">
				<img class="person-pic" src="{{ site.url }}{{ site.baseurl }}/images/teampic/SaraBeery.jpg" alt="Sara Beery photo"/>
			</div>
		</div>
		<h4><b>Sara Beery</b></h4>
		<i>Assistant Professor</i> <br>
        <a href="https://beerys.github.io"><i class="mdi mdi-web"></i></a>
        <a href="https://twitter.com/sarameghanbeery"><i class="mdi mdi-twitter"></i></a>
        <a href="https://scholar.google.com/citations?user=Hbr4c10AAAAJ"><i class="mdi mdi-school"></i></a>
		<p>Sara is an assistant professor at MIT EECS' Faculty of AI and Decision Making and CSAIL, and was previously a visiting researcher at Google working on Auto Arborist. She has always loved the natural world, and has seen a growing need for technology-based approaches to conservation and sustainability challenges. Her research focuses on building computer vision methods that enable global-scale environmental and biodiversity monitoring across data modalities, tackling real-world challenges including strong spatiotemporal correlations that lead to domain shift, imperfect data quality, fine-grained categories, and long-tailed distributions.</p>
	</div>
	{% assign counter = counter | plus: 1 %}
	{% for member in site.data.postdocs %}
	<div class="col-sm-4 clearfix" style="text-align: center; ">
		<div style="display: flex; justify-content: center;">
			<div class="image-cropper">
				<img class="person-pic" src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" alt="{{ member.name }} photo"/>
			</div>
		</div>
		<h4><b>{{ member.name }}</b></h4>
		<i>{{ member.info }} <br> </i>
        {% if member.website %}<a href="{{ member.website }}"><i class="mdi mdi-web"></i></a>{% endif %}
        {% if member.twitter %}<a href="{{ member.twitter }}"><i class="mdi mdi-twitter"></i></a>{% endif %}
        {% if member.linkedin %}<a href="{{ member.linkedin }}"><i class="mdi mdi-linkedin"></i></a>{% endif %}
        {% if member.google_scholar %}<a href="{{ member.google_scholar }}"><i class="mdi mdi-school"></i></a>{% endif %}
        {% if member.youtube %}<a href="{{ member.youtube }}"><i class="mdi mdi-youtube"></i></a>{% endif %}
        {% if member.instagram %}<a href="{{ member.instagram }}"><i class="mdi mdi-instagram"></i></a>{% endif %}
		<p>{{ member.description }}</p>
	</div>
	{% assign counter = counter | plus: 1 %}
	{% assign number_printed = counter | modulo: 3 %}
	{% if number_printed == 0 %}
	</div>
	<div class="row">
	{% endif %}
	{% endfor %}
	{% for member in site.data.grad_students %}
	<div class="col-sm-4 clearfix" style="text-align: center; ">
		<div style="display: flex; justify-content: center;">
			<div class="image-cropper">
				<img class="person-pic" src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" alt="{{ member.name }} photo"/>
			</div>
		</div>
		<h4><b>{{ member.name }}</b></h4>
		<i>{{ member.info }} <br> </i>
        {% if member.website %}<a href="{{ member.website }}"><i class="mdi mdi-web"></i></a>{% endif %}
        {% if member.twitter %}<a href="{{ member.twitter }}"><i class="mdi mdi-twitter"></i></a>{% endif %}
        {% if member.linkedin %}<a href="{{ member.linkedin }}"><i class="mdi mdi-linkedin"></i></a>{% endif %}
        {% if member.google_scholar %}<a href="{{ member.google_scholar }}"><i class="mdi mdi-school"></i></a>{% endif %}
        {% if member.youtube %}<a href="{{ member.youtube }}"><i class="mdi mdi-youtube"></i></a>{% endif %}
        {% if member.instagram %}<a href="{{ member.instagram }}"><i class="mdi mdi-instagram"></i></a>{% endif %}
		<p>{{ member.description }}</p>
	</div>
	{% assign counter = counter | plus: 1 %}
	{% assign number_printed = counter | modulo: 3 %}
	{% if number_printed == 0 %}
	</div>
	<div class="row">
	{% endif %}
	{% endfor %}
</div>

---
<h2 style="text-align: center; padding: 30px">Masters & Visiting Students</h2>
<div class="row">
{% for member in site.data.msvisit %}
<div class="col-sm-4 clearfix" style="text-align: center; ">
<div style="display: flex; justify-content: center;">
</div>
<h4><b>{{ member.name }}</b></h4>
<i>{{ member.info }} <br> </i>
</div>
{% assign number_printed = forloop.index | modulo: 3 %}
{% if number_printed == 0 %}
</div>
<div class="row">
{% endif %}
{% endfor %}
</div>

---
<h2 style="text-align: center; padding: 30px">Undergraduates</h2>
<div class="row">
{% for member in site.data.undergrads %}
<div class="col-sm-4 clearfix" style="text-align: center; ">
<div style="display: flex; justify-content: center;">
</div>
<h4><b>{{ member.name }}</b></h4>
<i>{{ member.info }} <br> </i>
</div>
{% assign number_printed = forloop.index | modulo: 3 %}
{% if number_printed == 0 %}
</div>
<div class="row">
{% endif %}
{% endfor %}
</div>

## Lab Alumni
{% for member in site.data.alumni %}
{% if member.link %}
- [{{ member.name }}]({{ member.link }}) ({{ member.previous }}) {% if member.current %} &rarr; {{ member.current }} {% endif %}
{% else %}
- {{ member.name }} ({{ member.previous }}) {% if member.current %} &rarr; {{ member.current }} {% endif %}
{% endif %}
{% endfor %}
