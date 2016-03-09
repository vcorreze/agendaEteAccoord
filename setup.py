try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(name='agenda',
      version='1.2.0',
      description="",
      long_description="",
      classifiers=[],
      keywords='',
      author='Mathieu Leduc-Hamel',
      author_email="marrakis@gmail.com",
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'babel==2.2.0',
          'bumpversion==0.5.3',
          'django==1.6.5',
          'django-recaptcha==1.0.5',
          'reindent==0.1.1',
          'requests==2.9.1',
          'simplejson==3.8.2',
          'South==1.0.2',
          'twitter==1.17.1',
          'unidecode==0.4.19',
          'vobject==0.9.1',
          'werkzeug==0.11.4'
      ],
      entry_points={
          'django.apps': [
              'agenda = agenda'
          ],
          'console_scripts': [
              'debug = agenda.command:debug'
          ],
      },
  )
