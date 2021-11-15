###                                            -*- Mode: Python -*-
###                                            -*- coding UTF-8 -*-
### aws_notifications.py
### Author :  Adam-Nicolas Pelletier
### Last modified On: 2021-11-09
### Version 1.00


import boto3
import botocore
import re
import json




def new_notification(job_id,jobName, date_time, events, sns, email):
	event_pattern = {"source":["aws.batch"],
						"detail-type":["Batch Job State Change"],
						"detail":{"jobId":[job_id],
								"status":["FAILED","SUCCEEDED"]}}
	ruleName = "rule-" + jobName
	notification_rule = events.put_rule(
		Name = ruleName, 
		EventPattern = json.dumps(event_pattern, indent = 4), 
		State = "ENABLED", 
		Description = job_id, 
		EventBusName = "default"
		)
	topic = sns.create_topic(
		Name = "job-" + date_time
		)
	topicArn = topic["TopicArn"]
	attributeValue= {"Version":"2012-10-17",
					"Id":"__default_policy_ID",
					"Statement":[{	"Sid":"__default_statement_ID", 
									"Effect":"Allow",
									"Principal":{"AWS":"*"},
									"Action":["SNS:GetTopicAttributes",
												"SNS:SetTopicAttributes",
												"SNS:AddPermission",
												"SNS:RemovePermission",
												"SNS:DeleteTopic",
												"SNS:Subscribe",
												"SNS:ListSubscriptionsByTopic",
												"SNS:Publish",
												"SNS:Receive"],
									"Resource":topicArn,
									"Condition":{"StringEquals":{"AWS:SourceOwner":"943708588556"}}},
									{"Sid":"AWSEvents_" + ruleName + "_1",
									 "Effect":"Allow",
									"Principal":{"Service":"events.amazonaws.com"},
									"Action":"sns:Publish",
									"Resource":topicArn}]}
	
	topic_attr = sns.set_topic_attributes(
		TopicArn = topicArn,
		AttributeName = "Policy",
		AttributeValue = json.dumps(attributeValue, indent = 4)
		)
	subs = sns.subscribe(
		TopicArn = topicArn,
		Protocol = "email",
		Endpoint = email )

	return({"rule":notification_rule, "topicArn":topicArn, "topic":topic, "AttributeValue":attributeValue, "policy_number": 1, "date_time":date_time })


def add_notification(notification, job_id,jobName, events, sns):
	event_pattern = {"source":["aws.batch"],
 					"detail-type":["Batch Job State Change"],
					"detail":{"jobId":[job_id],"status":["FAILED","SUCCEEDED"]}} 
	dict_out = notification
	dict_out["policy_number"] = dict_out["policy_number"] + 1

	ruleName = "rule-" + jobName 

	notification_rule = events.put_rule(
		Name = ruleName, 
		EventPattern = json.dumps(event_pattern, indent = 4), 
		State = "ENABLED", 
		Description = job_id, 
		EventBusName = "default"
		)

	oldAttribute = notification["AttributeValue"]

	topicArn = notification["topicArn"]

	new_attributeValue={"Sid":"AWSEvents_" + ruleName + "_1",
					"Effect":"Allow",
					"Principal":{"Service":"events.amazonaws.com"},
					"Action":"sns:Publish",
					"Resource":topicArn}

	oldAttribute["Statement"].append(new_attributeValue)
	dict_out["AttributeValue"] = oldAttribute
	topic_attr = sns.set_topic_attributes(
		TopicArn = topicArn,
		AttributeName = "Policy",
		AttributeValue = json.dumps(dict_out["AttributeValue"], indent = 4)
		)
	subs = events.put_targets(
			Rule = ruleName,
			Targets = [{
				'Id' : "1",
				'Arn' : topicArn
				}]
		)	
	return(dict_out)

