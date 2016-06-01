# coding: utf-8
import urllib, json

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render_to_response, render
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import resolve, reverse
from django.db.models import Count
from django.db.models.signals import post_save
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.dispatch import Signal
from django.core.files import File
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from annoying.decorators import render_to
from forms_builder.forms.signals import form_valid, form_invalid

from crowdataapp import models, forms

@render_to('document_set_index.html')
def document_set_index(request):
    try:
      document_sets = models.DocumentSet.objects.all().order_by('-created_at')
    except:
      document_sets = []
    return { 'document_sets': document_sets, 'header_title': _('Choose one of this project') }

@render_to('document_set_landing.html')
def document_set_view(request, document_set):
    document_set = get_object_or_404(models.DocumentSet,
                                     slug=document_set)
    return {
        'document_set': document_set,
    }

def form_detail(request, slug, template="forms/form_detail.html"):
    form = get_object_or_404(models.DocumentSetForm, slug=slug)
    request_context = RequestContext(request)
    args = (form, request_context, request.POST or None)

    form_for_form = forms.DocumentSetFormForForm(*args)

    if request.method == 'POST':
        if not form_for_form.is_valid():
            form_invalid.send(sender=request, form=form_for_form)
            return HttpResponseBadRequest(json.dumps(form_for_form.errors), content_type='application/json')
        else:
            entry = form_for_form.save()
            form_valid.send(sender=request, form=form_for_form, entry=entry, document_id=request.session['document_id_for_entry'])
            return HttpResponse('')
    return render_to_response(template, { 'form': form }, request_context)

def show_document(request, document_set,document_id):
  document_set = get_object_or_404(models.DocumentSet, slug=document_set)
  document = get_object_or_404(models.Document, id=int(document_id))

  return render(request,
                'show_document.html',
                {
                    'document': document,
                    'document_set': document_set,
                    'head_html': document.document_set.head_html
                })

@render_to('document_set_ranking.html')
def ranking_all(request, document_set, ranking_id):
    document_set = get_object_or_404(models.DocumentSet,
                                slug=document_set)

    ranking = get_object_or_404(models.DocumentSetRankingDefinition,
                              pk=ranking_id)
    return {
            'document_set': document_set,
            'ranking': ranking,
            'ranking_definition_id': ranking_id,
            'page': request.GET.get('page', '1'),
            'search_term': request.REQUEST.get('q'),
            }

@login_required
def transcription_new(request, document_set):
    doc_set = get_object_or_404(models.DocumentSet, slug=document_set)

    document = None
    if request.GET.get('document_id') is not None and request.user.is_staff:
        document = get_object_or_404(models.Document, pk=request.GET.get('document_id'),
                                     document_set=doc_set)
    else:
        candidates = doc_set.get_pending_documents().exclude(form_entries__user=request.user)

        if candidates.count() == 0:
            # TODO Redirect to a message page: "you've gone through all the documents in this project!"
            return render_to_response('no_more_documents.html',
                                      { 'document_set': doc_set },
                                      context_instance=RequestContext(request))

        document = candidates.order_by('?')[0]

    # save the candidate document in the session, for later use
    # in signals.create_entry
    request.session['document_id_for_entry'] = document.id

    return render(request,
                  'transcription_new.html',
                  {
                      'document': document,
                      'head_html': document.document_set.head_html,
                      'pending_documents_count': doc_set.get_pending_documents_count_for_user(request.user),
                      'verified_documents_count': doc_set.get_verified_documents_count_for_user(request.user),
                      'reviewed_documents_count': doc_set.get_reviewed_documents_count_for_user(request.user)
                  })

def autocomplete_field(request, document_set, field_name):
    document_set = get_object_or_404(models.DocumentSet, slug=document_set)
    field = document_set.form.all()[0].fields.get(slug=field_name)

    q = request.REQUEST.get('q')
    if q is not None:
        verified_entries = models.DocumentSetFieldEntry.objects\
            .order_by('value') \
            .filter(field_id=field.pk, verified=True) \
            .extra(
                where=['unaccent(value) ilike %s'], params=["%%%s%%" % q]
            ) \
            .prefetch_related('canonical_label')
    else:
        verified_entries = models.DocumentSetFieldEntry.objects\
            .order_by('value') \
            .filter(field_id=field.pk, verified=True)

    return HttpResponse(json.dumps(map(lambda e: {'value': e.canonical_label.value if e.canonical_label is not None else e.value,
                                                  'tokens': e.value.split(' ') },
                                       verified_entries)),
                        content_type='application/json')

@render_to('login_page.html')
def login(request):
    next_page = request.REQUEST.get(auth.REDIRECT_FIELD_NAME, reverse('document_set_index'))

    if request.user.is_authenticated():
        return HttpResponseRedirect(next_page)

    request.session['redirect_after_login'] = next_page

    user = auth.authenticate(request=request)
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect(reverse('after_login'))
    else:
        return { }

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('document_set_index'))

@login_required
def after_login(request):
    if 'redirect_after_login' in request.session:
        redir = request.session['redirect_after_login']
        del request.session['redirect_after_login']
        return redirect(redir)

    return redirect(reverse('document_set_index'))

@render_to('edit_profile.html')
@login_required
def edit_profile(request):
    """ Profile Edit """
    try:
        profile = models.UserProfile.objects.get(user=request.user)
    except models.UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = forms.UserProfileForm(data=request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            if 'redirect_after_login' in request.session:
                redir = request.session['redirect_after_login']
                del request.session['redirect_after_login']
                return redirect(redir)
            else:
                return redirect(reverse('edit_profile'))
    else:
        form = forms.UserProfileForm(instance=profile)

    return {
        'profile_form': form
    }

@render_to('shutdown.html')
def on_shutdown(request, document_set):
    document_set = get_object_or_404(models.DocumentSet,slug=document_set)
    return {
        'document_set': document_set
        }

@render_to('show_profile.html')
def user_profile(request, document_set, username):
    """ Show User Profile """
    document_set = get_object_or_404(models.DocumentSet, slug=document_set)
    user = get_object_or_404(models.User, username=username)
    organizations = user.organization_set.all()

    try:
      profile = models.UserProfile.objects.get(user=user)
    except models.UserProfile.DoesNotExist:
          profile = models.UserProfile(user=user, name=user.get_full_name())
          profile.save()

    return {
      'document_set' : document_set,
      'profile': profile,
      'full_name' : profile.user.get_full_name(),
      'verified_documents_count': document_set.get_verified_documents_count_for_user(profile.user),
      'verified_documents' : document_set.get_verified_documents_for_user(profile.user),
      'pending_documents_count' : document_set.get_pending_documents_count_for_user(profile.user),
      'pending_documents' : document_set.get_pending_documents_for_user(profile.user),
      'users_ranking_list' : document_set.userboard(profile.user.pk),
      'page': request.GET.get('page', '1'),
      'search_term': request.REQUEST.get('search'),
      'organizations': organizations
    }
@render_to("users_all.html")
def users_all(request, document_set):
    """ Show all ranking of Users """
    document_set = get_object_or_404(models.DocumentSet, slug=document_set)

    return {
            'document_set': document_set,
            'users_list':document_set.leaderboard(),
            'page': request.GET.get('page', '1'),
            'search_term': request.REQUEST.get('search'),
            }

@render_to("organizations_ranking.html")
def document_set_organizations_ranking(request, document_set):
    """ Show all ranking of Organization """
    document_set = get_object_or_404(models.DocumentSet, slug=document_set)
    organizations = document_set.organization_board()

    return {
             'document_set': document_set,
             'page': request.GET.get('page', '1'),
             'organizations': organizations
    }

@render_to("documents_by_entry_value.html")
def documents_by_entry_value(request, document_set, field_id, canon_id, ranking_id):
    """ Show all documents that have a field value in the field_id"""

    canon = get_object_or_404(models.CanonicalFieldEntryLabel, pk=canon_id)
    document_set = get_object_or_404(models.DocumentSet, slug=document_set)

    documents = canon.get_verified_documents_rankings(document_set, ranking_id)

    return {
            'entry_value': canon.value,
            'field_name': models.DocumentSetFormField.objects.get(pk=field_id).label,
            'documents': documents,
            'document_set': document_set,
    }

#/download/{{document_set.slug}}/"
def download_data(request, document_set):
  """ Download all data by format"""

  document_set = get_object_or_404(models.DocumentSet, slug=document_set)

  f = open('/home/vozdata/crowdatastatic/data/%s.csv' % document_set.slug, 'rb')
  data_file = File(f)

  response = HttpResponse(data_file, mimetype='application/csv')
  response['Content-Disposition'] = 'attachment; filename=%s.csv' % document_set.slug

  return response

@login_required
def choose_current_organization(request):
    """ Show which Organizations can be selected """
    organizations = request.user.organization_set.all()
    
    current_organization = None
    
    try:
        user_profile = request.user.get_profile()      
    except models.UserProfile.DoesNotExist:
        user_profile = models.UserProfile(user=request.user, name=request.user.get_full_name())
        user_profile.save()
        
    if user_profile:
        current_organization = user_profile.current_organization

    template = 'choose_current_organization.html' if organizations.count() > 0 else 'without_organization.html'
    return render_to_response(template, {
                                'organizations': organizations, 
                                'current_organization': current_organization,
                                'organization_signup_link': settings.ORGANIZATION_SIGNUP_LINK
                               },
                               context_instance = RequestContext(request))        

@render_to('organizations.html')
def organizations(request):
    organizations = models.Organization.objects.all().order_by('name')

    user_organizations = None
    if request.user and request.user.is_authenticated():
        user_organizations = request.user.organization_set.all()
    
    return {
        'organizations': organizations,
        'user_organizations': user_organizations,
        'organization_signup_link': settings.ORGANIZATION_SIGNUP_LINK
    }

@login_required
def change_current_organization(request):
    response = { 'success': False }
    
    if request.method == 'POST':
        organization_id = request.POST.get('organization_id')
        if organization_id == "none":
            organization_name = "none"
            organization = None
        else:
            organization = get_object_or_404(models.Organization, id=organization_id)
            organization_name = organization.name


        user_profile = request.user.get_profile()
        if user_profile:
            user_profile.current_organization = organization
            user_profile.save()

        response['organization_name'] = organization_name            
        response['success'] = True

    return HttpResponse(json.dumps(response), content_type='application/json')

@render_to('organization_profile.html')
def organization_profile(request, organization_slug):
    """ Show Organization Profile """
    organization = get_object_or_404(models.Organization, slug=organization_slug)

    document_set_filter = request.GET.get('document_set_filter')
    if document_set_filter:
        try:
            document_set_filter = int(document_set_filter)
            document_form_entries_list = organization.documentsetformentry_set.filter(document__document_set__id = document_set_filter)
        except ValueError:
            document_form_entries_list = organization.documentsetformentry_set.all()
    else:
        document_form_entries_list = organization.documentsetformentry_set.all()
        
    document_form_entries_list = document_form_entries_list.filter(document__document_set__published = True)

    document_form_entries_paginator = Paginator(document_form_entries_list, 10)
    reset_filter = request.GET.get('reset_filter')
    if reset_filter:
        organization_page = 1
    else:
        organization_page = request.GET.get('organization_page')
    show_documents = request.GET.get('show_documents')

    try:
        document_form_entries = document_form_entries_paginator.page(organization_page)
    except PageNotAnInteger:
        document_form_entries = document_form_entries_paginator.page(1)
    except EmptyPage:
        document_form_entries = document_form_entries_paginator.page(document_form_entries_paginator.num_pages)

    users_list = organization.users.all()
    users_paginator = Paginator(users_list, 10)        
    user_page = request.GET.get('user_page')
    show_users = request.GET.get('show_users')    
        
    try:
        users = users_paginator.page(user_page)
    except PageNotAnInteger:
        users = users_paginator.page(1)        
    except EmptyPage:
        users = users_paginator.page(users_paginator.num_pages)                

    already_member = None
    documents_without_organization = None
    if request.user and request.user.is_authenticated():
        already_member = organization.users.filter(id = request.user.id).exists()
        documents_without_organization = models.DocumentSetFormEntry.get_user_documents_without_organization(request.user).count()
    
    document_sets = organization.documentsetformentry_set.filter(document__document_set__published = True).values('document__document_set__name', 'document__document_set__id').distinct()
    
    return {
        'organization' : organization,
        'document_form_entries': document_form_entries,
        'already_member': already_member,
        'users': users,
        'show_users': show_users,
        'show_documents': show_documents,
        'documents_without_organization': documents_without_organization,
        'document_sets': document_sets,
        'document_set_filter': document_set_filter
    }

@login_required
def signup_organization(request):
    response = { 'success': False }
    
    if request.method == 'POST':
        organization_slug = request.POST.get('organization_slug')
        organization = get_object_or_404(models.Organization, slug=organization_slug)
        
        organization.users.add(request.user)
        organization.save()

        response['success'] = True

    return HttpResponse(json.dumps(response), content_type='application/json')

@login_required
def signout_organization(request):
    user = request.user
    response = { 'success': False }
    
    if request.method == 'POST':
        organization_slug = request.POST.get('organization_slug')

        if organization_slug:
            organization = user.organization_set.get(slug = organization_slug)
            user.organization_set.remove(organization)

            user_profile = user.get_profile()

            if user_profile.current_organization == organization:
               user_profile.current_organization = None
               user_profile.save()
               

            response['success'] = True

    return HttpResponse(json.dumps(response), content_type='application/json')

@login_required
def assign_docs_to_organization(request):
    user = request.user
    response = { 'success': False }
    
    if request.method == 'POST':
        organization_slug = request.POST.get('organization_slug')
        if organization_slug:
            organization = user.organization_set.get(slug=organization_slug)
            documents_without_organization = models.DocumentSetFormEntry.get_user_documents_without_organization(user)

            if documents_without_organization.count() > 0:
                documents_without_organization.update(organization = organization) 

                response['success'] = True

    return HttpResponse(json.dumps(response), content_type='application/json')

def check_if_doc_set_is_private(doc_set, user):
    if doc_set.is_private and not user.is_staff:
        return HttpResponseRedirect(reverse('document_set_index',kwargs={}))
