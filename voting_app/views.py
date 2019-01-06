from django.shortcuts import render
from django.http import JsonResponse
from django.forms.models import model_to_dict

from voting_app.models import Poll, Choice


POLL_DETAIL_FIELDS = ['id', 'name', 'description', 'format_modified']


def get_choices_data(poll_pk):
    poll_instance = Poll.objects.get(pk=poll_pk)
    choices_values = poll_instance.choice_set.all()
    choices_data = list(choices_values.values('text', 'total'))
    return choices_data  


def poll_list(request):
    polls = Poll.objects.all()
    polls_values = polls.values(
        'id', 
        'name', 
        'description', 
        'format_modified'
    )
    data = {
        'results': list(polls_values),
    }

    # add choices
    for poll_data in data['results']:
        poll_data['choices'] = get_choices_data(poll_data['id'])

    return JsonResponse(data)


def poll_detail(request, pk):
    poll = Poll.objects.get(pk=pk)
    data = model_to_dict(poll, fields=POLL_DETAIL_FIELDS)
    data['choices'] = get_choices_data(poll.id)

    return JsonResponse(data)
