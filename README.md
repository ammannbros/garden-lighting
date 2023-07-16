# Building

* Install *Python 3*
* Check out this repo and run `python setup.py build && python setup.py sdist`.

# Deploy

`scp dist/garden-lighting-0.2.tar.gz pi@ammann.dyn.maxammann.org:`

# Running using virtualenv

* Install *virtualenv* for *Python 3*
* Check out this repo and run `virtualenv dev-env`
* Activate by running `source dev-env/bin/activate`
* Install by running `python setup.py develop`
* Run `garden-lighting`. That's it!
