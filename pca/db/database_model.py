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
    "UserReportDoc"
]

from pymongo.errors import OperationFailure
from pymodm import MongoModel, fields
from pymodm.errors import DoesNotExist, ValidationError
from bson.binary import Binary
from bson import ObjectId
import ipaddress
from pprint import pprint
from pca.core.common import INDICATOR_LOOKUP

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
    def save(self, *args, **kwargs):
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
    _id = fields.CharField(primary_key=True, required=True)
    name = fields.CharField(required=True)
    acronym = fields.CharField(required=True)
    contacts = fields.ListField(required=True, validators=[valid_customer_contacts])

    class Meta:
        collection_name = CUSTOMER_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def get_all_customers():
        query_set = CustomerDoc.objects.all().order_by([("_id", 1)])
        all_customers = []
        for customer in query_set:
            all_customers.append(customer._id)
        return all_customers

    def save(self, *args, **kwargs):
        super(CustomerDoc, self).save(*args, **kwargs)


class AssessmentDoc(RootDoc):
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
        collection_name = ASSESSMENT_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        super(AssessmentDoc, self).save(*args, **kwargs)


def valid_template_appearance(appearance_dict):
    indicator_category = "appearance"
    for key in appearance_dict.keys():
        if key not in INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in INDICATOR_LOOKUP[indicator_category].keys():
        valid_keys = INDICATOR_LOOKUP[indicator_category][indicator_name].keys()
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
        if key not in INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in INDICATOR_LOOKUP[indicator_category].keys():
        valid_keys = INDICATOR_LOOKUP[indicator_category][indicator_name].keys()
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
        if key not in INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in INDICATOR_LOOKUP[indicator_category].keys():
        valid_keys = INDICATOR_LOOKUP[indicator_category][indicator_name].keys()
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
        if key not in INDICATOR_LOOKUP[indicator_category].keys():
            raise ValidationError(
                'Unknown key "{}" in template "{}" section'.format(
                    key, indicator_category
                )
            )

    for indicator_name in INDICATOR_LOOKUP[indicator_category].keys():
        valid_keys = INDICATOR_LOOKUP[indicator_category][indicator_name].keys()
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
    name = fields.CharField(required=True)
    text = fields.CharField(required=True)
    appearance = fields.DictField(required=True, validators=[valid_template_appearance])
    sender = fields.DictField(required=True, validators=[valid_template_sender])
    relevancy = fields.DictField(required=True, validators=[valid_template_relevancy])
    behavior = fields.DictField(required=True, validators=[valid_template_behavior])
    complexity = fields.IntegerField(required=True)

    class Meta:
        collection_name = TEMPLATE_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        super(TemplateDoc, self).save(*args, **kwargs)


class ImageDoc(RootDoc):
    data = fields.ImageField(required=True)
    filename = fields.CharField(required=True)
    url = fields.URLField(blank=True)
    img_class = fields.CharField(required=True)

    class Meta:
        collection_name = IMAGE_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def save(self, *args, **kwargs):
        super(ImageDoc, self).save(*args, **kwargs)


class CampaignDoc(RootDoc):
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
        collection_name = CAMPAIGN_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        super(CampaignDoc, self).save(*args, **kwargs)


class UserDoc(RootDoc):
    _id = fields.CharField(primary_key=True, required=True)
    customer = fields.ReferenceField(
        CustomerDoc, required=True
    )  # TODO add validator to confirm customer exists
    display_name = fields.CharField()
    employee_type = fields.CharField()
    customer_defined_labels = fields.DictField(blank=True, default={})

    class Meta:
        collection_name = USER_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")

    def save(self, *args, **kwargs):
        super(UserDoc, self).save(*args, **kwargs)


class EmailDoc(RootDoc):
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
        collection_name = EMAIL_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_user_campaign_time(user_id, campaign_id, time):
        try:
            doc = EmailDoc.objects.raw(
                {"user": user_id, "campaign": campaign_id, "time": time}
            ).first()
        except DoesNotExist:
            return None
        return doc

    def save(self, *args, **kwargs):
        super(EmailDoc, self).save(*args, **kwargs)


class ClickDoc(RootDoc):
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
        collection_name = CLICK_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_user_time_ip(user_id, time, source_ip_str):
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
        if type(ipaddress.ip_address(self.source_ip)) == ipaddress.IPv4Address:
            self.source_ip_int = int(ipaddress.ip_address(self.source_ip))
        else:
            self.source_ip_int = None  # IPv6 integer representations are too large to store in MongoDB currently
        super(ClickDoc, self).save(*args, **kwargs)


class ApplicationDoc(RootDoc):
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
        collection_name = APPLICATION_COLLECTION
        final = True  # so we don't get a '_cls' field in these documents (e.g. "_cls" : "__main__.Customer")
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_user_time_name_version(user_id, time, app_name, app_version):
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
    """Provides schema for User Report doc.
    customer - a customer ID that corresponds to a CustomerDoc
    assessment - an assessment ID that corresponds to an AssessmentDoc
    campaign - a campaign ID that corresponds to a CampaignDoc
    first_report - the timestamp when the first user a user click ("report") was received during a phishing campaign
    total_num_reports - the total number of user clicks ("reports") for a campaign
    """
    customer = fields.ReferenceField(CustomerDoc, required=True)
    assessment = fields.ReferenceField(AssessmentDoc, required=True)
    campaign = fields.ReferenceField(CampaignDoc, required=True)
    first_report = fields.DateTimeField(blank=True)
    total_num_reports = fields.IntegerField(blank=False)

    class Meta:
        """Meta class for UserReportDoc."""

        collection_name = USER_REPORT_COLLECTION
        final = True
        ignore_unknown_fields = True  # TODO see if this can be inherited from RootDoc

    def find_by_customer_assessment_campaign(customer_id, assessment_id, campaign_id):
        try:
            doc = UserReportDoc.objects.raw(
                {"customer": customer_id,
                 "assessment": assessment_id,
                 "campaign": campaign_id}).first()
        except DoesNotExist:
            return None
        return doc

    def save(self, *args, **kwargs):
        """Save UserReportDoc to MongoDB."""
        super(UserReportDoc, self).save(*args, **kwargs)
