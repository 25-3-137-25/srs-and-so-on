from rest_framework import serializers
from .models import Faculty, StudyGroup


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ("id", "name", "code")


class StudyGroupSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source="faculty.name", read_only=True)
    curator_name = serializers.CharField(source="curator.get_full_name", read_only=True, default="—")

    class Meta:
        model = StudyGroup
        fields = (
            "id", "name", "faculty", "faculty_name",
            "curator", "curator_name", "status",
            "students_count", "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        if len(value.strip()) < 4:
            raise serializers.ValidationError(
                "Номер группы должен содержать не менее 4 символов."
            )
        return value.strip()

    def validate(self, attrs):
        if self.instance is None:
            if attrs.get("status", StudyGroup.Status.RECRUITING) != StudyGroup.Status.RECRUITING:
                raise serializers.ValidationError({
                    "status": "Новая группа должна иметь статус «Набор открыт»."
                })
        return attrs

    def validate_status(self, value):
        if self.instance is None:
            return value

        old_status = self.instance.status
        new_status = value

        if new_status == old_status:
            return new_status

        allowed_transitions = {
            StudyGroup.Status.RECRUITING: {StudyGroup.Status.STUDYING},
            StudyGroup.Status.STUDYING: {StudyGroup.Status.GRADUATED},
            StudyGroup.Status.GRADUATED: set(),
        }

        if new_status not in allowed_transitions.get(old_status, set()):
            raise serializers.ValidationError(
                f"Недопустимый переход статуса: "
                f"«{dict(StudyGroup.Status.choices)[old_status]}» → "
                f"«{dict(StudyGroup.Status.choices)[new_status]}»."
            )
        return new_status