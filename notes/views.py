from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

from icalendar import Calendar
import colorsys, random, math

from .models import Note, Class, Lecture, ArchivedNote, Tag, ToDo
from .forms import AddClass, AddEvent, ImportEvent, EditEventForm, NoteForm


from schedule.models.events import Event, Occurrence
from schedule.models.rules import Rule

# Create your views here.

# handles the note editor page
def editor(request, lectureid):
    # the id of the requested note (0 if none specified which opens a new note)
    noteid = int(request.GET.get('noteid',0))
    # notes a displayed by lecture so finding the correct lecture is needed
    lec = Lecture.objects.get(id=lectureid)
    # the set of all notes for the requested lecture
    note = lec.note_set.all()
    # the set of all archived notes for the requested lecture
    archived_notes = lec.archivednote_set.all()
    # all of the tags
    all_tags = Tag.objects.all()

    # sorting notes
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

    document = None
    if noteid > 0:
        document = Note.objects.get(pk=noteid)

    # if it's a form submission, either create new note or update existing note 
    if request.method == 'POST':
        form = NoteForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            new_tag = form.cleaned_data['new_tag']
            selected_tag = form.cleaned_data['tag']

            delete_tag = request.POST.get('delete_tag')
            selected_tag = request.POST.get('tag')
            new_tag = request.POST.get('new_tag')
            color = request.POST.get('color')
            tag = None
        
            if new_tag:
                tag, created = Tag.objects.get_or_create(name=new_tag)
            elif delete_tag == 'on':
                if document.tag is not None:
                    if selected_tag == document.tag.name:
                        document.tag.delete()
                if not selected_tag:
                    tag = document.tag
                else:
                    tag_deleted = Tag.objects.get(pk=selected_tag)
                    tag_deleted.delete()
                    tag = document.tag
            elif selected_tag:
                tag = Tag.objects.get(pk=selected_tag)

            # if they are changing an existing note update all the fields
            if noteid > 0:
                document = Note.objects.get(pk=noteid) # Change document 
                document.title = title
                document.content = content
                document.color = color
                if tag is not None:
                    document.tag = tag
                else:
                    document.tag = None
                document.save()
            else: 
                document = Note.objects.create(title=title, content=content, lecture=lec, color=color, tag=tag)       
                noteid = document.id
            return redirect('/notes/{}?noteid=%i&sort_by=%s'.format(lectureid) % (noteid, sort_by))
    else:
        if noteid > 0:
            initial_data = {
                'title': document.title,
                'content': document.content,
                'tag': document.tag,
            }
            form = NoteForm(initial=initial_data, instance=document)
        else:
            form = NoteForm()

    form = NoteForm(request.POST or None, instance=document)

    context = {
        'lecture' : lec,
        'noteid' : noteid,
        'note' : note,
        'document' : document,
        'sort_by' : sort_by, 
        'archived_notes' : archived_notes,
        'form': form,
        'all_tags': all_tags,
    }
    return render(request, 'notes/editor.html',context)                 

# send only the classes associated with this account to be displayed on the home page
def home_calendar_view(request):
    if (request.user.is_authenticated):
        all_classes = Class.objects.filter(calendar_event__calendar_id=request.user.profile.calendar.id)
        todos = ToDo.objects.all();

        if request.method == 'POST':
            tdids_str = request.POST.getlist('checkbox_data')
            tdids = []
            for s in tdids_str:
                tdids.append(int(s))
            for td in todos:
                if td.id in tdids:
                    td.completed = True
                else:
                    td.completed = False
                    
                td.save()
        
        context = {
            'classes' : all_classes,
            'ToDos'   : todos,
        }
              
    else:
        context = None
    return render(request, "notes/calendar.html", context)

# find the correct class to display (as well as all other classes of this account for the side bar)
def view_class(request, classid):
    if (request.user.is_authenticated):
        classes = Class.objects.filter(calendar_event__calendar_id=request.user.profile.calendar.id)
        class_instance = Class.objects.get(name=classid)

        lecture_queryset = class_instance.lecture_set.all()
        sort_by = request.GET.get('sort_by', 'latest')  # Default to sorting by latest
        if sort_by == 'latest':
            lecture_queryset = class_instance.lecture_set.order_by('-lecture_number')
        elif sort_by == 'earliest':
            lecture_queryset = class_instance.lecture_set.order_by('lecture_number')
        todos = class_instance.todo_set.all()
        context = {
            'classes' : classes,
            'classid' : class_instance,
            'sort_by' : sort_by,
            'lecture_queryset' : lecture_queryset,
            'ToDos'   : todos
        }
    else:
        context = None
    return render(request, "notes/view-class.html", context)

# creating a new lecture in a specific class
def create_lecture(request):
    # get which class this is for from the request
    classid = request.GET.get('classid',0)
    cls = Class.objects.get(id=classid)
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
    
def outline_view(request, lectureid, noteid):
    lec = Lecture.objects.get(id=lectureid)    
    
    # the set of all notes for the requested lecture
    notes = lec.note_set.all()
    # the set of all archived notes for the requested lecture
    archived_notes = lec.archivednote_set.all()
    
    note = Note.objects.get(pk=noteid)
    
    outline = []
    
    for line in note.content.splitlines():
        if (line[:4] == "<h1>" or 
            line[:4] == "<h2>" or
            line[:4] == "<h3>"):
            new_line = line[:3] + " class=\"subtitle is-" + str(int(line[2]) + 3) + "\"" + line[3:]
            outline.append(new_line)
    
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

    context = {
        'lecture' : lec,
        'note': note,
        'outline' : outline,
        'sort_by' : sort_by,
        'notes' : notes,
        'archived_notes' : archived_notes,
    }
    return render(request, 'notes/outline.html',context)                 

    
# translater between api calendar and visual calendar    
def occurrence_api(request):    
    start = request.GET.get("start").rstrip('Z')
    end = request.GET.get("end").rstrip('Z')
    timezone = request.GET.get("timeZone")
    calendar_slug = request.GET.get("calendar_slug")
    
    return redirect(f'/schedule/api/occurrences?calendar_slug={calendar_slug}&start={start}&end={end}&timezone={timezone}')

def update_note_color(request):
    if request.method == 'POST' and request.is_ajax():
        color = request.POST.get('color', None)
        if color:
            note_id = request.session.get('noteid')  # Change this to your actual method of identifying the note
            if note_id:
                try:
                    note = Note.objects.get(id=note_id)
                    note.color = color
                    note.save()
                    return JsonResponse({'message': 'Note color updated successfully'})
                except Note.DoesNotExist:
                    return JsonResponse({'message': 'Note not found'}, status=404)

    return JsonResponse({'message': 'Invalid request'}, status=400)

def edit_todo(request, classid):

    todoid = int(request.GET.get('todoid',0))

    cls = Class.objects.get(id=classid)

    todo = cls.todo_set.all()

    if request.method == 'POST':
        todoid = int(request.POST.get('tdid',0))
        title = request.POST.get('title')
        description = request.POST.get('description')
        # if they are changing an existing todo update all the fields
        if todoid > 0:
            document = ToDo.objects.get(pk=todoid) # Change document 
            document.title = title
            document.description = description
            document.save()

            return redirect('/todo/{}?todoid=%i'.format(classid) % (todoid))
        else: 
            document = ToDo.objects.create(title=title, description=description, cls=cls, completed=False)

            return redirect('/todo/{}?todoid=%i'.format(classid) % (document.id))

    if todoid > 0:
        document = ToDo.objects.get(pk=todoid)
    else:
        document = ''

    context = {
        'cls' : cls,
        'todoid' : todoid,
        'todo' : todo,
        'document' : document,
    }
    return render(request, 'notes/todo.html',context)  