from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def uglify(field):
    x = ''
    for i in range(len(field)):

        if i % 2 == 0:
            x += field[i].lower()
        else:
            x += field[i].upper()
    return x
