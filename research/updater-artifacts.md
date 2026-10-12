# A1c — Updater and comparison-artifact acquisition ledger

## Scope and provenance rules

Investigation date: **2026-10-12, America/Los_Angeles**. Starting current `main`:
`c3cb29018a85be959560edf2be6c570b4197c1d9` (PR #3 confirmed merged).
Branch: `analysis/a1c-updater`. This ledger records offline acquisition research;
the [A1c report](../analysis/reports/A1c-updater.md) assesses its implications.

**OBSERVED:** no updater, installer, historical archive, extracted application
component, or second SXI was acquired. The existing user-supplied SXI was recovered
and reverified. A rendered download page is not a downloaded binary. `Unavailable`
size/hash below means **no bytes obtained**, not an empty file. Reported names,
versions, formats and sizes are source claims, not binary measurements.

Browser failures describe this access path on this date. They do not prove that
an origin permanently removed a file, that an archive has no capture, or that a
401 file could never be shared legitimately. No login, security-control bypass,
driver installation, legacy updater execution or device communication occurred.

## Obtained artifact

| Field | Verified value |
| --- | --- |
| ID | A1c-F01, existing A1/A1b sample; **not a second sample** |
| Original distribution/source | Historical RAR name reported in [firmware custody](../firmware/README.md); original public URL unknown. Actual bytes came from the user attachment recorded in [A1](../analysis/reports/A1-container.md) |
| Reported target/version | Original iPV3 160W upgrade V3.5, filename date `20141126`; no factory-150W identity claim |
| Attachment | `sediment://file_0000000029a481fd85e5b7dbaa475783`, recovered through `download_file` on the investigation date |
| Downloaded source | `/workspace/attachments/23d719a9-0696-42f6-8fc6-266942b9816c/ipv3_160W_V3.5.SXI` |
| Staged unchanged | `work/firmware/ipv3_160W_V3.5.SXI`, copied to a previously nonexistent destination |
| Independently measured size | **56,009 bytes**, source and staged |
| Independently measured SHA-256 | **`ead7034350cd72aa2a804b5897b377be53d0100eead2d7f432b1624fa091b71d`**, source and staged |
| Actual binary obtained | **Yes, SXI only**; original RAR not obtained |
| Generation confidence | High for byte identity with A1/A1b; exact header and grammar rechecked. Historical archive chain is still the prior user provenance, not a fresh manufacturer download |
| Exclusion | `.gitignore:2:work/`; `git ls-files -- work/` empty |

The historical RAR's previously reported 32,079-byte size is not independently
reverified here. The supplied filename differs from the historical extracted
name; the SXI hash establishes sample identity, not RAR identity.

## Updater candidates — documentation only

All candidates below were researched on the investigation date. **None has a
measured size or SHA-256; no actual executable was obtained.** Firmware-version
numbers must not be treated as updater-version numbers.

| ID | Reported artifact/version and target | Original link/distribution source | Retrieval/provenance result | Confidence for our SXI generation |
| --- | --- | --- | --- | --- |
| U01 | `YiHi SXi Setup-v20140808-60w.msi`, SX350 60W interface, reportedly inside a RAR | [Manufacturer SXI Driver 20140808 page](http://www.yihiecigar.com/download_info/SXI-Driver-20140808-d59080.html), linked by [2015-02-02 firsthand SX350 tutorial](https://forum.planetofthevapes.co.uk/threads/sx350-logo-change-tutorial.61606/), post #1, installer paragraph | Link followed to HTTPS; browser reported **404**. Original archive URL was not recovered. `.msi` format is reported only | **Unknown**; contemporary and numeric date matches the sample header substring, but neither that similarity nor SX350 support proves iPV3/SX330-V3S parser compatibility |
| U02 | `YiHi-SXi-Setup-v20150522-1621.rar`; contained MSI reported by 2015 instructions; SXmini M Class | [Manufacturer direct RAR](http://www.yihisxmini.com/download/YiHi-SXi-Setup-v20150522-1621.rar), reproduced in [2015-05-28 discussion](https://forums.overclockers.co.uk/threads/the-vapers-lounge-2-0.18642758/page-256), dated passage; [2015-06-04 MSI description](https://www.forum-ecigarette.com/viewtopic.php?t=176023), sole post | Direct RAR inaccessible via browser. Alternate manufacturer link below returned **404**. No RAR/MSI bytes | **Unknown**; contemporary related device family, no demonstrated support for the verified iPV3 sample |
| U03 | Unversioned “YiHi Upgrade Install Program”, SX350 | [Retailer listing](https://www.ecigareta-shop.cz/diy-elektro/1808-yihi-sx350.html), upgrade section → [Drive object](https://drive.google.com/file/d/0B61oDGxskBGhdXAydWRWa1BUcWc/edit?usp=sharing) | Browser reported **401 Unauthorized**. Listing describes approximately 50 MB; this is **reported**, not measured. No date/version or file format independently established | **Unknown**; SX350 attribution on retailer page only |
| U04 | “New SXi upgrade package”, iPV3 Li / SX330-V3SL, version unspecified | [Pioneer4You article #27](http://www.pioneer4you.com/article.php?id=27), linked in [retailer release note with 2015-06-27 update](https://clubvapejuice.com/blogs/news/ipv-3-li-165w-box-mod-by-pioneer4you/) | Manufacturer article inaccessible via browser; no underlying package URL or binary | **Unknown**; later iPV3 **Li** is a distinct reported target, not established compatibility with original iPV3 |
| U05 | Catalogue labels YiHi SXi 2.3.0 and old version 1.9; target described generically | [Software Informer listing](https://yihi-sxi.software.informer.com/) and [download page](https://yihi-sxi.software.informer.com/download/) | Readable catalogue; download page offers developer homepage rather than binary. No date, package hash or model list. No request-link form submitted | **Unknown**; catalogue labels cannot be tied to U01/U02 or dated 2014–2015 |

U02's alternative manufacturer link, recovered by following post #31 in the
[2015-05-28 POTV discussion](https://forum.planetofthevapes.co.uk/threads/yihi-sxmini-m-class-1st-upgrade-software-news.72668/page-4):

```text
http://www.yihiecigar.com/down/uploadfile/y3/yihiecigar5183/download/Other/YiHi-SXi-Setup-v20150522-1621.rar.html
```

Its HTTPS retrieval returned 404. Preserve the literal `.rar.html` suffix: it is
a source-linked endpoint, not an acquired RAR or license to guess a different URL.

## Firmware candidates and fallback

**OBSERVED:** fallback sought a second compatible-generation sample, using named
devices, dates and historical distribution context rather than extension alone.
None was obtained; **all sizes and SHA-256 values are unavailable**.

| ID | Candidate/version and reported target | Source/original link | Result and compatibility limit |
| --- | --- | --- | --- |
| F02 | `Only-for-IPV3-160W-Upgrade-Software_20141126_V3.5-1417490378.rar`, original iPV3 V3.5 | Mission anchor and existing repository custody; original public URL unknown | Searches did not recover an independently retrievable archive. F01 is the existing extracted sample, not reacquisition of this RAR |
| F03 | `1417136803311769852.zip`, reported historical 165W iPV3 upgrade | Mission anchor; original public URL unknown | Exact-name queries yielded no usable acquisition lead. No guessed manufacturer path constructed; target/version remain unverified for these archive bytes |
| F04 | `SX350_OldBoot_60W_YH_Logo-20140808-v2.3.SXI`, SX350 | [POTV tutorial](https://forum.planetofthevapes.co.uk/threads/sx350-logo-change-tutorial.61606/), post #1 says bundled with U01 | U01's manufacturer page returned 404; no bundled SXI recovered. Contemporary candidate; shared header/grammar not tested |
| F05 | `Yihiecigar SX350 60W Upgrade Software_YH_Logo_60W_20141202_V2.6.SXI` | Same tutorial → [manufacturer firmware page](http://www.yihiecigar.com/download_info/Upgrade-Software-for-SX350-50W-or-60W-d61630.html) | HTTPS page returned **404**. No archive link/bytes. Model context identifies a research candidate, not proven SXI encoding compatibility |
| F06 | SX350 “50W Upgrade sxi File”, version unspecified | [Retailer](https://www.ecigareta-shop.cz/diy-elektro/1808-yihi-sx350.html) → [Drive object](https://drive.google.com/file/d/0B61oDGxskBGhY2FjWDZGUWUybTg/edit?usp=sharing) | **401 Unauthorized**. Filename, header, prefix, token counts and size unknown |
| F07 | SX350 “60W Upgrade sxi FIle”, version unspecified | Same retailer → [Drive object](https://drive.google.com/file/d/0B61oDGxskBGhc2VlMGFGV0F5NG8/edit?usp=sharing) | **401 Unauthorized**. Same untested compatibility limits as F06 |
| F08 | `Upgrade-Firmware-for-M-Class-150W.rar`; discussion labels release 1711 v2.1 and separately reports beta 1849 v2.21 | [Manufacturer RAR](http://www.yihisxmini.com/download/Upgrade-Firmware-for-M-Class-150W.rar), [POTV 2015 discussion](https://forum.planetofthevapes.co.uk/threads/yihi-sxmini-m-class-1st-upgrade-software-news.72668/page-4), posts #31/#38 | **404** on linked RAR. No evidence that the beta is that URL's content. SXmini M Class candidate only |
| F09 | `SXmini-M-Class-120W_20150530-V2.2.rar` / corresponding `.SXI` | [2015-06-04 tutorial](https://www.forum-ecigarette.com/viewtopic.php?t=176023) → [manufacturer RAR](http://www.yihisxmini.com/download/SXmini-M-Class-120W_20150530-V2.2.rar) | **404**. No independent sample or header/token comparison |
| F10 | `SX330_iPV3Li_T_200W_20150623-1034_V1.6.SXI` and archive `SX330-iPV3Li-Upgrade-200W-V1.6-20150623-1435556516.rar` | [2015 public troubleshooting log](https://www.techspot.com/community/topics/random-spyware-that-i-think-ive-managed-to-remove.219077/) lists these local names; [retailer](https://clubvapejuice.com/blogs/news/ipv-3-li-165w-box-mod-by-pioneer4you/) links manufacturer [article #26](http://www.pioneer4you.com/article.php?id=26) | Search-level provenance lead, no binary URL recovered; article #26 not separately probed. Log reports archive size 39,918, **not measured here**. Li target is distinct; presence of a nearby runtime DLL in a log does not establish updater dependencies |
| F11 | `SX350_Logo_Changer_Release.zip`, reportedly includes version-specific `.data` files | [POTV tutorial](https://forum.planetofthevapes.co.uk/threads/sx350-logo-change-tutorial.61606/) → [Dropbox](https://www.dropbox.com/s/3jsvzwh2a99w68t/SX350_Logo_Changer_Release.zip) | Browser rendered Dropbox error page with no content/bytes. Third-party editor, not an authentic YiHi updater. No modified firmware generated; reported `.data` files not assumed to be SXI images |

A search excerpt at [forum post 4337485](https://www.forum-ecigarette.com/viewtopic.php?p=4337485)
also mentions a `toonsmil.chez-alice.fr` mirror and `350Mini_V1.3.data`. Opening
the post timed out, leaving a truncated mirror URL. It was not reconstructed,
downloaded or renamed. A suggestion in a forum is not evidence of byte identity.

## Endpoint and search log

The search used two stages: contemporary updater acquisition, then second-sample
fallback. It stopped after the fallback's three retailer Drive links returned
401. It did not repeat requests to those protected objects. Browser rendering
was read-only; no installer instructions in source pages were followed.

| Endpoint/method | Observed outcome on investigation date |
| --- | --- |
| `git fetch origin main` through configured executor proxy | Exit 128: `Failed to connect to proxy port 8080`; failed before origin contact. No direct route/proxy bypass attempted |
| `https://www.yihiecigar.com/download.html` | Browser **404**, independently of the executor proxy failure |
| `https://www.yihiecigar.com/product_cat_list/YiHiEcigar-SX330-V3-S-150W-c20092.html` | Browser inaccessible; linked by [2014 original-iPV3 discussion](https://vapingunderground.com/threads/p4y-ipv3-150watt-box-mod-in-hand-first-looks.20024/) |
| `https://www.yihisxmini.com/download-center.html` | Readable current manufacturer shell, no historical download links in rendition |
| `https://www.yihisxmini.com/firmware-download.html` | Readable rendition shows zero firmware entries and a current SX416/SX304 web tool link; catalogue completeness unknown; current generations not substituted for target |
| Wayback CDX, `https://web.archive.org/cdx/search/cdx?url=yihiecigar.com/download_info/SXI-Driver-20140808-d59080.html&output=json&filter=statuscode:200&collapse=digest` | Browser inaccessible; **no CDX response/capture inventory obtained** |
| Wayback CDX, `https://web.archive.org/cdx/search/cdx?url=pioneer4you.com/*&output=json&filter=urlkey:.*1417136803311769852.*` | Browser inaccessible; no archive result obtained |
| Wayback timestamp request, `https://web.archive.org/web/20150201000000/http://www.yihiecigar.com/download_info/SXI-Driver-20140808-d59080.html` | Browser inaccessible; timestamp was a **requested lookup**, not an observed capture date |
| POTV `https://forum.planetofthevapes.co.uk/goto/post?id=805091` | Timeout; canonical thread page subsequently readable, supplied U02 alternate link |
| GitHub repository searches: `yihi` (first 20), `sx350` (first 20), `yihi firmware` (first 10), `sx330` (first 10) | `sx350` returned none; `yihi` results were unrelated; latter two returned this project only. Bounded search does not prove global absence |
| GitHub code searches: `v20140808-SXi-YiHiEcigar`, `SX350_OldBoot_60W` (up to 10 each) | Empty results; no implementation or artifact obtained. Index/access limits apply |

Reproduce web discovery with these exact query strings (grouped by stage, not
claims that every query had independent results). Combined search responses
often repeated the same forum pages or unrelated products.

Updater stage, 25 queries:

```text
"YiHi" "SXi" download 2014 updater
"Only-for-IPV3-160W" software
"1417136803311769852.zip"
"IPV3" "SXi" download software 2014
"YiHi SXi" "20140808"
"1417136803311769852"
"Only-for-IPV3-160W-Upgrade-Software_20141126"
"YiHi" "SXi" site:github.com
"ipv3" "165w" "zip" download
"YiHi SXi Setup-v20140808" download
ipv3 165w firmware download pioneer4you 2014
"SXi" "v20140808" download -site:forum.planetofthevapes.co.uk
"YiHi-SXi-Setup-v20150522-1621.rar"
"SX330-V3S" software download
"ipv3" "165w" "download" "software"
"ipv3" "SXi" "2014" "msi"
"ipv3" "1417136803"
"1417136803311769852.zip"
"YiHi" "SXi" "github"
"SX350" "Logo" "Changer" source code
"SXi" "YiHi" "download" "2014" MSI
"ipv3" "165" "firmware" "pioneer4you.com/download"
"ipv3" "150w" "software" download -site:techspot.com
"YiHi" "SXi" "software" archive.org
"SX350_OldBoot_60W" download
```

Fallback stage, seven queries:

```text
"SX350" "SXI" download firmware 20141202
"ipv3" "SXI" firmware download 160W
"SX330" "SXI" firmware github
"SXmini-M-Class-120W_20150530-V2.2.rar"
"Yihiecigar SX350 60W Upgrade Software_YH_Logo_60W_20141202_V2.6.SXI"
"ipv3_160W_V3.5.SXI"
"SX350_Logo_Changer_Release.zip"
```

Optional local audit cache: `work/updater/A1c-retrieval-log.json`, **305,430 bytes**,
SHA-256 `692ad263596b1272fe1fac2e34f0b91f073341ab2763ccb1379cd8d55f0d5e48`.
It preserves tool-rendered responses for the subsequent research batches, including
endpoint errors; the initial three-query response is not in this cache. It is
**not original HTTP content, a binary download, or a complete web archive**, and
is deliberately Git-ignored. The committed URLs, post references, query strings
and explicit outcomes above are the durable acquisition record.

## Reacquisition gate

For a legitimately obtained original archive/MSI, retain its original filename
unchanged under ignored `work/updater/`. Before extraction or inspection, record
source URL or supplied attachment, retrieval date, byte size and SHA-256 with:

```sh
python -c 'import hashlib,pathlib,sys; p=pathlib.Path(sys.argv[1]); b=p.read_bytes(); print(p.name,len(b),hashlib.sha256(b).hexdigest())' work/updater/ORIGINAL_FILENAME
git check-ignore -v work/updater/ORIGINAL_FILENAME
git ls-files -- work/
```

Extract using an archive reader in an isolated offline workspace, without running
installer entry points, custom actions or drivers. Hash each extracted component
and trace supported-model/header checks before using its parser to interpret F01.
No artifact has passed that gate in A1c.
