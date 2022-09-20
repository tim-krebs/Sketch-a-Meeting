import logging
import time
import re
import requests
import json 
from . import meetings
logger = logging.getLogger(__name__)
PRINCETON_BASE_URL = https://ma.princetondev.customspeech.ai
# PRINCETON_BASE_URL = https://ma.princetonppe.customspeech.ai
COGSERV_SUB_KEY_HEADER = "Ocp-Apim-Subscription-Key"

class Session:
    REQUEST_ROUTE = "/api/v1/MeetingMinutes/SubmitMeetingMinutesJob"
    RESULT_ROUTE = "/api/v1/MeetingMinutes/GetMeetingMinutesJobResult"
    DEFAULT_TIMEOUT = 60 * 20  # 10 minutes in seconds
    DEFAULT_WAIT = 10  # 10 seconds

    def __init__(self, cs_api_key="YOUR_KEY", session=None, timeout=None, poll_wait=None):
        self.base_url = PRINCETON_BASE_URL
        self.cs_api_key = cs_api_key
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.wait = poll_wait or self.DEFAULT_WAIT

        self.session = session or requests.Session()
    
    def get_chapters(self, meeting):
        job_id = self.request_chapters(meeting)

        start = time.time()
        while (time.time() - start) < self.timeout:
            logger.debug("Trying to retrieve result with {0} seconds remaining until timeout."
                         .format(self.timeout - (time.time() - start)))
            result = self.get_result(job_id)
            if result is not None:
                return result
            else:
                logger.debug("Waiting {0} seconds and retrying...".format(self.wait))
                time.sleep(self.wait)
            
        raise TimeoutError("Chaptering service did not respond in {0} seconds".format(time.time() - start))

    def request_chapters(self, meeting):
        
        # Convert to meeting doc
        cs_meeting_doc = self.get_meeting_for_chapters_extraction(meeting)
        # Request job
        print(self.base_url + self.REQUEST_ROUTE + "*******************************************************************************!!!!")
        response = self.session.post(
            self.base_url + self.REQUEST_ROUTE, 
            json=cs_meeting_doc, 
            headers={COGSERV_SUB_KEY_HEADER: self.cs_api_key})
        
        if response.status_code != 200:
            raise RuntimeError("{0}: {1} {2}".format(response.status_code, response.reason, response.text))
        
        job_id = response.json()
        logger.info("Successfully submitted job.  Job ID: {0}".format(job_id))
        return job_id
    
    def get_result(self, job_id):
        print(self.base_url + self.RESULT_ROUTE + "*******************************************************************************!!!!")
        response = self.session.get(
            self.base_url + self.RESULT_ROUTE, 
            params={'jobId': job_id}, 
            headers={COGSERV_SUB_KEY_HEADER: self.cs_api_key})
        
        if response.status_code in (201, 202):
            # The result is not ready yet
            logger.debug("Status code {0}. Result not ready yet."
                        .format(response.status_code))
            return None
        else:
            if response.status_code == 200:
                # Success!  Print the result.
                return response.json()
            else:
                # Something went wrong
                raise RuntimeError("{0}: {1} {2}".format(response.status_code, response.reason, response.text))
        

    def get_meeting_for_chapters_extraction(self, meeting):
            cognitive_meeting =  {
                "MeetingMetadata": {
                    "meetingId": meeting.meeting_id,
                    "meetingSubject": "Arbitrary meeting provided to the prototype",
                    "ClientApplication": "Summarization prototype test"
                },
                "Options": {},
                "Transcripts": []
            }

            for i, u in enumerate(meeting.utterances):
                if re.search('[a-zA-Z]', u.text):
                    cognitive_meeting["Transcripts"].append({"EntryId": u.utterance_id,
                                                "AttendeeId": u.speaker_name,
                                                "StartTimeTicks": u.start_time * 10000000,
                                                "DurationTicks": (u.end_time - u.start_time) * 10000000,
                                                "AutoRecognizedText": u.text})
                
                

            return cognitive_meeting
