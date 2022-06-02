# INGV Earthquakes

<p class='img'>
  <img src='https://github.com/caiosweet/Home-Assistant-custom-components-INGV/blob/main/assets/brand/logo_128.png'/>
</p>

[![hacs][hacsbadge]][hacs] [![Validate](https://github.com/caiosweet/Home-Assistant-custom-components-INGV/actions/workflows/validate.yaml/badge.svg)](https://github.com/caiosweet/Home-Assistant-custom-components-INGV/actions/workflows/validate.yaml)

[![GitHub latest release]][githubrelease] ![GitHub Release Date] [![Maintenancebadge]][Maintenance] [![GitHub issuesbadge]][GitHub issues]

[![Websitebadge]][website] [![Forum][forumbadge]][forum] [![telegrambadge]][telegram] [![facebookbadge]][facebook]

[![Don't buy me a coffee](https://img.shields.io/static/v1.svg?label=Don't%20buy%20me%20a%20coffee&message=🔔&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://paypal.me/hassiohelp)

Instructions on how to integrate the INGV Earthquakes feed into Home Assistant.

All credit goes to Malte Franken [@exxamalte](https://github.com/exxamalte).

The `ingv_centro_nazionale_terremoti` integration lets you use a QuakeML feeds provided by the
Italian [Istituto Nazionale di Geofisica e Vulcanologia](http://www.ingv.it/it/) with information
about seismic events like earthquakes on the Italian Peninsula.
It retrieves incidents from a feed and shows information of those
incidents filtered by distance to Home Assistant's location.

Entities are generated, updated and removed automatically with each update
from the feed. Each entity defines latitude and longitude and will be shown
on the default map automatically, or on a map card by defining the source
`ingv_centro_nazionale_terremoti`. The distance in kilometers is available as the state
of each entity.

<p class='img'>
  <img src='https://github.com/caiosweet/Home-Assistant-custom-components-INGV/blob/main/assets/images/map.png' />
</p>

The data is updated every 5 minutes and retrieve all events from the last 24 hours by default.

<div class='note'>

The material used by this integration is provided under the [Creative Commons Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/).
It has only been modified for the purpose of presenting the material in Home Assistant.
Please refer to the [creator's disclaimer notice](hhttp://terremoti.ingv.it/en/webservices_and_software) and [Terms of service](http://www.fdsn.org/webservices/) for more information.

We acknowledge the INGV and ISIDe Working Group at National Earthquake Observatory project and its sponsors by the Italian Presidenza del Consiglio dei Ministri, Dipartimento della Protezione Civile, for providing data/images used in this integration.

</div>

## How to install

1. Install via [HACS](https://hacs.xyz/)
  or
    you can copy the entire  **ingv_centro_nazionale_terremoti** folder into **custom_components** folder in your root directory.
    You will need to create the dir **custom_components** if this is your first custom component.
2. Restart Home Assistant.

## Configuration

### Config flow user interface

To configure this integration go to: `Configurations` -> `Integrations` -> `ADD INTEGRATIONS` button, search for `INGV` and configure the component.

You can also use following [My Home Assistant](http://my.home-assistant.io/) link

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ingv_centro_nazionale_terremoti)

### Config yaml

1. Add the following lines to your `configuration.yaml`:

   ```yaml
    # Example configuration.yaml entry
    ingv_centro_nazionale_terremoti:
        location: "Home"
   ```

2. Save it.
3. Restart again Home Assistant.

> NOTE:
> In an environment other than HassOS, you will probably need to install the dependencies manually.
> Activate Python environment Home Assistant is running in and use following command:
>
> `python3 -m pip install aio_quakeml_ingv_centro_nazionale_terremoti_client`

### CONFIGURATION VARIABLES

| Variables          | Type        | Requirement   | Default   |  Description |
|--------------------|-------------|---------------|------------|--------------|
|**location**| string | optional | Location name defined in your `configuration.yaml` | Location name.
|**latitude**| string | optional | Latitude defined in your `configuration.yaml` | Latitude of the coordinates around which events are considered.
|**longitude**| string | optional | Longitude defined in your `configuration. yaml` | Longitude of the coordinates around which events are considered.
|**radius**| float | optional | 50.0 | The distance in kilometers around Home Assistant's coordinates in which seismic events are included.
|**minimum_magnitude**| float | optional | 3.0 | The minimum magnitude of an earthquake to be included.
|**scan_interval**| int | optional | 300 | The time in seconds for each update.
|**start_time**| int | optional | 24 | The start-time delta in hours. (ex last 24 hours)

## State Attributes

The following state attributes are available for each entity in addition to the standard ones:

| Attribute          | Description |
|--------------------|-------------|
| latitude           | Latitude of the earthquake. |
| longitude          | Longitude of the earthquake. |
| source             | `ingv_centro_nazionale_terremoti` to be used in conjunction with `geo_location` automation trigger. |
| region             | Textual description of named geographic region near to the event. |
| magnitude          | Reported magnitude of the earthquake. |
| depth              | The depth of the quake in km. |
| status             | The Evaluation Status of the quake (preliminary, confirmed, reviewed, final, rejected). |
| mode               | The Evaluation Mode of the quake (manual or automatic). |
| publication_date   | Date and time when this event occurred. |
| event_id           | Return the short id used in the feed to identify the earthquake in the feed. |
| image_url          | URL for a map not provided in the feed that marks the location of the event. This could for example be used in notifications. **Images are only available for magnitude >= 3**. |

![geo_location](https://github.com/caiosweet/Home-Assistant-custom-components-INGV/blob/main/assets/images/geo_location.png)

## Sensor

This integration automatically creates a sensor that shows how many entities
are currently managed by this integration. In addition to that the sensor has
some useful attributes that indicate the currentness of the data retrieved
from the feed.

![sensor](https://github.com/caiosweet/Home-Assistant-custom-components-INGV/blob/main/assets/images/sensor.png)

| Attribute              | Description |
|------------------------|-------------|
| status                 | Status of last update from the feed ("OK" or "ERROR").  |
| last update            | Timestamp of the last update from the feed.  |
| last update successful | Timestamp of the last successful update from the feed.  |
| last timestamp         | Timestamp of the latest entry from the feed.  |
| created                | Number of entities that were created during last update (optional).  |
| updated                | Number of entities that were updated during last update (optional).  |
| removed                | Number of entities that were removed during last update (optional).  |

## Full Configuration

```yaml
# Example configuration.yaml entry
ingv_centro_nazionale_terremoti:
  location: "Home"
  latitude: 41.89
  longitude: 12.51
  radius: 100
  minimum_magnitude: 2.0
  scan_interval: 300
  start_time: 24

```

___

## [Other information](https://hassiohelp.eu/2019/10/06/home-assistant-package-eventi-naturali/)

## [My Package](https://github.com/caiosweet/Package-Natural-Events/tree/main/config/packages)

## Example Zone

```yaml
zone:
  - name: geoalert
    latitude: !secret latitude_home
    longitude: !secret longitude_home
    radius: 100000 #The radius of the zone in meters
    passive: true
```

## Example Automation

```yaml
automation:
  alias: INGV Quakes Notification Send
  description: ''
  trigger:
    - platform: geo_location
      source: ingv_centro_nazionale_terremoti
      zone: zone.geoalert
      event: enter
  condition: []
  action:
    - service: notify.discord
      data:
        title: New INGV Quakes
        message: |
          Rilevato terremoto a una distanza di {{trigger.to_state.state}} Km da
          casa. Magnitudo: {{trigger.to_state.attributes.magnitude}}  Epicentro:
          {{trigger.to_state.attributes.region}} Profondità:
          {{trigger.to_state.attributes.depth}} km. {% set data_utc =
          trigger.to_state.attributes.publication_date %}
          {{as_timestamp(data_utc)|timestamp_custom('%H:%M:%S - %d/%m/%Y')}}
  mode: queued
```

## Example Lovelace Map Card

```yaml
type: map
entities:
  - entity: person.YUOR_PERSON
geo_location_sources:
  - ingv_centro_nazionale_terremoti
dark_mode: true
default_zoom: 8
aspect_ratio: '16:9'
hours_to_show: 72
```

<p class='img'>
  <img src='https://github.com/caiosweet/Home-Assistant-custom-components-INGV/blob/main/assets/images/ingv-terremoti-feed-image-url.png' />
</p>

## Trademark Legal Notices

All product names, trademarks and registered trademarks in the images in this repository, are property of their respective owners. All images in this repository are used by the author for identification purposes only. The use of these names, trademarks and brands appearing in these image files, do not imply endorsement.

[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg

[GitHub latest release]: https://img.shields.io/github/v/release/caiosweet/Home-Assistant-custom-components-INGV
[githubrelease]: https://github.com/caiosweet/Home-Assistant-custom-components-INGV/releases
[GitHub Release Date]: https://img.shields.io/github/release-date/caiosweet/Home-Assistant-custom-components-INGV

[Maintenancebadge]: https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg
[Maintenance]: https://github.com/caiosweet/Home-Assistant-custom-components-INGV/graphs/commit-activity
[GitHub issuesbadge]: https://img.shields.io/github/issues/caiosweet/Home-Assistant-custom-components-INGV
[GitHub issues]: https://github.com/caiosweet/Home-Assistant-custom-components-INGV/issues

[website]: https://hassiohelp.eu/
[Websitebadge]: https://img.shields.io/website?down_message=Offline&label=HssioHelp&logoColor=blue&up_message=Online&url=https%3A%2F%2Fhassiohelp.eu

[telegram]: https://t.me/HassioHelp
[telegrambadge]: https://img.shields.io/badge/Chat-Telegram-blue?logo=Telegram

[facebook]: https://www.facebook.com/groups/2062381507393179/
[facebookbadge]: https://img.shields.io/badge/Group-Facebook-blue?logo=Facebook

[forum]: https://forum.hassiohelp.eu/
[forumbadge]: https://img.shields.io/badge/HassioHelp-Forum-blue?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAA0ppVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8%2BIDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNS1jMDIxIDc5LjE1NTc3MiwgMjAxNC8wMS8xMy0xOTo0NDowMCAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6ODcxMjY2QzY5RUIzMTFFQUEwREVGQzE4OTI4Njk5NDkiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6ODcxMjY2QzU5RUIzMTFFQUEwREVGQzE4OTI4Njk5NDkiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTQgKFdpbmRvd3MpIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo0MWVhZDAwNC05ZWFmLTExZWEtOGY3ZS1mNzQ3Zjc1MjgyNGIiIHN0UmVmOmRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDo0MWVhZDAwNC05ZWFmLTExZWEtOGY3ZS1mNzQ3Zjc1MjgyNGIiLz4gPC9yZGY6RGVzY3JpcHRpb24%2BIDwvcmRmOlJERj4gPC94OnhtcG1ldGE%2BIDw/eHBhY2tldCBlbmQ9InIiPz4xQPr3AAADq0lEQVR42rRVW2wMURj%2Bz5lL7V27KG26KIuUEJemdalu3VN3Ei/ipSWUuIV4FB4kHrwo8VLRROJBgkYElZCi4olG4rVoROOSbTa0u7pzO/6Z2Zmd3Z2uevBn/8zsf/7zff/tnKGMMRi/pjM6/j08oKiqCm1tbTA4OAhuoqkS8KKPVjceOcgJngkfnl%2B5JiWH0pQvcfUPhULQ0dEBPp8PDBZZlqGyshLGFKG0fHHr/QfNlxnbjFp7uOcl8VVVj%2BXu9XohkUgY2NRpdJMpc5qWN5971zu7ftsWkSAX2iKLYg3NZ/t6Kxbu2Oi2x4g8IxSKSDR2tLXh2JOn3nAkKv9GAzPtyigS%2BSdV1B3sejhv09lTxTBcCXjRK9buu96%2BZG/7dUYEryK59EXWewNcza7zl%2Br237kpessC4yIITIlGGk88666OtR6VMFKmZhZY9sGsdw1ATgFU1O7et%2Brki56JVUtqsl4kl0CVUjB57vo1Tad7X4Wj9U1S0vRj8HfRSQKVC5auPN7zctqiPTs1Rz2pBV6xcOuq%2BkOPusVAeZWxDg5wl%2Bhz1vW%2BpBFMDIYXt9y%2BF6lr2a6kR7IEmipDeFYsRkVewFcTyAXcBtNMhTxCTTErUxZdu96qLW8varhFsyrnQCQOYNXU8qBp//4TH/jkHZ3UCTXFoncQGKciP1SiN1JDVY2IJwgEjq3jYMVsZgC/HSBw9RnA8CgBjmS3MkdefE638sCV0WGQk9/QXYNRicH%2B7eWwYUGpOT4oq%2Bfq0Upw4SEPVOCLnwOWp5o%2BgskfWEoZe8Qg6CGwcp7XWFVxTc0UYdlMrLmQsP8zVuQcWFNiORFCTSvRQTWQs6W101SRXE7/xiDSBeC5BKywRLx/KqbuA44TYUQS4HHfsLHEcZyhulP32zjEUwL2ACuPt24%2BR0HhnONJBA8IoRlG/4P4/%2B57FTTyC9bUMAQk8OJ9Am69VsHjC2cOJbPaU0iQn4DxrjnSwVwp4eF2XwC63uBVLCchpXgQPAiUUrM8xBwlfeqs%2Bc7JwFn//KHKtAI8IkVejFgIgY8p2etEB7cPDbF32wSE8pwx926XTx6pAcPxxmFlzIo2o/qPy84sb4JTSMb7v3qiGFhJIaAzw1wbkmh8tu4IrqKm4v347V1qmvQGKvjJjEyf7v/pX3GmrGp%2BtT73UDyRHCPLMBDKwUj801dl4P7Fwc8fh0rLwiaBrp2dN2Do%2Bxfb%2Bd%2BE2GwEe%2BEPTYaW1gNQUiKaBP9T/ggwAJik5dEKYSC3AAAAAElFTkSuQmCC
