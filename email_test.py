import csv
import email
from datetime import datetime
from html.parser import HTMLParser
from io import StringIO

import boto3

LOCAL_OUTPUT = "/tmp/test.csv"
MSG_QUERY_CONSTANTS = {
    "msg_sent_datetime": {
        "start": "Sent: ",
        "end": "To: MOTStatistics"
    },
    "fcn":{
        "start": "FCN",
        "end": ", Fatal Traffic"
    },
    "body": {
        "start": "To: MOTStatistics",
        "end": "email or telephone the sender immediately"
    }
}

class html_stripper(HTMLParser):
    """remove HTML specific characters

    Args:
        HTMLParser (_type_): _description_
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, data):
        self.text.write(data)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html: str) -> str:
    """strip tags from html string

    Args:
        html (str): _description_

    Returns:
        str: _description_
    """
    feed_input = html_stripper()
    feed_input.feed(html)
    return feed_input.get_data()


def obtain_email_sent_time(msg_input: str) -> dict:
    """Obtain the email sent time

    Args:
        parsed_msg (str):the parsed email body (after strip_tags)

    Returns:
        dict: email time to be used in csv
    """
    msg_sent_datetime_str = msg_input[
        msg_input.index(MSG_QUERY_CONSTANTS["msg_sent_datetime"]["start"]): 
        msg_input.index(MSG_QUERY_CONSTANTS["msg_sent_datetime"]["end"])
    ]
    msg_sent_datetime = datetime.strptime(msg_sent_datetime_str, "Sent: %A, %d %B %Y %H:%M %p\n")

    msg_sent_time_str = msg_sent_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    msg_sent_date_str = msg_sent_datetime.strftime("%Y-%m-%d")

    return {"time": msg_sent_time_str, "date": msg_sent_date_str}


def obtain_fcn(event_subject: str) -> str:
    """FCN number from the event subject

    Args:
        event_subject (str): _description_

    Returns:
        str: fcn number to be written to csv
    """
    return event_subject[
        event_subject.index(MSG_QUERY_CONSTANTS["fcn"]["start"]): 
        event_subject.index(MSG_QUERY_CONSTANTS["fcn"]["end"])
    ]

def obtain_body(msg_input: str) -> str:
    """Obtain the email body information

    Args:
        msg_input (str): msg input, a long decoded html message from email

    Returns:
        str: body in string to be written to csv
    """
    body_start_loc = msg_input.index(MSG_QUERY_CONSTANTS["body"]["start"])
    body_end_loc = msg_input.index(MSG_QUERY_CONSTANTS["body"]["end"])
    body_str = msg_input[body_start_loc:body_end_loc] + MSG_QUERY_CONSTANTS["body"]["end"].replace("=\n", "")

    # body_str = body_str.replace("=3D=\n=3D", "=3D=3D")

    return body_str.replace("=\n", "").replace("=3D", "=")


def write_csv(msg_datetime: dict, fcn_number: str, body_str: str):

    header = ["SentDateTime", "FCN", "Body", "SentDate"]
    data = [msg_datetime["time"], fcn_number, body_str, msg_datetime["date"]]

    with open(LOCAL_OUTPUT, "w") as fid:
        csv_writer = csv.writer(fid)

        # write the header
        csv_writer.writerow(header)

        # write the data
        csv_writer.writerow(data)


event = {
    'summaryVersion': '2019-07-28',
    'envelope': {
        'mailFrom': {'address': 'S.Zhang@transport.govt.nz'},
        'recipients': [
            {'address': 'fatal-report@fatal-report-test.awsapps.com'}]
    },
    'truncated': False,
    'sender': None,
    'subject': 'Updated Ref: FCN220618/0187, Fatal Traffic Incident Report (TLA - Tauranga)',
    'messageId': 'f23965de-da0c-381a-8b36-3237b669bac5',
    'invocationId': '23f919cdd8636bff084c0c251a1b6d619a1db65e',
    'flowDirection': 'INBOUND'
}


aws_region = "us-east-1"
workmail = boto3.client('workmailmessageflow', region_name=aws_region)
raw_msg = workmail.get_raw_message_content(messageId=event['messageId'])
parsed_msg = email.message_from_bytes(raw_msg['messageContent'].read()).as_string()
parsed_msg = strip_tags(parsed_msg)

# obtain the sent date
msg_datetime = obtain_email_sent_time(parsed_msg)

# obtain FCN
fcn_number = obtain_fcn(event["subject"])

# obtain body
body_str = obtain_body(parsed_msg)

# write csv
write_csv(msg_datetime, fcn_number, body_str)