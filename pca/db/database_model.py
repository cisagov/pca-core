"""Provides document schemas for the underlying MongoDB."""
__all__ = [
    "CustomerDoc",
    "AssessmentDoc",
    "CampaignDoc",
    "UserDoc",
    "EmailDoc",
    "ClickDoc",
    "ApplicationDoc",
    "ImageDoc",
    "TemplateDoc",
    "UserReportDoc",
]

# Standard Python Libraries
import ipaddress
from pprint import pprint

# Third-Party Libraries
from pymodm import MongoModel, fields
from pymodm.errors import DoesNotExist, ValidationError

# cisagov Libraries
from pca.core.common import Indicator

CUSTOMER_COLLECTION = "customers"
ASSESSMENT_COLLECTION = "assessments"
CAMPAIGN_COLLECTION = "campaigns"
USER_COLLECTION = "users"
EMAIL_COLLECTION = "emails"
CLICK_COLLECTION = "clicks"
APPLICATION_COLLECTION = "applications"
IMAGE_COLLECTION = "images"
TEMPLATE_COLLECTION = "templates"
USER_REPORT_COLLECTION = "user_reports"


class RootDoc(MongoModel):
    """Provides the basic schema for all docs that inherit."""

    def save(self, *args, **kwargs):
        """Save document to MongoDB."""
        try:
            super(RootDoc, self).save(*args, **kwargs)
        except Exception as e:
            print("Exception raised on save:", e)
            print("Subject document follows:")
            pprint(self)
            raise e

    # TODO Replace get_indices with 'class Meta: indexes'
    # def get_indices(self):
    #     # allow documents to create their required indices
    #     # should return a list of triples
    #     # ((name, spec, unique), ...)
    #     pass

    # TODO? Figure out way to make get_by_id work; avoid "AttributeError: Manager isn't accessible via CustomerDoc instances"
    # def get_by_id(self, id):
    #     try:
    #         doc = self.objects.get({'_id':id})
    #     except DoesNotExist:
    #         return None
    #     return doc

    class Meta:
        """Basic meta class for all inherited docs."""

        ignore_unknown_fields = True


def valid_customer_contacts(contacts_list):
    for contact in contacts_list:
        for req_field in ("email", "name", "type"):
            if not contact.get(req_field):
                raise ValidationError(
                    "{} is required in every customer contact".format(req_field)
                )
        if contact["type"] not in ["TECHNICAL", "DISTRO"]:
            raise ValidationError(
                "customer contact type must be either TECHNICAL or DISTRO, not {}".format(
                    contact["type"]
                )
            )


class CustomerDoc(RootDoc):
    """Provides schema for Customer doc."""

    _id = fields.CharField(primary_key=True, required=True)
    name = fields.CharField(required=True)
    acronym = fields.CharField(required=True)
    contacts = fields.ListField(required=True, validators=[valid_customer_contacts])

    class Meta:
        """Meta class for CustomerDoc."""

        collection_name = CUSTOMER_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def get_all_customers(self):
        """Retrieve all customer documents."""
        query_set = CustomerDoc.objects.all().order_by([("_id", 1)])
        all_customers = []
        for customer in query_set:
            all_customers.append(customer._id)
        return all_customers

    def save(self, *args, **kwargs):
        """Save CustomerDoc to MongoDB."""
        super(CustomerDoc, self).save(*args, **kwargs)


class AssessmentDoc(RootDoc):
    """Provides schema for Assessment doc."""

    _id = fields.CharField(primary_key=True, required=True)
    customer = fields.ReferenceField(
        CustomerDoc, required=True
    )  # TODO add validator to confirm customer exists
    team_lead = fields.CharField(required=True)
    start_time = fields.DateTimeField(required=True)
    end_time = fields.DateTimeField(required=True)
    methodology_text = fields.CharField(
        required=False, blank=True
    )  # Field not required, allowed to be blank

    class Meta:
        """Meta class for CustomerDoc."""

        collection_name = ASSESSMENT_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        """Save AssessmentDoc to MongoDB."""
        super(AssessmentDoc, self).save(*args, **kwargs)


def valid_template_appearance(appearance_dict):
    indicator_category = "appearance"
    for key in appearance_dict.keys():
        if key not in Indicator.Indicator.INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in Indicator.Indicator.INDICATOR_LOOKUP[
        indicator_category
    ].keys():
        valid_keys = Indicator.Indicator.INDICATOR_LOOKUP[indicator_category][
            indicator_name
        ].keys()
        if appearance_dict.get(indicator_name) not in valid_keys:
            raise ValidationError(
                'Template {0} "{1}" value must be: {2}.  Invalid "{1}" value provided: {3}'.format(
                    indicator_category,
                    indicator_name,
                    ", ".join(str(k) for k in valid_keys),
                    appearance_dict.get(indicator_name),
                )
            )


def valid_template_sender(sender_dict):
    indicator_category = "sender"
    for key in sender_dict.keys():
        if key not in Indicator.Indicator.INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in Indicator.INDICATOR_LOOKUP[indicator_category].keys():
        valid_keys = Indicator.INDICATOR_LOOKUP[indicator_category][
            indicator_name
        ].keys()
        if sender_dict.get(indicator_name) not in valid_keys:
            raise ValidationError(
                'Template {0} "{1}" value must be: {2}.  Invalid "{1}" value provided: {3}'.format(
                    indicator_category,
                    indicator_name,
                    ", ".join(str(k) for k in valid_keys),
                    sender_dict.get(indicator_name),
                )
            )


def valid_template_relevancy(relevancy_dict):
    indicator_category = "relevancy"
    for key in relevancy_dict.keys():
        if key not in Indicator.INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in Indicator.INDICATOR_LOOKUP[indicator_category].keys():
        valid_keys = Indicator.INDICATOR_LOOKUP[indicator_category][
            indicator_name
        ].keys()
        if relevancy_dict.get(indicator_name) not in valid_keys:
            raise ValidationError(
                'Template {0} "{1}" value must be: {2}.  Invalid "{1}" value provided: {3}'.format(
                    indicator_category,
                    indicator_name,
                    ", ".join(str(k) for k in valid_keys),
                    relevancy_dict.get(indicator_name),
                )
            )


def valid_template_behavior(behavior_dict):
    indicator_category = "behavior"
    for key in behavior_dict.keys():
        if key not in Indicator.INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in Indicator.INDICATOR_LOOKUP[indicator_category].keys():
        valid_keys = Indicator.INDICATOR_LOOKUP[indicator_category][
            indicator_name
        ].keys()
        if behavior_dict.get(indicator_name) not in valid_keys:
            raise ValidationError(
                'Template {0} "{1}" value must be: {2}.  Invalid "{1}" value provided: {3}'.format(
                    indicator_category,
                    indicator_name,
                    ", ".join(str(k) for k in valid_keys),
                    behavior_dict.get(indicator_name),
                )
            )


class TemplateDoc(RootDoc):
    """Provides schema for Template doc."""

    name = fields.CharField(required=True)
    text = fields.CharField(required=True)
    appearance = fields.DictField(required=True, validators=[valid_template_appearance])
    sender = fields.DictField(required=True, validators=[valid_template_sender])
    relevancy = fields.DictField(required=True, validators=[valid_template_relevancy])
    behavior = fields.DictField(required=True, validators=[valid_template_behavior])
    complexity = fields.IntegerField(required=True)

    class Meta:
        """Meta class for TemplateDoc."""

        collection_name = TEMPLATE_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        """Save TemplateDoc to MongoDB."""
        super(TemplateDoc, self).save(*args, **kwargs)


class ImageDoc(RootDoc):
    """Provides schema for Image doc."""

    data = fields.ImageField(required=True)
    filename = fields.CharField(required=True)
    url = fields.URLField(blank=True)
    img_class = fields.CharField(required=True)

    class Meta:
        """Meta class for ImageDoc."""

        collection_name = IMAGE_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def save(self, *args, **kwargs):
        """Save ImageDoc to MongoDB."""
        super(ImageDoc, self).save(*args, **kwargs)


class CampaignDoc(RootDoc):
    """Provides schema for Campaign doc."""

    _id = fields.CharField(primary_key=True, required=True)
    assessment = fields.ReferenceField(
        AssessmentDoc, required=True
    )  # TODO add validator to confirm assessment exists
    customer = fields.ReferenceField(
        CustomerDoc, required=True
    )  # TODO add validator to confirm customer exists
    start_time = fields.DateTimeField()
    end_time = fields.DateTimeField()
    url = fields.URLField()
    template = fields.ReferenceField(TemplateDoc, required=True)
    subject = fields.CharField()
    users = fields.ListField(blank=True)  # this field is allowed to be blank
    images = fields.DictField(
        default={}, blank=True
    )  # {} considered 'blank', so 'blank=True' is needed

    class Meta:
        """Meta class for CampaignDoc."""

        collection_name = CAMPAIGN_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        """Save CampaignDoc to MongoDB."""
        super(CampaignDoc, self).save(*args, **kwargs)


class UserDoc(RootDoc):
    """Provides schema for User doc."""

    _id = fields.CharField(primary_key=True, required=True)
    customer = fields.ReferenceField(
        CustomerDoc, required=True
    )  # TODO add validator to confirm customer exists
    display_name = fields.CharField()
    employee_type = fields.CharField()
    customer_defined_labels = fields.DictField(blank=True, default={})

    class Meta:
        """Meta class for UserDoc."""

        collection_name = USER_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        """Save UserDoc to MongoDB."""
        super(UserDoc, self).save(*args, **kwargs)


class EmailDoc(RootDoc):
    """Provides schema for Email doc."""

    user = fields.ReferenceField(
        UserDoc, required=True
    )  # TODO add validator to confirm user exists
    customer = fields.ReferenceField(
        CustomerDoc, required=True
    )  # TODO add validator to confirm customer exists
    assessment = fields.ReferenceField(
        AssessmentDoc, required=True
    )  # TODO add validator to confirm assessment exists
    campaign = fields.ReferenceField(
        CampaignDoc, required=True
    )  # TODO add validator to confirm campaign exists
    time = fields.DateTimeField(required=True)
    status = fields.CharField()

    class Meta:
        """Meta class for EmailDoc."""

        collection_name = EMAIL_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_user_campaign_time(self, user_id, campaign_id, time):
        """Retrieve documents by provided user, campaign, and time."""
        try:
            doc = EmailDoc.objects.raw(
                {"user": user_id, "campaign": campaign_id, "time": time}
            ).first()
        except DoesNotExist:
            return None
        return doc

    def save(self, *args, **kwargs):
        """Save EmailDoc to MongoDB."""
        super(EmailDoc, self).save(*args, **kwargs)


class ClickDoc(RootDoc):
    """Provides schema for Click doc."""

    user = fields.ReferenceField(
        UserDoc, blank=True
    )  # user (token) is not guaranteed with each click
    customer = fields.ReferenceField(
        CustomerDoc, required=True
    )  # TODO add validator to confirm customer exists
    assessment = fields.ReferenceField(
        AssessmentDoc, required=True
    )  # TODO add validator to confirm assessment exists
    campaign = fields.ReferenceField(
        CampaignDoc, blank=True
    )  # TODO add validator to confirm campaign exists
    time = fields.DateTimeField(required=True)
    source_ip = fields.GenericIPAddressField(required=True)
    source_ip_int = fields.BigIntegerField(required=True)

    class Meta:
        """Meta class for ClickDoc."""

        collection_name = CLICK_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_user_time_ip(self, user_id, time, source_ip_str):
        """Retrieve docs by user, time, and source ip address."""
        try:
            doc = ClickDoc.objects.raw(
                {
                    "user": user_id,
                    "time": time,
                    "source_ip_int": int(ipaddress.ip_address(source_ip_str)),
                }
            ).first()
        except DoesNotExist:
            return None
        return doc

    def save(self, *args, **kwargs):
        """Save ClickDoc to MongoDB."""
        if type(ipaddress.ip_address(self.source_ip)) == ipaddress.IPv4Address:
            self.source_ip_int = int(ipaddress.ip_address(self.source_ip))
        else:
            self.source_ip_int = None  # IPv6 integer representations are too large to store in MongoDB currently
        super(ClickDoc, self).save(*args, **kwargs)


class ApplicationDoc(RootDoc):
    """Provides schema for Application doc."""

    user = fields.ReferenceField(
        UserDoc, blank=True
    )  # user (token) is not guaranteed with each click
    customer = fields.ReferenceField(
        CustomerDoc, required=True
    )  # TODO add validator to confirm customer exists
    assessment = fields.ReferenceField(
        AssessmentDoc, required=True
    )  # TODO add validator to confirm assessment exists
    campaign = fields.ReferenceField(
        CampaignDoc, blank=True
    )  # TODO add validator to confirm campaign exists
    time = fields.DateTimeField(required=True)
    external_ip = fields.GenericIPAddressField(required=True)
    external_ip_int = fields.BigIntegerField(
        blank=True
    )  # will be None if external_ip is an IPv6Address
    internal_ip = fields.GenericIPAddressField(blank=True)
    internal_ip_int = fields.BigIntegerField(
        blank=True
    )  # will be None if internal_ip is an IPv6Address
    name = fields.CharField(required=True)
    version = fields.CharField(blank=True)

    class Meta:
        """Meta class for ApplicationDoc."""

        collection_name = APPLICATION_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_user_time_name_version(self, user_id, time, app_name, app_version):
        """Retrieve ApplicationDocs by user, time, app, and version."""
        try:
            doc = ApplicationDoc.objects.raw(
                {
                    "user": user_id,
                    "time": time,
                    "name": app_name,
                    "version": app_version,
                }
            ).first()
        except DoesNotExist:
            return None
        return doc

    def save(self, *args, **kwargs):
        """Save ApplicationDoc to MongoDB."""
        if type(ipaddress.ip_address(self.external_ip)) == ipaddress.IPv4Address:
            self.external_ip_int = int(ipaddress.ip_address(self.external_ip))
        else:
            self.external_ip_int = None  # IPv6 integer representations are too large to store in MongoDB currently

        if (
            self.internal_ip
            and type(ipaddress.ip_address(self.internal_ip)) == ipaddress.IPv4Address
        ):
            self.internal_ip_int = int(ipaddress.ip_address(self.internal_ip))
        else:
            self.internal_ip_int = None  # IPv6 integer representations are too large to store in MongoDB currently
        super(ApplicationDoc, self).save(*args, **kwargs)


class UserReportDoc(RootDoc):
    """Provides schema for User Report doc."""

    customer = fields.ReferenceField(CustomerDoc, required=True)
    assessment = fields.ReferenceField(AssessmentDoc, required=True)
    campaign = fields.ReferenceField(CampaignDoc, required=True)
    first_report = fields.DateTimeField(blank=True)
    total_num_reports = fields.IntegerField(blank=True)

    class Meta:
        """Meta class for UserReportDoc."""

        collection_name = USER_REPORT_COLLECTION
        final = True
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_customer_campaign(self, customer_id, campaign_id):
        """Retrieve UserReport by customer and campaign."""
        try:
            doc = UserReportDoc.objects.raw(
                {
                    "customer": customer_id,
                    "assessment": campaign_id,
                }
            ).first()
        except DoesNotExist:
            return None
        return doc

    def save(self, *args, **kwargs):
        """Save UserReportDoc to MongoDB."""
        super(UserReportDoc, self).save(*args, **kwargs)
