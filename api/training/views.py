from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from fitness.models import TrainingPlan

from .serializers import TrainingPlanSerializer


@extend_schema(
    request=TrainingPlanSerializer,
    responses={201: TrainingPlanSerializer},
)
@extend_schema(
    methods=['GET'],
    responses={200: TrainingPlanSerializer(many=True)},
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_training_plan(request):
    if request.method == 'GET':
        plans = TrainingPlan.objects.filter(
            user=request.user,
        ).order_by('-created_at')
        return Response(TrainingPlanSerializer(plans, many=True).data)

    serializer = TrainingPlanSerializer(
        data=request.data,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    request=TrainingPlanSerializer,
    responses={200: TrainingPlanSerializer, 204: None},
)
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def training_plan_detail(request, plan_id):
    plan = get_object_or_404(
        TrainingPlan,
        id=plan_id,
        user=request.user,
    )

    if request.method == 'GET':
        return Response(TrainingPlanSerializer(plan).data)

    if request.method == 'DELETE':
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = TrainingPlanSerializer(
        plan,
        data=request.data,
        partial=True,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
