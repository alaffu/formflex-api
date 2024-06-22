from rest_framework.routers import DefaultRouter

from api.views.choice_viewset import ChoiceViewset
from api.views.form_viewset import FormViewset
from api.views.question_viewset import QuestionViewset
from api.views.response_viewset import ResponseViewset

router = DefaultRouter()
router.register(r"forms", FormViewset)
router.register(r"questions", QuestionViewset)
router.register(r"choices", ChoiceViewset)
router.register(r"responses", ResponseViewset)


urlpatterns = router.urls
