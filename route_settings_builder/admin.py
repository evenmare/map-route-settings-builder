from django.contrib import admin
from django.db.models import JSONField

from django_json_widget.widgets import JSONEditorWidget

from route_settings_builder import models


@admin.register(models.Criterion)
class CriterionAdmin(admin.ModelAdmin):
    """ Администраторская страница для критериев """
    search_fields = ('internal_name', 'name', )
    list_display = ('internal_name', 'name', 'value_type', )
    list_filter = ('value_type', )


class PlaceCriterionInline(admin.TabularInline):
    """ Inline-панель для страницы мест. Отображает блок критериев для места """
    autocomplete_fields = ('criterion', )

    model = models.PlaceCriterion
    extra = 1


@admin.register(models.Place)
class PlaceAdmin(admin.ModelAdmin):
    """ Администраторская страница для мест """
    search_fields = ('name', )
    list_display = ('name', 'longitude', 'latitude', )
    inlines = (PlaceCriterionInline, )


class RouteCriterionInline(admin.TabularInline):
    """ Inline-панель для страницы маршрута. Отображает блок критериев для маршрута """
    autocomplete_fields = ('criterion', )

    model = models.RouteCriterion
    extra = 1


class GuideInline(admin.TabularInline):
    """ Inline-панель для страницы маршрута. Отображает блок путеводителя для маршрута """
    model = models.Guide


@admin.register(models.Route)
class RouteAdmin(admin.ModelAdmin):
    """ Администраторская страница для маршрутов """
    search_fields = ('name', 'author__username', )
    list_display = ('name', 'author', )

    autocomplete_fields = ('places', 'author', )
    inlines = (GuideInline, RouteCriterionInline, )

    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }
