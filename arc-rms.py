#!/usr/bin/env python3
import csv
import collections
import tkinter
from tkinter import filedialog, messagebox
import os
import sys
import traceback
import requests


API_URL = 'https://rms.arc.gov.au/RMS/Report/ResearchOfficeAPI/{report_name}/'
API_KEY_FILENAME = '.rms-api-key'


def download_report(report_name, scheme_round, api_key):
    params = [
        ('schemeRound', scheme_round),
        ('apiKey', api_key)
    ]
    response = requests.get(API_URL.format(report_name=report_name),
                            params=params)
    response.raise_for_status()
    response_json = response.json()
    status = response_json.get('status')
    if status != 'success':
        if status == 'fail':
            raise ValueError('Report failed. Reason: %s' %
                             response_json.get('data'))
        elif status == 'error':
            raise ValueError('We experienced an error. Reason: %s' %
                             response_json.get('message'))
        else:
            raise ValueError('Unknown error occurred.')

    return response_json.get('data')


def get_file_path():
    file_path = filedialog.asksaveasfilename(
        defaultextension='.csv',
        filetypes=(('Comma-Separated Value File', '.csv', "TEXT"),)
    )

    if not file_path:
        messagebox.showerror(
            title='No path chosen',
            message='You must choose a path to save your file.')

    return file_path


def unsuccessful_feedback(scheme_round, api_key, file_path):
    """ Handle UnsuccessfulFeedback Banded and Comments.

    See:
        https://rms.arc.gov.au/RMS/Report/Home/ResearchOfficeAPI#Reports-UnsuccessfulBanded
        https://rms.arc.gov.au/RMS/Report/Home/ResearchOfficeAPI#Reports-UnsuccessfulComment
    """
    data = download_report('UnsuccessfulFeedback', scheme_round, api_key)
    writer = None

    with open(file_path, 'w') as output:
        for item in data:
            project = collections.OrderedDict()
            project['Project ID'] = item.get('projectId')
            project['Proposal Rating Band'] = item.get('proposalRatingBand')

            for rating_band in item.get('criterionRatingBands'):
                project[
                    'Criterion Rating Band (%s)' %
                    rating_band.get('criterionName')] = rating_band.get('band')

            project['Feedback Comments'] = \
                '; '.join(item.get('feedbackComments', ()))

            if not writer:
                writer = csv.DictWriter(output, project.keys())
                writer.writeheader()

            writer.writerow(project)


def ineligible_proposals(scheme_round, api_key, file_path):
    """

    See https://rms.arc.gov.au/RMS/Report/Home/ResearchOfficeAPI#Reports-Ineligible
    Example structure:

    {
        "status":"success",
        "data":[
            {
                "projectId":"XX150200028",
                "comment":"Comment"
            },
        ]
    }
    """
    data = download_report('IneligibleProposals', scheme_round, api_key)
    writer = None

    with open(file_path, 'w') as output:
        for item in data:
            project = collections.OrderedDict()
            project['Project ID'] = item.get('projectId')
            project['Project ID'] = item.get('comment')

            if not writer:
                writer = csv.DictWriter(output, project.keys())
                writer.writeheader()

            writer.writerow(project)


def funding_details_for_successful_proposals(scheme_round,
                                             api_key,
                                             file_path):
    """
    See https://rms.arc.gov.au/RMS/Report/Home/ResearchOfficeAPI#Reports-Success
    """
    data = download_report('FundingDetailsForSuccessfulProposals',
                           scheme_round,
                           api_key)
    writer = None

    with open(file_path, 'w') as output:
        for item in data:
            project = collections.OrderedDict()
            project['Project ID'] = item.get('projectId')
            project['Project Summary'] = item.get('projectSummary')
            project['Special Conditions'] = \
                '; '.join(item.get('specialConditions', ()))

            for period in \
                    item.get('fundingAmountApprovedForEachFinancialYear'):
                project['%s (Financial Year)' %
                        period.get('year')] = period.get('fundingAmount')

            for period in item.get('fundingAmountApprovedForEachCalendarYear'):
                project['%s (Calendar Year)' %
                        period.get('year')] = period.get('fundingAmount')

            awards = \
                item.get('fundingAmountForAwardsApprovedForEachFinancialYear')
            for award in awards:
                for period in awards.get(award):
                    project['%s (%s Financial Year)' %
                            (award, period.get('year'))] = \
                        period.get('fundingAmount')

            awards = \
                item.get('fundingAmountForAwardsApprovedForEachCalendarYear')
            for award in awards:
                for period in awards.get(award):
                    project['%s (%s Calendar Year)' %
                            (award, period.get('year'))] = \
                        period.get('fundingAmount')

            if not writer:
                writer = csv.DictWriter(output, project.keys())
                writer.writeheader()

            writer.writerow(project)


REPORTS = (
    ('UnsuccessfulFeedback', unsuccessful_feedback),
    ('IneligibleProposals', ineligible_proposals),
    ('FundingDetailsForSuccessfulProposals',
     funding_details_for_successful_proposals)
)
REPORTS_DICT = dict(REPORTS)


if __name__ == '__main__':
    root = tkinter.Tk()
    root.wm_title("ARC Research Management System (RMS)")
    root.minsize(400, 400)

    w = tkinter.Label(
        root,
        text="This app downloads and exports\nARC Research Office reports.\n\n")
    w.pack()

    w = tkinter.Label(root, text="Report Type:")
    w.pack()

    report_name = tkinter.StringVar(root)
    report_name.set(REPORTS[0][0])  # default value
    w = tkinter.OptionMenu(root, report_name, *(r[0] for r in REPORTS))
    w.pack()

    scheme_round = tkinter.StringVar(root)
    w = tkinter.Label(root, text="Scheme Round:")
    w.pack()
    w = tkinter.Entry(root, textvariable=scheme_round, width=8)
    w.pack()

    api_key = tkinter.StringVar(root)
    if os.path.exists(API_KEY_FILENAME):
        with open(API_KEY_FILENAME, 'r') as api_key_file:
            key = api_key_file.read()
            if key:
                api_key.set(key.strip())
    w = tkinter.Label(root, text="API Key:")
    w.pack()
    w = tkinter.Entry(root, textvariable=api_key, width=40)
    w.pack()

    def download_export():
        if not report_name.get() or not scheme_round.get() \
                or not api_key.get():
            messagebox.showerror(
                title="Error",
                message="All fields are required.")
            return

        file_path = get_file_path()
        if not file_path:
            return

        # Run the given report!
        try:
            REPORTS_DICT[report_name.get()](
                scheme_round.get(),
                api_key.get(),
                file_path)
            messagebox.showinfo(
                title="Done!",
                message="Download complete! File saved to\n%s" % file_path)
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            message = ''.join(traceback.format_exception(exc_type,
                                                         exc_value,
                                                         exc_traceback))
            messagebox.showerror(
                title="Error",
                message="We experienced an error:\n " + message)

    def save_api_key():
        with open(API_KEY_FILENAME, 'w') as api_key_file:
            key = api_key.get()
            if key:
                api_key_file.write(key.strip())
            messagebox.showinfo(
                title="Done!",
                message="Key saved to file %s" % API_KEY_FILENAME)

    start = tkinter.Button(root, text='Download and export')
    start['command'] = lambda: download_export()
    start.pack()

    save = tkinter.Button(root, text='Save API Key')
    save['command'] = lambda: save_api_key()
    save.pack()

    quit = tkinter.Button(root, text='Quit')
    quit['command'] = lambda: exit()
    quit.pack()

    root.mainloop()
