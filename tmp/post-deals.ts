// Posts the best new PC game deals to your Discord #daily-deals channel and to
// Bluesky. Runs on a schedule (see supabase/migrations/20261027010000_social.sql)
// and never posts the same deal twice within 7 days.
//
// Secrets (supabase secrets set NAME=value):
//   DISCORD_DEALS_WEBHOOK  printed by social/discord/setup_server.py
//   BLUESKY_HANDLE         e.g. steelgames.bsky.social        (optional)
//   BLUESKY_APP_PASSWORD   Bluesky → Settings → App passwords (optional, never your real password)
//   WEBSITE_URL            e.g. https://steelgamesapp.github.io
//
// Deploy: supabase functions deploy post-deals   (the schedule calls it with the public anon key)
import { createClient } from "jsr:@supabase/supabase-js@2";

const DEALS_PER_RUN = 3;
const MIN_DISCOUNT = 50;  // percent
const STORES = "1,3,7,11,15,25"; // Steam, Green Man Gaming, GOG, Humble, Fanatical, Epic

type Deal = {
  title: string; dealID: string; storeID: string; gameID: string;
  salePrice: string; normalPrice: string; savings: string; thumb: string; steamRatingPercent?: string; steamAppID?: string | null;
};

const STORE_NAMES: Record<string, string> = { "3": "Green Man Gaming", "1": "Steam", "7": "GOG", "11": "Humble", "15": "Fanatical", "25": "Epic" };
const money = (v: string) => `$${Number(v).toFixed(2)}`;

// Store commission links, as a JSON secret AFFILIATE_TEMPLATES, e.g.
// {"3":"https://greenmangaming.sjv.io/c/A/B/C?u={url}","15":"https://www.awin1.com/cread.php?awinmid=M&awinaffid=Y&ued={url}"}
function storePage(d: Deal): string {
  const q = encodeURIComponent(d.title);
  switch (d.storeID) {
    case "1": return d.steamAppID && d.steamAppID !== "0" ? `https://store.steampowered.com/app/${d.steamAppID}/` : `https://store.steampowered.com/search/?term=${q}`;
    case "3": return `https://www.greenmangaming.com/search/?query=${q}`;
    case "7": return `https://www.gog.com/en/games?query=${q}`;
    case "11": return `https://www.humblebundle.com/store/search?search=${q}`;
    case "15": return `https://www.fanatical.com/en/search?search=${q}`;
    case "25": return `https://store.epicgames.com/en-US/browse?q=${q}&sortBy=relevancy&sortDir=DESC`;
    default: return `https://www.cheapshark.com/redirect?dealID=${d.dealID}`;
  }
}
function buyLink(d: Deal): string {
  let templates: Record<string, string> = {};
  try { templates = JSON.parse(Deno.env.get("AFFILIATE_TEMPLATES") ?? "{}"); } catch { /* ignore */ }
  const page = storePage(d); const t = templates[d.storeID];
  return t ? t.replace("{url}", encodeURIComponent(page)).replace("{title}", encodeURIComponent(d.title)) : page;
}

const MIN_HOURS_BETWEEN_RUNS = 3; // extra calls inside this window do nothing

Deno.serve(async () => {
  const admin = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);

  // Whoever calls this, it posts at most once every few hours.
  const { data: last } = await admin.from("posted_deals").select("posted_at")
    .order("posted_at", { ascending: false }).limit(1);
  if (last?.[0] && Date.now() - Date.parse(last[0].posted_at) < MIN_HOURS_BETWEEN_RUNS * 3600e3) {
    return new Response("Too soon");
  }
  if (!Deno.env.get("DISCORD_DEALS_WEBHOOK") && !Deno.env.get("BLUESKY_APP_PASSWORD")) {
    return new Response("No destinations set yet");
  }
  const website = Deno.env.get("WEBSITE_URL") ?? "https://steelgamesapp.github.io/app";

  const url = `https://www.cheapshark.com/api/1.0/deals?storeID=${STORES}&onSale=1&sortBy=Deal%20Rating&pageSize=30`;
  const deals: Deal[] = await (await fetch(url)).json();

  const { data: recent } = await admin.from("posted_deals").select("game_id")
    .gte("posted_at", new Date(Date.now() - 7 * 864e5).toISOString());
  const seen = new Set((recent ?? []).map((r) => r.game_id));

  const fresh: Deal[] = [];
  for (const d of deals) {
    if (fresh.length >= DEALS_PER_RUN) break;
    if (seen.has(d.gameID) || Math.round(Number(d.savings)) < MIN_DISCOUNT) continue;
    seen.add(d.gameID);
    fresh.push(d);
  }
  if (fresh.length === 0) return new Response("Nothing new");

  const results: string[] = [];

  // Discord: one message with an embed per deal.
  const webhook = Deno.env.get("DISCORD_DEALS_WEBHOOK");
  if (webhook) {
    const embeds = fresh.map((d) => ({
      title: d.title,
      url: buyLink(d),
      color: 0xff7a1a,
      description: `**${money(d.salePrice)}** ~~${money(d.normalPrice)}~~ · **-${Math.round(Number(d.savings))}%** at ${STORE_NAMES[d.storeID] ?? "store"}`,
      thumbnail: { url: d.thumb },
      footer: { text: "Official/authorized store price · compare every store in the Steel Games app" },
    }));
    const res = await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: "Steel Games Deals",
        content: website ? `🔥 New price drops · track any game: ${website}` : "🔥 New price drops",
        embeds,
        allowed_mentions: { parse: [] },
      }),
    });
    results.push(`discord ${res.status}`);
  }

  // Bluesky: one post per run, listing the deals, with a clickable website link.
  const handle = Deno.env.get("BLUESKY_HANDLE") ?? "steelgames.bsky.social";
  const appPassword = Deno.env.get("BLUESKY_APP_PASSWORD");
  if (handle && appPassword) {
    try {
      results.push(await postToBluesky(handle, appPassword, fresh, website));
    } catch (e) {
      results.push(`bluesky error ${e}`);
    }
  }

  await admin.from("posted_deals").insert(
    fresh.map((d) => ({ game_id: d.gameID, title: d.title, price: Number(d.salePrice) })),
  );

  return new Response(results.join("\n"));
});

async function postToBluesky(handle: string, appPassword: string, deals: Deal[], website: string) {
  const session = await (await fetch("https://bsky.social/xrpc/com.atproto.server.createSession", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identifier: handle, password: appPassword }),
  })).json();
  if (!session.accessJwt) throw new Error("Bluesky sign-in failed");

  const lines = deals.map((d) =>
    `• ${d.title}: ${money(d.salePrice)} (-${Math.round(Number(d.savings))}%) on ${STORE_NAMES[d.storeID] ?? "PC"}`
  );
  let text = `🔥 PC game price drops\n${lines.join("\n")}`;
  // Bluesky allows 300 characters; trim the list if needed.
  while ([...text].length > 240 && lines.length > 1) {
    lines.pop();
    text = `🔥 PC game price drops\n${lines.join("\n")}`;
  }
  const facets = [];
  if (website) {
    const before = new TextEncoder().encode(text + "\n").length;
    text += `\n${website}`;
    facets.push({
      index: { byteStart: before, byteEnd: before + new TextEncoder().encode(website).length },
      features: [{ $type: "app.bsky.richtext.facet#link", uri: website }],
    });
  }

  const res = await fetch("https://bsky.social/xrpc/com.atproto.repo.createRecord", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${session.accessJwt}` },
    body: JSON.stringify({
      repo: session.did,
      collection: "app.bsky.feed.post",
      record: { $type: "app.bsky.feed.post", text, facets, createdAt: new Date().toISOString(), langs: ["en"] },
    }),
  });
  return `bluesky ${res.status}`;
}
