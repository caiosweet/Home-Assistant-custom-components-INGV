# INGV Terremoti

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
  <img src='/images/screenshots/ingv-terremoti-feed-map.png' />
</p>

The data is updated every 5 minutes.

## Configuration

To integrate the IGN Sismología feed, add the following lines to your `configuration.yaml`.

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
| event_id           | 
| image_url          | URL to a map supplied in the feed marking the location of the event. This could for example be used in notifications. |


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
