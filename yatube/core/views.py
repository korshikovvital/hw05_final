from django.shortcuts import render


def page_not_found(requests, exception):
    return render(requests, 'core/404.html', {'path': requests.path}, status=404)


def csrf_failure(requests, reason=''):
    return render(requests, 'core/403csrf.html')
