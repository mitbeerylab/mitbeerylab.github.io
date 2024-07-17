import { siteConfig } from "@/site-config";
import { type CollectionEntry, getCollection } from "astro:content";

/** filter out draft teaching based on the environment */
export async function getAllTeaching(noExternal=false) {
	return await getCollection("teaching", ({ data }) => {
		return (import.meta.env.PROD ? !data.draft : true) && (!noExternal || !data.external);
	});
}

/** returns the date of the teaching based on option in siteConfig.sortTeachingByUpdatedDate */
export function getTeachingSortDate(teaching: CollectionEntry<"teaching">) {
	return siteConfig.sortTeachingByUpdatedDate && teaching.data.updatedDate !== undefined
		? new Date(teaching.data.updatedDate)
		: new Date(teaching.data.publishDate);
}

/** sort teaching by date (by siteConfig.sortTeachingByUpdatedDate), desc.*/
export function sortMDByDate(teaching: CollectionEntry<"teaching">[]) {
	return teaching.sort((a, b) => {
		const aDate = getTeachingSortDate(a).valueOf();
		const bDate = getTeachingSortDate(b).valueOf();
		return bDate - aDate;
	});
}

/** groups teaching by year (based on option siteConfig.sortTeachingByUpdatedDate), using the year as the key
 *  Note: This function doesn't filter draft teaching, pass it the result of getAllTeaching above to do so.
 */
export function groupTeachingByYear(teaching: CollectionEntry<"teaching">[]) {
	return teaching.reduce<Record<string, CollectionEntry<"teaching">[]>>((acc, teaching) => {
		const year = getTeachingSortDate(teaching).getFullYear();
		if (!acc[year]) {
			acc[year] = [];
		}
		acc[year].push(teaching);
		return acc;
	}, {});
}

/** returns all tags created from teaching (inc duplicate tags)
 *  Note: This function doesn't filter draft teaching, pass it the result of getAllTeaching above to do so.
 *  */
export function getAllTags(teaching: CollectionEntry<"teaching">[]) {
	return teaching.flatMap((teaching) => [...teaching.data.tags]);
}

/** returns all unique tags created from teaching
 *  Note: This function doesn't filter draft teaching, pass it the result of getAllTeaching above to do so.
 *  */
export function getUniqueTags(teaching: CollectionEntry<"teaching">[]) {
	return [...new Set(getAllTags(teaching))];
}

/** returns a count of each unique tag - [[tagName, count], ...]
 *  Note: This function doesn't filter draft teaching, pass it the result of getAllTeaching above to do so.
 *  */
export function getUniqueTagsWithCount(teaching: CollectionEntry<"teaching">[]): [string, number][] {
	return [
		...getAllTags(teaching).reduce(
			(acc, t) => acc.set(t, (acc.get(t) ?? 0) + 1),
			new Map<string, number>(),
		),
	].sort((a, b) => b[1] - a[1]);
}
