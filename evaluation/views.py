from django.shortcuts import render

# Create your views here.
def evaluator(request):
    """privacy.html renderer.

    :param request: rest API request object.
    :type request: Request
    :return: Just another django mambo.
    :rtype: HttpResponse
    """
    return render(request, 'evaluation/evaluator.html', {})
