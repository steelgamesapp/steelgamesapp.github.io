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
            '<a href="/military.html">Open the Veteran Hub &rarr;</a></div>')


SAVINGS_CHECKED = "November 11, 2026"

# Veteran Hub: savings and money help for veterans and their families. Every entry comes from the official page
# linked (or the official source named in the text), read on SAVINGS_CHECKED. Re-check before changing wording.
# who codes: vet = any honorably discharged veteran, dis = disabled / service-connected veterans,
# fam = spouses and kids, gs = Gold Star families and survivors, ret = retirees, tx = Texas, fr = first responders.
WHO = [("all", "Everyone"), ("vet", "Any veteran"), ("dis", "Disabled veterans"), ("fam", "Spouses and kids"),
       ("gs", "Gold Star and survivors"), ("ret", "Retirees"), ("tx", "Texas"), ("fr", "First responders")]

ICONS = {
    "start": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11.5" r="2.2"/><path d="M14 10h4M14 14h4M5.8 16.5c.8-1.3 1.9-2 3.2-2s2.4.7 3.2 2"/>',
    "shopping": '<path d="M6 7h12l1 13H5z"/><path d="M9 7a3 3 0 0 1 6 0"/>',
    "travel": '<path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4z"/>',
    "tickets": '<path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4z"/><path d="M14 7v2M14 11v2M14 15v2"/>',
    "money": '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "family": '<path d="m2 9 10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/><path d="M22 9v5"/>',
    "gaming": '<rect x="2" y="7" width="20" height="11" rx="5"/><path d="M7 10.5v4M5 12.5h4M16 11.5h.01M18 13.5h.01"/>',
    "gifts": '<rect x="3" y="9" width="18" height="12" rx="1.5"/><path d="M3 13h18M12 9v12"/><path d="M12 9C10 6 6.5 5.8 6.5 7.6 6.5 9 12 9 12 9zm0 0c2-3 5.5-3.2 5.5-1.4C17.5 9 12 9 12 9z"/>',
    "star": '<path d="M12 2l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 15.4l-5.3 3 1.2-6L3.4 8.3l6-.7z"/>',
}


def icon(name, size=22):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


# (id, title, short label, one-line intro, color, [(card id, name, url, you get, who qualifies, how, tags, who codes)])
SAVINGS = [
    ("start", "Start here: prove you served", "Start here", "One ID and one verification account unlock most of the offers in this hub.", "#FFB020", [
        ("vic", "VA Veteran ID Card", "https://www.va.gov/records/get-veteran-id-cards/vic/",
         "A digital photo ID from VA to show for veteran discounts at stores, restaurants and hotels.",
         "Veterans who served on active duty, in the Reserves or in the National Guard (including the Coast Guard) with an honorable or general discharge.",
         "Apply online with your DD214, a government photo ID and a color photo. The card arrives by email.",
         ["Digital ID", "DD214"], "vet"),
        ("idme", "ID.me", "https://www.id.me",
         "One login that many stores use to confirm military status for discounts.",
         "Veterans, retirees, spouses, surviving spouses, and adult children or parents of service members.",
         "Make one account and verify once, then choose ID.me at checkout.",
         ["Family can verify"], "vet fam gs ret"),
        ("govx", "GovX", "https://www.govx.com",
         "A members-only discount store for the military community.",
         "Current and former military and other service groups.",
         "Sign up on GovX. GovX says registration is free for life.",
         ["Free to join"], "vet ret fr"),
    ]),
    ("shopping", "Shopping and everyday discounts", "Shopping", "Tax-free exchange shopping, home store discounts and phone plans.", "#5CE08A", [
        ("exchange", "Military exchanges online", "https://www.aafes.com/veterans/",
         "Military pricing with no sales tax at shopmyexchange.com, mynavyexchange.com, mymcx.com and shopcgx.com.",
         "Honorably discharged veterans of every branch, including Guard and Reserve. The veteran only, not family members.",
         "Create an account. If asked, verify at VetVerify.org (it can take up to 3 days). Online only, with no base access.",
         ["No sales tax", "Online"], "vet"),
        ("commissary", "Commissary and exchange in person", "https://corp.commissaries.com/Expanding-Access",
         "In-store commissary and exchange shopping plus MWR, open since 2020.",
         "Purple Heart recipients, former POWs, veterans with service-connected disabilities, and approved VA family caregivers.",
         "Bring a VA Health ID Card marked PURPLE HEART, FORMER POW or SERVICE CONNECTED (or a VA letter plus a REAL ID) and pass the base visitor check.",
         ["In person", "Caregivers"], "dis"),
        ("lowes", "Lowe's", "https://www.lowes.com/l/about/honor-our-military",
         "10% off most full-priced items, with no yearly cap. Sale items, major appliances and some other items are excluded.",
         "Service members and veterans. An enrolled spouse can use it too.",
         "Verify with ID.me and link a MyLowe's Rewards account.",
         ["10%", "Spouse too"], "vet fam"),
        ("homedepot", "The Home Depot", "https://www.homedepot.com/c/military",
         "Up to 10% off select in-stock items.",
         "Military. Home Depot's 2021 announcement extended it to all US veterans and spouses.",
         "Register in the Home Depot app and check the current terms there.",
         ["Up to 10%", "Check terms"], "vet fam"),
        ("tmobile", "T-Mobile", "https://www.t-mobile.com/cell-phone-plans/military-discount-plans",
         "Military Savings plans, such as 4 lines for $25 a month per line on T-Mix, plus fees.",
         "People who serve or have served. Family lines go on the veteran's account.",
         "The service member is the account holder and shows proof at activation.",
         ["4 lines at $25/line"], "vet fam"),
        ("verizon", "Verizon", "https://www.verizon.com/military/",
         "10% off mobile plans.",
         "Active duty, retirees, veterans, current or former Guard and Reserve, and Gold Star family members.",
         "Verify through ID.me.",
         ["10%", "Gold Star families"], "vet gs ret"),
        ("att", "AT&T", "https://www.att.com/offers/discount-program/military-discount/",
         "10% off Value 2.0, 15% off Extra 2.0 and 20% off Premium 2.0, per line on up to 10 lines.",
         "Veterans, active-duty service members, reservists and military family members.",
         "Verify online with AT&T or in a store.",
         ["10% to 20%", "Up to 10 lines"], "vet fam"),
    ]),
    ("travel", "Travel and vacations", "Travel", "Military travel deals and resorts, and who can actually book them.", "#66C0F4", [
        ("aft", "American Forces Travel", "https://www.militaryonesource.mil/recreation-travel-shopping/travel-lodging/american-forces-travel-discounts/",
         "Discounted hotels, flights, rental cars, cruises and vacation packages on the official MWR travel site.",
         "Honorably discharged veterans and eligible family members, according to Military OneSource.",
         "The site checks DEERS, or you can verify through VetVerify.",
         ["Hotels", "Cruises", "Cars"], "vet fam ret"),
        ("shades", "Shades of Green at Walt Disney World", "https://www.shadesofgreen.org/about-shades-green/eligibility",
         "The military resort at Walt Disney World.",
         "Every honorably discharged veteran in January and September, subject to availability. All year: veterans rated 100% service-connected, VA Health ID Card holders (Purple Heart, POW, service-connected) and VA caregivers.",
         "Book with the resort and bring a current DD214.",
         ["Disney World", "Jan and Sept for all veterans"], "vet dis ret"),
        ("afvc", "Armed Forces Vacation Club", "https://www.armymwr.com/travel/armed-forces-vacation-club",
         "Week-long resort condo stays for $349 a week (according to Army MWR) in units that sleep 2 to 8.",
         "Army MWR lists active duty, Guard, Reserve and retired members, and VA has also named Gold Star families. It does not say every veteran qualifies.",
         "Check eligibility on afvclub.com before you plan.",
         ["$349 a week", "Check eligibility"], "ret gs"),
        ("resorts", "Hale Koa (Hawaii) and Edelweiss (Germany)", "https://www.halekoa.com/about-hale-koa-hotel/eligibility",
         "Military resort hotels in Honolulu and the German Alps.",
         "Hale Koa: veterans rated 100% service-connected, Purple Heart recipients, former POWs, service-connected VA Health ID Card holders and caregivers. Edelweiss: 100% service-connected veterans and retirees.",
         "Check each resort's eligibility page before you book.",
         ["Hawaii", "Germany"], "dis ret"),
    ]),
    ("tickets", "Tickets, parks and days out", "Tickets and parks", "Free park passes, free event tickets and the theme park fine print.", "#B388FF", [
        ("parks", "Free lifetime national parks pass", "https://www.nps.gov/planyourvisit/veterans-and-gold-star-families-free-access.htm",
         "Free lifetime entry to national parks and other federal lands.",
         "Veterans and Gold Star families.",
         "Free in person or as a digital pass on Recreation.gov (a mailed pass costs a small fee). Show a VA Health ID Card, VA Veteran ID Card, veteran-marked license or a DD Form 2. Gold Star families print a voucher.",
         ["Free", "Lifetime"], "vet gs"),
        ("vettix", "Vet Tix", "https://www.vettix.org",
         "Free tickets to sports, concerts and shows. Members pay a small delivery fee.",
         "Serving members, honorably discharged veterans, families of those killed in action, Gold Star next of kin and some surviving spouses.",
         "Join and verify through ID.me or the Vet Tix team.",
         ["Free tickets"], "vet gs"),
        ("seaworld", "SeaWorld San Antonio Military Silver Pass", "https://seaworld.com/san-antonio/tickets/military-discount/veterans/",
         "A season pass for SeaWorld San Antonio for military.",
         "US military veterans and retirees who served honorably.",
         "Verify with ID.me. Check the page for the price and dates.",
         ["San Antonio"], "vet ret tx"),
        ("themeparks", "Disney and Universal: who qualifies", "https://disneyworld.disney.go.com/events-tours/veterans-day/",
         "Military theme park tickets.",
         "Disney World and Disneyland: active and retired military only. Universal Orlando's 2026 Military Freedom Pass: active duty, Guard, Reserve, retirees and 100% disabled veterans.",
         "Most veterans don't qualify, so watch the parks' regular sales instead.",
         ["Know before you go"], "ret dis"),
    ]),
    ("money", "Home loans and money help", "Home and money", "VA home loan basics, where to compare rates, grants and state tax breaks.", "#FF8A3D", [
        ("valoan", "VA home loan", "https://www.va.gov/housing-assistance/home-loans/loan-types/purchase-loan/",
         "Usually no down payment (if the price is not above the appraised value), no private mortgage insurance, and no VA loan limit with full entitlement.",
         "Veterans with a Certificate of Eligibility who meet lender credit and income standards and will live in the home.",
         "Request your Certificate of Eligibility online, through a lender or by mail, then compare lenders.",
         ["No PMI", "No down payment for most"], "vet"),
        ("fundingfee", "VA funding fee", "https://www.va.gov/housing-assistance/home-loans/funding-fee-and-closing-costs/",
         "A one-time fee: 2.15% for a first use with under 5% down on VA's chart (effective April 7, 2023), less with a bigger down payment. It can be rolled into the loan.",
         "Exempt: veterans who receive VA disability compensation, and surviving spouses who receive DIC.",
         "Your Certificate of Eligibility shows whether you are exempt.",
         ["Disability pay = no fee"], "vet dis gs"),
        ("rates", "Compare mortgage rates", "https://www.consumerfinance.gov/owning-a-home/explore-rates/",
         "The government's free rate tool shows typical VA loan rates by credit score, down payment and term. We don't list rates because they change every day.",
         "Anyone shopping for a mortgage.",
         "Get Loan Estimates from at least three lenders and compare the APR and fees, not just the rate.",
         ["Free tool", "Compare 3 lenders"], "vet"),
        ("irrrl", "VA streamline refinance (IRRRL)", "https://www.va.gov/housing-assistance/home-loans/loan-types/interest-rate-reduction-loan/",
         "Refinances a VA loan to a lower rate, or from adjustable to fixed.",
         "Veterans who already have a VA-backed loan on the home.",
         "Go through a private lender. Divide the costs by your monthly savings to find the break-even point, and ignore mailers that promise skipped payments.",
         ["Refinance", "Watch for scams"], "vet"),
        ("nadl", "VA Native American Direct Loan", "https://www.va.gov/housing-assistance/home-loans/loan-types/native-american-direct-loan/",
         "A VA loan to buy, build or improve a home on federal trust land, usually with no down payment and no PMI.",
         "Native American veterans, or non-Native veterans married to a Native American, where the tribe has an agreement with VA.",
         "Contact VA's direct loan team at NADL@va.gov.",
         ["Trust land"], "vet"),
        ("grants", "VA adaptive housing grants", "https://www.va.gov/housing-assistance/disability-housing-grants/",
         "Up to $126,526 (SAH) or $25,350 (SHA) in fiscal year 2026 to buy, build or change a home.",
         "Veterans with certain service-connected disabilities.",
         "Apply with VA Form 26-4555.",
         ["Up to $126,526"], "dis"),
        ("txtax", "Texas veteran property tax exemptions", "https://comptroller.texas.gov/taxes/property-tax/exemptions/disabledvet-faq.php",
         "$5,000 to $12,000 off one property's taxable value for a 10% to 100% rating. A 100% rating or unemployability exempts the whole homestead.",
         "Texas veterans with a disability rating, and some surviving spouses and children.",
         "File with your county appraisal district by April 30.",
         ["Texas", "Up to the whole homestead"], "tx dis gs"),
        ("txvlb", "Texas Veterans Land Board home loans", "https://www.glo.texas.gov/veterans/home-loans",
         "Fixed-rate home loans up to $832,750, with a discounted rate for a 30% or higher rating.",
         "Texas veterans with 90 or more days of active duty and an honorable, general or medical discharge, and some surviving spouses.",
         "Apply through a participating lender.",
         ["Texas", "Up to $832,750"], "tx vet gs"),
        ("states", "Your state's veteran benefits", "https://nasdva.us/resources/",
         "Links to every state's veterans agency for property tax breaks, park passes, license plates and tuition help.",
         "Veterans in every state.",
         "Pick your state from the directory.",
         ["All states"], "vet"),
        ("miltax", "Free tax filing (MilTax)", "https://www.militaryonesource.mil/financial-legal/taxes/miltax-military-tax-services/",
         "Free tax software and free tax consultants.",
         "Veterans for 365 days after separation or retirement, plus serving members and their families.",
         "Use it through Military OneSource. The software for the next tax season opens in January 2027.",
         ["Free", "First year out"], "vet fam"),
        ("vre", "Veteran Readiness and Employment", "https://www.va.gov/careers-employment/vocational-rehabilitation/eligibility/",
         "Job training or school paid for, plus a monthly allowance.",
         "Veterans with a VA disability rating of 10% or more who were not dishonorably discharged.",
         "Apply with VA Form 28-1900.",
         ["Monthly allowance"], "dis"),
    ]),
    ("family", "For spouses and kids of veterans", "Spouses and kids", "Education money and scholarships for military families.", "#FF6B8A", [
        ("dea", "Dependents' Educational Assistance (DEA)", "https://www.va.gov/family-and-caregiver-benefits/education-and-careers/dependents-education-assistance/",
         "Up to 36 months of education benefits: $1,621 a month for full-time school from Oct 1, 2026 to Sept 30, 2027.",
         "Children and spouses of a veteran who is permanently and totally disabled by a service-connected condition, or who died from one or in the line of duty.",
         "Apply with VA Form 22-5490.",
         ["$1,621 a month", "Up to 36 months"], "fam dis gs"),
        ("fry", "Fry Scholarship", "https://www.va.gov/family-and-caregiver-benefits/education-and-careers/fry-scholarship/",
         "Up to 36 months of tuition, housing and book money.",
         "Children and surviving spouses of service members who died in the line of duty on or after Sept 11, 2001.",
         "Apply with VA Form 22-5490.",
         ["Tuition", "Housing", "Books"], "fam gs"),
        ("gibill", "Pass on the GI Bill (while serving)", "https://www.va.gov/education/transfer-post-9-11-gi-bill-benefits/",
         "Post-9/11 GI Bill benefits passed to a spouse or child.",
         "Parents who are still serving, with at least 6 years in and an agreement to serve 4 more. It can't be done after separation.",
         "Request it in DoD's milConnect while still serving.",
         ["Plan while serving"], "fam"),
        ("folds", "Folds of Honor scholarships", "https://foldsofhonor.org/scholarships/",
         "Up to $2,500 per term for college and up to $5,000 for private K-12 school.",
         "Spouses and children of fallen or disabled service members.",
         "Apply between Feb 1 and Mar 31 each year.",
         ["Opens Feb 1"], "fam dis gs"),
        ("smc", "Scholarships for Military Children", "https://corp.commissaries.com/Scholarship",
         "$2,000 scholarships (500 awarded for 2026-27).",
         "Unmarried children under 23 with a military ID card whose parent is active duty, Guard or Reserve, retired or deceased.",
         "Watch for the next cycle. The last deadline was in February.",
         ["$2,000 awards"], "fam ret gs"),
        ("search", "Free scholarship search", "https://search.militaryscholar.org/",
         "A free scholarship search from Fisher House.",
         "Service members, veterans, retirees and their families.",
         "Search by state, school and family situation.",
         ["Free"], "fam vet"),
        ("hazlewood", "Texas Hazlewood Legacy", "https://tvc.texas.gov/education/hazlewood/",
         "Texas veterans may be able to pass unused Hazlewood college tuition hours to a child.",
         "Texas veterans and their children.",
         "Check the current rules with the Texas Veterans Commission before you plan on it.",
         ["Texas"], "tx fam"),
    ]),
]

TOP_PICKS = [("parks", "Free lifetime national parks pass"), ("vic", "VA Veteran ID Card"), ("exchange", "Tax-free exchange shopping online"),
             ("vettix", "Free event tickets from Vet Tix"), ("aft", "American Forces Travel deals"), ("shades", "Disney World's military resort in Jan and Sept")]

HUB_CSS = """<style>
.vet-hero{background:radial-gradient(120% 140% at 85% 0%,rgba(255,176,32,.20),transparent 60%),radial-gradient(100% 120% at 0% 100%,rgba(102,192,244,.14),transparent 60%)}
.vstats{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.vstats span{padding:8px 12px;border-radius:12px;background:rgba(255,255,255,.06);border:1px solid var(--line);font-size:14px;color:var(--steel)}
.vstats b{color:#FFB020;font-family:var(--display)}
.vnote{margin-top:14px;padding:12px 14px;border-radius:12px;background:var(--surface);border:1px solid var(--line);font-size:14px;color:var(--muted)}
.vtiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
@media (max-width:900px){.vtiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
.vtile{--c:#FFB020;display:flex;gap:12px;align-items:center;padding:14px;border-radius:14px;background:var(--surface);border:1px solid var(--line);text-decoration:none;color:#fff;min-height:64px}
.vtile:hover{border-color:var(--c);color:#fff}
.vtile .vico{flex:none}
.vtile b{display:block;font-family:var(--display);font-size:16px;line-height:1.2}
.vtile small{display:block;color:var(--muted);font-size:13px}
.vico{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;background:color-mix(in srgb,var(--c) 22%,transparent);color:var(--c)}
.vtop{background:linear-gradient(135deg,rgba(255,176,32,.14),rgba(255,176,32,.04));border:1px solid rgba(255,176,32,.45);border-radius:18px;padding:18px}
.vtop h2{font-size:20px;display:flex;gap:8px;align-items:center;color:#FFD76A}
.vtop ol{margin:12px 0 0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 16px;counter-reset:t}
@media (max-width:760px){.vtop ol{grid-template-columns:1fr}}
.vtop li{counter-increment:t;display:flex;gap:10px;align-items:center}
.vtop li::before{content:counter(t);flex:none;width:26px;height:26px;border-radius:50%;display:grid;place-items:center;background:#FFB020;color:#1A0E04;font:700 14px var(--display)}
.vtop a{color:#fff;font-weight:600;text-decoration:none;min-height:24px}
.vtop a:hover{color:#FFD76A;text-decoration:underline}
.vsec{scroll-margin-top:170px}
@media (max-width:760px){.vbar{position:static!important}.vsec{scroll-margin-top:12px}.vcard{scroll-margin-top:12px}}
.vbar{position:sticky;top:0;z-index:5;background:rgba(15,10,36,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:10px 0}
.vbar .wrap{display:flex;flex-direction:column;gap:10px}
.vbar input{width:100%;min-height:46px;padding:0 14px;border-radius:12px;border:1px solid var(--line-strong);background:var(--surface);color:#fff;font:inherit;font-size:16px}
.vwho{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.vwho::-webkit-scrollbar{display:none}
.vwho button{flex:none;min-height:38px;padding:0 14px;border-radius:999px;border:1px solid var(--line-strong);background:var(--surface);color:var(--steel);font:600 14px var(--body);cursor:pointer}
.vwho button[aria-pressed="true"]{background:#FFB020;border-color:#FFB020;color:#1A0E04}
.vcount{font-size:14px;color:var(--muted)}
.vsec h2{display:flex;gap:12px;align-items:center}
.vsec .sub{color:var(--muted);margin:6px 0 16px}
.vgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
@media (max-width:960px){.vgrid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:600px){.vgrid{grid-template-columns:minmax(0,1fr)}}
.vcard{--c:#66C0F4;display:flex;flex-direction:column;gap:10px;padding:16px;border-radius:16px;background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--c);scroll-margin-top:150px}
.vcard:target{outline:2px solid #FFB020;outline-offset:2px}
.vcard h3{font-size:18px}
.vcard dl{margin:0;display:grid;gap:8px}
.vcard dt{font:700 12px var(--body);letter-spacing:.6px;text-transform:uppercase;color:var(--c)}
.vcard dd{margin:2px 0 0;font-size:15px;color:var(--steel);line-height:1.5}
.vcard p{font-size:15px;color:var(--steel);flex:1}
.vcard .tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:auto}
.vcard .tags span{font-size:12px;font-weight:600;padding:3px 9px;border-radius:999px;background:rgba(255,255,255,.08);color:var(--steel)}
.vgo{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 14px;border-radius:12px;border:1px solid var(--c);color:#fff;font-weight:700;font-size:14px;text-decoration:none}
.vgo:hover{background:color-mix(in srgb,var(--c) 25%,transparent);color:#fff}
.vcard[hidden],.vsec.is-empty{display:none}
.vempty{color:var(--muted)}
</style>
"""


def vcard(cid, name, url, get, who, how, tags, codes, color):
    e = html.escape
    t = "".join(f"<span>{e(x)}</span>" for x in tags)
    return (f'<article class="vcard" id="{cid}" data-who="{codes}" style="--c:{color}"><h3>{e(name)}</h3>'
            f'<dl><div><dt>You get</dt><dd>{e(get)}</dd></div><div><dt>Who qualifies</dt><dd>{e(who)}</dd></div>'
            f'<div><dt>How to get it</dt><dd>{e(how)}</dd></div></dl><span class="tags">{t}</span>'
            f'<a class="vgo" href="{e(url)}" target="_blank" rel="noopener noreferrer">Official page &rarr;</a></article>')


def brand_vcard(b):
    e = html.escape
    codes = " ".join({"mil": "vet ret", "fr": "fr"}[w] for w in b["who"])
    t = "".join(f"<span>{e(x)}</span>" for x in [b["cat"]] + b["tags"])
    return (f'<article class="vcard" data-who="{codes}" style="--c:{b["c"]}"><h3>{e(b["name"])}</h3><p>{e(b["desc"])}</p>'
            f'<span class="tags">{t}</span><a class="vgo" href="{e(b["url"])}" target="_blank" rel="noopener noreferrer">See the program &rarr;</a></article>')


HUB_JS = """<script>
(function(){var q=document.getElementById('vq'),btns=[].slice.call(document.querySelectorAll('.vwho button')),cnt=document.getElementById('vcount'),
cards=[].slice.call(document.querySelectorAll('.vcard')),secs=[].slice.call(document.querySelectorAll('.vsec')),empty=document.getElementById('vempty'),who='all';
cards.forEach(function(c){c.dataset.t=c.textContent.toLowerCase();});
function run(){var words=(q.value||'').trim().toLowerCase().split(/\\s+/).filter(Boolean),n=0;
cards.forEach(function(c){var ok=who==='all'||(' '+c.dataset.who+' ').indexOf(' '+who+' ')>-1;
for(var i=0;ok&&i<words.length;i++)if(c.dataset.t.indexOf(words[i])<0)ok=false;c.hidden=!ok;if(ok)n++;});
secs.forEach(function(s){s.classList.toggle('is-empty',!s.querySelector('.vcard:not([hidden])'));});
cnt.textContent=(who==='all'&&!words.length)?cards.length+' programs in the hub':n+(n===1?' program matches':' programs match');empty.hidden=n>0;}
btns.forEach(function(b){b.addEventListener('click',function(){who=b.dataset.w;btns.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});run();});});
q.addEventListener('input',run);run();})();
</script>"""


def build():
    title = "Veteran Hub: Discounts, Travel, Free Tickets and Money Help for Veterans and Families | SteelGames"
    desc = ("SteelGames Veteran Hub, from a veteran-owned site: military discounts, tax-free exchange shopping, travel deals, "
            "free park passes and event tickets, VA home loan basics, and education money for veterans' spouses and kids.")
    url = f"{SITE}/military.html"
    e = html.escape
    n_programs = sum(len(items) for *_, items in SAVINGS)
    tiles = "".join(f'<a class="vtile" style="--c:{color}" href="#{sid}"><span class="vico">{icon(sid)}</span><span><b>{e(short)}</b><small>{len(items)} programs</small></span></a>'
                    for sid, _, short, _, color, items in SAVINGS)
    tiles += (f'<a class="vtile" style="--c:#4DD0E1" href="#gaming"><span class="vico">{icon("gaming")}</span><span><b>Gaming discounts</b><small>{len(BRANDS)} brands</small></span></a>'
              f'<a class="vtile" style="--c:#FF6B74" href="/gifts/"><span class="vico">{icon("gifts")}</span><span><b>Holiday gift shop</b><small>Gifts by budget</small></span></a>')
    top = "".join(f'<li><a href="#{cid}">{e(label)}</a></li>' for cid, label in TOP_PICKS)
    who_btns = "".join(f'<button type="button" data-w="{w}" aria-pressed="{"true" if w == "all" else "false"}">{e(label)}</button>' for w, label in WHO)
    sections = ""
    for sid, t, short, sub, color, items in SAVINGS:
        cards = "".join(vcard(cid, n, u, g, w, h, tg, codes, color) for cid, n, u, g, w, h, tg, codes in items)
        sections += (f'<section class="block vsec" id="{sid}"><div class="wrap"><h2><span class="vico" style="--c:{color}">{icon(sid)}</span>{e(t)}</h2>'
                     f'<p class="sub">{e(sub)}</p><div class="vgrid">{cards}</div></div></section>\n')
    tips = "".join(f'<div class="tip"><b>{i}</b><p>{e(t)}</p></div>' for i, t in enumerate(TIPS, 1))
    mail = "mailto:steelgames.app@outlook.com?subject=Veteran%20Hub%20tip"
    return (layout.head(title, desc, url, HUB_CSS)
            + layout.header("military")
            + f"""<main>
<section class="hero vet-hero"><div class="wrap">
<p class="eyebrow">Veteran-owned &middot; SteelGames Veteran Hub</p>
<h1>Veteran Hub: savings for veterans and their families</h1>
<p class="lede">Discounts, tax-free shopping, travel deals, free park passes and event tickets, VA home loan basics and education money for veterans' spouses and kids, all in one place. SteelGames is veteran-owned, so this hub is personal.</p>
<div class="vstats"><span><b>{n_programs + len(BRANDS)}</b> programs and brands</span><span><b>6</b> ways to save</span><span>Checked <b>{e(SAVINGS_CHECKED)}</b></span><span><b>No</b> affiliate links in the hub</span></div>
<p class="vnote">SteelGames is not part of VA or the Department of Defense, and nothing here is financial or legal advice. Each program sets its own rules and they can change, so confirm on the official page before you plan or buy.</p>
</div></section>
<section class="block"><div class="wrap"><div class="vtiles">{tiles}</div></div></section>
<section class="block"><div class="wrap"><div class="vtop"><h2>{icon("star", 20)}Top picks for any veteran</h2><ol>{top}</ol></div></div></section>
<div class="vbar"><div class="wrap"><input type="search" id="vq" placeholder="Search the hub, like parks, mortgage, tickets or scholarship" aria-label="Search the Veteran Hub">
<div class="vwho" role="group" aria-label="Show programs for">{who_btns}</div><p class="vcount" id="vcount" aria-live="polite"></p></div></div>
{sections}<section class="block vsec" id="gaming"><div class="wrap"><h2><span class="vico" style="--c:#4DD0E1">{icon("gaming")}</span>Gaming discounts for veterans and first responders</h2>
<p class="sub">Brands that give service members, veterans, police, firefighters and EMTs a better price on gaming PCs, peripherals, chairs and audio. Amounts are as last reported (checked {CHECKED}); confirm on the brand's page before you buy.</p>
<div class="vgrid">{"".join(brand_vcard(b) for b in BRANDS)}</div></div></section>
<p class="wrap vempty" id="vempty" hidden>Nothing matches that search. Try a shorter word, like "loan", "park" or "tickets", or pick Everyone.</p>
<section class="block" id="verify"><div class="wrap"><h2>How to claim veteran discounts</h2>
<div class="tips">{tips}</div></div></section>
<section class="block" id="tip"><div class="wrap"><h2>Know a program we missed?</h2>
<p class="lede">Tell us about a discount, travel deal or money program for veterans and their families. We check it on the official page before we add it.</p>
<div class="chips"><a href="{mail}">Send a tip</a><a href="https://discord.gg/ekrRaejc6">Join the Discord</a><a href="/gifts/">Holiday gift shop</a></div></div></section>
</main>
{HUB_JS}"""
            + layout.footer())


if __name__ == "__main__":
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    open(os.path.join(root, "military.html"), "w").write(build())
