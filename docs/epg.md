# EPG API

There is a public API that can be called without authentication to get the EPG details:

## Request
* GET `https://www.vier.be/api/epg/{date}`
* GET `https://www.vijf.be/api/epg/{date}`
* GET `https://www.zestv.be/api/epg/{date}`

`{date}` is in the format `YYYY-MM-DD`. It seems the backend supports an EPG window of -7 days to +13 days.
When there is no data, an empty array is returned.

## Response

An array is returned with `item[]`.

### `item`

| Key               | Description         | Example |
|-------------------|---------------------|---------|
| `program_title`   | Program Title       | Two and a Half Men |
| `episode_title`   | Episode Title       | I Always Wanted a Shaved Monkey |
| `original_title`  | Original Title      | I Always Wanted a Shaved Monkey - TWO AND A HALF MEN Y2 - 44 |
| `episode_nr`      | Episode Nr          | 20 |
| `season`          | Season Nr           | 2 |
| `genre`           | Genre               | Komische serie |
| `timestamp`       | Timestamp of airing | 1584117000 |
| `date_string`     | Date of airing      | 2020-03-13 |
| `time_string`     | Time of airing      | 17:30 |
| `won_id`          | WON ID              | 10126759315600527 |
| `won_program_id`  | WON Program ID      | 10126709310101527 |
| `program_concept` | Program description | De Harperbroers zijn volledig tegengesteld, maar vormen een fantastisch team. Charlie staat Alan "tijdelijk" toe om samen met zijn zoon Jake bij hem in te trekken... |
| `content_episode` | Episode description | Evelyn belt op de vaste telefoon, en Charlie neemt op. En Berta heeft Charlies dure kleren weggegooid. |
| `duration`        | Duration in seconds | 1800 |
| `program_node` °  | Program object      | |
| `video_node` °    | Video object        | |

> Note: `°` Optional field

### `program_node`
| Key               | Description                  | Example       |
|-------------------|------------------------------|---------------|
| `url`             | URL path to the program page | /huizenjagers |

### `video_node`

| Key             | Description                | Example |
|-----------------|----------------------------|-------- |
| `description`   | Description                | Gepassioneerde makelaars\u00a0openen opnieuw de jacht op Vlaanderens verleidelijkste vastgoed \u00e9n op de Huizenjagerstrofee.",
| `duration`      | Actual video duration      | 2154 |
| `image`         | Episode image              | https://images.viervijfzes.be/www.vier.be/production/meta/vlcsnap-2020-03-12-08h55m41s209-q72m81.png?auto=format&fit=crop&h=452&ixlib=php-1.1.0&q=85&w=682&s=3d4a0a6a079bc5b41ddfed72e9985d10 |
| `latest_video`  |                            | true |
| `created`       |                            | 1584036000 | 
| `title`         | Title                      | Huizenjagers - S6 - Aflevering 28 |
| `url`           | URL path to the video page | /video/huizenjagers/huizenjagers-s6/huizenjagers-s6-aflevering-28 |

## Examples

```json
[
  {
    "program_title": "Two and a Half Men",
    "episode_title": "I Always Wanted a Shaved Monkey",
    "original_title": "I Always Wanted a Shaved Monkey - TWO AND A HALF MEN Y2 - 44",
    "episode_nr": "20",
    "season": "2",
    "genre": "Komische serie",
    "timestamp": 1584117000,
    "date_string": "2020-03-13",
    "time_string": "17:30",
    "won_id": "10126759315600527",
    "won_program_id": "10126709310101527",
    "program_concept": "De Harperbroers zijn volledig tegengesteld, maar vormen een fantastisch team. Charlie staat Alan \u0027tijdelijk\u0027 toe om samen met zijn zoon Jake bij hem in te trekken...",
    "content_episode": "Evelyn belt op de vaste telefoon, en Charlie neemt op. En Berta heeft Charlies dure kleren weggegooid.",
    "duration": 1800
  },
  {
    "program_title": "Huizenjagers",
    "episode_title": "Antwerpen",
    "original_title": "W49 ANTWERPEN Dag 4 - HUIZENJAGERS Y6 - 28",
    "episode_nr": "28",
    "season": "6",
    "genre": "Reality",
    "timestamp": 1584114300,
    "date_string": "2020-03-13",
    "time_string": "16:45",
    "won_id": "10141609938550527",
    "won_program_id": "10135234661743527",
    "program_concept": "Gepassioneerde makelaars\u00a0openen opnieuw de jacht op Vlaanderens verleidelijkste vastgoed \u00e9n op de Huizenjagerstrofee.",
    "content_episode": "Momenteel huren Nickola en Ja\u00ebla een huis in Duffel, maar nu gaan ze voor een eigen huis met drie slaapkamers, een dressing en een grote tuin. Gemakkelijker gezegd dan gedaan, want ze houden elk van een andere stijl. Over het budget zijn ze het wel eens: 550.000 euro.",
    "duration": 2700,
    "program_node": {
      "url": "\/huizenjagers"
    },
    "video_node": {
      "description": "Gepassioneerde makelaars\u00a0openen opnieuw de jacht op Vlaanderens verleidelijkste vastgoed \u00e9n op de Huizenjagerstrofee.",
      "duration": 2154,
      "image": "https:\/\/images.viervijfzes.be\/www.vier.be\/production\/meta\/vlcsnap-2020-03-12-08h55m41s209-q72m81.png?auto=format&fit=crop&h=452&ixlib=php-1.1.0&q=85&w=682&s=3d4a0a6a079bc5b41ddfed72e9985d10",
      "latest_video": true,
      "created": 1584036000,
      "title": "Huizenjagers - S6 - Aflevering 28",
      "url": "\/video\/huizenjagers\/huizenjagers-s6\/huizenjagers-s6-aflevering-28"
    }
  }
  # ...
]
```