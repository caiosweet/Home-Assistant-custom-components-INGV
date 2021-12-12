# INGV Terremoti

<p class='img'>
  <img src='https://github.com/caiosweet/Home-Assistant-custom-components-INGV/blob/main/assets/brand/logo_128.png'/>
</p>

[![hacs][hacsbadge]][hacs] [![Validate](https://github.com/caiosweet/Home-Assistant-custom-components-INGV/actions/workflows/validate.yaml/badge.svg)](https://github.com/caiosweet/Home-Assistant-custom-components-INGV/actions/workflows/validate.yaml)

[![GitHub latest release]][githubrelease] ![GitHub Release Date] [![Maintenancebadge]][Maintenance] [![GitHub issuesbadge]][GitHub issues]

[![Websitebadge]][website] [![Forum][forumbadge]][forum] [![telegrambadge]][telegram] [![facebookbadge]][facebook] 

[![Don't buy me a coffee](https://img.shields.io/static/v1.svg?label=Don't%20buy%20me%20a%20coffee&message=🔔&color=black&logo=buy%20me%20a%20coffee&logoColor=white&labelColor=6f4e37)](https://paypal.me/hassiohelp)



Instructions on how to integrate the Istituto Nazionale di Geofisica e Vulcanologia (Earthquakes) Feed feed into Home Assistant.

All credit goes to Malte Franken [@exxamalte](https://github.com/exxamalte).

The `ingv_centro_nazionale_terremoti` platform lets you integrate a GeoRSS feed provided by the 
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

The data is updated every 5 minutes.

## Configuration

To integrate the INGV Centro Nazionale Terremoti feed, add the following lines to your `configuration.yaml`.

```yaml
# Example configuration.yaml entry
geo_location:
  - platform: ingv_centro_nazionale_terremoti
```

#### CONFIGURATION VARIABLES


| Variables          | Type        | Requirement   | Default   |  Description |
|--------------------|-------------|---------------|------------|--------------|
|**minimum_magnitude**| float | optional | 0.0 | The minimum magnitude of an earthquake to be included. 
|**radius**| float | optional | 50.0 | The distance in kilometers around Home Assistant's coordinates in which seismic events are included.
|**latitude**| string | optional | Latitude defined in your `configuration.yaml` | Latitude of the coordinates around which events are considered.
|**longitude**| string | optional | Longitude defined in your `configuration. yaml` | Longitude of the coordinates around which events are considered.


## State Attributes

The following state attributes are available for each entity in addition to 
the standard ones:

| Attribute          | Description |
|--------------------|-------------|
| latitude           | Latitude of the earthquake. |
| longitude          | Longitude of the earthquake. |
| source             | `ingv_centro_nazionale_terremoti` to be used in conjunction with `geo_location` automation trigger. |
| external_id        | The external ID used in the feed to identify the earthquake in the feed. |
| title              | Original title from the feed. |
| region             | Textual description of named geographic region near to the event. |
| magnitude          | Reported magnitude of the earthquake. |
| publication_date   | Date and time when this event occurred. |
| event_id           | Return the short id of the event. |
| image_url          | URL to a map supplied in the feed marking the location of the event. This could for example be used in notifications. **Images are only available for magnitude >= 3**. |


## Full Configuration

```yaml
# Example configuration.yaml entry
geo_location:
  - platform: ingv_centro_nazionale_terremoti
    radius: 100
    minimum_magnitude: 2.0
    latitude: 41.89
    longitude: 12.51
```

___

## [Other information](https://hassiohelp.eu/2019/10/06/home-assistant-package-eventi-naturali/)

## [My Package](https://github.com/caiosweet/Package-Natural-Events/tree/main/config/packages)

## Example Binary Sensor
```yaml
binary_sensor:
  - platform: template
    sensors:
      lastquake:
        friendly_name: Evento terremoto
        device_class: vibration
        # availability_template: False
        value_template: >-
          {% set last_date = states.geo_location
            | selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
            | sort(attribute='attributes.publication_date')
            | map(attribute='attributes.publication_date') |list|last|default %}
          {{ ((as_timestamp(utcnow())-as_timestamp(last_date))/3600) <= 24 if last_date else False }}
        attribute_templates:
          distance: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='state')|list|last|default}}
          lat: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.latitude')|list|last|default}}
          long: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.longitude')|list|last|default}}
          title: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.title')|list|last|default}}
          region: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.region')|list|last|default}}
          magnitude: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.magnitude')|list|last|default}}
          publication_date: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.publication_date')|list|last|default}}
          event_id: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.event_id')|list|last|default}}
          image_url: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.image_url')|list|last|default}}
          attribution: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.attribution')|list|last|default}}
          level: >-
            {%set m = states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
              |sort(attribute='attributes.publication_date')|map(attribute='attributes.magnitude')|list|last|default(0)%}
              {% set m = m|float %}
              {%if 0<=m<=1.9%}0{%elif 2<=m<=2.9%}1{%elif 3<=m<=3.9%}2{%elif 4<=m<=5.9%}3{%else%}4{%endif%}
          external_id: >-
            {{states.geo_location|selectattr('attributes.source','eq','ingv_centro_nazionale_terremoti')
            |sort(attribute='attributes.publication_date')|map(attribute='attributes.external_id')|list|last|default|replace('smi:','')}}
```

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
  - alias: Quake Notifications
    mode: queued
    max_exceeded: silent
    initial_state: true
    trigger:
      - platform: geo_location
        source: "ingv_centro_nazionale_terremoti"
        zone: zone.geoalert
        event: enter
    condition: >-
      {{ ((as_timestamp(utcnow()) - as_timestamp(trigger.to_state.attributes.publication_date))/3600*60)|int < 90 }}
    action:
      - service: notify.telegram
        data:
          title: >-
            🚧 Rilevato terremoto.
          message: >-
            {% set data_utc = trigger.to_state.attributes.publication_date %}
            Rilevato terremoto di magnitudo: {{ trigger.to_state.attributes.magnitude }} 
            a una distanza di {{ trigger.to_state.state }} Km da casa. Epicentro: {{ trigger.to_state.attributes.region }} 
            {{ as_timestamp(data_utc)|timestamp_custom ('Data %d/%m/%Y Ore %H:%M:%S') }}
            {% if trigger.to_state.attributes.image_url is defined %}
            {{ trigger.to_state.attributes.image_url }}
            {% endif %}
      - choose:
          - conditions: "{{ trigger.to_state.attributes.image_url is defined }}"
            sequence:
              - service: telegram_bot.send_photo
                  data:
                    url: "{{ trigger.to_state.attributes.image_url }}"
                    caption: "{{ trigger.to_state.attributes.title }}"
                    target: '12345'
                    parse_mode: html
                    timeout: 1000
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

## Example My Lovelace card
Required custom auto-entities, card-mod and [binary_sensor.lastquake](#example-binary-sensor)
```yaml

type: conditional
conditions:
  - entity: binary_sensor.lastquake
    state: 'on'
card:
  type: vertical-stack
  cards:
    - type: markdown
      card_mod:
        style: |
          ha-card {background: none; border-radius: 0px; box-shadow: none;}
          ha-markdown {padding-bottom: 0 !important;}
      content: >-
        ___

        #### TERREMOTI - ULTIME 24h 
        [<img src="https://www.hsit.it/images/favicon.png"/> Hai Sentito Il Terremoto](http://www.haisentitoilterremoto.it/)

        {%- set url = "http://shakemap.rm.ingv.it/shake4/data/{}/current/products/{}.jpg" -%}
        {%- set url2 = "http://shakemap.ingv.it/shake4/data/{}/current/products/{}.jpg" -%}
        {%- set entityid = 'binary_sensor.lastquake' -%}
        {%- set id = state_attr(entityid, 'event_id') -%}
        {%- set data_utc = state_attr(entityid, 'publication_date') -%}
        {%- set magnitudo = (state_attr(entityid, 'magnitude')|float) if not none else '0' -%}
        {%- set code = {0:'White', 1:'Green', 2:'Yellow', 3:'Orange', 4:'Red'} -%}
        {%- set color = code[state_attr('binary_sensor.lastquake', 'level')|int] -%}
        {%- set lat = state_attr(entityid, 'lat') -%}
        {%- set long = state_attr(entityid, 'long') -%}
        <font>

        **<font color="{{color}}">{{as_timestamp(data_utc)|timestamp_custom ('%H:%M:%S del %d/%m/%Y')}}</font>**<br><br>
        Un terremoto di magnitudo **<font color="{{color}}">{{magnitudo}}</font>**<br>
        è avvenuto nella zona: [{{state_attr(entityid, 'region')}}](https://www.openstreetmap.org/?mlat={{lat}}&mlon={{long}}#map=12/{{lat}}/{{long}})<br>
        a <font color="{{color}}">**{{state_attr(entityid, 'distance')}}**</font> km da casa,<br>
        con coordinate geografiche (lat, long) {{lat}},{{long}}.
        {%for person in expand(states.person) %}
        <br>{{"{} è a {} km dall'epicentro.".format(person.name, distance(lat, long, person.entity_id)) if is_state(person.entity_id, 'not_home') else ''}}<br>
        {%endfor %}
        </font>
        {% if magnitudo >= 3 %}
        [Intensity]({{url.format(id,'intensity')}}) ~ 
        [PGA]({{url.format(id,'pga')}}) ~ [PGV]({{url.format(id,'pgv')}}) ~ [PSA0]({{url.format(id,'psa0p3')}}) ~ [PSA1]({{url.format(id,'psa1p0')}}) ~ 
        [HaiSentitoIlTerremoto](http://eventi.haisentitoilterremoto.it/{{id}}/{{id}}_mcs.jpg)<br>

        <a href="http://shakemap.rm.ingv.it/shake4/viewLeaflet.html?eventid={{id}}"><img src="{{url.format(id,'intensity')}}"></a>

        {% endif %}

        <center>
        <a href="http://terremoti.ingv.it/"> <img src="https://www.ingv.it/images/INGV_Acronimo_50.png" width="100" ></a>

        <!-- Examples
          Map Google
          [{{state_attr(entityid, 'region')}}](http://maps.google.com/maps?z=8&q=loc:{{lat}}+{{long}})
          Map Open Streat Map
          [{{state_attr(entityid, 'region')}}](https://www.openstreetmap.org/?mlat={{lat}}&mlon={{long}}#map=8/{{lat}}/{{long}})
        -->

    - type: custom:auto-entities # CONDITIONAL ULTIMI {count} TERREMOTI
      show_empty: false
      sort:
        {
          attribute: publication_date,
          method: attribute,
          reverse: true,
          count: 4,
          first: 0,
        }
      filter:
        include:
          - entity_id: geo_location.*
            attributes:
              source: ingv_centro_nazionale_terremoti
      card:
        type: entities
        entity_id: this.entity_id
        card_mod:
          style: |
            ha-card {background: none; border-radius: 0px; box-shadow: none;}

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

