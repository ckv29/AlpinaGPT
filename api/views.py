from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

from .models import Bot, Scenario, Step
from .serializers import (
    BotSerializer,
    BotCreateSerializer,
    ScenarioSerializer,
    ScenarioCreateSerializer,
    StepSerializer,
    StepCreateSerializer
)

@api_view(['POST'])
def test_gpt_step(request):
    """
    Тестовый эндпоинт для генерации ответа по шагу.
    Пример тела запроса:
    {
        "bot_id": 1,
        "step_id": 2,
        "context": {
            "user_name": "Алиса",
            "genre": "фантастика"
        }
    }
    """
    bot_id = request.data.get('bot_id')
    step_id = request.data.get('step_id')
    context = request.data.get('context', {})

    if not bot_id or step_id:
        return Response(
            {"error" : "Укажите bot_id и step_id"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        bot = Bot.objects.get(id=bot_id)
        step = Step.objects.get(id=step_id, scenario_bot = bot)
    except Bot.DoesNotExist:
        return Response({"error":"Бот не найден"}, status=status.HTTP_400_BAD_REQUEST)
    except Step.DoesNotExist:
        return Response({"error":"Шаг не найден или не принадлежит боту"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        final_promt = step.prompt_template.format(**context)
    except KeyError as e:
        return Response(
            {"error" : f"Не хватает переменной в контексте {e}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        gpt_response = generate_response(
            system_promt=bot.system_promt,
            user_promt=final_promt,
            model=bot.gpt_model,
            temperature=bot.temperature,
            max_tokens=bot.max_tokens
        )
    except Exception as e:
        return Response(
            {"error" : str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return Response({
        "promt_used" : final_promt,
        "gpt_response" : gpt_response,
        "model" : bot.gpt_model,
        "temperature" : bot.temperature
    })


class BotViewSet(viewsets.ModelViewSet):
    queryset = Bot.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BotCreateSerializer
        return BotSerializer


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ScenarioCreateSerializer
        return ScenarioSerializer

    def get_queryset(self):
        # Опционально: фильтрация по боту через query param ?bot_id=1
        bot_id = self.request.query_params.get('bot_id')
        if bot_id:
            return Scenario.objects.filter(bot_id=bot_id)
        return Scenario.objects.all()


class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StepCreateSerializer
        return StepSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Передаём scenario_id в сериализатор для валидации
        if 'scenario_pk' in self.kwargs:
            context['scenario_id'] = int(self.kwargs['scenario_pk'])
        return context

    def get_queryset(self):
        # Фильтруем шаги только по сценарию из URL: /scenarios/{id}/steps/
        if 'scenario_pk' in self.kwargs:
            return Step.objects.filter(scenario_id=self.kwargs['scenario_pk'])
        return Step.objects.all()

