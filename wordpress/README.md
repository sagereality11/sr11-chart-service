# WordPress snippets

Code that runs on sagereality11.com (installed as WPCode snippets), kept here so it is versioned
alongside the service it calls.

* `wealth-story.php` (PHP, Run Everywhere): Your Birth Chart's Wealth Story free calculator `[sr_wealth_story_calculator]`, the paid
  reading page `[sr_wealth_story_reading]`, order links, and the `sr11ws/v1` REST routes that forward to `/v1/wealth-story`.
* `your-2027-reading.php` (PHP, Run Everywhere): Your 2027 Reading access gate, order links,
  birth-data form shortcode `[sr_your_2027_reading]`, and the `sr11y27/v1/reading` REST route that
  forwards to `/v1/year-ahead` using the SR11 Birth Chart plugin's saved service URL and key.
* `sr11chart-client.js` (JavaScript, WPCode snippet 8268, sitewide): `SR11Chart`, the shared birthplace search and chart
  service client. Its birth-record time zone box also asks US visitors born April to October 1946-1966
  whether their town used daylight saving time, and sends the answer as `record_offset_minutes`.
