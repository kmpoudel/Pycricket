from django.shortcuts import render_to_response, get_object_or_404, redirect
from latest.models import Game
from latest.forms import NewSportForm, UserForm
from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
import json
import requests


def index(request):
    form=NewSportForm()
    #import pdb
    #pdb.set_trace()
    if request.method == 'POST':
        form = NewSportForm(request.POST)
        if form.is_valid():
            form.save()
            print "success"
            return render_to_response('latest/error.html', {'error_message': form})
        return render_to_response('latest/index.html', {'form': form})


def latest(request):
    form = NewSportForm()
    #import pdb
    #pdb.set_trace()
    if request.method == 'POST':
        form = NewSportForm(request.POST)
        if form.is_valid():
            form.save()
            print "success"
            return render_to_response('latest/error.html', {'error_message': form})
    return render_to_response('latest/success.html', {'form': form})


def game(request):
    from xml.dom import minidom
    import urllib
    url = "http://synd.cricbuzz.com/j2me/1.0/livematches.xml"
    dom = minidom.parse(urllib.urlopen(url))
    #minidom.parse('livematches.xml')
    print dom
    #mATCH nAME
    itemlist = dom.getElementsByTagName('match')
    statelist = dom.getElementsByTagName('state')
    momlist = dom.getElementsByTagName('mom')
    # only for json data saving
    #r = requests.get("cricscore-api.appspot.com/csa",headers={"content-type":"application/json"})
    #with open('data.txt', 'w') as outfile:
    #    json.dump(r.json(), outfile)
    return render_to_response('latest/gamedetails.html', {'itemlist': itemlist, 'statelist': statelist,
                                                          'momlist': momlist})


class ListGameView(ListView):
    model = Game
    template_name = 'latest/game_list.html'
    paginate_by = 5


class CreateGameView(CreateView):
    model = Game
    template_name = 'latest/edit_game.html'

    def get_success_url(self):
        return reverse('game-list')


def register(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()

    # Render the template depending on the context.
    return render_to_response(
        'latest/register.html',
        {'user_form': user_form, 'registered': registered}, context)


def about(request):
    return render_to_response('latest/about.html')


def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/latest/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Pycricinfo account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('latest/login.html', {}, context)


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/latest/games')
