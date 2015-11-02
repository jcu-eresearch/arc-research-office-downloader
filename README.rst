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
