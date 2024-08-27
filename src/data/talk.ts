import { siteConfig } from "@/site-config";
import { type CollectionEntry, getCollection } from "astro:content";

/** filter out draft talks based on the environment */
export async function getAllTalks(noExternal=false) {
	return await getCollection("talk", ({ data }) => {
		return (import.meta.env.PROD ? !data.draft : true) && (!noExternal || !data.external);
	});
}

/** returns the date of the talk based on option in siteConfig.sortTalksByUpdatedDate */
export function getTalkSortDate(talk: CollectionEntry<"talk">) {
	return siteConfig.sortTalksByUpdatedDate && talk.data.updatedDate !== undefined
		? new Date(talk.data.updatedDate)
		: new Date(talk.data.publishDate);
}

/** sort talk by date (by siteConfig.sortTalksByUpdatedDate), desc.*/
export function sortMDByDate(talks: CollectionEntry<"talk">[]) {
	return talks.sort((a, b) => {
		const aDate = getTalkSortDate(a).valueOf();
		const bDate = getTalkSortDate(b).valueOf();
		return bDate - aDate;
	});
}

/** groups talks by year (based on option siteConfig.sortTalksByUpdatedDate), using the year as the key
 *  Note: This function doesn't filter draft talks, pass it the result of getAllTalks above to do so.
 */
export function groupTalksByYear(talks: CollectionEntry<"talk">[]) {
	return talks.reduce<Record<string, CollectionEntry<"talk">[]>>((acc, talk) => {
		const year = getTalkSortDate(talk).getFullYear();
		if (!acc[year]) {
			acc[year] = [];
		}
		acc[year].push(talk);
		return acc;
	}, {});
}

/** returns all tags created from talks (inc duplicate tags)
 *  Note: This function doesn't filter draft talks, pass it the result of getAllTalks above to do so.
 *  */
export function getAllTags(talks: CollectionEntry<"talk">[]) {
	return talks.flatMap((talk) => [...talk.data.tags]);
}

/** returns all unique tags created from talks
 *  Note: This function doesn't filter draft talks, pass it the result of getAllTalks above to do so.
 *  */
export function getUniqueTags(talks: CollectionEntry<"talk">[]) {
	return [...new Set(getAllTags(talks))];
}

/** returns a count of each unique tag - [[tagName, count], ...]
 *  Note: This function doesn't filter draft talks, pass it the result of getAllTalks above to do so.
 *  */
export function getUniqueTagsWithCount(talks: CollectionEntry<"talk">[]): [string, number][] {
	return [
		...getAllTags(talks).reduce(
			(acc, t) => acc.set(t, (acc.get(t) ?? 0) + 1),
			new Map<string, number>(),
		),
	].sort((a, b) => b[1] - a[1]);
}
