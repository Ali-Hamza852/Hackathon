from unittest.mock import MagicMock, patch

import httpx

from app.config import Settings
from app.db.models import BroadcastLog, BroadcastStatus, SchoolSource, Subscriber, SubscriberChannel
from app.time_utils import utc_now
from distribution.whatsapp.bot import on_scores_computed, send_whatsapp_message


def _configured_settings() -> Settings:
    return Settings(
        whatsapp_cloud_api_token="token123",
        whatsapp_phone_number_id="1234567890",
        whatsapp_verify_token="test-verify",
    )


def _unconfigured_settings() -> Settings:
    return Settings(whatsapp_cloud_api_token="", whatsapp_phone_number_id="", whatsapp_verify_token="test-verify")


def _add_subscriber(db_session, school_id, contact="+923001112222"):
    subscriber = Subscriber(
        school_id=school_id,
        channel=SubscriberChannel.whatsapp,
        contact=contact,
        opted_in_at=utc_now(),
    )
    db_session.add(subscriber)
    db_session.commit()
    db_session.refresh(subscriber)
    return subscriber


def test_send_whatsapp_message_success_needs_only_one_attempt():
    response = MagicMock()
    response.raise_for_status.return_value = None

    with patch("distribution.whatsapp.bot.httpx.post", return_value=response) as mock_post:
        result = send_whatsapp_message("+923001234567", "hello", _configured_settings())

    assert result is True
    mock_post.assert_called_once()


def test_send_whatsapp_message_strips_leading_plus_for_graph_api():
    response = MagicMock()
    response.raise_for_status.return_value = None

    with patch("distribution.whatsapp.bot.httpx.post", return_value=response) as mock_post:
        send_whatsapp_message("+923001234567", "hello", _configured_settings())

    sent_body = mock_post.call_args.kwargs["json"]
    assert sent_body["to"] == "923001234567"


def test_send_whatsapp_message_retries_once_then_fails():
    with patch(
        "distribution.whatsapp.bot.httpx.post", side_effect=httpx.ConnectTimeout("boom")
    ) as mock_post:
        result = send_whatsapp_message("+923001234567", "hello", _configured_settings())

    assert result is False
    assert mock_post.call_count == 2


def test_on_scores_computed_writes_sent_log(db_session, seeded_scores):
    subscriber = _add_subscriber(db_session, seeded_scores[0].school_id)
    response = MagicMock()
    response.raise_for_status.return_value = None

    with patch("distribution.whatsapp.bot.httpx.post", return_value=response):
        on_scores_computed(db_session, seeded_scores, _configured_settings())

    logs = db_session.query(BroadcastLog).filter(BroadcastLog.subscriber_id == subscriber.id).all()
    assert len(logs) == 1
    assert logs[0].status == BroadcastStatus.sent
    assert logs[0].score_id == seeded_scores[0].id


def test_on_scores_computed_writes_failed_log(db_session, seeded_scores):
    subscriber = _add_subscriber(db_session, seeded_scores[0].school_id)

    with patch("distribution.whatsapp.bot.httpx.post", side_effect=httpx.ConnectTimeout("boom")):
        on_scores_computed(db_session, seeded_scores, _configured_settings())

    logs = db_session.query(BroadcastLog).filter(BroadcastLog.subscriber_id == subscriber.id).all()
    assert len(logs) == 1
    assert logs[0].status == BroadcastStatus.failed


def test_on_scores_computed_writes_skipped_log_when_not_configured(db_session, seeded_scores):
    subscriber = _add_subscriber(db_session, seeded_scores[0].school_id)

    with patch("distribution.whatsapp.bot.httpx.post") as mock_post:
        on_scores_computed(db_session, seeded_scores, _unconfigured_settings())

    mock_post.assert_not_called()
    logs = db_session.query(BroadcastLog).filter(BroadcastLog.subscriber_id == subscriber.id).all()
    assert len(logs) == 1
    assert logs[0].status == BroadcastStatus.skipped


def test_on_scores_computed_ignores_subscribers_without_a_school(db_session, seeded_scores):
    subscriber = _add_subscriber(db_session, school_id=None, contact="+923009998888")

    on_scores_computed(db_session, seeded_scores, _configured_settings())

    logs = db_session.query(BroadcastLog).filter(BroadcastLog.subscriber_id == subscriber.id).all()
    assert logs == []


def test_on_scores_computed_skips_subscriber_whose_school_was_not_scored(db_session, seeded_scores):
    from app.db.models import School

    unscored_school = School(
        name="Unscored School", zone="Cantt", lat=31.52, lon=74.4, source=SchoolSource.manual
    )
    db_session.add(unscored_school)
    db_session.commit()
    db_session.refresh(unscored_school)

    subscriber = _add_subscriber(db_session, school_id=unscored_school.id)

    on_scores_computed(db_session, seeded_scores, _configured_settings())

    logs = db_session.query(BroadcastLog).filter(BroadcastLog.subscriber_id == subscriber.id).all()
    assert logs == []


def test_on_scores_computed_does_not_resend_after_already_sent(db_session, seeded_scores):
    subscriber = _add_subscriber(db_session, seeded_scores[0].school_id)
    response = MagicMock()
    response.raise_for_status.return_value = None

    with patch("distribution.whatsapp.bot.httpx.post", return_value=response) as mock_post:
        on_scores_computed(db_session, seeded_scores, _configured_settings())
        on_scores_computed(db_session, seeded_scores, _configured_settings())

    assert mock_post.call_count == 1
    logs = db_session.query(BroadcastLog).filter(BroadcastLog.subscriber_id == subscriber.id).all()
    assert len(logs) == 1
    assert logs[0].status == BroadcastStatus.sent


def test_on_scores_computed_retries_after_a_previous_failure(db_session, seeded_scores):
    _add_subscriber(db_session, seeded_scores[0].school_id)

    with patch("distribution.whatsapp.bot.httpx.post", side_effect=httpx.ConnectTimeout("boom")):
        on_scores_computed(db_session, seeded_scores, _configured_settings())

    response = MagicMock()
    response.raise_for_status.return_value = None
    with patch("distribution.whatsapp.bot.httpx.post", return_value=response):
        on_scores_computed(db_session, seeded_scores, _configured_settings())

    logs = db_session.query(BroadcastLog).all()
    assert len(logs) == 2
    assert [log.status for log in logs] == [BroadcastStatus.failed, BroadcastStatus.sent]


def test_on_scores_computed_does_not_duplicate_skipped_log_when_rerun(db_session, seeded_scores):
    subscriber = _add_subscriber(db_session, seeded_scores[0].school_id)

    on_scores_computed(db_session, seeded_scores, _unconfigured_settings())
    on_scores_computed(db_session, seeded_scores, _unconfigured_settings())

    logs = db_session.query(BroadcastLog).filter(BroadcastLog.subscriber_id == subscriber.id).all()
    assert len(logs) == 1
    assert logs[0].status == BroadcastStatus.skipped


def test_on_scores_computed_sends_once_credentials_are_added_after_a_skip(db_session, seeded_scores):
    subscriber = _add_subscriber(db_session, seeded_scores[0].school_id)

    on_scores_computed(db_session, seeded_scores, _unconfigured_settings())

    response = MagicMock()
    response.raise_for_status.return_value = None
    with patch("distribution.whatsapp.bot.httpx.post", return_value=response):
        on_scores_computed(db_session, seeded_scores, _configured_settings())

    logs = (
        db_session.query(BroadcastLog)
        .filter(BroadcastLog.subscriber_id == subscriber.id)
        .order_by(BroadcastLog.id)
        .all()
    )
    assert [log.status for log in logs] == [BroadcastStatus.skipped, BroadcastStatus.sent]


def test_on_scores_computed_keeps_going_after_one_subscriber_fails(db_session, seeded_scores):
    good_subscriber = _add_subscriber(db_session, seeded_scores[0].school_id, contact="+923001112222")
    other_subscriber = _add_subscriber(db_session, seeded_scores[1].school_id, contact="+923003334444")

    response = MagicMock()
    response.raise_for_status.return_value = None

    call_count = {"n": 0}

    def flaky_post(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] <= 2:
            raise httpx.ConnectTimeout("boom")
        return response

    with patch("distribution.whatsapp.bot.httpx.post", side_effect=flaky_post):
        on_scores_computed(db_session, seeded_scores, _configured_settings())

    all_logs = db_session.query(BroadcastLog).all()
    assert len(all_logs) == 2
    statuses = {log.subscriber_id: log.status for log in all_logs}
    assert statuses[good_subscriber.id] == BroadcastStatus.failed
    assert statuses[other_subscriber.id] == BroadcastStatus.sent
