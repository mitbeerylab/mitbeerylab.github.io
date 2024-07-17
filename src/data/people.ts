import { getCollection } from "astro:content";

/** filter out draft people based on the environment */
export async function getAllPeople() {
	const people = await getCollection("people", ({ data }) => {
		return import.meta.env.PROD ? !data.draft : true;
	});
	const peopleSorted = [...people].sort((a, b) => a.data.order - b.data.order)
	return peopleSorted;
}