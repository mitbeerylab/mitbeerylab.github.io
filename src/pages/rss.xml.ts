import { getAllPublications } from "@/data/publication";
import { siteConfig } from "@/site-config";
import rss from "@astrojs/rss";

export const GET = async () => {
	const publications = await getAllPublications();

	return rss({
		description: siteConfig.description,
		items: publications.map((publication) => ({
			description: publication.data.description,
			link: `publications/${publication.slug}`,
			pubDate: publication.data.publishDate,
			title: publication.data.title,
		})),
		site: import.meta.env.SITE,
		title: siteConfig.title,
	});
};
