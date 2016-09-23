from django.template import Library

register = Library()

@register.filter
def as_percentage_of(part, whole):
	try:
		return "%d%%" % (float(part) / whole * 100)
	except (ValueError, ZeroDivisionError):
		return ""
