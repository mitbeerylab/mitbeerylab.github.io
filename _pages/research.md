---
title: "BeeryLab • Research"
layout: research
excerpt: "BeeryLab •- Research"
sitemap: false
permalink: /research
---

# Research


### Overview 
---

We develop computational methods to expand scientific understanding of life on earth while advancing the state of the art in artificial intelligence. Working collaboratively with ecological researchers and conservation practitioners, we deploy these methods to inform sustainable development and conservation action locally and globally.

<div style="text-align: center">
<img style="width: 70%;" src="{{ site.url }}{{ site.baseurl }}/images/researchpic/what-we-work-on.png" alt=""/>
</div>

Biodiversity is fundamental to ecosystem function, human well-being, and global stability. Yet we face unprecedented rates of species loss and habitat degradation. Distributed networks of sensors—including camera traps, acoustic recorders, environmental DNA sampling, satellite sys- tems, and citizen science platforms—now generate massive volumes of observational data. These datasets contain rich ecological signals about species distributions, interactions, phenological shifts, and community dynamics. However, accessing this information largely relies on manual expert an- notation, limiting our capacity to extract scientific insights at scale. While recent advances in machine learning have created opportunities for automated analysis across geographic scales and taxonomic group, fundamental research advances are still needed to build AI-enabled systems that can be deployed to reliably and efficiently monitor biodiversity change, understand key drivers, and inform conservation and restoration action on the ground.

 Current and ongoing research in the lab addresses three key, interconnected technical challenges: (1) efficient, interactive discovery of ecological evidence from large-scale biodiversity databases; (2) development of multimodal inference methods that reason across diverse, non-aligned data streams to characterize biodiversity patterns; and (3) design AI evaluation frameworks appropriate for high- stakes deployment, with implications for the trustworthy use of AI across consequential domains.

<div style="text-align: center">
<img style="width: 70%;" src="{{ site.url }}{{ site.baseurl }}/images/researchpic/our-process.png" alt="Our process"/>
</div>

Discovering evidence for ecological hypotheses. Biodiversity databases are growing expo- nentially. For example, iNaturalist contains nearly 300 million georeferenced observations with photographic evidence spanning over 550,000 species. Though already invaluable in understand- ing species range and co-occurrence, these images encode far richer information including species traits, biotic and abiotic interactions, behavior, and microhabitats. So far, the vast majority of this information remains hidden: we don’t have the right tools to find and extract it at scale–even with modern AI–due to compounding technical challenges. Common species receive orders of magnitude more observations than rare species. Ecologically relevant categories are inherently fine-grained, requiring discrimination of subtle visual attributes. The set of possible categories of interest is vast, and may never have been previously observed (e.g. novel species, unrecorded interactions).