from wq.db import rest
from wq.db.patterns import rest as patterns
from .models import Campaign, Event, Report
from vera.models import Result
from vera.serializers import ResultSerializer
from .maps import basemaps, index_map, event_map
from .serializers import CampaignSerializer, EventSerializer
from django.conf import settings


def no_json_filter(qs, request):
    if request.accepted_renderer.format == 'json':
        return qs.none()
    return qs


def report_filter(qs, request):
    if request.accepted_renderer.format == 'json':
        if request.user.is_authenticated():
            return qs.filter(user=request.user)
        else:
            return qs.none()
    return qs


def result_filter(qs, request):
    if request.accepted_renderer.format == 'json':
        if request.user.is_authenticated():
            return qs.filter(report__user=request.user)
        else:
            return qs.none()
    return qs

rest.router.register_model(
    Campaign,
    lookup='slug',
    serializer=CampaignSerializer,
    has_parameters=True,
)
rest.router.register_filter(Report, report_filter)
rest.router.update_config(
    Report,
    has_results=True,
    reversed=True,
    partial=True,
    parents={
        "reportstatus": ["status"],
        "event": ["event"],

        # Trick wq/app.js into referencing campaign/site as if foreign keys on
        # Report (really on Event)
        "campaign": ["campaign"],
        "site": ["site"],
    }
)
rest.router.register_serializer(Event, EventSerializer)
rest.router.register_filter(Event, no_json_filter)
rest.router.update_config(
    Event,
    max_local_pages=0,
    partial=True,
    map=event_map,
)

rest.router.register_model(
    Result,
    filter=result_filter,
    serializer=ResultSerializer,
)

rest.router.add_page('index', {
    'url': '',
    'map': index_map
})

rest.router.set_extra_config(
    debug=settings.DEBUG,
    map={
        'bounds': [[-70, -180], [70, 180]],
        'basemaps': basemaps
    },
    attachmentTypes={
        'parameter': {
            'predicate': 'has_parameters',
            'type': None,
        },
        'result': {
            'predicate': 'has_results',
            'type': 'parameter',
            # See trywq/config.js for other settings
        }
    }
)
