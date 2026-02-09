from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 1. Основной роутер для ботов и сценариев
router = DefaultRouter()
router.register(r'bots', views.BotViewSet)        # → /api/bots/
router.register(r'scenarios', views.ScenarioViewSet)  # → /api/scenarios/

# 2. Отдельный роутер для шагов (вложенный)
step_router = DefaultRouter()
step_router.register(r'steps', views.StepViewSet, basename='scenario-steps')

# 3. Собираем всё вместе
urlpatterns = [
    path('', include(router.urls)),  # → /api/bots/, /api/scenarios/
    path('scenarios/<int:scenario_pk>/', include(step_router.urls)),  # → /api/scenarios/1/steps/
    path('test-gpt/', views.test_gpt_step, name='test_gpt_step'),
]

