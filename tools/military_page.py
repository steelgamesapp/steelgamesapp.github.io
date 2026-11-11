"""Veteran and first responder discounts page for SteelGames (static content, no live data)."""
import html
import layout

SITE = layout.SITE
CHECKED = "October 31, 2026"

# Each entry only states what a brand page or public source reported. Amounts can change.
# who: "mil" = military/veterans, "fr" = first responders (police, fire, EMS).
BRANDS = [
    {"name": "Razer", "cat": "Peripherals & PCs", "c": "#5CE08A", "url": "https://www.razer.com/campaigns/heroes", "who": ["mil", "fr"],
     "desc": "The Razer Heroes Program covers active duty, retirees, veterans, military spouses and family, plus active police, firefighters and EMTs (and medical providers). US only. Reported at 15% off peripherals and accessories and 5% off desktops and laptops, verified through ID.me. Codes are single-use, last one month and exclude refurbished items.",
     "tags": ["15% peripherals", "5% PCs", "ID.me"]},
    {"name": "Dell", "cat": "PCs", "c": "#66C0F4", "url": "https://www.dell.com/en-us/lp/govx", "who": ["mil", "fr"],
     "desc": "Dell's Heroes program covers military, veterans and retirees, police, firefighters, EMTs, search and rescue, and healthcare workers in the US. Dell advertises up to 10% extra off eligible products on Dell.com, limited to two products per order and two orders a year. Verification runs through SheerID.",
     "tags": ["Up to 10%", "SheerID", "2 orders/yr"]},
    {"name": "ORIGIN PC", "cat": "Gaming PCs", "c": "#B388FF", "url": "https://www.originpc.com", "who": ["mil", "fr"],
     "desc": "Custom-built gaming desktops and laptops. ORIGIN PC announced a 2.5% ID.me discount in 2022 for military, government workers, nurses, first responders, teachers and students. Confirm it is still active before you order.",
     "tags": ["2.5% (2022)", "ID.me"]},
    {"name": "Glorious", "cat": "Peripherals", "c": "#FFB020", "url": "https://www.gloriousgaming.com", "who": ["mil"],
     "desc": "Mice, keyboards and desk gear from a Dallas-based brand. Its Heroes Discount Program gave 10% off to verified active-duty military and veterans through ID.me (announced May 2024).",
     "tags": ["10% reported", "ID.me"]},
    {"name": "Corsair", "cat": "PC parts", "c": "#FFD76A", "url": "https://www.corsair.com", "who": ["mil"],
     "desc": "Cases, coolers, memory and peripherals for builders. Corsair offers a military discount through ID.me verification. Past offers have been around 5% off qualifying purchases.",
     "tags": ["ID.me", "~5% past offers"]},
    {"name": "Lenovo", "cat": "PCs", "c": "#FF6B8A", "url": "https://www.lenovo.com", "who": ["mil"],
     "desc": "Laptops and desktops for US military, reservists, veterans and their immediate families. Lenovo also ships to APO, FPO and DPO addresses.",
     "tags": ["Families eligible", "APO/FPO shipping"]},
    {"name": "Xotic PC", "cat": "Gaming PCs", "c": "#4DD0E1", "url": "https://www.xoticpc.com", "who": ["mil"],
     "desc": "Custom gaming laptops and desktops. Listed by the Kansas Office of Veterans Services (verified February 2026) as offering special pricing for veterans. Ask them for the current amount.",
     "tags": ["Special veteran pricing"]},
    {"name": "Vertagear", "cat": "Chairs", "c": "#FF8A3D", "url": "https://www.vertagear.com", "who": ["mil"],
     "desc": "Gaming chairs and accessories. The Military Appreciation Program is reported at 20% off. You fill out a form with your name, email and a copy of your DD-214.",
     "tags": ["20% reported", "DD-214 form"]},
    {"name": "Chairs4Gaming", "cat": "Chairs & desks", "c": "#5CE08A", "url": "https://www.chairs4gaming.com", "who": ["mil"],
     "desc": "Gaming chairs, desks and accessories. Reported at 15% off after a quick verification, which gives you a one-time code. It does not apply to Black Friday, Cyber Monday or holiday sales.",
     "tags": ["15% reported", "Not valid Black Friday"]},
    {"name": "Skullcandy", "cat": "Audio", "c": "#66C0F4", "url": "https://www.skullcandy.com", "who": ["mil"],
     "desc": "Headsets and earbuds. Skullcandy offers military discounts and cash back on gaming audio when you verify with ID.me.",
     "tags": ["ID.me", "Cash back"]},
    {"name": "GameStop", "cat": "Games & collectibles", "c": "#FF6B8A", "url": "https://www.gamestop.com/military-discount", "who": ["mil"],
     "desc": "Limited. GameStop gives active military 10% off toys, collectibles and pre-owned items in store only. New games, new accessories, consoles and PC hardware are excluded.",
     "tags": ["10% in store", "Many exclusions"]},
]

STAR = ('<svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        'stroke-linejoin="round" aria-hidden="true"><path d="M12 2l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 15.4l-5.3 3 1.2-6L3.4 8.3l6-.7z"/></svg>')

TIPS = [
    "Verification usually runs through ID.me, SheerID or GovX. Set up an ID.me account once and several of these brands accept it.",
    "Some brands ask for a DD-214 instead. Keep a clean copy on hand so you can upload it.",
    "Codes often can't be combined with other offers, and many are blocked on Black Friday and Cyber Monday. Compare the sale price against your code price.",
    "Terms change often. Check the brand's program page before you check out, and send us a note if something is out of date.",
]

FILTER_JS = """<script>
(function(){var chips=document.querySelectorAll('#who button');var cards=document.querySelectorAll('.scard[data-who]');
function show(w){cards.forEach(function(c){c.hidden=!(w==='all'||c.dataset.who.split(' ').indexOf(w)>-1);});
chips.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.w===w?'true':'false');});}
chips.forEach(function(b){b.addEventListener('click',function(){show(b.dataset.w);});});show('all');})();
</script>
"""


def card(b):
    e = html.escape
    tags = "".join(f"<span>{e(t)}</span>" for t in b["tags"])
    return (f'<a class="scard" data-who="{" ".join(b["who"])}" style="--c:{b["c"]}" href="{e(b["url"])}" target="_blank" rel="noopener noreferrer">'
            f'<span class="ph">{STAR}</span><h3>{e(b["name"])}</h3><p>{e(b["desc"])}</p>'
            f'<span class="tags"><span>{e(b["cat"])}</span>{tags}</span><span class="go">See the program &rarr;</span></a>')


def best_for_game_html():
    """Compact callout used on game pages."""
    return ('<div class="vetbox"><strong>Veteran, military family or first responder?</strong> '
            'Razer, Dell and ORIGIN PC take extra off for those who serve, and our veterans page adds travel deals, free tickets and money help. '
            '<a href="/military.html">See veteran savings &rarr;</a></div>')


SAVINGS_CHECKED = "November 11, 2026"

# Savings and money help for veterans and their families. Every entry comes from the official page linked (or the
# official source named in the text), read on SAVINGS_CHECKED. Programs change: re-check before changing wording.
SAVINGS = [
    ("start", "Start here: prove you served", "One ID and one verification account unlock most of the offers below.", "#FFB020", [
        ("VA Veteran ID Card", "https://www.va.gov/records/get-veteran-id-cards/vic/",
         "A digital photo ID from VA that you can show for veteran discounts at stores, restaurants and hotels. It is for veterans who served on active duty, in the Reserves or in the National Guard (including the Coast Guard) with an honorable or general (under honorable conditions) discharge. Apply online with your DD214, a government photo ID and a color photo.",
         ["Digital ID", "DD214 needed"]),
        ("ID.me", "https://www.id.me",
         "Many stores check military status through ID.me. Veterans, retirees, spouses, surviving spouses and adult children or parents of service members can verify, so family members can often claim offers on their own.",
         ["Family can verify"]),
        ("GovX", "https://www.govx.com",
         "A members-only discount store for current and former military and other service groups. GovX says registration is free for life.",
         ["Free to join"]),
    ]),
    ("shopping", "Shopping and everyday discounts", "Tax-free exchange shopping, home store discounts and phone plans.", "#5CE08A", [
        ("Military exchanges online (tax-free)", "https://www.aafes.com/veterans/",
         "Honorably discharged veterans of every branch, including Guard and Reserve, can shop the military exchanges online with military pricing and no sales tax: shopmyexchange.com, mynavyexchange.com, mymcx.com and shopcgx.com. If asked, verify through VetVerify.org (up to 3 days). It covers the veteran only, online only, and does not give base access.",
         ["No sales tax", "Veteran only", "Online"]),
        ("Commissary and exchange in person", "https://corp.commissaries.com/Expanding-Access",
         "Since 2020, Purple Heart recipients, former POWs, all veterans with service-connected disabilities and approved VA family caregivers can shop in person at commissaries and exchanges and use MWR. Bring a VA Health ID Card showing PURPLE HEART, FORMER POW or SERVICE CONNECTED (or a VA letter plus a REAL ID) and pass the base visitor check.",
         ["Service-connected", "Caregivers", "In person"]),
        ("Lowe's", "https://www.lowes.com/l/about/honor-our-military",
         "10% off most full-priced items for current service members and veterans, with no yearly cap. A registered member's enrolled spouse can use it too. Sale items, major appliances and some other items are excluded. Sign up with ID.me and a MyLowe's Rewards account.",
         ["10%", "Spouse too", "ID.me"]),
        ("The Home Depot", "https://www.homedepot.com/c/military",
         "Home Depot advertises up to 10% off select in-stock items for the military. Its 2021 announcement extended it to all US veterans and spouses who register in the Home Depot app. Check the current terms in the app or at the register.",
         ["Up to 10%", "Check terms"]),
        ("T-Mobile", "https://www.t-mobile.com/cell-phone-plans/military-discount-plans",
         "Military Savings plans for people who serve or have served, such as 4 lines for $25 a month per line on its T-Mix plan, plus fees. The service member must be the account holder and show proof at activation.",
         ["4 lines at $25/line", "Family lines"]),
        ("Verizon", "https://www.verizon.com/military/",
         "10% off mobile plans for active duty, retirees, veterans, current or former Guard and Reserve, and Gold Star family members, verified through ID.me.",
         ["10%", "Gold Star families"]),
        ("AT&T", "https://www.att.com/offers/discount-program/military-discount/",
         "For veterans, active-duty service members, reservists and military family members: 10% off Value 2.0, 15% off Extra 2.0 and 20% off Premium 2.0 plans, per line on up to 10 lines.",
         ["10% to 20%", "Up to 10 lines"]),
    ]),
    ("travel", "Travel and vacations", "Military travel deals and resorts, and who can actually book them.", "#66C0F4", [
        ("American Forces Travel", "https://www.militaryonesource.mil/recreation-travel-shopping/travel-lodging/american-forces-travel-discounts/",
         "The official MWR travel site for discounted hotels, flights, rental cars, cruises and vacation packages. Military OneSource says its shopping privileges include honorably discharged veterans and eligible family members. The site checks DEERS, or you can verify through VetVerify.",
         ["Veterans eligible", "Hotels, cruises, cars"]),
        ("Shades of Green at Walt Disney World", "https://www.shadesofgreen.org/about-shades-green/eligibility",
         "The military resort at Walt Disney World. Under its Salute to Our Veterans program, every honorably discharged veteran can stay in January and September, subject to availability, with a current DD214. Veterans rated 100% service-connected, VA Health ID Card holders (Purple Heart, former POW, service-connected) and VA caregivers can stay all year.",
         ["Disney World", "Jan and Sept for all veterans"]),
        ("Armed Forces Vacation Club", "https://www.armymwr.com/travel/armed-forces-vacation-club",
         "Week-long resort condo stays for $349 a week, according to Army MWR, in units that sleep 2 to 8. Army MWR lists active duty, Guard, Reserve and retired members, and VA has also named Gold Star families. It does not say every veteran qualifies, so check afvclub.com before you plan.",
         ["$349 a week", "Retirees", "Check eligibility"]),
        ("Hale Koa (Hawaii) and Edelweiss (Germany)", "https://www.halekoa.com/about-hale-koa-hotel/eligibility",
         "The Hale Koa hotel in Honolulu takes honorably discharged veterans with a 100 percent service-connected disability, Purple Heart recipients, former POWs, service-connected VA Health ID Card holders and caregivers. Edelweiss Lodge in Germany takes veterans rated 100% service-connected and retirees, but not the other groups.",
         ["Hawaii", "Germany", "Disabled veterans"]),
    ]),
    ("tickets", "Tickets, parks and days out", "Free park passes, free event tickets, and the theme park fine print.", "#B388FF", [
        ("Free lifetime national parks pass", "https://www.nps.gov/planyourvisit/veterans-and-gold-star-families-free-access.htm",
         "Veterans and Gold Star families get a free lifetime pass to national parks and other federal lands. It is free in person or as a digital pass on Recreation.gov; a mailed pass costs a small fee. Bring a VA Health ID Card, VA Veteran ID Card, a driver's license or state ID marked veteran, or a DD Form 2. Gold Star families print a voucher from the park service site.",
         ["Free", "Gold Star families"]),
        ("Vet Tix", "https://www.vettix.org",
         "Free tickets to sports, concerts and shows for currently serving members, honorably discharged veterans and families of those killed in action, plus Gold Star next of kin and some surviving spouses. Members pay a small delivery fee. Verify through ID.me or the Vet Tix team.",
         ["Free tickets", "Families of the fallen"]),
        ("SeaWorld San Antonio Military Silver Pass", "https://seaworld.com/san-antonio/tickets/military-discount/veterans/",
         "Open to US military veterans and retirees who served honorably, verified through ID.me. Check the page for the current price and blackout dates.",
         ["Texas", "Veterans", "ID.me"]),
        ("Disney and Universal: who qualifies", "https://disneyworld.disney.go.com/events-tours/veterans-day/",
         "Walt Disney World and Disneyland military tickets are for active and retired US military only, not every veteran. Universal Orlando's 2026 Military Freedom Pass, sold at Shades of Green, is for active duty, Guard and Reserve, retirees and 100% disabled veterans. If you don't fit, watch the parks' regular sales instead.",
         ["Retirees and active duty", "Know before you go"]),
    ]),
    ("money", "Home loans and money help", "VA home loan basics, where to compare rates, and state tax breaks.", "#FF8A3D", [
        ("VA home loan", "https://www.va.gov/housing-assistance/home-loans/loan-types/purchase-loan/",
         "A VA-backed purchase loan usually needs no down payment if the price is not above the appraised value, and there is no private mortgage insurance. With full entitlement there is no VA loan limit. Start with a Certificate of Eligibility (COE), which you can request online, through your lender or by mail.",
         ["No PMI", "No down payment for most"]),
        ("VA funding fee", "https://www.va.gov/housing-assistance/home-loans/funding-fee-and-closing-costs/",
         "A one-time fee you can pay at closing or roll into the loan. VA's chart (effective April 7, 2023) shows 2.15% for a first use with under 5% down, and less with a bigger down payment. Veterans who receive VA disability compensation, and surviving spouses who receive DIC, don't pay it.",
         ["Disability pay = no fee"]),
        ("Compare mortgage rates", "https://www.consumerfinance.gov/owning-a-home/explore-rates/",
         "Rates change every day, so we don't list them. The Consumer Financial Protection Bureau's free rate tool shows typical rates for VA loans by credit score, down payment and term. The CFPB says to get Loan Estimates from at least three lenders and compare the APR and fees, not just the rate.",
         ["Free government tool", "Compare 3 lenders"]),
        ("VA streamline refinance (IRRRL)", "https://www.va.gov/housing-assistance/home-loans/loan-types/interest-rate-reduction-loan/",
         "Already have a VA loan? An IRRRL refinances it to a lower rate, or from adjustable to fixed, through a private lender. VA suggests dividing the costs by your monthly savings to see how long it takes to break even. Be wary of mailers that promise skipped payments or rates that seem too good to be true.",
         ["Refinance", "Watch for scams"]),
        ("VA adaptive housing grants", "https://www.va.gov/housing-assistance/disability-housing-grants/",
         "For certain service-connected disabilities, VA grants help buy, build or change a home: up to $126,526 (SAH) or $25,350 (SHA) in fiscal year 2026.",
         ["Up to $126,526"]),
        ("Texas veteran property tax exemptions", "https://comptroller.texas.gov/taxes/property-tax/exemptions/disabledvet-faq.php",
         "Texas takes $5,000 to $12,000 off the taxable value of one property for veterans with a 10% to 100% disability rating, and a 100% rating or unemployability exempts the whole homestead. Some surviving spouses and children qualify. Apply with your county appraisal district by April 30.",
         ["Texas", "Up to the whole homestead"]),
        ("Texas Veterans Land Board home loans", "https://www.glo.texas.gov/veterans/home-loans",
         "Fixed-rate home loans up to $832,750 for Texas veterans with 90 or more days of active duty and an honorable, general or medical discharge, plus some surviving spouses. Veterans rated 30% or more get a discounted rate. Apply through a participating lender.",
         ["Texas", "Up to $832,750"]),
        ("Your state's veteran benefits", "https://nasdva.us/resources/",
         "Every state has its own veteran perks, such as property tax breaks, park passes and tuition help. This directory from the state veterans directors' association links to every state's veterans agency.",
         ["All states"]),
        ("Free tax filing (MilTax)", "https://www.militaryonesource.mil/financial-legal/taxes/miltax-military-tax-services/",
         "Free tax software and tax consultants from Military OneSource. Veterans can use it for 365 days after separation or retirement. The software for the next tax season opens in January 2027.",
         ["Free", "First year out"]),
        ("Veteran Readiness and Employment", "https://www.va.gov/careers-employment/vocational-rehabilitation/eligibility/",
         "Veterans with a VA disability rating of 10% or more (and not a dishonorable discharge) can get job training or school paid for, plus a monthly allowance.",
         ["10% rating or more", "Monthly allowance"]),
    ]),
    ("family", "For spouses and kids of veterans", "Education money, scholarships and the family side of the offers above.", "#FF6B8A", [
        ("Dependents' Educational Assistance (DEA)", "https://www.va.gov/family-and-caregiver-benefits/education-and-careers/dependents-education-assistance/",
         "Children and spouses of a veteran who is permanently and totally disabled from a service-connected condition, or who died from one or in the line of duty, can get up to 36 months of education benefits. For Oct 1, 2026 to Sept 30, 2027, VA pays $1,621 a month for full-time school. Apply with VA Form 22-5490.",
         ["$1,621 a month full time", "Up to 36 months"]),
        ("Fry Scholarship", "https://www.va.gov/family-and-caregiver-benefits/education-and-careers/fry-scholarship/",
         "For children and surviving spouses of service members who died in the line of duty on or after Sept 11, 2001: up to 36 months of tuition, housing and book money.",
         ["Tuition, housing, books"]),
        ("Pass on the GI Bill (while serving)", "https://www.va.gov/education/transfer-post-9-11-gi-bill-benefits/",
         "A parent can transfer Post-9/11 GI Bill benefits to a spouse or child only while still serving, with at least 6 years in and an agreement to serve 4 more. After separation it is too late, so tell family members who still serve.",
         ["Plan while serving"]),
        ("Folds of Honor scholarships", "https://foldsofhonor.org/scholarships/",
         "Scholarships for spouses and children of fallen or disabled service members: up to $2,500 per term for college and up to $5,000 for private K-12 school. Applications open Feb 1 to Mar 31 each year.",
         ["Opens Feb 1", "Fallen or disabled"]),
        ("Scholarships for Military Children", "https://corp.commissaries.com/Scholarship",
         "$2,000 scholarships (500 awarded for 2026-27) for unmarried military children under 23 with a military ID card whose parent is active duty, Guard or Reserve, retired or deceased. The last deadline was in February, so watch for the next cycle.",
         ["$2,000 awards", "Retirees' kids"]),
        ("Free scholarship search", "https://search.militaryscholar.org/",
         "A free scholarship search from Fisher House for service members, veterans, retirees and their families.",
         ["Free"]),
        ("Texas Hazlewood Legacy", "https://tvc.texas.gov/education/hazlewood/",
         "Texas veterans may be able to pass unused Hazlewood college tuition hours to a child through the Hazlewood Legacy Program. Check the Texas Veterans Commission for the current rules before you plan on it.",
         ["Texas", "Check current rules"]),
    ]),
]

SAVINGS_CSS = """<style>
.rgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
@media (max-width:960px){.rgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:600px){.rgrid{grid-template-columns:minmax(0,1fr)}}
.rcard{--c:#66C0F4;display:flex;flex-direction:column;gap:8px;padding:16px;border-radius:16px;background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--c);text-decoration:none;color:#fff;transition:transform .15s ease,border-color .15s ease}
.rcard:hover{transform:translateY(-3px);border-color:var(--c);color:#fff}
.rcard h3{font-size:18px}
.rcard p{font-size:15px;color:var(--steel);flex:1}
.rcard .tags{display:flex;gap:6px;flex-wrap:wrap}
.rcard .tags span{font-size:12px;font-weight:600;padding:3px 9px;border-radius:999px;background:rgba(255,255,255,.08);color:var(--steel)}
.rcard .go{font-weight:700;font-size:14px;color:var(--c)}
.vet-hero{background:radial-gradient(120% 140% at 85% 0%,rgba(255,176,32,.18),transparent 60%),radial-gradient(100% 120% at 0% 100%,rgba(102,192,244,.14),transparent 60%)}
.vet-note{margin-top:14px;padding:14px 16px;border-radius:14px;background:var(--surface);border:1px solid var(--line);font-size:15px;color:var(--steel)}
.sec-sub{color:var(--muted);margin:6px 0 16px}
</style>
"""


def rcard(name, url, desc, tags, color):
    e = html.escape
    t = "".join(f"<span>{e(x)}</span>" for x in tags)
    return (f'<a class="rcard" style="--c:{color}" href="{e(url)}" target="_blank" rel="noopener noreferrer">'
            f'<h3>{e(name)}</h3><p>{e(desc)}</p><span class="tags">{t}</span><span class="go">Official page &rarr;</span></a>')


def build():
    title = "Veteran Discounts, Travel, Free Tickets and Money Help for Veterans and Families | SteelGames"
    desc = ("Savings for veterans and their families from a veteran-owned site: military discounts, tax-free exchange shopping, "
            "travel deals, free park passes and event tickets, VA home loan basics, and education money for veterans' kids.")
    url = f"{SITE}/military.html"
    e = html.escape
    tips = "".join(f'<div class="tip"><b>{i}</b><p>{e(t)}</p></div>' for i, t in enumerate(TIPS, 1))
    mail = "mailto:steelgames.app@outlook.com?subject=Veteran%20savings%20tip"
    jump = "".join(f'<a href="#{sid}">{e(t.replace("Start here: prove you served", "Start here"))}</a>' for sid, t, _, _, _ in SAVINGS)
    sections = ""
    for sid, t, sub, color, items in SAVINGS:
        cards = "".join(rcard(n, u, d, tg, color) for n, u, d, tg in items)
        sections += (f'<section class="block" id="{sid}"><div class="wrap"><h2>{e(t)}</h2><p class="sec-sub">{e(sub)}</p>'
                     f'<div class="rgrid">{cards}</div></div></section>\n')
    return (layout.head(title, desc, url, SAVINGS_CSS)
            + layout.header("military")
            + f"""<main>
<section class="hero vet-hero"><div class="wrap">
<p class="eyebrow">Veteran-owned &middot; For veterans and their families</p>
<h1>Savings for veterans and their families</h1>
<p class="lede">Military discounts, tax-free exchange shopping, travel deals, free park passes and event tickets, VA home loan basics and education money for veterans' kids, in one place. SteelGames is veteran-owned, so this page is personal. Every card links to the official page, and we checked them on {SAVINGS_CHECKED}.</p>
<div class="chips">{jump}<a href="#gaming">Gaming discounts</a></div>
<p class="vet-note">SteelGames is not part of VA or the Department of Defense, and nothing here is financial or legal advice. Eligibility is set by each program and can change, so confirm on the official page before you plan or buy. These links are not affiliate links.</p>
</div></section>
{sections}<section class="block" id="gaming"><div class="wrap"><h2>Gaming discounts for veterans and first responders</h2>
<p class="fine">Brands that give service members, veterans, police, firefighters and EMTs a better price on gaming PCs, peripherals, chairs and audio. Amounts are as last reported by each brand or a public source (checked {CHECKED}). Confirm the current offer on the brand's page before you buy.</p>
<div class="chips" id="who" role="group" aria-label="Filter by who qualifies"><button type="button" data-w="all" aria-pressed="true">All</button><button type="button" data-w="mil" aria-pressed="false">Military &amp; veterans</button><button type="button" data-w="fr" aria-pressed="false">First responders</button></div>
<div class="sgrid">{"".join(card(b) for b in BRANDS)}</div></div></section>
<section class="block" id="verify"><div class="wrap"><h2>How to claim these discounts</h2>
<div class="tips">{tips}</div>
<div class="chips"><a href="https://www.va.gov/records/get-veteran-id-cards/vic/" target="_blank" rel="noopener noreferrer">VA Veteran ID Card</a><a href="https://www.id.me" target="_blank" rel="noopener noreferrer">ID.me</a><a href="https://www.govx.com" target="_blank" rel="noopener noreferrer">GovX</a></div></div></section>
<section class="block" id="tip"><div class="wrap"><h2>Know a program we missed?</h2>
<p class="lede">Tell us about a discount, travel deal or money program for veterans and their families, and we will check it on the official page and add it.</p>
<div class="chips"><a href="{mail}">Send a tip</a><a href="https://discord.gg/ekrRaejc6">Join the Discord</a></div></div></section>
</main>
{FILTER_JS}"""
            + layout.footer())


if __name__ == "__main__":
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    open(os.path.join(root, "military.html"), "w").write(build())
