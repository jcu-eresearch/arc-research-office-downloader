#!/usr/bin/env python3
import requests
import tkinter
from tkinter import filedialog, messagebox


API_URL = 'https://rms.arc.gov.au/RMS/Report/ResearchOfficeAPI/{report_name}/'


def download_report(report_name, scheme_round, api_key):
    params = [
        ('schemeRound', scheme_round),
        ('apiKey', api_key)
    ]
    response = requests.get(API_URL.format(report_name=report_name),
                            params=params)
    response.raise_for_status()
    return response.json().get('data')


def get_file_path():
    # root = tkinter.Tk()
    # root.withdraw()
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

    for item in data:
        project = {
            'Project ID': item.get('projectId'),
            'Proposal Rating Band': item.get('proporalRatingBand'),
        }
        for rating_band in item.get('criterionRatingBands'):
            project[
                'Criterion Rating Band (%s)'
                % rating_band.get('criterionName')] = rating_band.get('band')
        print(project)


def ineligible_proposals(file_path, scheme_round):
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
    pass


def funding_details_for_successful_proposals(file_path, scheme_round):
    """
    See https://rms.arc.gov.au/RMS/Report/Home/ResearchOfficeAPI#Reports-Success
    """
    pass


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
    with open('.api-key', 'r') as api_key_file:
        key = api_key_file.read()
        if key:
            api_key.set(key.strip())
    w = tkinter.Label(root, text="API Key:")
    w.pack()
    w = tkinter.Entry(root, textvariable=api_key, width=40)
    w.pack()

    def callback():
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
        REPORTS_DICT[report_name.get()](
            scheme_round.get(),
            api_key.get(),
            file_path)

        messagebox.showinfo(
            title="Done!",
            message="Download complete! File saved to\n%s" % file_path)

    start = tkinter.Button(root, text='Download and export')
    start['command'] = lambda: callback()
    start.pack()

    quit = tkinter.Button(root, text='Quit')
    quit['command'] = lambda: exit()
    quit.pack()

    root.mainloop()
