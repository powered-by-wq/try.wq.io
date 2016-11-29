from django.db import models
from wq.db.patterns import models as patterns
from vera import base_models as vera
from natural_keys import NaturalKeyModel
import reversion


class Campaign(NaturalKeyModel):
    slug = models.SlugField()
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='campaigns')
    description = models.TextField()
    creator = models.ForeignKey("auth.User", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['slug']


class Event(vera.BaseEvent):
    date = models.DateField()
    campaign = models.ForeignKey(Campaign)

    # Inherited from vera's series.BaseEvent:
    #   site = models.ForeignKey('vera.Site')

    def __str__(self):
        return "%s Observation on %s" % (
            self.campaign, self.date
        )

    class Meta:
        unique_together = ('campaign', 'site', 'date')
        ordering = ('-date', 'campaign', 'site')


class Report(vera.BaseReport):
    photo = models.ImageField(
        null=True, blank=True, upload_to='reports'
    )

    # Inherited from vera's series.BaseReport:
    #   event = models.ForeignKey(Event)
    #   entered = models.DateTimeField()
    #   user = models.ForeignKey('auth.User')
    #   status = models.ForeignKey('vera.ReportStatus')


class Parameter(vera.BaseParameter):
    campaign = models.ForeignKey(Campaign, related_name='parameters')
    description = models.TextField()

    # Inherited from vera's params.BaseParameter:
    #   name = models.CharField()
    #   slug = models.CharField()
    #   is_numeric = models.BooleanField()
    #   units = models.CharField()

    class Meta:
        ordering = ['pk']


# Other vera models (not overridden in this project):
#    params.Site
#    params.ReportStatus
#    results.Result

EventResult = vera.create_eventresult_model(Event, vera.Result)

reversion.register(patterns.Identifier)
reversion.register(Parameter, follow=['identifiers'])
reversion.register(Campaign, follow=['parameters'])
