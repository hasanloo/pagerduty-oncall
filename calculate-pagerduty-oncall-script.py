import os
import json
import re
from datetime import date, datetime
import string
from pdpyras import APISession
import argparse
from dotenv import load_dotenv
import chevron

load_dotenv()
api_key = os.environ["PAGERDUTY_API_KEY"]
session = APISession(api_key)


def getScheduleOncallUsers(schedule_id, since, until):
    schedule_response = session.get(
        "/schedules/{schedule}?since={since}&until={until}".format(schedule=schedule_id, since=since, until=until))
    schedule = None
    schedule_users = {}
    schedule_escalation_policy_id = None

    if schedule_response.ok:
        schedule = schedule_response.json()["schedule"]
        final_schedule = schedule["final_schedule"]["rendered_schedule_entries"]
        for user in final_schedule:
            user_id = user["user"]["id"]
            # caret user_id in schedule users dict if not exists
            if user_id not in schedule_users:
                schedule_users[user_id] = {
                    "summary": user["user"]["summary"],
                    "html_url": user["user"]["html_url"],
                    "days_oncall": 0,
                    "shifts": [],
                    "extra_hours": []
                }
            # calculate the date differences in days
            # not sure how it will behave if it is not a full day
            days_oncall = datetime.strptime(
                user["end"], "%Y-%m-%dT%H:%M:%S%z") - datetime.strptime(user["start"], "%Y-%m-%dT%H:%M:%S%z")
            schedule_users[user_id]["days_oncall"] += days_oncall.days
            schedule_users[user_id]["shifts"].append(
                {"start": user["start"], "end": user["end"], "days": days_oncall.days})

            # this is an intended bug, we are just getting the first escalation policy
            # in the future we need to conside how to handle if schedule being used in more than one escalation policies
            schedule_escalation_policy_id = schedule["escalation_policies"][0]["id"]

    return schedule_users, schedule_escalation_policy_id


def getEscalationPolicyServices(escalation_policy_id):
    escalation_policy_response = session.get(
        "/escalation_policies/{id}?include%5B%5D=services".format(id=escalation_policy_id))
    escalation_policy = escalation_policy_response.json()["escalation_policy"]
    escalation_policy_services = []
    for service in escalation_policy["services"]:
        escalation_policy_services.append(service["id"])

    return escalation_policy_services


def getIncidentNotes(incident_id):
    incident_notes_response = session.get(
        "/incidents/{id}/notes".format(id=incident_id))
    incident_notes = incident_notes_response.json()["notes"]
    return incident_notes

# def getIncidentAcknowledgedBy(incident_id):
#   acknowledged_by = None
#   incident_log_entries_response = session.get("/incidents/{id}/log_entries".format(id = incident_id))
#   incident_log_entries = incident_notes_response.json()["log_entries"]
#   for log_entry in incident_log_entries:
#     if log_entry["type"] == "acknowledge_log_entry":
#       acknowledged_by = log_entry["agent"]["id"]
#
#   return acknowledged_by


def getIncidentsforServices(service_ids, since, until):
    seperator = ','
    services_id_string = seperator.join(service_ids)

    incidents_response = session.get("/incidents?service_ids%5B%5D={service_ids}&since={since}&until={until}".format(
        service_ids=services_id_string, since=since, until=until))
    incidents = incidents_response.json()["incidents"]
    return incidents


def setUserExtraOnCallHours(escalation_policy_id, users, since, until):
    service_ids = getEscalationPolicyServices(escalation_policy_id)
    incidents = getIncidentsforServices(service_ids, since, until)
    for incident in incidents:
        incident_id = incident["id"]
        incident_notes = getIncidentNotes(incident_id)
        for note in incident_notes:
            note_user_id = note["user"]["id"]
            if note_user_id in users:
                x = re.findall("^time spent:\s*([0-9hm]+)$", note["content"])
                if (x):
                    users[note_user_id]["extra_hours"].append(
                        {"incident": incident["html_url"], "time_spent": x[0]})

def main(schedule, since, until):
    schedule_oncall_users, escalation_policy_id = getScheduleOncallUsers(schedule, since, until)
    if schedule_oncall_users and escalation_policy_id is not None:
        setUserExtraOnCallHours(escalation_policy_id,
                                schedule_oncall_users, since, until)

    with open('template.mustache', 'r') as f:
        print(chevron.render(f, {"users": list(schedule_oncall_users.values())}))

if __name__ == '__main__':
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='PagerDuty on-call calculator script')

    # Required positional argument
    parser.add_argument('schedule', 
                        help='Schedule if to calculate the oncall schedule')
    parser.add_argument('since', 
                        help='start date to calculate oncall schedule. format is d/m/y')
    parser.add_argument('until', 
                        help='end date to calculate oncall schedule. format is d/m/y')

    args = parser.parse_args()
    config = vars(args)

    since = config['since']
    until = config['until'] 
    schedule = config['schedule'] 
  
    main(schedule, since, until)