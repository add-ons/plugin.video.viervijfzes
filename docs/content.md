# Content API

## Programs

Programs can be scraped of the homepage of the channel from `a.program-overview__link`. We have a title and a path.

Examples:
* https://www.vier.be/
* https://www.vijf.be/
* https://www.zestv.be/

## Program info

The path can be used to lookup the program info. A GET request has to be made to the channel url appended with the path.
On that page, we can extract a JSON from a `div` with an attribute `data-hero`.

```json
{
  "data": {
    "id": "66c7e887-b468-4e2b-b0f1-534ffc51c327",
    "title": "Auwch_",
    "subtitle": "",
    "description": "Auwch_ draait ook in dit 2de seizoen rond alledaagse pijnlijke en g\u00eanante situaties waarin Ben Segers en Axel Daeseleire voortdurend verzeild geraken. Met de gekende ongemakkelijke stiltes tot gevolg\u2026",
    "label": "",
    "link": "/auwch",
    "images": {
      "hero": "https://images.viervijfzes.be/www.vier.be/production/meta/tnwallpaper3840x2160auwchs3-q5hc5b.jpg?auto=format&crop=edges&dpr=2&fit=crop&h=780&ixlib=php-1.1.0&q=95&w=1440&s=6424ebacd202c98c36e1f93f9e04896a",
      "mobile": "https://images.viervijfzes.be/www.vier.be/production/2020-02/auwchzp-q5hc5w.jpg?auto=format&crop=edges&dpr=2&fit=crop&h=530&ixlib=php-1.1.0&q=95&w=375&s=789a0652a41fea77ee7e59554de76a3c",
      "poster": "https://images.viervijfzes.be/www.vier.be/production/2020-02/auwchmp-q5hc5r.jpg?auto=format&fit=crop&h=590&ixlib=php-1.1.0&q=95&w=410&s=38200a4598b02fcf3fb28db0ffac92a6",
      "teaser": "https://images.viervijfzes.be/www.vier.be/production/meta/tnwallpaper3840x2160auwchs3-q5hc5b.jpg?auto=format&fit=crop&h=452&ixlib=php-1.1.0&q=85&w=682&s=48ad79e81dd385a7108dede9365a5208"
    },
    "header": {
      "title": "Trailer nieuw seizoen",
      "video": []
    },
    "pageInfo": {
      "site": "vier",
      "url": "https://www.vier.be/auwch",
      "nodeId": "365",
      "title": "Auwch_",
      "description": "Auwch_ draait ook in dit 2de seizoen rond alledaagse pijnlijke en g\u00eanante situaties waarin Ben Segers en Axel Daeseleire voortdurend verzeild geraken. Met de gekende ongemakkelijke stiltes tot gevolg\u2026",
      "type": "program",
      "program": "Auwch_",
      "programId": "365",
      "programUuid": "66c7e887-b468-4e2b-b0f1-534ffc51c327",
      "programKey": "auwch",
      "tags": [
        "Auwch_"
      ],
      "publishDate": 1452784345,
      "unpublishDate": 0,
      "author": "michiel.vandevelde@sbsbelgium.be",
      "notificationsScore": 0
    },
    "playlists": [
      {
        "episodes": [
          {
            "autoplay": false,
            "cimTag": "vid.tvi.ep.vod.free",
            "createdDate": 1584045900,
            "description": "<p>De foemp gaat trouwen met Livia. Axel en Ben kunnen natuurlijk niet ontbreken op zijn vrijgezellenfeestje, ook al is dat dik tegen de zin van Axel.</p>\r\n",
            "duration": 1501,
            "embedCta": null,
            "enablePreroll": true,
            "episodeNumber": 5,
            "episodeTitle": "S3 - Aflevering 5",
            "hasProductPlacement": true,
            "image": "https://images.viervijfzes.be/www.vier.be/production/meta/auwch-y03-e05-f0269534mp400072208still004-q72m4w.jpg?auto=format&fit=max&h=720&ixlib=php-1.1.0&q=65&w=1280&s=380f5f672e083e32082f6ed4b081526d",
            "isProtected": true,
            "isSeekable": false,
            "isStreaming": false,
            "link": "/video/auwch/auwch-s3/auwch-s3-aflevering-5",
            "midrollOffsets": [
              808
            ],
            "pageInfo": {
              "site": "vier",
              "url": "https://www.vier.be/video/auwch/auwch-s3/auwch-s3-aflevering-5",
              "nodeId": "30723",
              "title": "Auwch_ - S3 - Aflevering 5",
              "description": "De foemp gaat trouwen met Livia. Axel en Ben kunnen natuurlijk niet ontbreken op zijn vrijgezellenfeestje, ook al is dat dik tegen de zin van Axel.",
              "type": "video-long_form",
              "program": "Auwch_",
              "programId": "365",
              "programUuid": "66c7e887-b468-4e2b-b0f1-534ffc51c327",
              "programKey": "auwch",
              "tags": [
                "Auwch_",
                "Volledige Aflevering"
              ],
              "publishDate": 1584045900,
              "unpublishDate": 1672605900,
              "author": "ken.ceulemans@sbsbelgium.be",
              "notificationsScore": 17
            },
            "pageUuid": "1abd0018-ccc5-4635-871c-fd3082639919",
            "parentalRating": "12+",
            "path": "",
            "program": {
              "title": "Auwch_",
              "poster": "https://images.viervijfzes.be/www.vier.be/production/2020-02/auwchmp-q5hc5r.jpg?auto=format&fit=crop&h=590&ixlib=php-1.1.0&q=95&w=410&s=38200a4598b02fcf3fb28db0ffac92a6"
            },
            "seasonNumber": 3,
            "seekableFrom": 1584047401,
            "title": "Auwch_ - S3 - Aflevering 5",
            "type": "long_form",
            "unpublishDate": 1672605900,
            "videoUuid": "b73bfbba-11aa-4a01-a614-066a1251e3a2",
            "whatsonId": "10137607007678527"
          },
          # ... (more episodes)
        ],
        "id": "42a6f9fc-a451-44f3-9b9d-b9a38f1bebe8",
        "link": "/video/auwch/auwch-s3",
        "pageInfo": {
          "site": "vier",
          "url": "https://www.vier.be/video/auwch/auwch-s3",
          "nodeId": "30207",
          "title": "Auwch_ - Seizoen 3",
          "description": "Auwch_ draait ook in het 3e seizoen rond alledaagse pijnlijke en g\u00eanante situaties waarin Ben Segers en Axel Daeseleire voortdurend verzeild geraken. Met de gekende ongemakkelijke stiltes tot gevolg\u2026",
          "type": "playlist",
          "program": "Auwch_",
          "programId": "365",
          "programUuid": "66c7e887-b468-4e2b-b0f1-534ffc51c327",
          "programKey": "auwch",
          "tags": [],
          "publishDate": 1580728083,
          "unpublishDate": 0,
          "author": "delphine.desimpel@sbsbelgium.be",
          "notificationsScore": 0
        },
        "title": "Seizoen 3"
      },
      # ... (more seasons)
    ],
    "social": {
      "facebook": "https://www.facebook.com/Auwch-703879279714068/?fref=ts",
      "hashtag": "auwch",
      "instagram": "https://instagram.com/opVIER",
      "twitter": "https://twitter.com/@opVIER"
    }
  }
}
```

Examples:
* https://www.vier.be/auwch
* https://www.vijf.be/temptation-island
* https://www.zestv.be/million-dollar-mile

# Braindump
TODO

Interesting urls:

* GET https://www.vier.be/api/content_tree (no auth needed)
```json
# Json is to long
```
  
* GET https://api.viervijfzes.be/notifications (`authorization` header required)
```json
[
  {
    "nid": 30655,
    "notification_created": 1583784914,
    "site": "vier",
    "created": 1583784846,
    "id": "cc2f225f-873b-4b5e-b02b-dc9ef5ecc390",
    "image": "https://images.viervijfzes.be/www.vier.be/production/meta/f0271354-otmxf10220618still004-q6s0di.jpg?auto=format&fit=crop&h=60&ixlib=php-1.1.0&q=90&w=60&s=8722dc9e3db66c278633717c730e9ec7",
    "label": null,
    "program": "6f8eae82-4508-41e9-81ec-8f2e3dcc7fec",
    "program_title": "Topdokters",
    "program_category": "Human Interest",
    "score": 7,
    "title": "Dr. Ombelet is een dierenliefhebber “Ontsnapte beestjes belandden op autostrade\"",
    "type": "video",
    "url": "https://www.vier.be/video/topdokters/dr-ombelet-is-een-dierenliefhebber-ontsnapte-beestjes-belandden-op-autostrade",
    "video_type": "short_form",
    "video_uuid": "55ff7360-cd13-4eb4-ac72-e5cebc10d4b1",
    "read": false,
    "seen": false
  },
  {
    "nid": 30663,
    "notification_created": 1583782514,
    "site": "vier",
    "created": 1583782500,
    "id": "08ec347b-0247-4285-8670-c569b57a434a",
    "image": "https://images.viervijfzes.be/www.vier.be/production/meta/tdafl07gradev1mov00400720still015-q6x369.jpg?auto=format&fit=crop&h=60&ixlib=php-1.1.0&q=90&w=60&s=4da466058804e163920b1c10eb4af401",
    "label": null,
    "program": "6f8eae82-4508-41e9-81ec-8f2e3dcc7fec",
    "program_title": "Topdokters",
    "program_category": "Human Interest",
    "score": 17,
    "title": "Topdokters - S7 - Aflevering 7",
    "type": "video",
    "url": "https://www.vier.be/video/topdokters/topdokters-s7/topdokters-s7-aflevering-7",
    "video_type": "long_form",
    "video_uuid": "51ef9e4c-9b1f-47aa-adb7-3aa5c7155882",
    "read": false,
    "seen": false
  }
  # ...
]
```

* GET https://www.vier.be/api/video/e9c03e53-4895-47ed-a31e-03da9a0b6614 (no auth needed)
  GET https://api.viervijfzes.be/content/e9c03e53-4895-47ed-a31e-03da9a0b6614 (`authorization` header required)
```json
{
  "autoplay": false,
  "cimTag": "vid.tvi.ep.vod.free",
  "createdDate": 1556479170,
  "description": "\u003Cp\u003EDe kandidaten zijn aangekomen in Ho Chi Minh City, de grootste stad van Vietnam. De kleine steegjes en achterbuurten van de stad vormen het decor voor een zenuwslopend eindspel, met een torenhoge inzet. Wie legt zijn kaarten op tafel?\u003C/p\u003E\r\n",
  "duration": 3820,
  "embedCta": null,
  "enablePreroll": true,
  "episodeNumber": 8,
  "episodeTitle": "S7 - Aflevering 8",
  "hasProductPlacement": false,
  "image": "https://images.viervijfzes.be/www.vier.be/production/meta/p1140174-pqoli6.JPG?auto=format\u0026fit=max\u0026h=720\u0026ixlib=php-1.1.0\u0026q=65\u0026w=1280\u0026s=ad286f2ce519f014409fc6a8e1843416",
  "isProtected": true,
  "isSeekable": true,
  "isStreaming": false,
  "link": "/video/de-mol/de-mol-2019/de-mol-seizoen-7-aflevering-8",
  "midrollOffsets": [
    1276,
    2725
  ],
  "pageInfo": {
    "site": "vier",
    "url": "https://www.vier.be/video/de-mol/de-mol-2019/de-mol-seizoen-7-aflevering-8",
    "nodeId": "25359",
    "title": "De Mol - Seizoen 7 - Aflevering 8",
    "description": "De kandidaten zijn aangekomen in Ho Chi Minh City, de grootste stad van Vietnam. De kleine steegjes en achterbuurten van de stad vormen het decor voor een zenuwslopend eindspel.",
    "type": "video-long_form",
    "program": "De Mol",
    "programId": "337",
    "programUuid": "7f9c4278-8372-47ef-9cc8-cc10c7b7c9f5",
    "programKey": "de_mol",
    "tags": [
      "De Mol",
      "Volledige Aflevering",
      "Seizoen 2019",
      "Vietnam"
    ],
    "publishDate": 1556479170,
    "unpublishDate": 0,
    "author": "Wouter",
    "notificationsScore": 17
  },
  "pageUuid": "e9c03e53-4895-47ed-a31e-03da9a0b6614",
  "parentalRating": "",
  "path": "",
  "program": {
    "title": "De Mol",
    "poster": "https://images.viervijfzes.be/www.vier.be/production/2020-02/onlinempl1050x1500demol2020-q5y2eg.jpg?auto=format\u0026fit=crop\u0026h=590\u0026ixlib=php-1.1.0\u0026q=95\u0026w=410\u0026s=502e63c1887875d409865a548a83ff11"
  },
  "seasonNumber": 7,
  "seekableFrom": 1583939179,
  "title": "De Mol - Seizoen 7 - Aflevering 8",
  "type": "long_form",
  "unpublishDate": "",
  "videoUuid": "1f291b18-a50d-494a-a19d-a38b8945c62b",
  "whatsonId": "10138413273449527"
}
```

* GET https://images.viervijfzes.be/www.vier.be/production/meta/tnwallpaper3840x2160demol2020-q5y6k8.jpg?auto=format&fit=crop&h=752&ixlib=php-1.1.0&q=85&w=1394&s=5f78f68246dc3f40673acaa2d5f21451

* GET https://api.viervijfzes.be/content/{{ id }}
* POST https://api.viervijfzes.be/email/change
  - step
  - uuid
  - old_email
  - new_email
* POST https://api.viervijfzes.be/email/get
  - id
* POST https://api.viervijfzes.be/email/sync
  - email
* POST https://api.viervijfzes.be/email/valid
  - email
* GET https://api.viervijfzes.be/notifications
* POST https://api.viervijfzes.be/personalization
* POST https://api.viervijfzes.be/reset
  - Domain
  - Email
  - Url
* POST https://api.viervijfzes.be/search
  - query
  - sites ('vier', 'vijf', 'zes')
  - page
  - mode: 'byDate'
* POST https://api.viervijfzes.be/webform
  - FormId
  - Created
  - UserName: Wieni
  - Blob
* PUT https://api2.viervijfzes.be/selligent/lists/
  - options
* POST https://api2.viervijfzes.be/selligent/newsletter/
  - email
