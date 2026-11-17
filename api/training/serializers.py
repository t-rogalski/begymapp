from rest_framework import serializers

from fitness.models import TrainingPlan


class TrainingPlanSerializer(serializers.ModelSerializer):
    days_per_week = serializers.IntegerField(min_value=1)
    mesocycle_weeks = serializers.IntegerField(min_value=1)

    class Meta:
        model = TrainingPlan
        fields = [
            'id',
            'name',
            'created_at',
            'days_per_week',
            'mesocycle_weeks',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        user = self.context['request'].user
        plans = TrainingPlan.objects.filter(user=user, name=value)
        if self.instance:
            plans = plans.exclude(pk=self.instance.pk)
        if plans.exists():
            raise serializers.ValidationError(
                'You already have a training plan with this name.'
            )
        return value

    def create(self, validated_data):
        return TrainingPlan.objects.create(
            user=self.context['request'].user,
            **validated_data,
        )
