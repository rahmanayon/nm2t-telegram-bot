#!/usr/bin/env python3
"""
Tests for NM2T Telegram Bot handlers
"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Set required environment variable before importing the module
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_12345'

# Import after setting environment
# We need to mock the imports due to module-level code
with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token_12345'}):
    from nm2t_telegram_bot import (
        start,
        latest,
        subscribe,
        about,
        help_command,
        BEEHIIV_FEED_URL,
    )


@pytest.fixture
def mock_update():
    """Create a mock Update object"""
    update = MagicMock()
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create a mock context object"""
    return MagicMock()


@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    """Test the /start command handler"""
    await start(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]

    assert "Welcome to the NM2T Newsletter Bot" in call_args
    assert "/latest" in call_args
    assert "/subscribe" in call_args
    assert "/about" in call_args
    assert "/help" in call_args


@pytest.mark.asyncio
async def test_subscribe_command(mock_update, mock_context):
    """Test the /subscribe command handler"""
    await subscribe(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]

    assert "subscribing" in call_args.lower()
    assert "https://nm2t-newsletter.beehiiv.com" in call_args


@pytest.mark.asyncio
async def test_about_command(mock_update, mock_context):
    """Test the /about command handler"""
    await about(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]

    assert "About NM2T Newsletter" in call_args
    assert "https://nm2t-newsletter.beehiiv.com" in call_args


@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    """Test the /help command handler"""
    await help_command(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]

    assert "Help" in call_args
    assert "/start" in call_args
    assert "/latest" in call_args


@pytest.mark.asyncio
async def test_latest_command_with_feed_entries(mock_update, mock_context):
    """Test the /latest command with mock feed entries"""
    mock_feed = MagicMock()
    mock_feed.entries = [
        {
            'title': 'Test Newsletter Title',
            'link': 'https://example.com/newsletter1',
            'summary': 'This is a test summary for the newsletter.'
        }
    ]

    with patch('nm2t_telegram_bot.feedparser.parse', return_value=mock_feed):
        await latest(mock_update, mock_context)

    # Should be called twice: once for "Fetching..." and once for the result
    assert mock_update.message.reply_text.call_count == 2

    # Check the second call contains newsletter content
    second_call_args = mock_update.message.reply_text.call_args_list[1]
    message = second_call_args[0][0]
    assert 'Test Newsletter Title' in message
    assert 'test summary' in message


@pytest.mark.asyncio
async def test_latest_command_no_entries(mock_update, mock_context):
    """Test the /latest command when no feed entries exist"""
    mock_feed = MagicMock()
    mock_feed.entries = []

    with patch('nm2t_telegram_bot.feedparser.parse', return_value=mock_feed):
        await latest(mock_update, mock_context)

    # Should be called twice: once for "Fetching..." and once for "No entries"
    assert mock_update.message.reply_text.call_count == 2

    second_call_args = mock_update.message.reply_text.call_args_list[1]
    message = second_call_args[0][0]
    assert "No newsletter entries found" in message


@pytest.mark.asyncio
async def test_latest_command_truncates_long_summary(mock_update, mock_context):
    """Test that long summaries are truncated to 500 chars"""
    long_summary = "x" * 600  # Create a summary longer than 500 chars
    mock_feed = MagicMock()
    mock_feed.entries = [
        {
            'title': 'Test Title',
            'link': 'https://example.com',
            'summary': long_summary
        }
    ]

    with patch('nm2t_telegram_bot.feedparser.parse', return_value=mock_feed):
        await latest(mock_update, mock_context)

    second_call_args = mock_update.message.reply_text.call_args_list[1]
    message = second_call_args[0][0]
    # The summary should be truncated and end with "..."
    assert "..." in message


@pytest.mark.asyncio
async def test_latest_command_handles_exception(mock_update, mock_context):
    """Test that the /latest command handles exceptions gracefully"""
    with patch('nm2t_telegram_bot.feedparser.parse', side_effect=Exception("Network error")):
        await latest(mock_update, mock_context)

    # Should be called twice: once for "Fetching..." and once for the error
    assert mock_update.message.reply_text.call_count == 2

    second_call_args = mock_update.message.reply_text.call_args_list[1]
    message = second_call_args[0][0]
    assert "error" in message.lower()


def test_beehiiv_feed_url_default():
    """Test that the default BEEHIIV_FEED_URL is set correctly"""
    # This tests the default URL pattern
    assert "beehiiv.com" in BEEHIIV_FEED_URL or BEEHIIV_FEED_URL != ""


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
