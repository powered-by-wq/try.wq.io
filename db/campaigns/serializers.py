from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer
from wq.db.patterns import serializers as patterns
from vera.models import Site
from .models import Parameter, Report
from vera.results.serializers import ResultSerializer as VeraResultSerializer
from vera.series.serializers import ReportSerializer as VeraReportSerializer


class ParameterInlineSerializer(patterns.AttachmentSerializer):
    class Meta(patterns.AttachmentSerializer.Meta):
        model = Parameter
        exclude = ('campaign',)
        object_field = 'campaign'


class CampaignSerializer(patterns.AttachedModelSerializer):
    parameters = ParameterInlineSerializer(many=True, required=False)
    icon = serializers.FileField(required=False)

    def to_internal_value(self, data):
        data = data.copy()
        if 'request' in self.context:
            user = self.context['request'].user
            if user.is_authenticated():
                data['creator_id'] = user.pk
        return super(CampaignSerializer, self).to_internal_value(data)

    def to_representation(self, obj):
        result = super(CampaignSerializer, self).to_representation(obj)
        result.pop('creator', None)
        return result


class ResultSerializer(VeraResultSerializer):
    class Meta(VeraResultSerializer.Meta):
        type_filter = {
            'campaign_id': '{{campaign_id}}',
        }


class ReportSerializer(VeraReportSerializer):
    results = ResultSerializer(many=True)

    def to_representation(self, obj):
        # FIXME: See https://github.com/wq/wq.db/issues/61
        result = super(ReportSerializer, self).to_representation(obj)
        if result.get('results', None):
            return result

        campaign_id = (
            'request' in self.context and
            self.context['request'].GET.get('campaign_id', None)
        )
        if not campaign_id:
            return result

        result['results'] = [
            {
                '@index': i,
                'type': self.router.serialize(parameter),
                'type_label': str(parameter),
                'type_id': parameter.slug,
            }
            for i, parameter in enumerate(Parameter.objects.filter(
                campaign__slug=campaign_id
            ))
        ]
        return result

    def to_internal_value(self, data):
        # In vera, Site is usually managed as a separate table, but we want to create
        # new sites on the fly for this demo.
        if data.get('latitude', None) and data.get('longitude', None):

            lat = float(data['latitude'])
            lng = float(data['longitude'])
            site, is_new = Site.objects.get_or_create(
                name="%s, %s" % (round(lat, 3), round(lng, 3)),
                latitude=lat,
                longitude=lng,
            )

            data = data.copy()
            data['event[site][slug]'] = site.slug

        return super(ReportSerializer, self).to_internal_value(data)


class EventResultSerializer(serializers.Serializer):
    parameter = serializers.ReadOnlyField(source="result_type.__str__")
    units = serializers.ReadOnlyField(source="result_type.units")
    value = serializers.ReadOnlyField(source="result_value")

    def get_wq_config(self):
        # FIXME: See https://github.com/wq/wq.db/issues/60
        return {'form': []}


class EventSerializer(ModelSerializer):
    latitude = serializers.ReadOnlyField(source='site.latitude')
    longitude = serializers.ReadOnlyField(source='site.longitude')
    valid_reports = ModelSerializer.for_model(
        Report, include_fields="__all__"
    )(many=True)
    photo = serializers.SerializerMethodField()
    results = EventResultSerializer(many=True, source='eventresult_set')

    def get_photo(self, instance):
        report = instance.valid_reports.exclude(photo='').first()
        if report:
            return report.photo.name
