===========================
Django-Select2 Introduction
===========================

The documentation is not extremely rich, but the original author's blog post is extremely enlightning:

http://blog.applegrew.com/2012/08/django-select2/


SELECT2
-------

Select2 is an excellent Javascript framework which transforms mundane <select> fields to cool looking and searchable. This is a very handy when there are quite a number of options to select from.

.. image:: http://blog.applegrew.com/wp-content/uploads/2012/08/Screen-Shot-2012-08-05-at-10.06.00-AM.png

Select2 also allows dynamic fetching of options from server via Ajax. Select2′s webpage has a neat demo of this.

.. image:: http://blog.applegrew.com/wp-content/uploads/2012/08/Screen-Shot-2012-08-05-at-10.32.34-AM.png

DJANGO-SELECT2
--------------

Django includes basic select widget, which just generates <select><option>…</option>…</select> tags.
Although their ‘looks’ can be improved using basic CSS, but we hit a usability problem when there are too many options to select from.
This is where Django-Select2 comes into picture.

LIGHT COMPONENTS
================

Django-Select2 includes many widgets suited to various use-cases. Select2Widget and Select2MultipleWidget widgets are suited for scenarios where we have a static list of choices which may not may not be large. They are not meant to be used when the options are too many, say, in thousands. This is because all those options would have to be pre-rendered onto the page and Javascript would be used to search through them. Said that, they are also one the most easiest to use. They are almost drop-in-replacement for Django’s default select widgets.

HEAVY COMPONENTS
================

HeavySelect2Widget and HeavySelect2MultipleWidget widgets are suited for scenarios when the number of options are large and need complex queries (from maybe different sources) to get the options. This dynamic fetching of options undoubtably requires Ajax communication with the server. Django-Select2 includes a helper JS file which is included automatically, so you need not worry about writing any Ajax related JS code. Although on the server side you do need to create a view specifically to respond to the queries. The format of the response is decided by the JS code being used on the client side. The included abstract view – Select2View, will make sure to format the response into the format expected by the helper JS code. Below is a example on how to use it.

.. code:: python

    from django.db.models import Q
    from django_select2 import Select2View, NO_ERR_RESP
    from .models import Employee
    class EmployeeSelect2View(Select2View):
        def check_all_permissions(self, request, *args, **kwargs):
            user = request.user
            if not (user.is_authenticated() and user.has_perms('emp.view_employees')):
                raise PermissionDenied
        def get_results(self, request, term, page, context):
            emps = Employee.objects.filter(
                Q(first_name__icontains=term) | Q(last_name__icontains=term) | Q(emp_no__icontains=term))
            res = [ (emp.id, "%s %s" % (emp.first_name, emp.last_name),)
                for emp in emps ]
            return (NO_ERR_RESP, False, res) # Any error response, Has more results, options list

How many such views you will need depends totally on your use-case. From Django-Select2 there is no restriction on their reuse.
If you feel that writing these views are too much of a hassel then you have an alternate option – sub-class AutoSelect2Field field. In your sub-classed field you need to override security_check(self, request, *args, **kwargs) and get_results(self, request, term, page, context) methods. When your field will be instantiated for the first time, it will register its own instance with AutoResponseView. When the related field is used in the browser, the queries would be directed to AutoResponseView which will direct it to your ‘auto’ field instance. For ‘auto’ fields to work you must use the following code in your urls.py to register the url for AutoResponseView.

.. code:: python

    urlpatterns += patterns("",
        url(r"^select2/", include("django_select2.urls")),
    )

DJANGO-SELECT2 FIELDS
=====================

The following fields are available in Django-Select2.

* Select2ChoiceField – Uses Select2Widget.
* Select2MultipleChoiceField – Uses Select2MultipleWidget.
* HeavySelect2ChoiceField – Uses HeavySelect2Widget.
* HeavySelect2MultipleChoiceField – Uses HeavySelect2MultipleWidget.
* ModelSelect2Field – Uses Select2ChoiceField. It additionally requires queryset argument. It similar to Django’s ModelChoiceField.
* AutoSelect2Field – Uses HeavySelect2ChoiceField. Auto register’s itself with AutoResponseView.
* AutoModelSelect2Field – Similar to AutoSelect2Field, but like ModelSelect2Field, normalizes values to Django model objects.

