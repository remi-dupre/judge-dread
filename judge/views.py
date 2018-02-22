from django.shortcuts import render,redirect
from django.template.loader import get_template
from django.http import HttpResponse, Http404

from .forms import ProblemForm
from .models import Problem, ProblemDescription

def home(request):
    """
    Main page.
    """
    template = get_template("home.html")
    return HttpResponse(template.render({},request))

def problem_display(request, problem_id):
    try:
        problem_description = ProblemDescription.objects.get(pk=problem_id)
    except ProblemDescription.DoesNotExist:
        raise Http404('Problem does not exist')

    template = get_template("problem.html")
    context = {
        'problem_description': problem_description,
        'problem': problem_description.problem
    }
    return HttpResponse(template.render(context, request))

def creation(request):
    """"
    Display a form to create a new task.
    If the form is filled, create the new problem and returns.
    """
    # Recover form datas
    if request.method == 'POST':
        form = ProblemForm(request.POST, request.FILES)
    else:
        form = ProblemForm()

    # Save form datas and redirect to main page
    if form.is_valid():
        problem = Problem(
            name = form.cleaned_data['name'],
            soluce_language = form.cleaned_data['soluce_language'],
            soluce_code = form.cleaned_data['soluce_code']
        )
        problem.save()
        description = ProblemDescription(
            problem = problem,
            language = form.cleaned_data['language'],
            name = form.cleaned_data['name'],
            content = form.cleaned_data['description']

        )
        description.save()
        return redirect(home)

    else:
        context = {
            'form': form
        }
        template = get_template('creation.html')
        return HttpResponse(template.render(context, request))

# Create your views here.
