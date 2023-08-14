from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from icalendar import Calendar
from datetime import datetime
import colorsys, random, math, pytz

from .models import Note, Class, Lecture, ArchivedNote, Tag, ToDo, ArchivedClass
from .forms import AddClass, AddEvent, ImportEvent, EditEventForm, NoteForm


from schedule.models.calendars import Calendar
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

    document = None
    if noteid > 0:
        document = Note.objects.get(pk=noteid)

    
    # if it's a form submission, either create new note or update existing note 
    if request.method == 'POST':
        # get the necessary data
        title = request.POST.get('title')
        content = request.POST.get('content')

        form = NoteForm(request.POST)
        delete_tag = request.POST.get('delete_tag')
        color = request.POST.get('color')
      
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            new_tag = form.cleaned_data['new_tag']
            tag = form.cleaned_data['tag']

            if delete_tag == 'on' and document and tag:
                tag_to_delete = Tag.objects.get(name=tag)
                document.tag = None
                tag_to_delete.delete()
            
            if new_tag:
                tag, created = Tag.objects.get_or_create(name=new_tag)
                # document.tag = tag
            else: 
                try:
                    tag = Tag.objects.get(name=tag)
                except Tag.DoesNotExist:
                    tag = None

            # updates existing note
            if noteid > 0:
                # document = Note.objects.get(pk=noteid) # Change document 
                document.title = title
                document.content = content
                document.color = color
                document.tag = tag
                document.save()

                return redirect('/notes/{}?noteid=%i&sort_by=%s'.format(lectureid) % (noteid, sort_by))
            # creates new note
            else: 
                document = Note.objects.create(title=title, content=content, lecture=lec, tag=tag, color=color)
                return redirect('/notes/{}?noteid=%i&sort_by=%s'.format(lectureid) % (document.id,sort_by))
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

    context = {
        'lecture' : lec,
        'noteid' : noteid,
        'note' : note,
        'document' : document,
        'sort_by' : sort_by,
        'archived_notes' : archived_notes,
        'form': form,
    }
    return render(request, 'notes/editor.html',context)                 

# send only the classes associated with this account to be displayed on the home page
def home_calendar_view(request):
    #make sure the user is signed in
    if (request.user.is_authenticated):
        #get all the classes associated with this account
        all_classes = Class.objects.filter(calendar_event__calendar_id=request.user.profile.calendar.id)
        todos = ToDo.objects.all();
        archived_classes = ArchivedClass.objects.all()

        #if they submit a change to the to-dos
        if request.method == 'POST':
            #gather all the checked items
            tdids_str = request.POST.getlist('checkbox_data')
            tdids = []
            for s in tdids_str:
                tdids.append(int(s))
            for td in todos:
                #if the to-do should be checked make it
                if td.id in tdids:
                    td.completed = True
                #otherwise uncheck it
                else:
                    td.completed = False
                #save the object    
                td.save()
        
        context = {
            'classes' : all_classes,
            'archived_classes' : archived_classes,
            'ToDos'   : todos,
        }
              
    else:
        context = None
    return render(request, "notes/calendar.html", context)

# find the correct class to display (as well as all other classes of this account for the side bar)
def view_class(request, classid):
    #if the user is signed in
    if (request.user.is_authenticated):
        #gather all their classes as well as the specific class
        classes = Class.objects.filter(calendar_event__calendar_id=request.user.profile.calendar.id)
        class_instance = Class.objects.get(name=classid)
        archived_classes = ArchivedClass.objects.all()

        #get all the lectures for that class
        lecture_queryset = class_instance.lecture_set.all()

        #sort the notes
        sort_by = request.GET.get('sort_by', 'latest')  # Default to sorting by latest
        if sort_by == 'latest':
            lecture_queryset = class_instance.lecture_set.order_by('-lecture_number')
        elif sort_by == 'earliest':
            lecture_queryset = class_instance.lecture_set.order_by('lecture_number')
        #get all the to-do items
        todos = class_instance.todo_set.all()

        context = {
            'classes' : classes,
            'classid' : class_instance,
            'sort_by' : sort_by,
            'lecture_queryset' : lecture_queryset,
            'ToDos'   : todos,
            'archived_classes' : archived_classes,
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
        try:
            occurr = next(generator)
        except:
            messages.info(request, 'There are no more lectures to create!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
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
    messages.info(request, 'New lecture created successfully!')
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
    #if they select to delete 
    if request.method == 'POST':
        sort_by = request.GET.get('sort_by', 'title')
        #get and delete the archived note they want deleted
        note = get_object_or_404(ArchivedNote, id=noteid)
        lectureid = note.lecture.id
        note.delete()
        #return to the notes page
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
    #grab the form information and create the new event
    event_title = form.cleaned_data['title']
    event = Event.objects.create(title=event_title, 
                                 start=form.cleaned_data['start'], 
                                 end=form.cleaned_data['end'], 
                                 calendar=form.cleaned_data['calendar'], 
                                 color_event=form.cleaned_data['color_event'],
                                )
    #create the class off of the event
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
    #when they submit the information
    if request.POST:
        #make the event with the collected data
        form = AddEvent(request.POST,request.FILES)
        #gather the data for the class and make the event
        if form.is_valid():
            event = form.save(commit=False)
            
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]
            
            event.start = datetime.combine(start_date, start_time)
            event.end = datetime.combine(start_date, end_time)
            event.end_recurring_period = end_date            
            
            repeat = form.cleaned_data["repeat"]
            rule = create_rule(event.title, repeat)
            event.rule = rule
            
            hue = form.cleaned_data["color"]
            event.color_event = hue_to_pastel(hue)
            
            event.save()
            #create the class
            create_class_from_event(event)
        title = form.cleaned_data["title"]
        return redirect('/class/{}'.format(title))
    return render(request, "notes/add_event.html",{'form': AddEvent})

# import classes from a file from QUACS
def import_class(request):
    #when they submit
    if request.POST:
        #import the event details from the file using the ImportEvent form
        form = ImportEvent(request.POST,request.FILES)
        #create the classes with the events
        if form.is_valid():
            data = request.FILES['file'].read()
            cal = Calendar.from_ical(data)
            made = []
            for component in cal.walk():
                if component.name == "VEVENT" and component.get('summary') not in made:
                    made.append(component.get('summary'))
                    #create the event using the gathered data
                    event = Event.objects.create(   title = component.get('summary'),
                                                    start = component.decoded('dtstart'),
                                                    end = component.decoded('dtend'),
                                                    calendar = form.cleaned_data['calendar'], 
                                                    color_event = random_pastel(),
                                                    end_recurring_period = component.get('rrule').get('until')[0],
                                                    rule = create_rule(component.get('summary'), component.get('rrule').get('BYDAY')),      
                                                ) 
                    #create the class from the event
                    create_class_from_event(event)
            #redirect into the class page
            return redirect('/class/{}'.format(made[0]))
    return render(request, "notes/import_class.html",{'form': ImportEvent})

# archive a class
def archive_class(request, classid):
    a_class = Class.objects.get(pk=classid)
    a_name = a_class.name
    a_event = a_class.calendar_event
    a_date = a_class.created_at
    
    archived_class = ArchivedClass.objects.create(name=a_name,   
                                                calendar_event=a_event,
                                                created_at=a_date)
    archived_class.save()
    a_class.delete()
    # a_event.delete()

    # redirect to the home page
    return redirect('/')

# restore a class
def restore_class(request, classid):
    a_class = ArchivedClass.objects.get(pk=classid)
    class_object = Class.objects.create(name=a_class.name, 
                                        calendar_event=a_class.calendar_event, 
                                        created_at=a_class.created_at)
    class_object.save()
    a_class.delete()
    # redirect to the home page
    return redirect('/')

# delete a class
def delete_class(request, classid):

    #get the class and event
    a_class = ArchivedClass.objects.get(pk=classid)
    a_event = a_class.calendar_event

    #delete them both
    a_class.delete()
    a_event.delete()
    # redirect to the home page
    return redirect('/')

# change a class's color
def edit_class(request, classid):
    #get the class and event
    obj = get_object_or_404(Class, id=classid)
    event = obj.calendar_event
    #when they submit
    if request.method == "POST":
        #use the EditEventForm to get the edit data
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            #get the event
            event = form.save(commit=False)
            #change the data of the event
            hue = form.cleaned_data["color"]
            event.color_event = hue_to_pastel(hue)
            #save the event and class
            event.save()

            obj.name = event.title
            obj.save()
            #open that class page
            return redirect(f'/class/{event.title}')

    else:
        hue = hex_to_hue(event.color_event)
        form = EditEventForm(instance=event, hue=hue)

    return render(request, "notes/edit_class.html", {"form": form, "classid": classid})

# create a rule that dictates what days a class occurs on
def create_rule(ename, rep):
    #take the corect name and name the repeat pattern
    rrname = (ename + '_repeat')
    desc = rrname
    #set the frequency to weekly
    freq = "WEEKLY"    
    params = "byweekday:"
    #set which days every week it occurs
    for r in rep:
        params += (r + ',')
    #create the rule
    rule = Rule.objects.create(name = rrname,
                               description = desc,
                               frequency = freq,
                               params = params
                              )
    #save the rule
    rule.save()
    return rule

# make a class for a given event
def create_class_from_event(event):
    #class name should match event title
    class_name = event.title
    #create and save the class
    class_object = Class.objects.create(name=class_name, calendar_event=event)
    class_object.save() 
    
# show an outline_view of a note
def outline_view(request, lectureid, noteid):
    #grab the relevant lecture
    lec = Lecture.objects.get(id=lectureid)    
    
    # the set of all notes for the requested lecture
    notes = lec.note_set.all()
    # the set of all archived notes for the requested lecture
    archived_notes = lec.archivednote_set.all()
    #grab the relevant note
    note = Note.objects.get(pk=noteid)
    
    outline = []
    # if any line is a header or sub header add it to the outline view
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

# get set of to-do items to add to the calendar and return as a JSON file
def todo_api(request):
    start = request.GET.get("start").rstrip('Z')
    end = request.GET.get("end").rstrip('Z')
    timezone = request.GET.get("timeZone")
    calendar_slug = request.GET.get("calendar_slug")

    start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

    if timezone and timezone in pytz.common_timezones:
        # make start and end dates aware in given timezone
        current_tz = pytz.timezone(timezone)
        start = current_tz.localize(start)
        end = current_tz.localize(end)

    cal = get_object_or_404(Calendar, slug=calendar_slug)
    
    response_data = []
    
    # finds all of the user's classes and adds the todo items from them
    user_events = Event.objects.filter(calendar=cal)
    for e in user_events:
        user_class = Class.objects.get(calendar_event=e)
        class_color = e.color_event
        
        todo_items = ToDo.objects.filter(cls=user_class)
        for i in todo_items:
            url = reverse('notes:view_class', args=[user_class.name])
            fullcal_obj = {
                "title": i.title,
                "start": i.due_date,
                "color": class_color,
                "url": url,
            }
            response_data.append(fullcal_obj)
        
    return JsonResponse(response_data, safe=False)

# a function to change the color of a notes background
def update_note_color(request):
    #when they submmit
    if request.method == 'POST' and request.is_ajax():
        #get the selected color
        color = request.POST.get('color', None)
        if color:
            note_id = request.session.get('noteid')  # Change this to your actual method of identifying the note
            if note_id:
                try:
                    #get the relevant note and change its color
                    note = Note.objects.get(id=note_id)
                    note.color = color
                    note.save()
                    return JsonResponse({'message': 'Note color updated successfully'})
                except Note.DoesNotExist:
                    return JsonResponse({'message': 'Note not found'}, status=404)

    return JsonResponse({'message': 'Invalid request'}, status=400)

# a view to change (or create a new) to-do
def edit_todo(request, classid):
    #get the relevant to-do (or open up a new one)
    todoid = int(request.GET.get('todoid',0))
    #get the correct class for the to-do
    cls = Class.objects.get(id=classid)
    #get all this class's to-do items to display in the to-do list
    todo = cls.todo_set.all()
    #when they submit
    if request.method == 'POST':
        #grab the data
        todoid = int(request.POST.get('tdid',0))
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        # if they are changing an existing todo update all the fields
        if todoid > 0:
            document = ToDo.objects.get(pk=todoid)
            document.title = title
            document.description = description
            document.due_date = due_date
            document.save()

            return redirect('/todo/{}?todoid=%i'.format(classid) % (todoid))
        #otherwise create a new To-Do
        else: 
            document = ToDo.objects.create(title=title, description=description, due_date=due_date, cls=cls, completed=False)

            return redirect('/todo/{}?todoid=%i'.format(classid) % (document.id))

    formatted_date = ""

    #if a to-do is selected grab its description and format its due date
    if todoid > 0:
        document = ToDo.objects.get(pk=todoid)
        
        # get and format the due date
        formatted_date = document.due_date.strftime("%Y-%m-%d")
    #otherwise make it empty
    else:
        document = ''

    context = {
        'cls' : cls,
        'todoid' : todoid,
        'todo' : todo,
        'document' : document,
    }
    if (formatted_date != ""):
        context["date"] = formatted_date
    return render(request, 'notes/todo.html',context)  

# delete a to-do
def delete_todo(request, todoid):
    #get and delete the todo they want deleted
    todo = get_object_or_404(ToDo, id=todoid)
    cls = todo.cls
    todo.delete()
    #return to the class page
    return redirect(f'/class/{cls}')
