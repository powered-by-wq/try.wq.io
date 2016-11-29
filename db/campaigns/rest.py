from wq.db import rest
from .models import Campaign, Event, Report
from .serializers import (
    CampaignSerializer,
    ReportSerializer,
    EventSerializer,
)
from .maps import basemaps, index_map, event_map
from django.conf import settings


def no_json_filter(qs, request):
    if request.accepted_renderer.format == 'json' and request.path.count('/') < 2:
        return qs.none()
    return qs


def report_filter(qs, request):
    if request.accepted_renderer.format == 'json':
        if request.user.is_authenticated():
            return qs.filter(user=request.user)
        else:
            return qs.none()
    return qs


rest.router.register_model(
    Campaign,
    lookup='slug',
    serializer=CampaignSerializer,
    fields="__all__",
)

rest.router.register_serializer(Report, ReportSerializer)
rest.router.register_filter(Report, report_filter)
rest.router.update_config(
    Report,
    reversed=True,
    partial=True,
    map=[{
        'mode': 'edit',
        'layers': [],
    }],
    locate=True,
)

rest.router.register_serializer(Event, EventSerializer)
rest.router.register_filter(Event, no_json_filter)
rest.router.update_config(
    Event,
    max_local_pages=0,
    partial=True,
    map=event_map,
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
)
