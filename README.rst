ARC Research Office Report Downloader
=====================================

Does your Research Office need the ability to download reports from the
Australian Research Council (ARC) in a format that's not JSON and actually
human readable and usable)?  Here's your answer -- a small Python application
that helps with this, downloading the RMS reports from
https://rms.arc.gov.au/RMS and exporting them as a flat CSV file.

It's easy to use, simply start the application, enter your API key (provided
on the RMS site), select the report to run and enter your scheme round.  Press
the download button, choose a location to save your CSV (Excel compatible) and
that's it.  Any errors that occur will be show accordingly.


.. note:: This was built according to the API specifications at 2 November
   2015.  Any later changes may break how this application works.


Use
---

Downloads are available on the `Wiki
<https://github.com/jcu-eresearch/arc-research-office-downloader/wiki>`_.
Only limited builds are available.


Building
--------

This build process (using PyInstaller) works on all platforms.  Building the
project requires Python 3.x and has been tested with 3.4 and 3.5.  Once built,
the project is self-contained.

#. Install `Python 3.x <https://python.org>`_ and `setuptools
   <https://pypi.python.org/pypi/setuptools>`_.

#. Clone this repo using Git::

       git clone https://github.com/jcu-eresearch/arc-research-office-downloader.git

#. Open a terminal, ``cd`` to the repo directory and install the package and
   dependencies::

       cd arc-research-office-downloader
       python install setup.py

#. Build!

   ::
   
       pyinstaller --onefile --nowindowed arc_reports.py

#. Use or distribute the single file within ``dist/`` -- Python is not
   required.  On Windows, you'll be required to install the `Visual C++
   Redistributable
   <https://www.microsoft.com/en-us/download/details.aspx?id=48145>`_.

