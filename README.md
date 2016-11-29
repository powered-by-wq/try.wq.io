[![try.wq.io](https://raw.githubusercontent.com/powered-by-wq/try.wq.io/master/app/images/icon-192.png)](https://try.wq.io)

# Try WQ!

This is the source code for [Try WQ], the "kitchen sync" demo for the [wq Framework] as well as the [vera] data model.  If you are new to wq, you can visit the [Try WQ] site online to experiment with it and see how everything works together.

If you are implementing your own wq-powered site, you will want to start by [determining which data model to use][data model].  If you are using wq for the first time, we recommend using a simple relational model like that provided [Species Tracker], rather the relatively complex [ERAV] model utilized by Try WQ.  wq's [data model] documentation includes instructions for defining arbitrary relational models using the XLSForm and/or Django syntax.  Once your data model is defined, [wq start] can automatically create templates for listing, displaying, and editing your data.

On the other hand, if you are interested in building your own "form-builder" or "campaign" based site with an [ERAV]-powered database structure, the source code here (and for [vera](https://github.com/wq/vera)) should be helpful as a starting point.

## Implementation Details

The campaign edit screen incorporates a [nested serializer][nested forms] to make it possible to manage parameter definitions together with the campaign (see the [serializer code][serializers.py]).   The [campaign edit template][campaign_edit] utilizes the [wq/patterns.js] plugin to append new parameter forms on the fly.

The observation edit screen also references the Parameter model, as part of the [EAV] structure provided by [vera].  To facilitate this, the Parameter model is registered as a primary model in addition to its nested registration under the campaign model.  This dual registration is not officially supported by wq (see [nested forms]), so trywq/main.js includes an [additional bit of JavaScript][main.js] to ensure the parameter model is synced after any campaign edit.

Per the [ERAV] recommendations, observation editing is split across vera's `Report`/`Event` models, rather than a single `Observation` model.  This makes a number of things more complicated, but is necessary to support the multiple-provenance capabilities of ERAV.  The basic rule of thumb is that data *entry* uses the `Report` and `Result` models, while data *analysis* uses the `Event` and `EventResult` models.  Every incoming report is automatically associated with a corresponding `Event`, which is created on the fly if necessary.  The event fields are designated by a three-part [natural key], which is referenced in the [report edit template][report_edit] via [HTML JSON forms]-style field names:

```
event[campaign][slug]
event[site][slug]*
event[date]
```

In a typical vera implementation, the `Site` model is managed separately, with the assumption that the same locations will be visited several times to build up a time series of observations.  To facilitate this, `event[site][slug]` is usually defined in the [report edit template][report_edit] as a `<select>` foreign key lookup.  For this demo, however, a [wq/locate.js] widget is used instead to request the latitude and longitude with each observation.  The server automatically creates new sites on the fly as needed in a custom [report serializer][serializers.py].

To implement a simple EAV structure for observation editing (i.e. without vera), you could forgo the natural key requirement by defining all of the necessary fields (including location attributes) directly on an `Observation` model, which is essentially how [Species Tracker] works (though Species Tracker is not EAV).  Then, you can follow the instructions to [define and register a custom EAV structure][nested forms].

A number of important [configuration options][config] are set when each model is registered in [rest.py].  vera automatically registers its associated models with [wq.db's router][router], even if the models have been extended with custom versions.  For that reason, Try WQ's [rest.py] includes a number of calls to `update_config()` and related methods rather than to `register_model()`.  If you weren't using vera, these could be regular calls to `router.register_model()`.

The report/event distinction is used in Try WQ to support a common use case: making it so a user can edit their own records when offline, but can also view records by other people when online.  In Try WQ, the `Event` model is [configured][rest.py] in such a way to make sure that it is always rendered on the server, to avoid taking up offline storage space.  By contrast, the `Report` model is [configured][rest.py] to download and persist records entered by the user in offline storage, while also allowing for viewing `Report`s from other users (by going to an `Event` and then clicking one of the associated `Report`s.  The `Report` model [templates][report_edit] are also set up to use background syncing via the [outbox], versus the `Campaign` model which is explicitly [set to sync in the foreground][campaign_edit] more like a traditional `<form>`.

This workflow could be implemented in a combined `Observation` model by configuring it like the `Report` model is [configured][rest.py] in Try WQ: JSON version only includes user's data; HTML (server-rendered) version includes everyones data.  The main trick would be getting the `observations/` screen to show all entered records, since by default it would be rendered on the client and only show the user's locally stored records.  One trick would be to append a short meaningless parameter to the URL (e.g. `observations/?_=1` to trick [wq/app.js] into thinking it doesn't know how to handle the page (in which case it will automatically fall back to loading it from the server).  The [index template][index] might then look something like this:

```html
<ul data-role="listview">
  <li>
    <a href="/observations/">View My Observations</a>
  </li>
  <li>
    <a href="/observations/?_=1">View All Observations</a>
  </li>
</ul>
```

[wq Framework]: https://wq.io/
[vera]: https://wq.io/vera
[wq start]: https://wq.io/docs/setup
[Species Tracker]: https://github.com/powered-by-wq/species.wq.io
[Try WQ]: https://try.wq.io/

[ERAV]: https://wq.io/docs/erav
[EAV]: https://wq.io/docs/eav-vs-relational
[data model]: https://wq.io/docs/data-model
[nested forms]: https://wq.io/docs/nested-forms
[natural key]: https://github.com/wq/django-natural-keys
[HTML JSON forms]: https://github.com/wq/html-json-forms

[wq/app.js]: https://wq.io/docs/app-js
[wq/locate.js]: https://wq.io/docs/locate-js
[router]: https://wq.io/docs/router
[outbox]: https://wq.io/docs/outbox-js
[config]: https://wq.io/docs/config

[serializers.py]: https://github.com/powered-by-wq/try.wq.io/blob/master/db/campaigns/serializers.py
[campaign_edit]: https://github.com/powered-by-wq/try.wq.io/blob/master/templates/campaign_edit.html
[parameter_inline]: https://github.com/powered-by-wq/try.wq.io/blob/master/templates/partials/parameter_inline.html
[wq/patterns.js]: https://github.com/wq/wq.app/blob/master/js/wq/patterns.js
[rest.py]: https://github.com/powered-by-wq/try.wq.io/blob/master/db/campaigns/rest.py
[report_edit]:https://github.com/powered-by-wq/try.wq.io/blob/master/templates/report_edit.html
[config.js]: https://github.com/powered-by-wq/try.wq.io/blob/master/app/js/trywq/config.js
[main.js]: https://github.com/powered-by-wq/try.wq.io/blob/master/app/js/trywq/main.js
[index]: https://github.com/powered-by-wq/try.wq.io/blob/master/templates/index.html
