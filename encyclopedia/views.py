import re
from django.http import request
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django import forms
import random


class WikiForm(forms.Form):
    attributes = {'class': "form-control", 'style': 'width:600px;'}
    title = forms.CharField(label='Enter a title', max_length=100, widget=forms.TextInput(attrs=attributes))
    content = forms.CharField(label = "Content", widget=forms.Textarea(attrs=attributes))

from . import util
from markdown2 import Markdown

entry_list = util.list_entries()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": entry_list
    })

def wiki(request, title):
    markdowner = Markdown()
    page_content = util.get_entry(title)

    if page_content == None:
        return render(request, "encyxlopedia/error.html", {
            "error": "Page not found"
        })
    else:
        converted_to_html = markdowner.convert(page_content)
        return render(request, "encyclopedia/wiki.html", {
            "content": converted_to_html,
            "title": title
        })

def search(request):

    if request.method == "POST":
    
        query = request.POST.get("q")
    
        if util.get_entry(query) == None:
            matching_list = []
            for i in entry_list:
                if query.lower() in i.lower():
                    matching_list.append(i)
                
            return render(request, "encyclopedia/search.html", {
                "results": matching_list
            })
    
        else:
            return redirect(f"/wiki/{query}")

def save(request):
    if request.method == "POST":
        form = WikiForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in entry_list:
                return render(request, "encyclopedia/error.html", {
                    "error": "Wiki already exists"
                })
            else:
                util.save_entry(title, content)
                return HttpResponseRedirect(f"/wiki/{title}")
        else:
            return render(request, "encyclopedia/save.html", {
                "form": form
            })

    if request.method == "GET":
        return render(request, "encyclopedia/save.html", {
            "form": WikiForm()
        })

def edit(request, title):
    if request.method == "POST":
        form = WikiForm(request.POST)
        if form.is_valid():
            edited_title = form.cleaned_data["title"]
            edited_content = form.cleaned_data["content"]
            util.save_entry(edited_title, edited_content)
            return HttpResponseRedirect(f"/wiki/{edited_title}")

    
    if request.method == "GET":
        form = WikiForm({'title': title, 'content': util.get_entry(title)})
        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "title": title
        })

def random_page(request):
    return redirect(f"/wiki/{random.choice(entry_list)}")

def error(request):
    return render(request, "encyclopedia/error.html")