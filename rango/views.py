from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Import the Category model
from rango.models import Category
from datetime import datetime

def visitor_cookie_handler(request):
    # First get the number of visits to the site using the COOKIES.get() function
    # If the cookie exists the value is cast to an int, if not a default of 1 is used
    visits = int(get_server_side_cookie(request, 'visits', '1'))

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))

    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if(datetime.now() - last_visit_time).days > 0:
        visits = visits +1
        #Update the last visit cookie
        request.session['last_visit'] = str(datetime.now())
    else:
        #Set the last visit cookie to the same as it was before
        request.session['last_visit'] = last_visit_cookie
    # Update / set the visits cookie
    request.session['visits'] = visits

def get_server_side_cookie(request, cookie, default_val = None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def index(request):
     request.session.set_test_cookie()
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
                    'pages': most_view_pages,}

            visitor_cookie_handler(request)
            context_dict['visits'] = request.session['visits']
            response = render(request, 'rango/index.html', context=context_dict)

    return response
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
     if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    visitor_cookie_handler(request)
    context_dict = {'visits': request.session['visits']}
    return render(request, 'rango/about.html', context_dict)
    

@login_required
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

@login_required
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

def register (request):
    # Boolean value to store if the registration was successful.
    registered = False

    # If the form has been submitted(POST)
    if (request.method == 'POST'):
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # Check if both forms are filled out correctly:
        if user_form.is_valid() and profile_form.is_valid():
            # save the users registration data
            user = user_form.save()
            # now we hash the password and add it to the database
            user.set_password(user.password)
            user.save()

            # We can now deal with the user profile side of things
            profile = profile_form.save(commit=False)
            profile.user = user

            # Now to add the profile picture if provided!
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Save the new user and set flag to show it worked.
            profile.save()
            registered = True
        else:
            # Invalid form(s)
            print(user_form.errors, profile_form.errors)
    else:
        # have to display the forms for the user to fill in
        user_form = UserForm()
        profile_form = UserProfileForm()

    # render a display either a new registration form, errors in a submitted form
    # or a success message if succesfully registed user

    return render(request, 'rango/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered,
    })

def user_login(request):
    # Is the request is a POST request get the info out of it
    if request.method == 'POST':
        # The form will have a username and password section which will be passed along to the request

        username = request.POST.get('username')
        password = request.POST.get('password')

        #now check to see if they match
        user = authenticate(username= username, password= password)

        # If the details match then user will be set to a User variable
        if user:
            if user.is_active:
                # allow user to log in
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            #bad login details were given
            print("Invalid login details: {0}, {1}".format(username, password))

            return HttpResponse("Invalid login details supplied.")
    # It was probably a get request so send the login form.
    return render(request, 'rango/login.html', {})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!") 
