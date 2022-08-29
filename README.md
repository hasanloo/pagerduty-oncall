# Pagerduty Oncall
In the past few organization I have worked, it was a administrative difficulty for individual contorbutors and also managers to manually fetch the data from Pagerduty on monthly basis. This information is usually used in another spreadsheet for oncall compensation.

This script is to automate fetching information from Pagerduty.

## Requirement
You need to create a [general access readonly api key](https://support.pagerduty.com/docs/api-access-keys#generate-a-general-access-rest-api-key) in pagerduty and set the **PAGERDUTY_API_KEY** environment variable with its value. You can rename *.env.sample* file to *.env* and set the value in that file as well.

## Run script
To run the script you need schedule id (the string after # when you browse to your schedule), since and until dates in d/m/y format.

Example:
```
python3 calculate-pagerduty-oncall-script.py "SCHKJHDF" "1/8/2022" "31/8/2022"
```

Example output:
```
User: <a href="https://www.pagerduty.com/users/ABC">User 1</a>
  Total days oncall: 21
  Shifts:
    Start: 2022-08-01T00:00:00+02:00
    End: 2022-08-08T00:00:00+02:00
    Days: 7
    +++++++++++++++++++++++++++++++++++++++++
    Start: 2022-08-10T00:00:00+02:00
    End: 2022-08-17T00:00:00+02:00
    Days: 7
    +++++++++++++++++++++++++++++++++++++++++
    Start: 2022-08-24T00:00:00+02:00
    End: 2022-08-31T00:00:00+02:00
    Days: 7
    +++++++++++++++++++++++++++++++++++++++++
  Extra Hours:
    incident: https://www.pagerduty.com/incidents/SDFSADFAS
    time spent: 2h 30m
    *******************************************
-----------------------------------------------
  User: <a href="https://www.pagerduty.com/users/SDSFS">Use 2</a>
  Total days oncall: 9
  Shifts:
    Start: 2022-08-08T00:00:00+02:00
    End: 2022-08-10T00:00:00+02:00
    Days: 2
    +++++++++++++++++++++++++++++++++++++++++
    Start: 2022-08-17T00:00:00+02:00
    End: 2022-08-24T00:00:00+02:00
    Days: 7
    +++++++++++++++++++++++++++++++++++++++++
  Extra Hours:
-----------------------------------------------
```

## Extra hours
Extra hours are not calculated automatically using the incidents acknowledge by the user. For it to be calculated properly each user need to add a note to the related incident with this format `time spent: 2h 30m`

## Improvements
- Send emails to all participant and also the manager on a monthly basis (manager email can be tagged in the escalation policy)
- Execute the script using cron (or any equivalant cloud setup)
