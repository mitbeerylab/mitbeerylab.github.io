import { defineCollection, z } from "astro:content";

function removeDupsAndLowerCase(array: string[]) {
	if (!array.length) return array;
	const lowercaseItems = array.map((str) => str.toLowerCase());
	const distinctItems = new Set(lowercaseItems);
	return Array.from(distinctItems);
}

const publication = defineCollection({
	schema: ({ image }) =>
		z.object({
			authors: z.array(
				z.union([
					z.string(),
					z.object({
						link: z.string().url().optional(),
						name: z.string(),
					}),
				])
			),
			coverImage: z
				.object({
					alt: z.string(),
					src: image(),
				})
				.optional(),
			description: z.string().min(50).max(160).optional(),
			draft: z.boolean().default(false),
			external: z.string().url().optional(),
			ogImage: z.string().optional(),
			publishDate: z
				.string()
				.or(z.date())
				.transform((val) => new Date(val)),
			tags: z.array(z.string()).default([]).transform(removeDupsAndLowerCase),
			thumbnail: image(),
			title: z.string().max(120),
			updatedDate: z
				.string()
				.optional()
				.transform((str) => (str ? new Date(str) : undefined)),
			venue: z.string()
		}),
	type: "content",
});

const teaching = defineCollection({
	schema: ({ image }) =>
		z.object({
			coverImage: z
				.object({
					alt: z.string(),
					src: image(),
				})
				.optional(),
			description: z.string().min(50).max(160).optional(),
			draft: z.boolean().default(false),
			external: z.string().url().optional(),
			ogImage: z.string().optional(),
			publishDate: z
				.string()
				.or(z.date())
				.transform((val) => new Date(val)),
			tags: z.array(z.string()).default([]).transform(removeDupsAndLowerCase),
			title: z.string().max(120),
			updatedDate: z
				.string()
				.optional()
				.transform((str) => (str ? new Date(str) : undefined)),
		}),
	type: "content",
});

const people = defineCollection({
	schema: ({ image }) =>
		z.object({
			draft: z.boolean().default(false),
			image: image(),
			links: z.array(z.object({
				href: z.string(),
				icon: z.string(),
				label: z.string(),
			})).optional(),
			name: z.string(),
			order: z.number().default(0),
			position: z.string(),
		}),
	type: "content",
});

const talk = defineCollection({
	schema: ({ image }) =>
		z.object({
			coverImage: z
				.object({
					alt: z.string(),
					src: image(),
				})
				.optional(),
			description: z.string().min(50).max(160).optional(),
			draft: z.boolean().default(false),
			external: z.string().url().optional(),
			host: z.string().max(120),
			ogImage: z.string().optional(),
			publishDate: z
				.string()
				.or(z.date())
				.transform((val) => new Date(val)),
			tags: z.array(z.string()).default([]).transform(removeDupsAndLowerCase),
			title: z.string().max(120),
			updatedDate: z
				.string()
				.optional()
				.transform((str) => (str ? new Date(str) : undefined)),
		}),
	type: "content",
});

const albums = defineCollection({
	schema: ({ image }) =>
	  z.object({
		cover: image(),
		description: z.string().optional(),
		draft: z.boolean().default(false),
		title: z.string(),
	  }),
	type: "data",
  });

export const collections = { albums, people, publication, talk, teaching };
