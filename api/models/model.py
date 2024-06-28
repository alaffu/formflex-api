from django.db import models


class Form(models.Model):
    created_by = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=250)
    description = models.TextField()


class Question(models.Model):
    QUESTION_TYPES = (
        ("text", "Text"),
        ("number", "Number"),
        ("choice", "Choice"),
        ("checkbox", "Multiple Choice"),
    )

    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    parent = models.ForeignKey(
        "self", related_name="children", on_delete=models.CASCADE, null=True, blank=True
    )

    def is_root(self):
        return self.parent is None


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    next_question = models.ForeignKey(
        Question,
        related_name="preceding_choice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


class Response(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    answer_number = models.FloatField(blank=True, null=True)
    answer_choice = models.IntegerField(blank=True, null=True)
    created_by = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
