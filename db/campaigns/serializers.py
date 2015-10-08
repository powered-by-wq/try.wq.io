from rest_framework import serializers
from wq.db.rest.serializers import ModelSerializer
from wq.db.patterns import serializers as patterns
from .models import Parameter, Report
from vera.serializers import EventResultSerializer


class ParameterInlineSerializer(patterns.AttachmentSerializer,
                                patterns.IdentifiedModelSerializer):
    id = serializers.CharField(required=False)
    object_field = 'campaign'

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.primary_identifier:
            data['id'] = obj.primary_identifier.slug
        return data

    class Meta:
        model = Parameter
        list_serializer_class = patterns.AttachmentListSerializer
        exclude = ('campaign', 'identifiers')


class CampaignSerializer(patterns.AttachedModelSerializer):
    parameters = ParameterInlineSerializer(many=True, required=False)
    icon = serializers.FileField(required=False)

    def get_attachment(self, model, pk):
        return model.objects.get_by_identifier(pk)

    def create_attachment(self, model, attachment, name):
        instance = super().create_attachment(model, attachment, name)
        instance.identifiers.create(
            name=instance.name,
            is_primary=True,
        )
        return instance


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
