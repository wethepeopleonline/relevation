# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from judgementapp.models import *

def index(request):
    queries = Query.objects.order_by('qId')
    output = ', '.join([q.text for q in queries])

    template = loader.get_template('judgementapp/index.html')
    context = Context({
        'queries': queries,
    })
    return HttpResponse(template.render(context))


def query_list(request):
    queries = Query.objects.order_by('qId')

    template = loader.get_template('judgementapp/query_list.html')
    context = Context({
        'queries': queries,
    })

    return render_to_response('judgementapp/query_list.html', { 'queries': queries}, context_instance=RequestContext(request))

def query(request, qId):
    query = Query.objects.get(qId=qId)
    judgements = Judgement.objects.filter(query=query.id)

    if "difficulty" in request.POST:
        query.difficulty = int(request.POST['difficulty'])
        if "comment" in request.POST:
            query.comment = request.POST['comment']
        query.save()

    return render_to_response('judgementapp/query.html', {'query': query, 'judgements': judgements}, 
        context_instance=RequestContext(request))


def document(request, qId, docId):
    document = Document.objects.get(docId=docId)
    query = Query.objects.get(qId=qId)
    judgement = Judgement.objects.filter(query=query.id, document=document.id)[0]

    prev = None
    try:
        prev = Judgement.objects.filter(query=query.id).get(id=judgement.id-1)
    except:
        pass

    next = None
    try:
        next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
    except:
        pass

    content = document.get_content()

    return render_to_response('judgementapp/document.html', {'document': document, 'query': query, 'judgement': judgement, 
        'next': next, 'prev': prev, 'content': content.strip()}, context_instance=RequestContext(request))

def judge(request, qId, docId):
    query = get_object_or_404(Query, qId=qId)
    document = get_object_or_404(Document, docId=docId)
    relevance = request.POST['relevance']
    comment = request.POST['comment']

    judgement, created = Judgement.objects.get_or_create(query=query.id, document=document.id)
    judgement.relevance = int(relevance)
    if comment != 'Comment':
        judgement.comment = comment
    judgement.save()

    


    next = None
    try:
        next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
        if 'next' in request.POST:
            document = next.document
            judgement = next
            next = Judgement.objects.filter(query=query.id).get(id=judgement.id+1)
    except:
        pass

    prev = None
    try:
        prev = Judgement.objects.filter(query=query.id).get(id=judgement.id-1)
    except:
        pass

    content = document.get_content()

    return render_to_response('judgementapp/document.html', {'query':query, 'document': document, 'judgement': judgement, 
        'next': next, 'prev': prev, 'content': content.strip()}, RequestContext(request))

def upload(request):
    context = {}
    if 'queryFile' in request.FILES:
        f = request.FILES['queryFile']

        qryCount = 0
        for query in f:
            qid, txt = query.split("\t", 1)
            qryCount = qryCount + 1
            query = Query(qId=qid,text=txt)
            query.save()
        context['queries'] = qryCount

    if 'resultsFile' in request.FILES:
        f = request.FILES['resultsFile']

        docCount = 0
        for result in f:
            qid, z, doc, rank, score, desc = result.split()
            docCount = docCount + 1

            
            document, created = Document.objects.get_or_create(docId=doc)
            document.text = "TBA"

            query = Query.objects.get(qId=qid)
            document.save()

            judgement = Judgement()
            judgement.query = query
            judgement.document = document
            judgement.relevance = -1
            
            judgement.save()
                
        context['results'] = docCount

    return render_to_response('judgementapp/upload.html', context)







