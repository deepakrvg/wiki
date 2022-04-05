from django.shortcuts import render
from django.http import HttpResponse
from django import forms

from random import choice
from . import util
import markdown2

class NewSearchForm(forms.Form):
    search = forms.CharField(label="Search",required= False,
    widget= forms.TextInput(attrs={'placeholder':'Search Encyclopedia'}))

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", required=True, 
    widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    textarea = forms.CharField(label="Text Area", required=True, 
    widget=forms.Textarea(attrs={'placeholder':'Text'}))

class EditPageForm(forms.Form):
    title = forms.CharField(label="Title", required=True, widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    textarea = forms.CharField(label="Text Area", required=True, widget=forms.Textarea(attrs={'placeholder':'Text'}))

def index(request):
    form = NewSearchForm(request.GET)
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form":form
    })

def title(request, title):
    form = NewSearchForm(request.GET)
    try:
        text = markdown2.markdown(util.get_entry(title))
        return render(request, "encyclopedia/title.html", {
            "text": text,
            "title": title, 
            "form": form
        })
    except:
        return render(request, "encyclopedia/error.html")

def search(request):
    if request.method == "GET":
        form = NewSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["search"].lower()
            entries = util.list_entries()

            files = [name for name in entries if query in name.lower()]
            if len(files) == 0:
                return HttpResponse("No results found!")
            elif len(files) == 1:
                head = files[0]
                return title(request, head)
            else:
                head = [name for name in files if query == name.lower()]

                if len(head)>0:
                    return title(request, head[0])
                else:
                    return render(request,"encyclopedia/search.html",{
                        "files":files,
                        "form":form
                    })
        return index(request)
    return index(request)

def newpage(request):
    form = NewSearchForm()
    newpageform = NewPageForm()
    if request.method == "POST":
        newpageform = NewPageForm(request.POST)
        if newpageform.is_valid():
            head = newpageform.cleaned_data["title"]
            textarea = newpageform.cleaned_data["textarea"]
            entries = util.list_entries()
            for entry in entries:
                if head.lower() == entry.lower():
                    newpageform = NewPageForm()
                    return HttpResponse("Page already existed!")
            
            util.save_entry(head, textarea)
            return title(request, head)

    return render(request, "encyclopedia/newpage.html", {
        "newpageform": newpageform, 
        "form": form
    })

def edit(request):
    form = NewSearchForm()
    edit_form = EditPageForm()
    head = request.POST.get("edit")
    textarea = util.get_entry(head)
    edit_form = EditPageForm(initial={'title': head, 'textarea': textarea})
    if edit_form.is_valid():
        return render(request, "encyclopedia/editpage.html", {
            "edit_form": edit_form,
            "title": head,
            "form": form
        })
    
    return render(request, "encyclopedia/editpage.html", {
        "edit_form": edit_form,
        "title": head,
        "form": form
    })

def save(request):
    edit_form = EditPageForm(request.POST)
    if edit_form.is_valid():
        head = edit_form.cleaned_data["title"]
        textarea = edit_form.cleaned_data["textarea"]
        util.save_entry(head, textarea)
        return title(request, head)
    
    return render(request, "encyclopedia/editpage.html", {
        "edit_form": edit_form,
        "form": form
    })

def random(request):
    page_title = choice(util.list_entries())
    return title(request, page_title)
