from setuptools import setup, find_packages


setup(name='moz_inapp_pay',
      version='1.0.1',
      description='Utility for working with Mozilla in-app payments.',
      long_description='',
      author='Kumar McMillan',
      author_email='kumar.mcmillan@gmail.com',
      license='BSD',
      url='https://github.com/kumar303/moz_inapp_pay',
      include_package_data=True,
      classifiers=[],
      packages=find_packages(exclude=['tests']),
      install_requires=['PyJWT',
                        'M2Crypto>=0.2.0'])
