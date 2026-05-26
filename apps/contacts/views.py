import csv
import io
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Contact, ContactGroup


def contact_list(request):
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    group_filter = request.GET.get('group', '')

    contacts = Contact.objects.all()
    if query:
        contacts = contacts.filter(Q(name__icontains=query) | Q(phone__icontains=query))
    if group_filter:
        contacts = contacts.filter(groups__id=group_filter)

    paginator = Paginator(contacts, 25)
    contacts_page = paginator.get_page(page)

    groups = ContactGroup.objects.all()
    total = Contact.objects.count()
    active = Contact.objects.filter(is_active=True).count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = []
        for c in contacts_page:
            data.append({
                'id': c.id,
                'name': c.name,
                'phone': c.phone,
                'groups': [g.name for g in c.groups.all()],
                'is_active': c.is_active,
                'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({
            'contacts': data,
            'total': total,
            'active': active,
            'page': contacts_page.number,
            'num_pages': paginator.num_pages,
            'has_next': contacts_page.has_next(),
            'has_prev': contacts_page.has_previous(),
        })

    return render(request, 'contacts.html', {
        'contacts': contacts_page,
        'groups': groups,
        'total': total,
        'active': active,
        'query': query,
    })


def contact_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        group_ids = request.POST.getlist('groups')
        is_active = request.POST.get('is_active') == 'on'

        if not name or not phone:
            return JsonResponse({'error': 'Name and phone are required.'}, status=400)

        if Contact.objects.filter(phone=phone).exists():
            return JsonResponse({'error': 'Phone number already exists.'}, status=400)

        contact = Contact.objects.create(name=name, phone=phone, is_active=is_active)
        if group_ids:
            contact.groups.set(ContactGroup.objects.filter(id__in=group_ids))
        return JsonResponse({'success': True, 'contact': {
            'id': contact.id, 'name': contact.name, 'phone': contact.phone,
            'groups': [g.name for g in contact.groups.all()],
            'is_active': contact.is_active,
            'created_at': contact.created_at.strftime('%Y-%m-%d %H:%M'),
        }})

    groups = ContactGroup.objects.all()
    return render(request, 'contacts.html', {'groups': groups, 'show_add_form': True})


def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.name = request.POST.get('name', contact.name).strip()
        phone = request.POST.get('phone', '').strip()
        if phone and phone != contact.phone:
            if Contact.objects.filter(phone=phone).exclude(pk=pk).exists():
                return JsonResponse({'error': 'Phone number already exists.'}, status=400)
            contact.phone = phone
        contact.is_active = request.POST.get('is_active') == 'on'
        contact.save()
        group_ids = request.POST.getlist('groups')
        contact.groups.set(ContactGroup.objects.filter(id__in=group_ids))
        return JsonResponse({'success': True, 'contact': {
            'id': contact.id, 'name': contact.name, 'phone': contact.phone,
            'groups': [g.name for g in contact.groups.all()],
            'is_active': contact.is_active,
            'created_at': contact.created_at.strftime('%Y-%m-%d %H:%M'),
        }})

    return JsonResponse({'contact': {
        'id': contact.id, 'name': contact.name, 'phone': contact.phone,
        'groups': list(contact.groups.values_list('id', flat=True)),
        'is_active': contact.is_active,
    }})


def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return JsonResponse({'success': True})


@require_POST
def contact_bulk_delete(request):
    ids = json.loads(request.body).get('ids', [])
    Contact.objects.filter(id__in=ids).delete()
    return JsonResponse({'success': True, 'deleted': len(ids)})


def contact_import_csv(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file uploaded.'}, status=400)

        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        imported = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            name = row.get('name', '').strip()
            phone = row.get('phone', '').strip()
            if not name or not phone:
                errors.append(f'Row {row_num}: missing name or phone')
                continue
            try:
                Contact.objects.get_or_create(name=name, phone=phone)
                imported += 1
            except Exception as e:
                errors.append(f'Row {row_num}: {str(e)}')

        return JsonResponse({'success': True, 'imported': imported, 'errors': errors})

    return render(request, 'contacts.html', {'show_csv_import': True})


def contact_export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
    writer = csv.writer(response)
    writer.writerow(['name', 'phone', 'groups', 'is_active'])

    for contact in Contact.objects.all():
        writer.writerow([
            contact.name,
            contact.phone,
            ', '.join(contact.groups.values_list('name', flat=True)),
            contact.is_active,
        ])

    return response


def group_list(request):
    groups = ContactGroup.objects.all()
    data = [{'id': g.id, 'name': g.name, 'description': g.description,
             'contact_count': g.contact_set.count(), 'created_at': g.created_at.strftime('%Y-%m-%d')}
            for g in groups]
    return JsonResponse({'groups': data})


def group_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            return JsonResponse({'error': 'Name is required.'}, status=400)
        group = ContactGroup.objects.create(name=name, description=description)
        return JsonResponse({'success': True, 'group': {
            'id': group.id, 'name': group.name, 'description': group.description,
            'contact_count': 0, 'created_at': group.created_at.strftime('%Y-%m-%d'),
        }})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def group_edit(request, pk):
    group = get_object_or_404(ContactGroup, pk=pk)
    if request.method == 'POST':
        group.name = request.POST.get('name', group.name).strip()
        group.description = request.POST.get('description', group.description).strip()
        group.save()
        return JsonResponse({'success': True, 'group': {
            'id': group.id, 'name': group.name, 'description': group.description,
            'contact_count': group.contact_set.count(),
        }})
    return JsonResponse({'group': {'id': group.id, 'name': group.name, 'description': group.description}})


def group_delete(request, pk):
    group = get_object_or_404(ContactGroup, pk=pk)
    group.delete()
    return JsonResponse({'success': True})
