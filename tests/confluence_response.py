execute_response = [
    { "jobArn": "amazon-resource-name", 
      "jobName": "input_input_0", 
      "jobId": "d90d061b-c16d-4a47-ba25-260727bac56b" }, 
    { "jobArn": "amazon-resource-name", 
      "jobName": "prediagnostics_prediagnostics_0", 
      "jobId": "134ee8b1-0127-4c4e-aa6d-9bfbcd581aa6" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "flpe_geobam_0", 
      "jobId": "1d4b37c6-7dfb-4301-99f0-6181fe3ba124" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "flpe_hivdi_0", 
      "jobId": "1111161b-c16d-4a47-ba25-260727bac56b" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "flpe_metroman_0", 
      "jobId": "2222261b-c16d-4a47-ba25-260727bac56b" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "flpe_momma_0", 
      "jobId": "3333361b-c16d-4a47-ba25-260727bac56b" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "flpe_sad_0", 
      "jobId": "4444461b-c16d-4a47-ba25-260727bac56b" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "integrator_integrator_0", 
      "jobId": "5555561b-c16d-4a47-ba25-260727bac56b" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "consensus_consensus_0", 
      "jobId": "6666661b-c16d-4a47-ba25-260727bac56b" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "postdiagnostics_postdiagnostics_0", 
      "jobId": "7777761b-c16d-4a47-ba25-260727bac56b" },
    { "jobArn": "amazon-resource-name", 
      "jobName": "validation_validation_0", 
      "jobId": "8888861b-c16d-4a47-ba25-260727bac56b" }  
]

execute_expected = [
  "1d4b37c6-7dfb-4301-99f0-6181fe3ba124",
  "1111161b-c16d-4a47-ba25-260727bac56b",
  "2222261b-c16d-4a47-ba25-260727bac56b",
  "3333361b-c16d-4a47-ba25-260727bac56b",
  "4444461b-c16d-4a47-ba25-260727bac56b"
]

describe_response = [
  {
    "jobs" : [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "input_input_0", 
        "jobId": "d90d061b-c16d-4a47-ba25-260727bac56b",
        "status" : "SUBMITTED"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "prediagnostics_prediagnostics_0", 
        "jobId": "134ee8b1-0127-4c4e-aa6d-9bfbcd581aa6",
        "status" : "SUBMITTED"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "flpe_geobam_0", 
        "jobId": "1d4b37c6-7dfb-4301-99f0-6181fe3ba124",
        "status" : "SUBMITTED"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "flpe_hivdi_0", 
        "jobId": "1111161b-c16d-4a47-ba25-260727bac56b",
        "status" : "PENDING"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "flpe_metroman_0", 
        "jobId": "2222261b-c16d-4a47-ba25-260727bac56b",
        "status" : "PENDING"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "flpe_moma_0", 
        "jobId": "3333361b-c16d-4a47-ba25-260727bac56b",
        "status" : "PENDING"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "flpe_sad_0", 
        "jobId": "4444461b-c16d-4a47-ba25-260727bac56b",
        "status" : "STARTING"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "integrator_integrator_0", 
        "jobId": "5555561b-c16d-4a47-ba25-260727bac56b",
        "status" : "STARTING"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "consensus_consensus_0", 
        "jobId": "6666661b-c16d-4a47-ba25-260727bac56b",
        "status" : "STARTING"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "postdiagnostics_postdiagnostics_0", 
        "jobId": "7777761b-c16d-4a47-ba25-260727bac56b",
        "status" : "RUNNING"
      }
    ]
  },
  {
    "jobs": [
      {
        "jobArn": "amazon-resource-name", 
        "jobName": "validation_validation_0", 
        "jobId": "8888861b-c16d-4a47-ba25-260727bac56b",
        "status" : "RUNNING"
      }
    ]
  },
]

error_response = {
    'Error': {
        'Code': 'SomeServiceException',
        'Message': 'Details/context around the exception or error'
    },
    'ResponseMetadata': {
        'RequestId': '1234567890ABCDEF',
        'HostId': 'host ID data will appear here as a hash',
        'HTTPStatusCode': 400,
        'HTTPHeaders': {'header metadata key/values will appear here'},
        'RetryAttempts': 0
    }
}
