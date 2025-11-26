import { siteConfig } from "@/site-config";
import { type CollectionEntry, getCollection } from "astro:content";

type PublicationAuthor = CollectionEntry<"publication">["data"]["authors"][number];

/** filter out draft publications based on the environment */
export async function getAllPublications(noExternal=false, blog=false) {
	return await getCollection("publication", ({ data }) => {
		return (import.meta.env.PROD ? !data.draft : true) && (!noExternal || !data.external) && (data.blog === blog);
	});
}

/** returns the date of the publication based on option in siteConfig.sortPublicationsByUpdatedDate */
export function getPublicationSortDate(publication: CollectionEntry<"publication">) {
	return siteConfig.sortPublicationsByUpdatedDate && publication.data.updatedDate !== undefined
		? new Date(publication.data.updatedDate)
		: new Date(publication.data.publishDate);
}

/** sort publication by date (by siteConfig.sortPublicationsByUpdatedDate), desc.*/
export function sortMDByDate(publications: CollectionEntry<"publication">[]) {
	return publications.sort((a, b) => {
		const aDate = getPublicationSortDate(a).valueOf();
		const bDate = getPublicationSortDate(b).valueOf();
		return bDate - aDate;
	});
}

export async function getLabAuthorSlugs() {
	const peopleEntries = await getCollection("people", ({ data }) => {
		return import.meta.env.PROD ? !data.draft : true;
	});
	return new Set(peopleEntries.map((person) => person.slug));
}

function getAuthorSlug(author: PublicationAuthor) {
	if (typeof author === "string") {
		return author.startsWith("~") ? author.slice(1) : undefined;
	}
	if (!author.ref) return undefined;
	return author.ref.startsWith("~") ? author.ref.slice(1) : author.ref;
}

export function getLabAuthorCount(
	publication: CollectionEntry<"publication">,
	labAuthorSlugs: Set<string>,
) {
	return publication.data.authors.reduce((count, author) => {
		const slug = getAuthorSlug(author);
		return slug && labAuthorSlugs.has(slug) ? count + 1 : count;
	}, 0);
}

/** groups publications by year (based on option siteConfig.sortPublicationsByUpdatedDate), using the year as the key
 *  Note: This function doesn't filter draft publications, pass it the result of getAllPublications above to do so.
 */
export function groupPublicationsByYear(publications: CollectionEntry<"publication">[]) {
	return publications.reduce<Record<string, CollectionEntry<"publication">[]>>((acc, publication) => {
		const year = getPublicationSortDate(publication).getFullYear();
		if (!acc[year]) {
			acc[year] = [];
		}
		acc[year].push(publication);
		return acc;
	}, {});
}

/** returns all tags created from publications (inc duplicate tags)
 *  Note: This function doesn't filter draft publications, pass it the result of getAllPublications above to do so.
 *  */
export function getAllTags(publications: CollectionEntry<"publication">[]) {
	return publications.flatMap((publication) => [...publication.data.tags]);
}

/** returns all unique tags created from publications
 *  Note: This function doesn't filter draft publications, pass it the result of getAllPublications above to do so.
 *  */
export function getUniqueTags(publications: CollectionEntry<"publication">[]) {
	return [...new Set(getAllTags(publications))];
}

/** returns a count of each unique tag - [[tagName, count], ...]
 *  Note: This function doesn't filter draft publications, pass it the result of getAllPublications above to do so.
 *  */
export function getUniqueTagsWithCount(publications: CollectionEntry<"publication">[]): [string, number][] {
	return [
		...getAllTags(publications).reduce(
			(acc, t) => acc.set(t, (acc.get(t) ?? 0) + 1),
			new Map<string, number>(),
		),
	].sort((a, b) => b[1] - a[1]);
}

export async function getFeaturedPublications(noExternal = false, blog = false) {
	const publications = await getAllPublications(noExternal, blog);
	const labAuthorSlugs = await getLabAuthorSlugs();
	return publications.filter((publication) => getLabAuthorCount(publication, labAuthorSlugs) >= 2);
}
