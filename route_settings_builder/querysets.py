from django.db import models


class RouteQuerySet(models.QuerySet):
    """ QuerySet к модели Route """
    def add_is_draft_field(self):
        """
        Добавление поля is_draft в запрос
        :return: QuerySet
        """
        return self.annotate(is_draft=models.Case(models.When(details=None, then=True),
                                                  models.When(details={}, then=True),
                                                  default=False))
