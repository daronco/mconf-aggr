import collections
import logging

from mconf_aggr.webhook.exceptions import InvalidWebhookMessageError, InvalidWebhookEventError


WebhookEvent = collections.namedtuple('WebhookEvent', ['event_type', 'event'])

MeetingCreatedEvent = collections.namedtuple('MeetingCreatedEvent',
                                             [
                                                'server_url',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'name',
                                                'create_time',
                                                'create_date',
                                                'voice_bridge',
                                                'dial_number',
                                                'attendee_pw',
                                                'moderator_pw',
                                                'duration',
                                                'recording',
                                                'max_users',
                                                'is_breakout',
                                                'meta_data'
                                             ])

MeetingEndedEvent = collections.namedtuple('MeetingEndedEvent',
                                           [
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'end_time'
                                           ])

UserJoinedEvent = collections.namedtuple('UserJoinedEvent',
                                         [
                                                'name',
                                                'role',
                                                'internal_user_id',
                                                'external_user_id',
                                                'internal_meeting_id',
                                                'external_meeting_id',
                                                'join_time',
                                                'is_presenter',
                                                'meta_data'
                                         ])


UserLeftEvent = collections.namedtuple('UserLeftEvent',
                                       [
                                                'internal_user_id',
                                                'external_user_id',
                                                'internal_meeting_id',
                                                'external_meeting_id',
                                                'leave_time',
                                                'meta_data'
                                       ])

UserVoiceEnabledEvent = collections.namedtuple('UserVoiceEnabledEvent',
                                               [
                                                'internal_user_id',
                                                'external_user_id',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'has_joined_voice',
                                                'is_listening_only',
                                                'event_name'
                                               ])

UserEvent = collections.namedtuple('UserEvent',
                                   [
                                                'internal_user_id',
                                                'external_user_id',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'event_name'
                                   ])


RapPublishEndedEvent = collections.namedtuple('RapPublishEndedEvent',
                                              [
                                                'name',
                                                'is_breakout',
                                                'start_time'
                                                'end_time',
                                                'size',
                                                'raw_size',
                                                'meta_data',
                                                'playback',
                                                'download',
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'current_step'
                                              ])


RapEvent = collections.namedtuple('RapEvent',
                                  [
                                                'external_meeting_id',
                                                'internal_meeting_id',
                                                'current_step'
                                  ])


def map_webhook_event(event):
    logger = logging.getLogger(__name__)

    try:
        event_type = event["data"]["id"]
    except (KeyError, TypeError) as err:
        logger.warn("Webhook message dos not contain a valid id: {}".format(err))
        raise InvalidWebhookMessageError("Webhook message dos not contain a valid id")

    if event_type == "meeting-created":
        mapped_event = _map_create_event(event, event_type)

    elif event_type == "meeting-ended":
        mapped_event = _map_end_event(event, event_type)

    elif event_type == "user-joined":
        mapped_event = _map_user_joined_event(event, event_type)

    elif event_type == "user-left":
        mapped_event = _map_user_left_event(event, event_type)

    elif event_type == "user-audio-voice-enabled":
        mapped_event = _map_user_voice_enabled_event(event, event_type)

    elif (event_type in ["user-audio-voice-enabled", "user-audio-voice-disabled",
                "user-audio-listen-only-enabled", "user-audio-listen-only-disabled",
                "user-cam-broadcast-start", "user-cam-broadcast-end",
                "user-presenter-assigned", "user-presenter-unassigned"]):
        mapped_event = _map_user_event(event, event_type)

    elif event_type == "rap-publish-ended":
        mapped_event = map_rap_publish_ended_event(event, event_type)

    elif(event_type in ["rap-archive-started", "rap-archive-ended",
                "rap-sanity-started", "rap-sanity-ended",
                "rap-post-archive-started", "rap-post-archive-ended",
                "rap-process-started", "rap-process-ended",
                "rap-post-process-started", "rap-post-process-ended",
                "rap-publish-started", "rap-post-publish-started",
                "rap-post-publish-ended"]):
        mapped_event = _map_rap_event(event, event_type)

    else:
        logger.warn("Webhook event id is not valid: '{}'".format(event_type))
        raise InvalidWebhookEventError("Webhook event '{}' is not valid".format(event_type))

    return mapped_event


def _map_create_event(event, event_type):
    create_event = MeetingCreatedEvent(
                       server_url=event.get("server_url", ""),
                       external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                       internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                       name=_get_nested(event, ["data", "attributes", "meeting", "name"], ""),
                       create_time=_get_nested(event, ["data", "attributes", "meeting", "create-time"], ""),
                       create_date=_get_nested(event, ["data", "attributes", "meeting", "create-date"], ""),
                       voice_bridge=_get_nested(event, ["data", "attributes", "meeting", "voice-bridge"], ""),
                       dial_number=_get_nested(event, ["data", "attributes", "meeting", "dial-number"], ""),
                       attendee_pw=_get_nested(event, ["data", "attributes", "meeting", "attendee-pw"], ""),
                       moderator_pw=_get_nested(event, ["data", "attributes", "meeting", "moderator-pass"], ""),
                       duration=_get_nested(event, ["data", "attributes", "meeting", "duration"], ""),
                       recording=_get_nested(event, ["data", "attributes", "meeting", "recording"], False),
                       max_users=_get_nested(event, ["data", "attributes", "meeting", "max-users"], ""),
                       is_breakout=_get_nested(event, ["data", "attributes", "meeting", "is-breakout"], False),
                       meta_data=_get_nested(event, ["data", "attributes", "meeting", "metadata"], {}))

    webhook_event = WebhookEvent(event_type, create_event)

    return webhook_event


def _map_end_event(event, event_type):
    end_event = MeetingEndedEvent(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    end_time=_get_nested(event, ["data", "event", "ts"], ""))

    webhook_event = WebhookEvent(event_type, end_event)

    return webhook_event


def _map_user_joined_event(event, event_type):
    user_event = UserJoinedEvent(
                     name=_get_nested(event, ["data", "attributes", "user", "name"], ""),
                     role=_get_nested(event, ["data", "attributes", "user", "role"], ""),
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     join_time=_get_nested(event, ["data", "event", "ts"], ""),
                     is_presenter=_get_nested(event, ["data", "attributes", "user", "presenter"], True),
                     meta_data=_get_nested(event, ["data", "attributes", "user", "metadata"], {}))

    webhook_event = WebhookEvent(event_type, user_event)

    return webhook_event

def _map_user_left_event(event, event_type):
    user_event = UserLeftEvent(
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     leave_time=_get_nested(event, ["data", "event", "ts"], ""),
                     meta_data=_get_nested(event, ["data", "attributes", "user", "metadata"], {}))

    webhook_event = WebhookEvent(event_type, user_event)

    return webhook_event

def _map_user_voice_enabled_event(event, event_type):
    user_event = UserVoiceEnabledEvent(
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     has_joined_voice=_get_nested(event, ["data", "attributes", "user", "sharing-mic"], True),
                     is_listening_only=_get_nested(event, ["data", "attributes", "user", "listening_only"], True),
                     event_name=event_type)

    webhook_event = WebhookEvent(event_type, user_event)

    return webhook_event

def _map_user_event(event, event_type):
    user_event = UserEvent(
                     internal_user_id=_get_nested(event, ["data", "attributes", "user", "internal-user-id"], ""),
                     external_user_id=_get_nested(event, ["data", "attributes", "user", "external-user-id"], ""),
                     external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                     internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                     event_name=event_type)

    webhook_event = WebhookEvent(event_type, user_event)

    return webhook_event


def _map_rap_publish_ended_event(event, event_type):
    rap_event = RapPublishEndedEvent(
                    name=_get_nested(event, ["data", "attributes", "recording", "name"], ""),
                    is_breakout=_get_nested(event, ["data", "attributes", "recording", "isBreakout"], ""),
                    start_time=_get_nested(event, ["data", "attributes", "recording", "startTime"], ""),
                    end_time=_get_nested(event, ["data", "attributes", "recording", "endTime"], ""),
                    size=_get_nested(event, ["data", "attributes", "recording", "size"], ""),
                    raw_size=_get_nested(event, ["data", "attributes", "recording", "rawSize"], ""),
                    meta_data=_get_nested(event, ["data", "attributes", "recording", "metadata"], {}),
                    playback=_get_nested(event, ["data", "attributes", "recording", "playback"], ""),
                    download=_get_nested(event, ["data", "attributes", "recording", "download"], ""),
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    current_step=event_type)

    webhook_event = WebhookEvent(event_type, rap_event)

    return webhook_event


def _map_rap_event(event, event_type):
    rap_event = RapEvent(
                    external_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "external-meeting-id"], ""),
                    internal_meeting_id=_get_nested(event, ["data", "attributes", "meeting", "internal-meeting-id"], ""),
                    current_step=event_type)

    webhook_event = WebhookEvent(event_type, rap_event)

    return webhook_event


def _get_nested(d, keys, default):
    for k in keys:
        if k not in d:
            return default
        d = d[k]

    return d
