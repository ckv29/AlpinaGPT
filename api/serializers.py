# bots/serializers.py

from rest_framework import serializers
from .models import Bot, Scenario, Step


# 1. Сначала StepSerializer — он "листовой"
class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = [
            'id', 'order', 'prompt_template', 'expected_input_type',
            'buttons_json', 'next_step_on_success', 'is_final'
        ]


# 2. Потом ScenarioSerializer — он использует StepSerializer
class ScenarioSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)

    class Meta:
        model = Scenario
        fields = [
            'id', 'name', 'bot', 'is_active', 'steps'
        ]


# 3. Потом BotSerializer — он использует ScenarioSerializer
class BotSerializer(serializers.ModelSerializer):
    scenarios = ScenarioSerializer(many=True, read_only=True)

    class Meta:
        model = Bot
        fields = [
            'id', 'name', 'description', 'telegram_token',
            'gpt_model', 'temperature', 'max_tokens', 'system_prompt',
             'scenarios'
        ]


# === Сериализаторы для создания (без вложенности) ===

class BotCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bot
        fields = [
            'name', 'description', 'telegram_token',
            'gpt_model', 'temperature', 'max_tokens', 'system_prompt'
        ]


class ScenarioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['name','bot', 'is_active']


class StepCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = [
            'order','scenario','prompt_template', 'expected_input_type',
            'buttons_json', 'next_step_on_success', 'is_final'
        ]

    def validate_next_step_on_success(self, value):
        if value:
            scenario_id = self.context.get('scenario_id')
            if not scenario_id:
                raise serializers.ValidationError("Scenario context missing.")
            if value.scenario_id != scenario_id:
                raise serializers.ValidationError(
                    "Next step must belong to the same scenario."
                )
        return value