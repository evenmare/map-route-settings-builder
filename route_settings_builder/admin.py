from django.contrib import admin

from route_settings_builder import models


@admin.register(models.Criterion)
class CriterionAdmin(admin.ModelAdmin):
    """ Администраторская страница для критериев """
    search_fields = ('internal_name', 'name', )
    list_display = ('internal_name', 'name', 'value_type', 'updated_at', 'created_at', )
    list_filter = ('value_type', )
    ordering = ('-updated_at', )


class PlaceCriterionInline(admin.TabularInline):
    """ Inline-панель для страницы мест. Отображает блок критериев для места """
    model = models.PlaceCriterion

    autocomplete_fields = ('criterion', )
    extra = 0


@admin.register(models.Place)
class PlaceAdmin(admin.ModelAdmin):
    """ Администраторская страница для мест """
    search_fields = ('uuid', 'name', )
    list_display = ('name', 'latitude', 'longitude', 'updated_at', 'created_at', )
    ordering = ('-updated_at', )

    inlines = (PlaceCriterionInline, )


class RoutePlaceInline(admin.StackedInline):
    """ Inline-панель для страницы маршрута. Отображает блок мест для маршрута """
    model = models.RoutePlace

    autocomplete_fields = ('place',)
    extra = 0


class RouteCriterionInline(admin.TabularInline):
    """ Inline-панель для страницы маршрута. Отображает блок критериев для маршрута """
    model = models.RouteCriterion

    autocomplete_fields = ('criterion', )
    extra = 0


@admin.register(models.Route)
class RouteAdmin(admin.ModelAdmin):
    """ Администраторская страница для маршрутов """
    search_fields = ('uuid', 'name', 'author__username', )
    list_display = ('name', 'author', 'updated_at', 'created_at', )
    ordering = ('-updated_at', )
    readonly_fields = ('uuid', )

    autocomplete_fields = ('author', )
    inlines = (RoutePlaceInline, RouteCriterionInline, )
