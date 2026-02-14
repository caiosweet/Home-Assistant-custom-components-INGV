# Changes

## 2026.02.0 (14/02/2026)

* Fixed issue #40: invalid manually assigned `entity_id` values in `sensor` and `geo_location` entities.
* Removed explicit `self.entity_id = ...` assignments and now rely on Home Assistant to generate entity IDs automatically.
* This ensures all entity IDs are valid/sluggified and prevents the deprecation warning that will become blocking in Home Assistant 2027.2.0.
* After updating, some entity IDs may appear normalized (for example, uppercase segments converted to lowercase).
* Improved geo-location region handling by using the public feed description field and normalizing it to avoid showing the `Region name:` prefix in entity attributes and friendly names.
* Added safer event ID extraction from feed external IDs, with fallback handling for unexpected ID formats.
* Hardened config entry option handling by using safe defaults when options are missing, preventing potential `KeyError` issues on older or partially migrated entries.
* Added edge-case safeguards for geo-location naming so entity names remain valid and readable even when some feed fields are missing.
* Improved coordinator entity lifecycle handling to reduce duplicate geo-location notifications after transient feed errors: removals are queued and applied only after successful feed updates, while temporary `ERROR` updates no longer trigger delete/recreate churn.
* Improved duplicate-creation protection by deduplicating on stable INGV `event_id` (instead of raw `external_id`) to avoid repeated entities/notifications when feed external IDs vary for the same event.
* Removed aggressive geo-location entity registry removals during reload/teardown to align with Home Assistant lifecycle handling and reduce `_2`/`_3` entity churn when changing integration options.
* Added safe cleanup of stale INGV `geo_location` registry entries after successful feed updates, so outdated `Non disponibile` controls are pruned without impacting reload stability.
* Added a single config-entry migration to version `2` to clean legacy `geo_location` entities without `unique_id` and normalize legacy suffixed entity IDs (`_2`, `_3`) when safe.
* Added idempotent geo-location registry normalization during setup and after the first successful feed update to reduce recurring `_2`/`_3` suffixes after reloads or option changes.

## 2026.01.2 (29/01/2026)

* Improved feed updates by detecting whether the client's `update()` is sync or async and executing it appropriately.
* Prevented `coroutine was never awaited` warnings while avoiding event loop blocking.

## 2026.01.1 (29/01/2026)

* Fixed a Home Assistant warning about blocking imports by preloading `dateparser` translation data in an executor before coordinator setup.
* Kept feed updates on the event loop so async callbacks continue to work correctly.

## 2026.01.0 (28/01/2026)

* Swapped the feed update to run in the executor so `dateparser` dynamic import does not block the event loop.
* Updated `__init__.py`.

## 2024.08.0 (11/08/2024)

* Updated image URL pattern (Issue #31).

## 2024.02.0 (18/02/2024)

* Fixed deprecated constant usage (Issue #27).
* Bumped `aio_quakeml_ingv_centro_nazionale_terremoti_client` to `0.4`.

## 2023.03.0 (07/03/2023)

* Sorted manifest keys (`domain`, `name`, then alphabetical order).
* Bumped `aio_quakeml_ingv_centro_nazionale_terremoti_client` to `0.3`.

## 2023.02.0 (17/02/2023)

* Migrated integration setup to `async_forward_entry_setups`.
* Fixed Issue #22.

## 2022.11.0 (13/11/2022)

* Fixed deprecation related to Unit System `name` property (Issue #21).

## 2022.06.0 (04/06/2022)

* Migrated to a new async library. Thanks @exxamalte, for your hard work.
* Migrated to `DataUpdateCoordinator` to reduce code complexity and improve performance.
* Migrated geo_location platform to integration with config flow.
* Added INGV Earthquakes sensor.
* Added depth, mode and status to geo_location entities attributes.
* Deleted title and external_id from geo_location entities attributes.

## 2022.06.0b1 (02/06/2022) [pre-release]

* Added early support for configuration from the UI.

## 2022.02.0 (27/02/2022)

* Added geo_location setup type hints.
* Bumped `georss-ingv-centro-nazionale-terremoti-client` to `0.6`.

## 2021.06.0 (08/06/2021)

* Bumped `georss-ingv-centro-nazionale-terremoti-client` to `0.5`.
* Changed entity properties to class attributes.

## 2021.04.1 (29/04/2021)

* Added `iot_class` to manifest.

## 2021.04.0 (20/04/2021)

* Fixed image URLs by supporting new pattern.
* Replaced `Entity.device_state_attributes` with `Entity.extra_state_attributes`.
* Bumped `georss-ingv-centro-nazionale-terremoti-client` to `0.4`.

## 2021.03.1 (28/03/2021)

* Updated typing and changed the tag version.

## 1.0.3 (18/02/2021)

* Added version to `manifest.json`.
* Marked entities as unavailable when removed but still registered.
* Added config validator helper `positive_float`.
* Updated README (including zone radius clarification in meters).

## 1.0.2 (23/11/2020)

* Added more information about integration #6 (automation, binary sensor, Lovelace cards, and zone examples).

## 1.0.1 (08/11/2020)

* Fixed path of preview images (HACS information).

## 1.0.0 (27/10/2020)

* First release. All credit goes to Malte Franken [@exxamalte].
