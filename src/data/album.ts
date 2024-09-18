import { siteConfig } from "@/site-config";
import { type CollectionEntry, getCollection } from "astro:content";

/** filter out draft albums based on the environment */
export async function getAllAlbums() {
	return await getCollection("albums", ({ data }) => {
		return (import.meta.env.PROD ? !data.draft : true);
	});
}