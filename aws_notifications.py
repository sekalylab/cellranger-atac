###                                            -*- Mode: Python -*-
###                                            -*- coding UTF-8 -*-
### aws_notifications.py
### Copyright 2021 RPM Bioinfo Solutions
### Author :  Adam-Nicolas Pelletier
### Last modified On: 2021-11-09
### Version 1.00


import boto3
import botocore
import re




def new_notification(job_id,jobName, date_time, events, sns, ):
	event_pattern = """{\"source\":[\"aws.batch\"],
						\"detail-type\":[\"Batch Job State Change\"],
						\"detail\":{\"jobId\":[\"%s\"],
									\"status\":[\"FAILED\",\"SUCCEEDED\"]}}""" % job_id
	ruleName = "rule-" + jobName
	notification_rule = events.put_rule(
		Name = ruleName, 
		EventPattern = event_pattern, 
		State = "ENABLED", 
		Description = job_id, 
		EventBusName = "default"
		)
	topic = sns.create_topic(
		Name = "job-" + date_time
		)
	topicArn = topic["TopicArn"]
	attributeValue="""{\"Version\":\"2012-10-17\",
						\"Id\":\"__default_policy_ID\",
						\"Statement\":[{\"Sid\":\"__default_statement_ID\",
										\"Effect\":\"Allow\",
										\"Principal\":{\"AWS\":\"*\"},
										\"Action\":[\"SNS:GetTopicAttributes\",
													\"SNS:SetTopicAttributes\",
													\"SNS:AddPermission\",
													\"SNS:RemovePermission\",
													\"SNS:DeleteTopic\",
													\"SNS:Subscribe\",
													\"SNS:ListSubscriptionsByTopic\",
													\"SNS:Publish\",
													\"SNS:Receive\"],
										\"Resource\":\"%s\",
										\"Condition\":{\"StringEquals\":{\"AWS:SourceOwner\":\"943708588556\"}}},
									{\"Sid\":\"AWSEvents_%s_1\",
									\"Effect\":\"Allow\",
									\"Principal\":{\"Service\":\"events.amazonaws.com\"},
									\"Action\":\"sns:Publish\",
									\"Resource\":\"%s\"}]}""" % (topicArn, ruleName, topicArn)
	
	topic_attr = sns.set_topic_attributes(
		TopicArn = topicArn,
		AttributeName = "Policy",
		AttributeValue = attributeValue,
		)
	subs = sns.subscribe(
		TopicArn = topicArn,
		Protocol = "email",
		Endpoint = email )

	return({"rule":notification_rule, "topicArn":topicArn, "topic":topic, "AttributeValue":attribute_value, "policy_number": 1, "date_time":date_time })


def add_notification(notification, job_id,jobName, events, sns):
	# event_pattern = """{\"source\":[\"aws.batch\"],
	# 					\"detail-type\":[\"Batch Job State Change\"],
	# 					\"detail\":{\"jobId\":[\"%s\"],\"status\":[\"FAILED\",\"SUCCEEDED\"]}}""" % job_id
	dict_out = notification
	dict_out["policy_number"] = dict_out["policy_number"] + 1

	ruleName = "rule-" + jobName 

	notification_rule = events.put_rule(
		Name = ruleName, 
		EventPattern = event_pattern, 
		State = "ENABLED", 
		Description = job_id, 
		EventBusName = "default"
		)
	# topic = sns.create_topic(
	# 	Name = "job-" + notification["date_time"]
	# 	)
	oldAttribute = notification_rule["AttributeValue"]
	oldAttribute = re.sub("}]", ",", oldAttribute)
	topicArn = notification["topicArn"]

	attributeValue="""{\"Sid\":\"AWSEvents_%s_$s\",
					\"Effect\":\"Allow\",
					\"Principal\":{\"Service\":\"events.amazonaws.com\"},
					\"Action\":\"sns:Publish\",
					\"Resource\":\"%s\"}]}""" % (ruleName, str(dict_out["policy_number"]),  topicArn)

	dict_out["AttributeValue"] = oldAttribute + attributeValue
	
	topic_attr = sns.set_topic_attributes(
		TopicArn = topicArn,
		AttributeName = "Policy",
		AttributeValue = oldAttribute + attributeValue
		)
	subs = events.put_targets(
			Rule = ruleName,
			Targets = [{
				'Id' : dict_out["policy_number"],
				'Arn' : topicArn
				}]
		)	
	return(dict_out)

