from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect

from icalendar import Calendar
import colorsys, random, math

from .models import Note, Class, Lecture, ArchivedNote
from .forms import AddClass,AddEvent,ImportEvent,EditEventForm

from schedule.models.events import Event, Occurrence
from schedule.models.rules import Rule
# Create your views here.

# information for opening the note editor
def editor(request, lectureid):
    # the id of the requested note (0 if none specified which opens a new note)
    noteid = int(request.GET.get('noteid',0))

    # notes a displayed by lecture so finding the correct lecture is needed
    lec = Lecture.objects.get(id=lectureid)
    # the set of all notes for the requested lecture
    note = lec.note_set.all()
    # the set of all archived notes for the requested lecture
    archived_notes = lec.archivednote_set.all()

    # notes can be sorted in different ways
    sort_by = request.GET.get('sort_by', 'title')
    if sort_by == 'title_asc':
        note = note.order_by('title')
    elif sort_by == 'title_desc':
        note = note.order_by('-title')
    elif sort_by == 'created_by_asc':
        note = note.order_by('created_at')
    elif sort_by == 'created_by_desc':
        note = note.order_by('-created_at')
    #if they create a new note save it
    if request.method == 'POST':
        noteid = int(request.POST.get('noteid',0))
        title = request.POST.get('title')
        content = request.POST.get('content')
        # if they are changing an existing note update all the fields
        if noteid > 0:
            document = Note.objects.get(pk=noteid) # Change document 
            document.title = title
            document.content = content
            document.save()

            return redirect('/notes/{}?noteid=%i&sort_by=%s'.format(lectureid) % (noteid, sort_by))
        else: 
            document = Note.objects.create(title=title, content=content, lecture=lec)

            return redirect('/notes/{}?noteid=%i&sort_by=%s'.format(lectureid) % (document.id,sort_by))

    if noteid > 0:
        document = Note.objects.get(pk=noteid)
    else:
        document = ''

    context = {
        'lecture' : lec,
        'noteid' : noteid,
        'note' : note,
        'document' : document,
        'sort_by' : sort_by,
        'archived_notes' : archived_notes
    }
    return render(request, 'notes/editor.html',context)                 
# heh?
def home_calendar_view(request):
    all_classes = Class.objects.all()
    context = {
        'classes' : all_classes,
    }
    return render(request, "notes/calendar.html", context)
# heh?
def view_meeting_by_date(request):
    eventid = int(request.GET.get('event',0))
    start = request.GET.get('start',0)
    end = request.GET.get('end',0)
    
    
    
    return
# send only the classes associated with this account to be displayed on the home page
def home_calendar_view(request):
    if (request.user.is_authenticated):
        all_classes = Class.objects.filter(calendar_event__calendar_id=request.user.profile.calendar.id)
        context = {
            'classes' : all_classes,
        }
    else:
        context = None
    return render(request, "notes/calendar.html", context)
# unfinished
def view_meeting_by_date(request):
    eventid = int(request.GET.get('event',0))
    start = request.GET.get('start',0)
    end = request.GET.get('end',0)
    
    # TODO: Implement this. Needs to find the Lecture and Occurrence (link?)
    
    return
# find the correct class to display (as well as all other classes of this account for the side bar)
def view_class(request, classid):
    if (request.user.is_authenticated):
        classes = Class.objects.filter(calendar_event__calendar_id=request.user.profile.calendar.id)
        classid = Class.objects.get(name=classid)
        context = {
            'classes' : classes,
            'classid' : classid,
        }
    else:
        context = None
    return render(request, "notes/view-class.html", context)
# creating a new lecture in a specific class
def create_lecture(request):
    # get which class this is for from the request
    classid = request.GET.get('classid',0)
    cls = Class.objects.get(name=classid)
    # the event associated with the class
    eve = cls.calendar_event
    # the number of the next lecture (number of lectures currently made + 1)
    lecnum = len(cls.lecture_set.all()) + 1
    if (lecnum != 1):
        # use the previous lecture to find out the date when the new lecture should be
        time = cls.lecture_set.get(lecture_number = lecnum - 1).occurrence.start
    else:
        # if they are creating the first lecture there is no previous lecture to go off of
        time = eve.start

    # a generator which creates dates when lectures happen
    generator = eve.occurrences_after(time)
    # search through lectures until a new one is generated
    while(1):
        occurr = next(generator)
        # since some lectures overlap we need to find one that starts AFTER the previous lecture (or start of class)
        if (occurr.start > time):
            break
    occurr.save()
    # create the new lecture with the date (occurrence) we found
    lec = Lecture.objects.create(
        occurrence = occurr,
        cls = cls,
        lecture_number = lecnum,
    )
    lec.save()
    # redirect back to the page they were just on
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# def delete_document(request, noteid):
#     document = get_object_or_404(Note,pk=noteid)
#     #Archiving the document 
#     archived_document = ArchivedNote(
#         lecture = document.lecture,
#         title = document.title,
#         content = document.content,
#     )

#     archived_document.save() 

#     document.delete()
#     sort_by = request.GET.get('sort_by')
#     return redirect('/notes/?noteid=0&sort_by=%s' % sort_by)

# change a note over to an archived note
def archive_document(request, noteid):
    document = get_object_or_404(Note,pk=noteid)
    #Archiving the document 
    archived_document = ArchivedNote(
        lecture = document.lecture,
        title = document.title,
        content = document.content,
    )

    archived_document.save() 

    document.delete()
    sort_by = request.GET.get('sort_by')
    # return back to the notes page
    return redirect('/notes/{}?noteid=0&sort_by=%s' .format(document.lecture.id) % sort_by)

# change an archived note back to a note
def restore_archived_note(request,noteid):
    document = get_object_or_404(ArchivedNote,pk=noteid)
    #Archiving the document 
    note = Note(
        lecture = document.lecture,
        title = document.title,
        content = document.content,
    )

    note.save() 

    document.delete()
    sort_by = request.GET.get('sort_by')
    # return back to the notes page of this lecture
    return redirect(f'/notes/{document.lecture.id}?noteid={note.id}&sort_by={sort_by}')

# def archived_note_view(request):
#     archived_notes = ArchivedNote.objects.all()
#     return render(request,'notes/editor.html', {'archived_notes': archived_notes})

# delete an archived note (asks for confirmation first)
def delete_archived_note(request, noteid):
    if request.method == 'POST':
        sort_by = request.GET.get('sort_by', 'title')
        note = get_object_or_404(ArchivedNote, id=noteid)
        lectureid = note.lecture.id
        note.delete()
        return redirect(f'/notes/{lectureid}?noteid=0&sort_by={sort_by}')
    else:
        return render(request,'editor.html')
# creates a new class
def add_class(request):
    # if they send the class data create the new class
    if request.POST:
        form = AddClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        name = form.name
        # send them to the new class page
        return redirect('/class/{}'.format(name))
    # send them to the page where they can create a new class
    return render(request, "notes/add_class.html",{'form': AddClass})
# backend needed to create the event for a class
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
# make a random pastel color for imported classes
def random_pastel():
    random.seed()
    hue = random.randrange(360)
    return hue_to_pastel(hue)
# create pastel colors that look nice for classes
def hue_to_pastel(hue):
    color = colorsys.hsv_to_rgb(hue / 360, 0.4, 1.0)
    r, g, b = color[0], color[1], color[2]
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
# change a hex value to its hue
def hex_to_hue(hex):
    hex = hex.lstrip('#')
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    hsl = colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])
    return math.floor(hsl[0] * 360)
# add a new event (class)
def add_event(request):
    if request.POST:
        form = AddEvent(request.POST,request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            
            repeat = form.cleaned_data["repeat"]
            rule = create_rule(event.title, repeat)
            event.rule = rule
            
            hue = form.cleaned_data["color"]
            event.color_event = hue_to_pastel(hue)
            
            event.save()
            create_class_from_event(event)
        title = form.cleaned_data["title"]
        return redirect('/class/{}'.format(title))
    return render(request, "notes/add_event.html",{'form': AddEvent})
# import classes from a file from QUACS
def import_class(request):
    if request.POST:
        form = ImportEvent(request.POST,request.FILES)
        if form.is_valid():
            data = request.FILES['file'].read()
            cal = Calendar.from_ical(data)
            made = []
            for component in cal.walk():
                if component.name == "VEVENT" and component.get('summary') not in made:
                    made.append(component.get('summary'))
                    event = Event.objects.create(   title = component.get('summary'),
                                                    start = component.decoded('dtstart'),
                                                    end = component.decoded('dtend'),
                                                    calendar = form.cleaned_data['calendar'], 
                                                    color_event = random_pastel(),
                                                    end_recurring_period = component.get('rrule').get('until')[0],
                                                    rule = create_rule(component.get('summary'), component.get('rrule').get('BYDAY')),      
                                                ) 
                    create_class_from_event(event)
            return redirect('/class/{}'.format(made[0]))
    return render(request, "notes/import_class.html",{'form': ImportEvent})
# delete a class
def delete_class(request, classid):
    a_class = Class.objects.get(pk=classid)
    a_event = a_class.calendar_event
    a_class.delete()
    a_event.delete()
    # redirect to the home page
    return redirect('/')
# change a class's color
def edit_class(request, classid):
    obj = get_object_or_404(Class, id=classid)
    event = obj.calendar_event

    if request.method == "POST":
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            
            hue = form.cleaned_data["color"]
            event.color_event = hue_to_pastel(hue)
            
            event.save()

            obj.name = event.title
            obj.save()
            
            return redirect(f'/class/{event.title}')

    else:
        hue = hex_to_hue(event.color_event)
        form = EditEventForm(instance=event, hue=hue)

    return render(request, "notes/edit_class.html", {"form": form, "classid": classid})
# create a rule that dictates what days a class occurs on
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
# make a class for a given event
def create_class_from_event(event):
    class_name = event.title
    class_object = Class.objects.create(name=class_name, calendar_event=event)
    class_object.save() 
# translater between api calendar and visual calendar    
def occurrences(request):
    """
    ?calendar_slug=main-calendar
    &start=2023-07-30T00:00:00-04:00
    &end=2023-09-10T00:00:00-04:00
    
    start=2023-07-30T00:00:00Z
    &end=2023-09-10T00:00:00Z
    &timeZone=UTC
    
    America%2FNew_York
    &timeZone=UTC'
    """
    
    start = request.GET.get("start").rstrip('Z')
    end = request.GET.get("end").rstrip('Z')
    timezone = request.GET.get("timeZone")
    calendar_slug = request.GET.get("calendar_slug")
    
    return redirect(f'/schedule/api/occurrences?calendar_slug={calendar_slug}&start={start}&end={end}&timezone={timezone}')