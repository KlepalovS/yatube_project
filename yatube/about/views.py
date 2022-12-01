from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Вью-класс странички об авторе."""

    template_name = 'about/about.html'


class AboutTechView(TemplateView):
    """Вью-класс странички об используемых технологиях."""

    template_name = 'about/tech.html'
