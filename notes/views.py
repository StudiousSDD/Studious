from django.shortcuts import render, redirect

from .models import Note, Class, Lecture
from .forms import AddClass,AddEvent

from schedule.models.events import Event, Occurrence
from schedule.models.rules import Rule
# Create your views here.

def editor(request):
    noteid = int(request.GET.get('noteid',0))
    note = Note.objects.all()

    if request.method == 'POST':
        noteid = int(request.POST.get('noteid',0))
        title = request.POST.get('title')
        content = request.POST.get('content')

        if noteid > 0:
            document = Note.objects.get(pk=noteid) # Change document 
            document.title = title
            document.content = content
            document.save()

            return redirect('/notes/?noteid=%i' % noteid)
        else: 
            document = Note.objects.create(title=title, content=content)

            return redirect('/notes/?noteid=%i' % document.id)

    if noteid > 0:
        document = Note.objects.get(pk=noteid)
    else:
        document = ''

    context = {
        'noteid' : noteid,
        'note' : note,
        'document' : document,
    }
    return render(request, 'notes/editor.html',context)                 

def home_calendar_view(request):
    all_classes = Class.objects.all()
    context = {
        'classes' : all_classes,
    }
    return render(request, "notes/calendar.html", context)

def view_meeting_by_date(request):
    eventid = int(request.GET.get('event',0))
    start = request.GET.get('start',0)
    end = request.GET.get('end',0)
    
    # TODO: Implement this. Needs to find the Lecture and Occurrence (link?)
    
    return

def view_classes(request):
    classes = Class.objects.all()
    classid = int(request.GET.get('classid',0))

    if request.method == 'POST':
        classid = int(request.POST.get('classid',0))
        name = request.POST.get('name')
        if classid > 0:
            a_class = Class.objects.get(pk=classid) # Change document 
            a_class.name = name
            a_class.save()
            return redirect('/classes/?classid=%i' % classid)

        else:
            a_class = Class.objects.create
            return redirect('/classes/?classid=%i' % a_class.id)
        

    if classid > 0:
        a_class = Class.objects.get(pk=classid) 
    else: 
        a_class = ''

    context = {
        'classes' : classes,
        'classid' : classid,
        'a_class' : a_class,
    }
    return render(request, "notes/view-classes.html", context)


def delete_document(request, noteid):
    document = Note.objects.get(pk=noteid)
    document.delete()

    return redirect('/notes/?noteid=0')


def add_class(request):
    if request.POST:
        form = AddClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        return redirect('/classes/')
    
    return render(request, "notes/add_class.html",{'form': AddClass})

def create_event(form):
    event_title = form.cleaned_data['title']
    event = Event.objects.create(title=event_title, 
                                 start=form.cleaned_data['start'], 
                                 end=form.cleaned_data['end'], 
                                 calendar=form.cleaned_data['calendar'], 
                                 color_event=form.cleaned_data['color_event'],
                                )
    create_class_from_event(event)
    return event

def add_event(request):
    if request.POST:
        form = AddEvent(request.POST,request.FILES)
        if form.is_valid():
            event = form.save()
            repeat = form.cleaned_data["repeat"]
            rule = create_rule(event.title, repeat)
            event.rule = rule
            event.save()
            create_class_from_event(event)
        return redirect('/classes/')
    return render(request, "notes/add_event.html",{'form': AddEvent})

def delete_class(request, classid):
    a_class = Class.objects.get(pk=classid)
    a_event = a_class.calendar_event
    a_class.delete()
    a_event.delete()

    return redirect('/classes/')

def create_rule(ename, rep):
    rrname = (ename + '_repeat')
    desc = rrname
    freq = "WEEKLY"    
    params = "byweekday:"
    for r in rep:
        params += (r + ',')
    
    rule = Rule.objects.create(name = rrname,
                               description = desc,
                               frequency = freq,
                               params = params
                              )
    rule.save()
    return rule

def create_class_from_event(event):
    class_name = event.title
    class_object = Class.objects.create(name=class_name, calendar_event=event)
    class_object.save() 