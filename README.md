# About cmsplugin_remote_form

[cmsplugin-contact-plus](https://github.com/arteria/cmsplugin-contact-plus/) lets you build forms for your Django CMS project
with exactly the fields you want in the order you want with a minimal effort.

Beside the regular input fields there are "auto" fields, for example to submit the referral page, or additional, hidden values.
The form will be submitted to an email address that is defined per form. This allows to cover a lot of use cases with a single and simple plugin.

cmsplugin-contact-plus is licensed under the MIT License.

## Quickstart

1. To install from [PyPI](https://pypi.python.org/pypi/cmsplugin_remote_form/), in your virtualenv run

	```
	pip install cmsplugin_remote_form
	```

	or to get the latest commit from GitHub,

	```
	pip install -e git+git://github.com/arteria/cmsplugin-contact-plus.git#egg=cmsplugin_remote_form
	```
2. cmsplugin-contact-plus requires https://github.com/iambrandontaylor/django-admin-sortable as dependency. Please have a look at the "Supported Django Versions", "Installation", and "Configuration" sections of the [README](https://github.com/iambrandontaylor/django-admin-sortable/blob/master/README.md).

3. Put ``cmsplugin_remote_form`` and ``adminsortable`` in your INSTALLED_APPS `settings.py` section and verify that the [ADMINS](https://docs.djangoproject.com/en/dev/ref/settings/#admins) setting is set as well.

4. Don't forget to migrate your database.
5. Configure Django's [e-mail settings](https://docs.djangoproject.com/en/1.8/topics/email/#quick-example) appropriately.

## Configuration/Settings

### ``REMOTE_FORM_FROM_EMAIL``

Specify ``DEFAULT_FROM_EMAIL`` (https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email) in your projects settings to send emails from a specific address. Otherwise Django's default  'webmaster@localhost' will be used.

### ``REMOTE_FORM_REPLY_EMAIL_LABEL``

To set the reply-to header for the email automatically, specify ``REMOTE_FORM_REPLY_EMAIL_LABEL`` in your project settings. If the label is "your email" for example, then set ``REMOTE_FORM_REPLY_EMAIL_LABEL='your-email'`` - basically it's the slugified field label that is used to look up the reply-to email address.

### ``REMOTE_FORM_SEND_COPY_TO_REPLY_EMAIL``

To send a carbon copy to the submitter you can set the ``REMOTE_FORM_SEND_COPY_TO_REPLY_EMAIL`` to `True`. If a Field with the label `email` exists this email will be used as Cc Header.

### ``REMOTE_FORM_REQUIRED_CSS_CLASS``

Defines the required CSS class, default is `required`.

### ``CMSPLUGIN_CONTACT_FORM_VALIDATORS``

Specify ``CMSPLUGIN_CONTACT_FORM_VALIDATORS`` in your projects settings to one or more [validator functions](https://docs.djangoproject.com/en/dev/ref/validators/) that are used with the CharFieldWithValidator field. Expected is a list of strings, each string should point a validator function by its full path. For example:

CMSPLUGIN_CONTACT_FORM_VALIDATORS = [
  'myproject.utils.validators.phone_number_validator',
]

### reCAPTCHA

To make the reCAPTCHA field type available to your users, add `'captcha'` to your `INSTALLED_APPS` and define your `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` as described in [django-recaptcha's README](https://github.com/praekelt/django-recaptcha/blob/develop/README.rst). A single reCAPTCHA instance per page is supported.

## Templates

If you are not using the default template settings of Django, make sure that  ``'django.template.loaders.app_directories.Loader'`` is added to the [`TEMPLATES.OPTIONS.loaders`](https://docs.djangoproject.com/en/1.8/ref/templates/upgrading/#the-templates-settings) list in your `settings.py` file. Likewise, if your Django version is < 1.8, make sure that the above-mentioned loader is in your list of [`TEMPLATE_LOADERS`](https://docs.djangoproject.com/en/1.8/ref/settings/#template-loaders).

## Features

- Dynamic form creation
- Migrations included
- Store data in the database
- Multiple languages: currently English and Spanish translations
- reCAPTCHA and simple math captcha
- django CMS 3.0 compatible
- Template support
- Track/pass hidden data
- Signals
- Multiple file and image fields for media upload
- Handle multiple forms located on the same page

## Notes

- Migrations are available with django-cms >= 3.0.6 because we depend on [this](https://github.com/divio/django-cms/blob/3.0.6/cms/migrations_django/0003_auto_20140926_2347.py) migrations file.
- Collecting data is not available if ``from.is_multipart is True`` (= the form has attached files)
- If you render a form field manually, make sure that its name is: `name="{{ field.label|slugify }}"`. This is necessary for the proper validation of the form.

## TODO and planned features .
- Widget support for each field.
- Provide examples and real life case studies
- Formatted email messages, HTML?, .as_p, ?
- Allow to re-use forms on different pages.
- Add optional Honeypot field support.
- Support more Languages
- (Your great feature here)

## Changelog
### Development

Please have a look at the latest commits for the work-in-progress development version.

### 1.2 - Unreleased
- Drop python 2 support
- Drop support for django < 2.2
  