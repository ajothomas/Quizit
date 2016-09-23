from django.template import Library

register = Library()

@register.filter
def multiply(string, times):
	return string * int(times)

@register.filter
def anonymize(string, flag):
	if int(flag) == 1:
		return string[:2].title() + '*' *int(len(string)-2)
	else:
		return '*' * int(len(string))