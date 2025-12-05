import { siteConfig } from "@/site-config";
import { type CollectionEntry, getCollection } from "astro:content";

type ContentTalkEntry = CollectionEntry<"talk">;
export type TalkEntry = Omit<ContentTalkEntry, "id" | "slug"> & {
	id: string;
	slug: string;
};

type GoogleCell = { f?: string | null; v?: unknown };
type GoogleRow = { c?: GoogleCell[] };
type GoogleSheetResponse = { table?: { rows?: GoogleRow[] } };

type SheetTalkRow = {
	external?: string;
	host: string;
	publishDate: Date;
	speaker: string;
	title: string;
};

const GOOGLE_SHEET_GVIZ_URL =
	"https://docs.google.com/spreadsheets/d/1bPZ0LF_fTdVH5r650iiHv2MoYqLB0FF_t0C0ThH1KIA/gviz/tq?tqx=out:json";

let sheetRowCache: SheetTalkRow[] | null = null;

// Synthetic sheet-backed entries are list-only, so render can be a no-op.
const emptyRender: TalkEntry["render"] = async () =>
	({
		Content: () => null,
		headings: [] as Awaited<ReturnType<TalkEntry["render"]>>["headings"],
		remarkPluginFrontmatter: {},
	} as unknown as Awaited<ReturnType<TalkEntry["render"]>>);

function normalizeCellValue(cell?: GoogleCell) {
	if (!cell) return "";
	const raw = cell.v ?? cell.f;
	if (typeof raw === "string") return raw.trim();
	if (raw === null || raw === undefined) return "";
	return String(raw).trim();
}

function parseSheetDate(cell?: GoogleCell): Date | null {
	if (!cell) return null;
	const raw = (cell.v ?? cell.f) as string | number | undefined;
	if (!raw) return null;
	if (typeof raw === "string") {
		const match = raw.match(/Date\((\d+),(\d+),(\d+)\)/);
		if (match) {
			const [, year, month, day] = match;
			return new Date(Number(year), Number(month), Number(day));
		}
		const parsed = new Date(raw);
		return Number.isNaN(parsed.valueOf()) ? null : parsed;
	}
	const parsed = new Date(raw);
	return Number.isNaN(parsed.valueOf()) ? null : parsed;
}

function parseSheetResponse(text: string): SheetTalkRow[] {
	const match = text.match(/setResponse\((.*)\);?/s);
	if (!match || !match[1]) return [];
	const parsed = JSON.parse(match[1]) as GoogleSheetResponse;
	const rows = parsed.table?.rows ?? [];
	return rows.flatMap((row) => {
		const cells = row.c ?? [];
		const title = normalizeCellValue(cells[0]);
		const speaker = normalizeCellValue(cells[1]);
		const host = normalizeCellValue(cells[2]);
		const publishDate = parseSheetDate(cells[3]);
		const external = normalizeCellValue(cells[4]);

		if (!title || !speaker || !host || !publishDate) return [];

		const sheetRow: SheetTalkRow = {
			host,
			publishDate,
			speaker,
			title,
		};
		if (external) sheetRow.external = external;

		return [sheetRow];
	});
}

async function getSheetRows(): Promise<SheetTalkRow[]> {
	if (sheetRowCache) return sheetRowCache;
	try {
		const response = await fetch(GOOGLE_SHEET_GVIZ_URL);
		if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
		const body = await response.text();
		sheetRowCache = parseSheetResponse(body);
		return sheetRowCache;
	} catch (error) {
		console.warn(
			`Failed to load talks from Google Sheet: ${error instanceof Error ? error.message : String(error)}`,
		);
		sheetRowCache = [];
		return sheetRowCache;
	}
}

function buildSlug(title: string, usedSlugs: Set<string>) {
	const base = title
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/(^-|-$)/g, "")
		|| "talk";
	let slug = base;
	let suffix = 1;
	while (usedSlugs.has(slug)) {
		slug = `${base}-${suffix}`;
		suffix += 1;
	}
	usedSlugs.add(slug);
	return slug;
}

async function buildSheetTalkEntries(
	existingSlugs: Set<string>,
	existingExternals: Set<string>,
): Promise<TalkEntry[]> {
	const rows = await getSheetRows();
	const usedSlugs = new Set(existingSlugs);
	const usedExternals = new Set(existingExternals);

	const uniqueRows = rows.filter((row) => {
		if (!row.external) return true;
		if (usedExternals.has(row.external)) return false;
		usedExternals.add(row.external);
		return true;
	});

	return uniqueRows.map((row) => {
		const slug = buildSlug(row.title, usedSlugs);
		const data: TalkEntry["data"] = {
			draft: false,
			host: row.host,
			publishDate: row.publishDate,
			speaker: row.speaker,
			tags: [],
			title: row.title,
		};

		if (row.external) data.external = row.external;

		return {
			body: "",
			collection: "talk",
			data,
			id: `sheet-${slug}`,
			render: emptyRender,
			slug,
		} as TalkEntry;
	});
}

/** filter out draft talks based on the environment */
export async function getAllTalks(noExternal=false): Promise<TalkEntry[]> {
	const baseTalks = (await getCollection(
		"talk",
		({ data }) => (import.meta.env.PROD ? !data.draft : true),
	)) as TalkEntry[];
	const existingSlugs = new Set(baseTalks.map((talk) => talk.slug));
	const existingExternals = new Set(
		baseTalks
			.map((talk) => talk.data.external)
			.filter((external): external is string => Boolean(external)),
	);
	const sheetTalks = await buildSheetTalkEntries(existingSlugs, existingExternals);
	const combined = [...baseTalks, ...sheetTalks];

	return noExternal ? combined.filter((talk) => !talk.data.external) : combined;
}

/** returns the date of the talk based on option in siteConfig.sortTalksByUpdatedDate */
export function getTalkSortDate(talk: TalkEntry) {
	return siteConfig.sortTalksByUpdatedDate && talk.data.updatedDate !== undefined
		? new Date(talk.data.updatedDate)
		: new Date(talk.data.publishDate);
}

/** sort talk by date (by siteConfig.sortTalksByUpdatedDate), desc.*/
export function sortMDByDate(talks: TalkEntry[]) {
	return talks.sort((a, b) => {
		const aDate = getTalkSortDate(a).valueOf();
		const bDate = getTalkSortDate(b).valueOf();
		return bDate - aDate;
	});
}

/** groups talks by year (based on option siteConfig.sortTalksByUpdatedDate), using the year as the key
 *  Note: This function doesn't filter draft talks, pass it the result of getAllTalks above to do so.
 */
export function groupTalksByYear(talks: TalkEntry[]) {
	return talks.reduce<Record<string, TalkEntry[]>>((acc, talk) => {
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
export function getAllTags(talks: TalkEntry[]) {
	return talks.flatMap((talk) => [...talk.data.tags]);
}

/** returns all unique tags created from talks
 *  Note: This function doesn't filter draft talks, pass it the result of getAllTalks above to do so.
 *  */
export function getUniqueTags(talks: TalkEntry[]) {
	return [...new Set(getAllTags(talks))];
}

/** returns a count of each unique tag - [[tagName, count], ...]
 *  Note: This function doesn't filter draft talks, pass it the result of getAllTalks above to do so.
 *  */
export function getUniqueTagsWithCount(talks: TalkEntry[]): [string, number][] {
	return [
		...getAllTags(talks).reduce(
			(acc, t) => acc.set(t, (acc.get(t) ?? 0) + 1),
			new Map<string, number>(),
		),
	].sort((a, b) => b[1] - a[1]);
}
