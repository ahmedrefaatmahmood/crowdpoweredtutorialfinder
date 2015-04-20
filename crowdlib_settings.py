#!/usr/local/bin/python2.9
from crowdlib import settings as cls
import os
#SERVICE TYPE
cls.service_type = "sandbox"

#AWS ACCOUNT INFO
cls.aws_account_id = "AKIAJI2RF7CJXQAR2S7A"
cls.aws_account_key= "tBIlLLN+S7kQWWex0SMJmU863A1DczLwbYqO9la3"

#DIRECTORY FOR CROWDLIB DATABASE
cls.db_dir = os.path.abspath(os.path.expanduser("~/.crowdlib_data/"))

#DEFAULT PARAMETERS used when creating HITs
cls.default_autopay_delay          = 60*60*48 #48 HOURS
cls.default_reward                 = 0.01
cls.default_lifetime               = 60*60*24*7 #ONE WEEK
cls.default_max_assignments        =1
cls.default_time_limit             =60*30    #30 MINUTES
cls.default_qualification_requirements = ()
cls.default_requester_annotation   = ""
cls.default_keywords               =()
