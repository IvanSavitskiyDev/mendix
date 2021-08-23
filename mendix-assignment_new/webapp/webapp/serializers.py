from marshmallow import Schema, fields, ValidationError, validates_schema


class DateRangeSerializer(Schema):
    start_date = fields.DateTime(format='%Y-%m-%d', required=True)
    end_date = fields.DateTime(format='%Y-%m-%d', required=True)

    @validates_schema
    def validate_numbers(self, data, **kwargs):
        if data["start_date"] > data["end_date"]:
            raise ValidationError("end_date must be greater than start_date")


class DownloadIdSerializer(Schema):
    download_id = fields.UUID(required=True)
