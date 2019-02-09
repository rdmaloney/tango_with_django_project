from django.shortcuts import render

from django.http import HttpResponse

def index(request):
   # First construct a dictionary to pass to the template - this is it's "context".
    # The Key value should match the name of the {{ ToBeReplaced }} -> "ToBeReplaced"
    # text in the template.
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    #               ^Key to replace in template   ^Value

    return render(request, 'rango/index.html', context=context_dict)
    # Django finds the template file as refrenced in the settings, and takes the context to adapt
    # the template to add content "context". When Django encounters {{ key }} in the template file
    # it looks up the name in the context dictionary to find out what to replace it with.


def about(request):
    return render(request, 'rango/about.html')
