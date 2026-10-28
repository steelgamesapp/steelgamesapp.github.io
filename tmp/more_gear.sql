-- More gear: 67 highly rated Amazon picks, plus exact product links for existing items.
-- Run in Supabase -> SQL Editor. Safe to run twice (skips names that already exist).
with catalog(name, category, platform, summary, url) as (values
  ('ASUS Dual GeForce RTX 5060 8GB OC', 'Graphics cards', 'pc', 'Compact RTX 5060 with DLSS 4, a strong 1080p upgrade for most gaming PCs.', 'https://www.amazon.com/dp/B0F8PR9L3X'),
  ('AMD Ryzen 7 9800X3D', 'Processors', 'pc', '8-core gaming CPU with 3D V-Cache, one of the fastest processors for games.', 'https://www.amazon.com/dp/B0DKFMSMYK'),
  ('AMD Ryzen 9 9950X3D', 'Processors', 'pc', '16-core CPU for people who game and stream or edit on the same PC.', 'https://www.amazon.com/dp/B0DVZSG8D5'),
  ('AMD Ryzen 9 9900X', 'Processors', 'pc', '12-core processor for gaming plus heavy multitasking.', 'https://www.amazon.com/dp/B0D6NN87T8'),
  ('AMD Ryzen 5 9600X', 'Processors', 'pc', '6-core processor that''s a great value for a new gaming build.', 'https://www.amazon.com/dp/B0D6NN6TM7'),
  ('Corsair Vengeance DDR5 32GB (2x16GB) 6000MHz', 'Memory', 'pc', '32GB desktop memory kit at the speed most new builds want.', 'https://www.amazon.com/dp/B0CBRJ63RT'),
  ('Crucial 32GB DDR5 Laptop Memory (2x16GB)', 'Memory', 'pc', 'Memory upgrade for gaming laptops and mini PCs that take SODIMM sticks.', 'https://www.amazon.com/dp/B0BLTDRRLF'),
  ('WD_Black SN7100 2TB NVMe SSD', 'Storage', 'pc', 'Fast Gen4 drive with room for a big game library.', 'https://www.amazon.com/dp/B0DN6ZQ3PD'),
  ('Crucial P310 2TB NVMe SSD', 'Storage', 'pc', 'Fast, affordable 2TB drive for desktops, laptops and some handhelds.', 'https://www.amazon.com/dp/B0DC8RVRBZ'),
  ('Samsung 9100 PRO 2TB NVMe SSD', 'Storage', 'pc', 'Top-speed PCIe 5.0 drive for the newest motherboards.', 'https://www.amazon.com/dp/B0DX2DPJZ5'),
  ('SanDisk 2TB Extreme Portable SSD', 'Storage', null, 'Pocket-size fast drive for moving games and clips between devices.', 'https://www.amazon.com/dp/B08HN37XC1'),
  ('Samsung T7 Portable SSD 1TB', 'Storage', null, 'Small, fast external drive that works with PC and consoles.', 'https://www.amazon.com/dp/B0874XN4D8'),
  ('Seagate 2TB Portable Hard Drive', 'Storage', null, 'Cheap extra storage for older games and backups.', 'https://www.amazon.com/dp/B07CRG94G3'),
  ('SteelSeries Apex 3 Gaming Keyboard', 'Keyboards', 'pc', 'Quiet, water-resistant RGB keyboard at a budget price.', 'https://www.amazon.com/dp/B07ZGDPT4M'),
  ('AULA F75 Pro Wireless Mechanical Keyboard', 'Keyboards', 'pc', '75% wireless mechanical board with a volume knob and swappable switches.', 'https://www.amazon.com/dp/B0D14N2QZF'),
  ('Logitech G413 SE Mechanical Keyboard', 'Keyboards', 'pc', 'Full-size mechanical keyboard with an aluminum top.', 'https://www.amazon.com/dp/B08Z6X4NK3'),
  ('Redragon S101 Keyboard and Mouse Combo', 'Keyboards', 'pc', 'RGB keyboard and mouse set for a first gaming setup.', 'https://www.amazon.com/dp/B00NLZUM36'),
  ('Logitech G305 Lightspeed Wireless Mouse', 'Mice', 'pc', 'Light wireless mouse with long battery life at a low price.', 'https://www.amazon.com/dp/B07CMS5Q6P'),
  ('Logitech G502 Hero Wired Mouse', 'Mice', 'pc', 'Fan-favorite mouse with lots of buttons and adjustable weights.', 'https://www.amazon.com/dp/B07GBZ4Q68'),
  ('Logitech G502 Lightspeed Wireless Mouse', 'Mice', 'pc', 'The G502 shape without the cable.', 'https://www.amazon.com/dp/B07L4BM851'),
  ('Razer Basilisk V3 Wired Mouse', 'Mice', 'pc', 'Ergonomic mouse with a free-spinning scroll wheel and 11 buttons.', 'https://www.amazon.com/dp/B09C13PZX7'),
  ('GTPLAYER Gaming Chair with Footrest', 'Gaming chairs', null, 'Reclining chair with lumbar pillow and pull-out footrest.', 'https://www.amazon.com/dp/B08B12P6CS'),
  ('N-GEN Gaming Chair with Footrest', 'Gaming chairs', null, 'High-back chair with lumbar support and footrest.', 'https://www.amazon.com/dp/B0H2HR6XP3'),
  ('HUANUO Dual Monitor Stand', 'Desks and mounts', null, 'Gas-spring arms for two monitors that frees up desk space.', 'https://www.amazon.com/dp/B07T5SY43L'),
  ('HUANUO Single Monitor Arm', 'Desks and mounts', null, 'Adjustable clamp-on arm for one 13–32 inch monitor.', 'https://www.amazon.com/dp/B07T3KCQ94'),
  ('ErGear Electric Standing Desk 48x24', 'Desks and mounts', null, 'Motorized sit-stand desk for long sessions.', 'https://www.amazon.com/dp/B0B41YH9B6'),
  ('ODK 48-inch L-Shaped Gaming Desk', 'Desks and mounts', null, 'Corner desk with LED lights and built-in outlets.', 'https://www.amazon.com/dp/B0CG9G9VGK'),
  ('Samsung Odyssey G55C 32-inch QHD Curved Monitor', 'Monitors', null, '32-inch 1440p curved screen for PC and consoles.', 'https://www.amazon.com/dp/B0CRGJC5ZD'),
  ('SANSUI 27-inch 1440p 180Hz IPS Monitor', 'Monitors', null, 'Budget 1440p high-refresh monitor.', 'https://www.amazon.com/dp/B0CWCWL81G'),
  ('Govee RGBIC Gaming Light Bars', 'RGB lighting', null, 'Light bars that sync colors with your games and music.', 'https://www.amazon.com/dp/B0B6CQ2LQ2'),
  ('Govee Glide Wall Light Bars', 'RGB lighting', null, 'Wall-mounted light segments for a stream background.', 'https://www.amazon.com/dp/B09H5VSKTZ'),
  ('Govee RGBIC Floor Lamp', 'RGB lighting', null, 'Corner lamp that fills a game room with color.', 'https://www.amazon.com/dp/B099WTN2TR'),
  ('Corsair MM350 PRO Extended XL Mouse Pad', 'Mousepads', null, 'Spill-proof desk-size cloth pad.', 'https://www.amazon.com/dp/B08JH8C5T5'),
  ('KTRIO Extended Gaming Mouse Pad', 'Mousepads', null, 'Low-cost desk mat with stitched edges.', 'https://www.amazon.com/dp/B0788LMLZL'),
  ('New Bee RGB Headphone Stand with USB', 'Desk gadgets', null, 'Aluminum headset stand with lighting and charging ports.', 'https://www.amazon.com/dp/B09XHJBYTJ'),
  ('EURPMASK Clamp-On Headset Holder', 'Desk gadgets', null, 'Rotating under-desk hanger that keeps your headset off the desk.', 'https://www.amazon.com/dp/B07BVK2FQW'),
  ('Elgato Stream Deck +', 'Stream decks', null, 'LCD keys plus dials for audio mixing while you stream.', 'https://www.amazon.com/dp/B0BJL8SJ59'),
  ('Elgato Stream Deck XL', 'Stream decks', null, '32 keys for streamers who run a lot of scenes and shortcuts.', 'https://www.amazon.com/dp/B07RL8H55Z'),
  ('Logitech Blue Yeti USB Microphone', 'Microphones', null, 'Plug-in USB mic that''s a streaming classic.', 'https://www.amazon.com/dp/B00N1YPXW2'),
  ('FIFINE AmpliGame AM8 USB/XLR Microphone', 'Microphones', null, 'Dynamic mic that cuts room noise, with USB and XLR.', 'https://www.amazon.com/dp/B0BMFQP2ZZ'),
  ('FIFINE T669 USB Microphone Kit', 'Microphones', null, 'Budget condenser mic kit with arm and pop filter.', 'https://www.amazon.com/dp/B07Y1C6GDS'),
  ('Logitech Brio 101 1080p Webcam', 'Webcams', null, 'Simple, sharp 1080p webcam for streaming and calls.', 'https://www.amazon.com/dp/B0BXGFFSL1'),
  ('EMEET NOVA 4K Webcam', 'Webcams', null, '4K webcam with autofocus and two mics.', 'https://www.amazon.com/dp/B0CY2C7H6S'),
  ('Edifier G2000 Gaming Speakers', 'Speakers', null, 'Compact 32W speakers with Bluetooth and RGB.', 'https://www.amazon.com/dp/B00UAFSN5O'),
  ('Razer Nommo Chroma Speakers', 'Speakers', null, 'Full-sounding desktop speakers with a bass knob.', 'https://www.amazon.com/dp/B078H1T9YD'),
  ('Amazon Basics USB-Powered PC Speakers', 'Speakers', null, 'Cheap, small USB speakers for any desk.', 'https://www.amazon.com/dp/B07DDK3W5D'),
  ('Razer BlackShark V2 X Headset', 'Headsets', null, 'Light, comfortable wired headset at a low price.', 'https://www.amazon.com/dp/B086PKMZ21'),
  ('Logitech G733 Lightspeed Wireless Headset', 'Headsets', null, 'Very light wireless headset with RGB.', 'https://www.amazon.com/dp/B081415GCS'),
  ('HyperX Cloud III S Wireless Headset', 'Headsets', null, 'Wireless Cloud III with long battery life for PC and consoles.', 'https://www.amazon.com/dp/B0F6NZWPTC'),
  ('Elgato Cam Link 4K', 'Capture cards', null, 'Turns a camera into a high-quality webcam.', 'https://www.amazon.com/dp/B07K3FN5MR'),
  ('Elgato HD60 S+ Capture Card', 'Capture cards', null, 'Records and streams console gameplay in 1080p60 HDR.', 'https://www.amazon.com/dp/B07XB6VNLJ'),
  ('8BitDo Ultimate 2 Wireless Controller', 'Controllers', 'pc', 'Hall-effect sticks that resist drift, for PC and Steam.', 'https://www.amazon.com/dp/B0DR8V899R'),
  ('8BitDo Ultimate 2C Wireless Controller', 'Controllers', 'pc', 'Low-cost wireless PC controller with Hall-effect sticks.', 'https://www.amazon.com/dp/B0D739FJLG'),
  ('PlayStation DualSense Edge', 'Controllers', 'playstation', 'Sony''s pro controller with back buttons and swappable sticks.', 'https://www.amazon.com/dp/B0BSYFB99D'),
  ('Nintendo Switch 2 Pro Controller', 'Controllers', 'nintendo', 'Official pro controller for Switch 2.', 'https://www.amazon.com/dp/B0F3VTFD6J'),
  ('PowerA Twin Charging Station for DualSense', 'Charging docks', 'playstation', 'Drop-in charger for two PS5 controllers.', 'https://www.amazon.com/dp/B09B1XX1PN'),
  ('OIVO PS5 Controller Charging Station', 'Charging docks', 'playstation', 'Fast two-controller charging dock.', 'https://www.amazon.com/dp/B08LZGPPBH'),
  ('Anker 12-Outlet Surge Protector Power Strip', 'Cables and power', null, 'Protects a gaming setup, with USB charging.', 'https://www.amazon.com/dp/B09SG2Q23M'),
  ('Belkin 12-Outlet Surge Protector', 'Cables and power', null, 'Heavy-duty surge protector with an 8-foot cord.', 'https://www.amazon.com/dp/B0C6S6TPRH'),
  ('WD_Black SN850P 2TB for PS5', 'Extra storage', 'playstation', 'Officially licensed PS5 storage with heatsink installed.', 'https://www.amazon.com/dp/B0C47ZX1WB'),
  ('Sabrent PS5 SSD Heatsink', 'Extra storage', 'playstation', 'Heatsink cover for adding your own SSD to a PS5.', 'https://www.amazon.com/dp/B09HSQQWCL'),
  ('SanDisk 256GB Ultra microSD', 'Extra storage', 'nintendo', 'More room for Switch games, Steam Deck and handhelds.', 'https://www.amazon.com/dp/B0B7NV73PJ'),
  ('Orzly Nintendo Switch Carrying Case', 'Cases and bags', 'nintendo', 'Padded hard case with room for games.', 'https://www.amazon.com/dp/B01NAUKS62'),
  ('FINTIE Nintendo Switch Carrying Case', 'Cases and bags', 'nintendo', 'Slim protective case for Switch and Switch OLED.', 'https://www.amazon.com/dp/B0BMVJYZHL'),
  ('SUPCASE Case for Nintendo Switch 2', 'Cases and bags', 'nintendo', 'Protective grip case made for Switch 2.', 'https://www.amazon.com/dp/B0DT9HZH35'),
  ('Logitech G29 Racing Wheel and Pedals', 'Racing wheels', 'playstation', 'Force-feedback wheel for PS5, PS4 and PC.', 'https://www.amazon.com/dp/B00Z0UWWYC'),
  ('Logitech G920 Racing Wheel and Pedals', 'Racing wheels', 'xbox', 'Force-feedback wheel for Xbox and PC.', 'https://www.amazon.com/dp/B00Z0UWV98')
),
new_products as (
  insert into public.products (name, category, platform, summary)
  select c.name, c.category, c.platform, c.summary from catalog c
  where not exists (select 1 from public.products p where p.name = c.name)
  returning id, name
)
insert into public.product_offers (product_id, retailer, price, url, in_stock, note, earns_commission)
select p.id, 'Amazon', null, c.url, true, 'Check Amazon for the current price', true
from new_products p join catalog c on c.name = p.name;

update public.product_offers o set url = 'https://www.amazon.com/dp/B0BHJJ9Y77' from public.products p where o.product_id = p.id and p.name = 'Samsung 990 Pro 2TB NVMe SSD' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B0B7CKZGN6' from public.products p where o.product_id = p.id and p.name = 'WD Black SN850X 2TB NVMe SSD' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B0BPTKD797' from public.products p where o.product_id = p.id and p.name = 'Corsair Vengeance 32GB DDR5' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B0BTZB7F88' from public.products p where o.product_id = p.id and p.name = 'AMD Ryzen 7 7800X3D' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B0D1T1HZCC' from public.products p where o.product_id = p.id and p.name = 'SteelSeries QcK XXL Mousepad' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B09738CV2G' from public.products p where o.product_id = p.id and p.name = 'Elgato Stream Deck MK.2' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B07DYRS1WH' from public.products p where o.product_id = p.id and p.name = 'Elgato Stream Deck Mini' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B09V1KJ3J4' from public.products p where o.product_id = p.id and p.name = 'Elgato HD60 X Capture Card' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B01LPZM7VI' from public.products p where o.product_id = p.id and p.name = 'Xbox Wireless Controller' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B0CQKLS4RP' from public.products p where o.product_id = p.id and p.name = 'PlayStation DualSense Wireless Controller' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B01NAWKYZ0' from public.products p where o.product_id = p.id and p.name = 'Nintendo Switch Pro Controller' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B07PFB72NL' from public.products p where o.product_id = p.id and p.name = 'Logitech G923 Racing Wheel' and o.retailer = 'Amazon';
update public.product_offers o set url = 'https://www.amazon.com/dp/B0C3BV19Q3' from public.products p where o.product_id = p.id and p.name = 'HyperX Cloud III' and o.retailer = 'Amazon';
