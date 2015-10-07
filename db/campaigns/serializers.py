from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer
from wq.db.patterns import serializers as patterns
from .models import Parameter, Report
from vera.serializers import EventResultSerializer


class ParameterInlineSerializer(patterns.AttachmentSerializer,
                                patterns.IdentifiedModelSerializer):
    object_field = 'campaign'

    class Meta:
        model = Parameter
        list_serializer_class = patterns.AttachmentListSerializer
        exclude = ('campaign', 'identifiers')


class CampaignSerializer(patterns.AttachedModelSerializer):
    parameters = ParameterInlineSerializer(many=True, required=False)
    icon = serializers.FileField(required=False)


class EventSerializer(ModelSerializer):
    latitude = serializers.ReadOnlyField(source='site.latitude')
    longitude = serializers.ReadOnlyField(source='site.longitude')
    valid_reports = ModelSerializer.for_model(Report)(many=True)
    photo = serializers.SerializerMethodField()
    results = EventResultSerializer(many=True, source='eventresult_set')

    def get_photo(self, instance):
        reports = instance.valid_reports.exclude(photo='')
        if reports.count():
            return reports[0].photo.name
