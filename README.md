[![try.wq.io](https://raw.githubusercontent.com/powered-by-wq/try.wq.io/master/app/images/icon-192.png)](https://try.wq.io)

# Try WQ!

This is the source code for [Try WQ], the "kitchen sync" demo for the [wq Framework] as well as the [vera] data model.  If you are new to wq, you can visit the [Try WQ] site online to experiment with it and see how everything works together.

If you are implementing your own wq-powered site, you will want to start by [determining which data model to use][data model].  If you are using wq for the first time, we recommend using a simple relational model like that provided by the [wq start] template and [Species Tracker], rather the relatively complex [ERAV] model utilized by Try WQ.

On the other hand, if you are interested in building your own "form-builder" or "campaign" based site with an [ERAV]-powered database structure, the source code here (and for [vera](https://github.com/wq/vera)) should be helpful as a starting point.

## Implementation Details

### Campaign Editing
The campaign edit screen uses a [custom serializer][serializers.py] to make it possible to process multiple parameter definitions with foreign keys pointing to the campaign.  This is very similar to the existing [EAV-style][data model] format provided by the "attachment" or "pattern" [models provided by wq.db][patterns].  In fact, most of the heavy lifting is done by the generic attachment implementation in wq.db (which still [needs to be documented][issue-21]).  In this case, the `Entity` is the `Campaign`, the `Value` (attachment) is `Parameter`, and there is no `Attribute` model.  (Note that when it comes to editing *observations*, `Parameter` becomes the `Attribute` model.)

The `CampaignSerializer` (and the nested `ParameterInlineSerializer`) are complicated somewhat by the fact that vera's `Parameter` is an [IdentifiedModel][identify].  The use of the identify pattern is important for data import via [Django Data Wizard] but is not particularly critical for web-based data entry.  If the `Parameter` model was a plain Django model instead of vera's version, the serializers could be as simple as:

```python
class ParameterInlineSerializer(patterns.AttachmentSerializer):
    object_field = 'campaign'
    class Meta:
        model = Parameter
        list_serializer_class = patterns.AttachmentListSerializer
        exclude = ('campaign',)

class CampaignSerializer(patterns.AttachedModelSerializer):
    parameters = ParameterInlineSerializer(many=True, required=False)
    class Meta:
        list_exclude = ('parameters',)
```

The [campaign edit template][campaign_edit] leverages a [partial template for inline parameter][parameter_inline] definitions.  This same template is used by [trywq/campaigns.js][campaigns.js], a custom [wq/app.js plugin][wq/app.js] that can append new parameter fields on the fly.  For both new and existing parameters, the template references an `@index` context variable which is critical for differentiating the multiple parameter related fields.  There is nothing vera-specific in these files (`campaign_edit.html`, `partials/parameter_inline.html`, `trywq/campaigns.js`), and they would likely be nearly identical even if `Parameter` was a plain (non-identified) Django model.

Finally, the campaign+parameter attachment structure is configured via an [attachmentTypes config][wq/app.js] in  [rest.py] to ensure [wq/app.js] knows how to process parameter definitions that come back when the campaign is saved.  Parameters are stored in a separate model on the client to make them more easily accessible from the observation screens.  This configuration would likely be necessary even without a vera-based structure.

### Observation Editing
Per the [ERAV] recommendations, observation editing is split across vera's `Report`/`Event` models, rather than a single `Observation` model.  This makes a number of things more complicated, but is necessary to support the multiple-provenance capabilities of ERAV.  The basic rule of thumb is that data *entry* uses the `Report` and `Result` models, while data *analysis* uses the `Event` and `EventResult` models.  Every incoming report is automatically associated with a corresponding `Event`, which is created on the fly if necessary.  The event fields are designated by a four-part [natural key][ERAV], which is referenced in the [report edit template][report_edit] via [HTML JSON forms]-style field names:

```
event[campaign][slug]
event[site][latitude]
event[site][longitude]
event[date]
```

The specifics of processing this natural key into the respective models are handled by the [`ReportSerializer`][vera-serializers] provided by vera, which is itself a subclass of wq.db's [`NaturalKeyModelSerializer`][patterns-base-serializers].  The natural key implementation is useful on its own and will likely be [converted to a standalone library][issue-50].  vera's denormalized `EventResult` model is updated automatically whenever a `Report` or `Event` is saved.

To implement a simple EAV structure for observation editing (i.e. without vera), you could forgo the natural key requirement by defining all of the necessary fields (including location attributes) directly on an `Observation` model, which is essentially how [Species Tracker] works (though Species Tracker is not EAV).  You could also crate a predefined `Site` list and create a foreign key from `Observation` to `Site` (which can be rendered as a dropdown list).  The (new) default [`wq start`][wq start] template works like this and is useful as a reference.  Finally, you would need a custom `Result` (value) model to replace the one provided by vera.  You could then create a custom `ObservationSerializer` similar to `ReportSerializer` and `CampaignSerializer`:

```python
class ResultInlineSerializer(patterns.AttachmentSerializer):
    object_field = 'observation'
    class Meta:
        model = Result
        list_serializer_class = patterns.AttachmentListSerializer
        exclude = ('observation',)

class ObservationSerializer(patterns.AttachedModelSerializer):
    results = ResultInlineSerializer(many=True, required=False)
    class Meta:
        list_exclude = ('results',)
```

vera automatically registers its associated models with [wq.db's router][router], even if the models have been extended with custom versions.  For that reason, Try WQ's [rest.py] includes a number of calls to `update_config()` and related methods rather than to `register_model()`.  If you weren't using vera, these could be regular calls to `router.register_model()`.

```python
rest.router.register_model(
    Observation,
    serializer=ObservationSerializer,
    has_results=True,
)
```

Like the Campaign Edit configuration, the `Result` (`Value`) model (whether vera or custom) needs to be registered with [`attachmentTypes`][wq/app.js] to make it work as expected.  The `Result` model has one extra requirement: when editing a new observation, a default list of blank results should be present in the form.  wq/app.js can generate this list automatically, as long as the appropriate `attachmentType` configuration is present.  The trick is to tell wq/app.js which `Attribute` model to use to generate the blank `Result`/`Value` instances.  In this case, the results need to be filtered to ensure that only `Attributes` relevant for a particular campaign are selected.  Ideally, this would all be configured on the server, but [for now][issue-38] the configuration requires a bit of JavaScript.  In Try WQ, the `attachmentType` configuration is currently split between [rest.py] and [trywq/config.js][config.js] but it effectively looks like this:

```javascript
config.attachmentTypes.result = {
    // Define an arbitrary flag that determines whether a given model should 
    // use this attachment pattern.
    'predicate': 'has_results',
    
    // Which 'attribute' or 'attachment type' model to reference when generating
    // blank result lists
    'type': 'parameter',
    
    'getTypeFilter': function(page, context) {
        // For new forms, use the campaign_id to only create blank results for
        // the parameters associated with that campaign.
        // (campaign_id will hopefully be provided by the URL)
        return {'campaign_id': context.campaign_id}
        // Existing records will use whatever results are already present
    },
    'getDefaults': function(type, context) {
        // Generate context variables for use when rendering a new form
        return {
            'type_id': type.id,
            'type_label': type.name,
            'type': type
        };
    }
};
```

The [report edit template][report_edit] would likely be useful as a starting point for a combined `observation_edit` template.  The main caveat is that the ERAV model assumes that report instances are only created and never updated directly.  (The way to "edit" a report/event in ERAV is to create a new report that "masks" the old values).  An observation_edit template would need to support editing both new and existing records.  The default [observation edit template][observation_edit] in the new [`wq start`][wq start] template is set up this way.

The report/event distinction is used in Try WQ to support a common wq use case: making it so a user can edit their own records when offline, but can also view records by other people when online.  In Try WQ, the `Event` model is [configured][rest.py] in such a way to make sure that it is always rendered on the server, to avoid taking up offline storage space.  By contrast, the `Report` model is [configured](rest.py) to download and persist records entered by the user in offline storage, while also allowing for viewing `Report`s from other users (by going to an `Event` and then clicking one of the associated `Report`s.  The `Report` model [templates][report_edit] are also set up to use background syncing via the [outbox], versus the `Campaign` model which is explicitly [set to sync in the foreground][campaign_edit] more like a traditional `<form>`.

This workflow could be implemented in a combined `Observation` model by configuring it like the `Report` model is [configured][rest.py] in Try WQ: JSON version only includes user's data; HTML (server-rendered) version includes everyones data.  The existing `report_edit`, `report_detail` and `report_list` templates would largely be useful as-is (other than the field names).  The main trick would be getting the `observations/` screen to show all entered records, since by default it would be rendered on the client and only show the user's locally stored records.  One trick would be to append a short meaningless parameter to the URL (e.g. `observations/?_=1` to trick [wq/app.js] into thinking it doesn't know how to handle the page (in which case it will automatically fall back to loading it from the server).  The [index template][index] might then look something like this:

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
[data model]: https://wq.io/docs/eav-vs-relational

[wq/app.js]: https://wq.io/docs/app-js
[issue-21]: https://github.com/wq/wq/issues/21
[patterns]: https://wq.io/docs/about-patterns
[identify]: https://wq.io/docs/identify
[HTML JSON forms]: http://www.w3.org/TR/html-json-forms/
[Django Data Wizard]: https://github.com/wq/django-data-wizard
[issue-50]: https://github.com/wq/wq.db/issues/50
[wq start]: https://github.com/wq/wq-django-template
[router]: https://wq.io/docs/router
[issue-38]: https://github.com/wq/wq.app/issues/38
[outbox]: https://wq.io/docs/outbox-js

[serializers.py]: https://github.com/powered-by-wq/try.wq.io/blob/master/db/campaigns/serializers.py
[campaign_edit]: https://github.com/powered-by-wq/try.wq.io/blob/master/templates/campaign_edit.html
[parameter_inline]: https://github.com/powered-by-wq/try.wq.io/blob/master/templates/partials/parameter_inline.html
[campaigns.js]: https://github.com/powered-by-wq/try.wq.io/blob/master/app/js/trywq/campaigns.js
[rest.py]: https://github.com/powered-by-wq/try.wq.io/blob/master/db/campaigns/rest.py
[report_edit]:https://github.com/powered-by-wq/try.wq.io/blob/master/templates/report_edit.html
[vera-serializers]: https://github.com/wq/vera/blob/master/vera/serializers.py
[patterns-base-serializers]: https://github.com/wq/wq.db/blob/master/patterns/base/serializers.py
[config.js]: https://github.com/powered-by-wq/try.wq.io/blob/master/app/js/trywq/config.js
[observation_edit]: https://github.com/wq/wq-django-template/blob/master/django_project/templates/observation_edit.html
[index]: https://github.com/powered-by-wq/try.wq.io/blob/master/templates/index.html
