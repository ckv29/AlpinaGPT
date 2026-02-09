from django.db import models
import uuid


#class ApiUser(AbstractUser):
# pass

class Bot(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    #owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # опционально
    telegram_token = models.CharField(max_length=100, blank=True)

    #логическое удаление
    deleted = models.BooleanField(default=False)

    # GPT settings
    gpt_model = models.CharField(max_length=50, default="gpt-4o")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=500)
    system_prompt = models.TextField(default="You are a helpful assistant.")

    def __str__(self):
        if self.deleted:
            return f"Bot {self.name} deleted"
        return self.name

class Scenario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bot = models.ForeignKey(Bot, related_name="scenarios", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bot.name} : {self.name}"

class Step(models.Model):
    order = models.PositiveIntegerField()
    scenario = models.ForeignKey(Scenario, related_name="steps", on_delete=models.CASCADE)

    prompt_template = models.TextField(help_text="Может содержать шаблоны: {user_input}, {context} и т.д.")
    expected_input_type = models.CharField(
        max_length=50,
        choices=[
            ('text', 'Text'),
            ('choice', 'Choice from buttons'),
            ('email', 'Email'),
            ('phone', 'Phone number'),
        ],
        default='text'
    )
    buttons_json = models.JSONField(blank=True, null=True,
                                    help_text="Telegram inline buttons: [{'text': 'Yes', 'callback': 'yes'}]")

    # Условия перехода
    next_step_on_success = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_steps'
    )
    is_final = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        unique_together = ('scenario', 'order')

    def __str__(self):
        return f"Step {self.order} of {self.scenario.name}"