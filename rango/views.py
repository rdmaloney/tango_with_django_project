from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Page
from rango.forms import CategoryForm, PageForm
from django.core.urlresolvers import reverse

# Import the Category model
from rango.models import Category

def index(request):
    # Query the database to get a list of all the categories in the database.
    # Order these by number of likes in descending order.
    # If more than 5 results show only the top 5 results.
    category_list = Category.objects.order_by('-likes')[:5]

    most_view_pages = Page.objects.order_by('-views')[:5]

    
   # First construct a dictionary to pass to the template - this is it's "context".
    # The Key value should match the name of the {{ ToBeReplaced }} -> "ToBeReplaced"
    # text in the template. And add the results of the database query into the dictionary.
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!",
                    'categories': category_list,
                    'pages': most_view_pages}

    return render(request, 'rango/index.html', context=context_dict)
    # Django finds the template file as refrenced in the settings, and takes the context to adapt
    # the template to add content "context". When Django encounters {{ key }} in the template file
    # it looks up the name in the context dictionary to find out what to replace it with.

    def show_category(request, category_name_slug):
    # create a blank dictionary that will be used to populate the template
    context_dict  = {}

    try:
        # Try to find a category with the slug given.
        # If we can't the get() will raise an exception ewe should deal with.
        category = Category.objects.get(slug=category_name_slug)

        #Then if that didn't raise an exception we can query this category to find pages
        pages = Page.objects.filter(category=category)

        #Then add these pages to the context_dict
        context_dict['pages'] = pages

        #we should also add the category so we know what category the pages are for.
        context_dict['category'] = category

    except Category.DoesNotExist:
        # If the requested category doesn't exist we get here.
        # set the pages and category to none in the dictionary
        context_dict['pages'] = None
        context_dict['category'] = None

    # Now render the template with data as a response.
    return render(request, 'rango/category.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')

def add_category(request):
    form = CategoryForm()

    # HTTP Post request?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            # Save the new category to the database.
            cat = form.save(commit=True)
            print(cat, cat.slug)
            # New category saved, redirect the user to the index page
            return index(request)
        else:
            # the form was filled out incorrectly
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
            return show_category(request, category_name_slug)

        else:
            print(form.errors)
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict) 

